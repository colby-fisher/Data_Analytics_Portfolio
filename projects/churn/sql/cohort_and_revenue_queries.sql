-- Cohort/retention and revenue-at-risk queries for Telco churn

-- 1. Survival table by tenure month (percent remaining)
SELECT tenure,
  COUNT(*) AS customers,
  SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END) AS churned,
  ROUND(100.0 * SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_pct,
  ROUND(100.0 * SUM(CASE WHEN Churn='Yes' THEN 0 ELSE 1 END) / COUNT(*), 2) AS retention_pct
FROM customers
GROUP BY tenure
ORDER BY tenure;

-- 2. Retention by tenure for each contract type
SELECT Contract, tenure,
  COUNT(*) AS customers,
  ROUND(100.0 * SUM(CASE WHEN Churn='Yes' THEN 0 ELSE 1 END) / COUNT(*), 2) AS retention_pct
FROM customers
GROUP BY Contract, tenure
ORDER BY Contract, tenure;

-- 3. Estimated monthly revenue at risk by Contract x InternetService
WITH seg AS (
  SELECT Contract, InternetService, COUNT(*) AS customers, AVG(MonthlyCharges) AS avg_mch,
    SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END) AS churned
  FROM customers
  GROUP BY Contract, InternetService
)
SELECT Contract, InternetService, customers, ROUND(avg_mch,2) AS avg_monthly_charges,
  ROUND(churned * avg_mch, 2) AS est_monthly_revenue_lost
FROM seg
ORDER BY est_monthly_revenue_lost DESC;
