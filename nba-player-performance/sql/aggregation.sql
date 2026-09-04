-- SQL-style aggregation queries for the NBA rookie shot selection summary
-- These equivalent queries describe the same aggregations performed by build_summary.py

-- 1. Basic summary: attempts, makes, points per player and zone
SELECT PLAYER_NAME, SHOT_ZONE_BASIC,
  COUNT(*) AS attempts,
  SUM(SHOT_MADE_FLAG) AS makes,
  SUM(CASE WHEN SHOT_TYPE LIKE '%3PT%' THEN 3 * SHOT_MADE_FLAG ELSE 2 * SHOT_MADE_FLAG END) AS points,
  ROUND(1.0 * SUM(SHOT_MADE_FLAG) / COUNT(*), 4) AS fg_pct,
  ROUND(1.0 * SUM(CASE WHEN SHOT_TYPE LIKE '%3PT%' THEN 3 * SHOT_MADE_FLAG ELSE 2 * SHOT_MADE_FLAG END) / COUNT(*), 4) AS points_per_attempt
FROM rookie_shots -- replace with your consolidated shots table
GROUP BY PLAYER_NAME, SHOT_ZONE_BASIC
ORDER BY PLAYER_NAME, attempts DESC;

-- 2. Player totals and shot share (requires a CTE)
WITH zone_summary AS (
  SELECT PLAYER_NAME, SHOT_ZONE_BASIC, COUNT(*) AS attempts
  FROM rookie_shots
  GROUP BY PLAYER_NAME, SHOT_ZONE_BASIC
)
SELECT z.PLAYER_NAME, z.SHOT_ZONE_BASIC, z.attempts,
  ROUND(100.0 * z.attempts / SUM(z.attempts) OVER (PARTITION BY z.PLAYER_NAME), 2) AS shot_share_pct
FROM zone_summary z
ORDER BY z.PLAYER_NAME, z.attempts DESC;

-- 3. Top zones by points per attempt for each player
SELECT PLAYER_NAME, SHOT_ZONE_BASIC, points_per_attempt
FROM (
  SELECT PLAYER_NAME, SHOT_ZONE_BASIC,
    SUM(CASE WHEN SHOT_TYPE LIKE '%3PT%' THEN 3 * SHOT_MADE_FLAG ELSE 2 * SHOT_MADE_FLAG END) * 1.0 / COUNT(*) AS points_per_attempt,
    ROW_NUMBER() OVER (PARTITION BY PLAYER_NAME ORDER BY SUM(CASE WHEN SHOT_TYPE LIKE '%3PT%' THEN 3 * SHOT_MADE_FLAG ELSE 2 * SHOT_MADE_FLAG END) * 1.0 / COUNT(*) DESC) AS rn
  FROM rookie_shots
  GROUP BY PLAYER_NAME, SHOT_ZONE_BASIC
) t
WHERE rn <= 3
ORDER BY PLAYER_NAME, points_per_attempt DESC;

-- Notes:
-- Replace `rookie_shots` with your underlying shots table name or a view built from the raw CSVs.
-- These queries are intended for use in SQLite/Postgres-compatible engines with window function support.
