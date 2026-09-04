import streamlit as st
from pathlib import Path
import sys
# Ensure repository root is on sys.path for imports on Streamlit Cloud
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from projects.revenue.src.analytics import load_orders, monthly_kpis, top_products, region_breakdown, detect_monthly_anomalies
except Exception as exc:
    print(f'Package import failed: {exc}')
    import importlib.util
    analytics_path = Path(__file__).resolve().parent / 'src' / 'analytics.py'
    spec = importlib.util.spec_from_file_location('projects.revenue.src.analytics', analytics_path)
    analytics = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analytics)
    load_orders = analytics.load_orders
    monthly_kpis = analytics.monthly_kpis
    top_products = analytics.top_products
    region_breakdown = analytics.region_breakdown
    detect_monthly_anomalies = analytics.detect_monthly_anomalies
import plotly.express as px

st.set_page_config(page_title='Revenue Dashboard', layout='wide')
st.title('Revenue & Operations Dashboard')

project_dir = Path(__file__).resolve().parent
committed_db = project_dir / 'Data' / 'revenue.db'
DB = committed_db if committed_db.exists() else Path('/tmp/revenue.db')
if not DB.exists():
    st.info('Database not found in the deployed repository. Generating it from the committed sample CSV...')
    with st.spinner('Running ETL to create revenue.db...'):
        import subprocess
        etl_script = project_dir / 'src' / 'etl.py'
        csv_path = project_dir / 'Data' / 'sample_revenue.csv'
        result = subprocess.run(
            [sys.executable, str(etl_script), '--input', str(csv_path), '--db', str(DB)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            error = (result.stderr or result.stdout or 'ETL failed with unknown error')[:1500]
            st.error('ETL failed to create the database.')
            st.code(error)
            st.stop()

with st.spinner('Loading data...'):
    df = load_orders(DB)

col1, col2, col3 = st.columns(3)
col1.metric('Total orders', f"{len(df):,}")
col2.metric('Total revenue', f"${df['revenue'].sum():.2f}")
col3.metric('Avg order value', f"${(df['revenue'].sum()/len(df)) if len(df) else 0:.2f}")

st.markdown('---')

# Monthly trend
st.subheader('Monthly revenue trend')
kpi = monthly_kpis(df)
fig = px.line(kpi, x='month', y='revenue', markers=True, title='Monthly revenue', color_discrete_sequence=['#1170aa'])  # colorblind-friendly blue
# annotate anomalies
anoms = detect_monthly_anomalies(kpi)
fig.add_scatter(x=anoms[anoms['anomaly']]['month'], y=anoms[anoms['anomaly']]['revenue'], mode='markers', marker=dict(color='#d62728', size=10), name='Anomaly')
fig.update_layout(legend_title_text='')
st.plotly_chart(fig, use_container_width=True)

st.subheader('Top products')
st.dataframe(top_products(df))

st.subheader('Region breakdown')
region = region_breakdown(df)
st.dataframe(region)

st.markdown('**Notes:** Small sample data is synthetic. Use the SQL queries in sql/queries.sql for equivalent backend aggregations.')
