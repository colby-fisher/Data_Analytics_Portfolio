import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
# Ensure repository root is on sys.path so project packages import correctly on Streamlit Cloud
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from projects.churn.src.analytics import load_customers, survival_by_tenure, retention_by_contract, revenue_at_risk_by_segment
except Exception as e:
    print('Package import failed:', e)
    # Fallback: load module directly from file path to avoid package import issues in deploy
    import importlib.util
    analytics_path = Path(__file__).resolve().parent / 'src' / 'analytics.py'
    print('Loading analytics module from', analytics_path)
    spec = importlib.util.spec_from_file_location('projects.churn.src.analytics', str(analytics_path))
    analytics = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analytics)
    load_customers = analytics.load_customers
    survival_by_tenure = analytics.survival_by_tenure
    retention_by_contract = analytics.retention_by_contract
    revenue_at_risk_by_segment = analytics.revenue_at_risk_by_segment

st.set_page_config(page_title='Churn & Retention — Full', layout='wide')
st.title('Churn & Retention — Cohorts & Revenue at Risk')

# Preferred DB path inside the project data
committed_db = Path(__file__).resolve().parent / 'Data' / 'churn.db'
# Runtime DB should be writable; if deployed FS is read-only, use /tmp
runtime_db = committed_db
# If committed DB missing or not readable/writable, fall back to /tmp
import os
if not committed_db.exists() or not os.access(str(committed_db), os.R_OK):
    runtime_db = Path('/tmp') / 'churn.db'

# If runtime DB doesn't exist, attempt ETL (write into runtime_db)
if not runtime_db.exists():
    st.info('Database not found in the deployed repository. Attempting to generate it (writes to /tmp on this host)...')
    with st.spinner('Running ETL to create churn.db — this may take a few seconds'):
        import subprocess
        etl_script = Path(__file__).resolve().parent / 'src' / 'etl.py'
        csv_path = Path(__file__).resolve().parent / 'Data' / 'Telco-Customer-Churn.csv'
        try:
            res = subprocess.run([sys.executable, str(etl_script), '--input', str(csv_path), '--db', str(runtime_db)], capture_output=True, text=True, check=False)
        except Exception as exc:
            st.error(f'Failed to start ETL: {exc}')
            st.stop()
        if res.returncode != 0:
            # show a truncated stderr to assist debugging
            err = (res.stderr or res.stdout or 'ETL failed with unknown error')[:1500]
            st.error('ETL failed to create the database. See logs for details.')
            st.code(err)
            st.stop()

# Load
with st.spinner('Loading data...'):
    df = load_customers(runtime_db)

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
total = len(df)
churned = (df['Churn'] == 'Yes').sum()
churn_pct = 100 * churned / total if total else 0
avg_monthly = df['MonthlyCharges'].mean()
estimated_monthly_risk = df.loc[df['Churn']=='Yes','MonthlyCharges'].sum()

col1.metric('Customers', f'{total:,}')
col2.metric('Churned', f'{churned:,}', delta=f'{churn_pct:.2f}%')
col3.metric('Avg monthly charge', f'${avg_monthly:.2f}')
col4.metric('Estimated monthly revenue lost', f'${estimated_monthly_risk:,.2f}')

st.markdown('---')

# Retention / survival by tenure
st.subheader('Retention by tenure (survival curve)')
sv = survival_by_tenure(df)
fig = px.line(sv, x='tenure', y='retention_pct', markers=True, labels={'tenure':'Tenure (months)', 'retention_pct':'% retained'})
fig.update_layout(height=420)
st.plotly_chart(fig, use_container_width=True)

st.caption('Retention here is percent of customers at each tenure month who have not churned. This is an aggregate survival view (no cohort start date in dataset).')

# Retention by contract
st.subheader('Retention by tenure, by contract')
ret_contract = retention_by_contract(df)
contracts = ret_contract['Contract'].unique().tolist()
sel_contracts = st.multiselect('Contracts to show', options=contracts, default=contracts)
plot_df = ret_contract[ret_contract['Contract'].isin(sel_contracts)]
fig2 = px.line(plot_df, x='tenure', y='retention_pct', color='Contract', labels={'tenure':'Tenure (months)', 'retention_pct':'% retained'})
fig2.update_layout(height=420)
st.plotly_chart(fig2, use_container_width=True)

st.markdown('---')

# Revenue at risk heatmap
st.subheader('Estimated monthly revenue at risk by Contract & InternetService')
rev = revenue_at_risk_by_segment(df)
heat = rev.pivot(index='Contract', columns='InternetService', values='est_monthly_revenue_lost').fillna(0)
fig3 = px.imshow(heat, labels=dict(x='InternetService', y='Contract', color='Est monthly revenue lost'), text_auto='.2s', aspect='auto', color_continuous_scale='Viridis')
fig3.update_coloraxes(colorbar_title='Est monthly revenue lost')  # clearer label for accessibility
fig3.update_layout(height=420)
st.plotly_chart(fig3, use_container_width=True)

st.markdown('---')

st.subheader('Segment table: Estimated revenue at risk')
st.dataframe(rev[['Contract','InternetService','customers','avg_monthly_charges','churned','est_monthly_revenue_lost']].reset_index(drop=True))

st.markdown('**Notes & interpretation:**')
st.write('- These figures are estimates based on current churned customers and average monthly charges in each segment.')
st.write('- Use cohort tracking over time and customer lifetime value models before prioritizing retention spend.')
