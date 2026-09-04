-- SQL queries for revenue dashboard

-- Monthly KPIs
SELECT strftime('%Y-%m-01', order_date) AS month, COUNT(*) AS orders, ROUND(SUM(revenue),2) AS revenue, ROUND(AVG(revenue),2) AS avg_order_value
FROM orders
GROUP BY month
ORDER BY month;

-- Top products by revenue
SELECT product, SUM(units) AS units_sold, ROUND(SUM(revenue),2) AS revenue
FROM orders
GROUP BY product
ORDER BY revenue DESC
LIMIT 10;

-- Revenue by region
SELECT region, COUNT(*) AS orders, ROUND(SUM(revenue),2) AS revenue
FROM orders
GROUP BY region
ORDER BY revenue DESC;
