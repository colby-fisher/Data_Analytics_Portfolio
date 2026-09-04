Technical case study — Revenue & Operations Dashboard

Problem statement
Provide timely KPIs and drilldowns for revenue, products, and regions using transaction data to support ops and merchandising decisions.

Data
Small sample transactions in Data/sample_revenue.csv (order-level data: order_id, order_date, customer_id, region, product, units, unit_price).

Approach
- ETL: projects/revenue/src/etl.py computes revenue per order and writes SQLite orders table.
- Analytics: monthly_kpis, top_products, region_breakdown, anomaly detection (projects/revenue/src/analytics.py).
- Interactive: Streamlit dashboard at projects/revenue/app.py.

Reproducibility
- Run ETL and then the app as documented in README.

Limitations
- Provided sample is intentionally small; production datasets require batching, partitioning, and performance testing.
