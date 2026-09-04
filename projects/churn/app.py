import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import sys
# Ensure repository root is on sys.path for imports on Streamlit Cloud
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DB = Path(__file__).resolve().parents[1] / 'Data' / 'churn.db'

st.set_page_config(page_title='Churn & Retention Explorer', layout='wide')
st.title('Churn & Retention — Telco Customer Churn')

if not DB.exists():
    st.error('Database not found. Run the ETL: projects/churn/src/etl.py')
else:
    conn = sqlite3.connect(str(DB))
    df = pd.read_sql('SELECT * FROM customers LIMIT 10000', conn)

    col1, col2, col3 = st.columns(3)
    total = len(df)
    churned = (df['Churn'] == 'Yes').sum()
    churn_pct = 100 * churned / total if total else 0

    col1.metric('Customers', f'{total}')
    col2.metric('Churned', f'{churned}', delta=f'{churn_pct:.2f}%')
    col3.metric('Churn rate', f'{churn_pct:.2f}%')

    contract = st.selectbox('Contract type', options=['All'] + sorted(df['Contract'].dropna().unique().tolist()))
    if contract != 'All':
        df = df[df['Contract'] == contract]

    st.subheader('Churn by Contract & Monthly Charges')
    churn_by_contract = (
        df.groupby('Contract')
        .agg(customers=('customerID','count'), churned=('Churn', lambda x: (x=='Yes').sum()))
        .reset_index()
    )
    churn_by_contract['churn_pct'] = 100 * churn_by_contract['churned'] / churn_by_contract['customers']
    st.dataframe(churn_by_contract)

    st.subheader('Sample of customers (first 200)')
    st.dataframe(df.head(200))

    conn.close()
