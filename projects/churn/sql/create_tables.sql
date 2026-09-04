-- Create a simple normalized schema for churn analysis
BEGIN TRANSACTION;

DROP TABLE IF EXISTS customers_raw;
CREATE TABLE customers_raw AS SELECT * FROM csv_read('Telco-Customer-Churn.csv');

-- A target customers table with cleaned types for analysis
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    customerID TEXT PRIMARY KEY,
    gender TEXT,
    SeniorCitizen INTEGER,
    Partner TEXT,
    Dependents TEXT,
    tenure INTEGER,
    PhoneService TEXT,
    MultipleLines TEXT,
    InternetService TEXT,
    OnlineSecurity TEXT,
    OnlineBackup TEXT,
    DeviceProtection TEXT,
    TechSupport TEXT,
    StreamingTV TEXT,
    StreamingMovies TEXT,
    Contract TEXT,
    PaperlessBilling TEXT,
    PaymentMethod TEXT,
    MonthlyCharges REAL,
    TotalCharges REAL,
    Churn TEXT
);

COMMIT;

-- Note: csv_read is a placeholder for SQLite import; the ETL script loads CSV into SQLite programmatically.
