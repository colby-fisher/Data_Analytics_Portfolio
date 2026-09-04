"""ETL for Telco Customer Churn sample

Produces a local SQLite database with cleaned `customers` table and basic validation checks.
"""
import argparse
from pathlib import Path
import sqlite3
import pandas as pd


def clean_telco(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Standardize column names
    df.columns = [c.strip() for c in df.columns]

    # Convert TotalCharges to numeric (some rows may be blank)
    if 'TotalCharges' in df.columns:
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')

    # Tenure may be object; coerce
    if 'tenure' in df.columns:
        df['tenure'] = pd.to_numeric(df['tenure'], errors='coerce').fillna(0).astype(int)

    # Fill missing MonthlyCharges with median
    if 'MonthlyCharges' in df.columns:
        df['MonthlyCharges'] = pd.to_numeric(df['MonthlyCharges'], errors='coerce')
        df['MonthlyCharges'] = df['MonthlyCharges'].fillna(df['MonthlyCharges'].median())

    # Ensure Churn is Yes/No
    if 'Churn' in df.columns:
        df['Churn'] = df['Churn'].astype(str).str.strip()

    return df


def run(input_csv: Path, db_path: Path) -> None:
    df = pd.read_csv(input_csv)
    df_clean = clean_telco(df)

    # Basic validations
    required = ['customerID', 'Churn']
    missing = [c for c in required if c not in df_clean.columns]
    if missing:
        raise SystemExit(f"Input missing required columns: {missing}")

    # Write to SQLite
    conn = sqlite3.connect(str(db_path))
    df_clean.to_sql('customers_raw', conn, if_exists='replace', index=False)

    # Create a curated customers table
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS customers')
    cur.execute(
        '''
        CREATE TABLE customers AS
        SELECT
          customerID AS customerID,
          gender,
          CASE WHEN SeniorCitizen IN (1, '1') THEN 1 ELSE 0 END AS SeniorCitizen,
          Partner, Dependents, CAST(tenure AS INTEGER) AS tenure,
          PhoneService, MultipleLines, InternetService, OnlineSecurity,
          OnlineBackup, DeviceProtection, TechSupport, StreamingTV,
          StreamingMovies, Contract, PaperlessBilling, PaymentMethod,
          CAST(MonthlyCharges AS REAL) AS MonthlyCharges,
          CAST(TotalCharges AS REAL) AS TotalCharges,
          Churn
        FROM customers_raw;
        ''')
    conn.commit()

    # Quick validation checks
    total = cur.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
    churned = cur.execute("SELECT COUNT(*) FROM customers WHERE Churn='Yes'").fetchone()[0]
    print(f'Wrote {total:,} customers to {db_path}. Churned: {churned:,} ({100*churned/total:.2f}%)')
    conn.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True, help='Path to Telco CSV')
    p.add_argument('--db', required=True, help='Output SQLite DB path')
    args = p.parse_args()
    run(Path(args.input), Path(args.db))
