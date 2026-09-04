-- Sample analytic queries for churn project

-- 1. Overall churn rate
SELECT
  COUNT(*) AS customers,
  SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
  ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_pct
FROM customers;

-- 2. Churn rate by contract type
SELECT Contract, COUNT(*) AS customers,
  SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END) AS churned,
  ROUND(100.0 * SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_pct
FROM customers
GROUP BY Contract
ORDER BY churn_pct DESC;

-- 3. Estimated monthly revenue at risk by segment (MonthlyCharges * churn_rate * customers)
WITH seg AS (
  SELECT Contract, COUNT(*) AS customers, AVG(MonthlyCharges) AS avg_mch,
    SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END) AS churned
  FROM customers
  GROUP BY Contract
)
SELECT Contract, customers, avg_mch,
  ROUND(churned*avg_mch, 2) AS estimated_monthly_revenue_lost
FROM seg
ORDER BY estimated_monthly_revenue_lost DESC;
