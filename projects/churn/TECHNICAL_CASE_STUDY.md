Technical case study — Churn & Retention (Telco)

Problem statement
Estimate short-term revenue exposure and identify retention-priority customer segments using the IBM Telco Customer Churn sample.

Stakeholders
Retention manager, product-owner, finance analyst.

Data
IBM Telco Customer Churn CSV (stored at projects/churn/Data/Telco-Customer-Churn.csv). Key fields: customerID, tenure, MonthlyCharges, TotalCharges, Contract, InternetService, Churn.

Approach
- Reproducible ETL: projects/churn/src/etl.py to normalize types and write customers table to projects/churn/Data/churn.db.
- Validation: required-column checks and numeric coercion for monetary fields.
- Analytics: survival_by_tenure, retention_by_contract, revenue_at_risk_by_segment (see projects/churn/src/analytics.py).
- Interactive visualization: Streamlit app at projects/churn/app_full.py.

Key analyses
- Retention by tenure (survival-like curve) to identify months with high dropout.
- Retention by contract to prioritize contract-specific interventions.
- Estimated monthly revenue at risk by segment (customers churned * avg monthly charges).

Limitations
- Dataset lacks explicit signup date for true cohort start-date analysis; tenure is used as a proxy.
- Estimates assume churned customers represent immediate revenue loss; incorporate CLV for longer-term prioritization.

How to reproduce (local)
1. Create venv and install deps: pip install -r requirements.txt
2. Run ETL: python3 projects/churn/src/etl.py --input projects/churn/Data/Telco-Customer-Churn.csv --db projects/churn/Data/churn.db
3. Run Streamlit app: streamlit run projects/churn/app_full.py

Next steps
- Add unit tests for analytics (done in tests/). Add notebook explaining code and interpretive decisions.
