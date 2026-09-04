30-second recruiter summary — Churn & Retention

Problem: Identify customer segments with elevated churn risk and estimate monthly revenue at risk to prioritize retention investments.

Approach: Cleaned IBM Telco sample, compute retention by tenure and segment, and estimate revenue at risk by segment (Contract x InternetService). Visualized survival-like retention, contract-level trends, and a revenue-at-risk heatmap.

Key findings (sample):
- Overall churn: 26.54% (7,043 customers; 1,869 churned).
- Highest estimated monthly revenue at risk concentrated in contract/internet segments with higher churn and above-average monthly charges.

Tools: Python (pandas), SQLite, SQL, Plotly, Streamlit

Business value: Prioritizes high-impact retention actions by segment and quantifies short-term revenue exposure for business stakeholders.
