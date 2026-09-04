Revenue & Operations Dashboard — Sample Retail Data

Executive summary

This demo dashboard summarizes transaction-level sales data, tracks revenue trends, highlights top products and regions, and surfaces monthly anomalies. It is designed to show practical BI skills: SQL aggregations, reproducible ETL, interactive Streamlit visualizations, and clear KPI definitions.

How to run
1. Create venv & install deps: pip install -r requirements.txt
2. Run ETL to create SQLite DB:
   python3 projects/revenue/src/etl.py --input projects/revenue/Data/sample_revenue.csv --db projects/revenue/Data/revenue.db
3. Run dashboard:
   streamlit run projects/revenue/app.py

What's included
- Data/sample_revenue.csv — small sample transactions
- src/etl.py — reproducible ETL (computes revenue per order)
- src/analytics.py — aggregation and anomaly detection helpers
- sql/queries.sql — equivalent SQL queries
- app.py — Streamlit dashboard
- RECRUITER_SUMMARY.md, TECHNICAL_CASE_STUDY.md
