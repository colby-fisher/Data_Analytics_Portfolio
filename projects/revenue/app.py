import streamlit as st
from pathlib import Path
from projects.revenue.src.analytics import load_orders, monthly_kpis, top_products, region_breakdown, detect_monthly_anomalies
import plotly.express as px

st.set_page_config(page_title='Revenue Dashboard', layout='wide')
st.title('Revenue & Operations Dashboard')

DB = Path(__file__).resolve().parents[1] / 'Data' / 'revenue.db'
if not DB.exists():
    st.error('Database not found. Run ETL: projects/revenue/src/etl.py')
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
