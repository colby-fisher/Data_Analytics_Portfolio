"""ETL for sample revenue data: loads CSV, computes revenue, and writes SQLite DB."""
import argparse
from pathlib import Path
import sqlite3
import pandas as pd


def run(input_csv: Path, db_path: Path):
    df = pd.read_csv(input_csv, parse_dates=['order_date'])
    df = df.copy()
    df['revenue'] = df['units'] * df['unit_price']
    # Basic validation
    required = ['order_id','order_date','customer_id','units','unit_price']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f'Missing required columns: {missing}')

    # Write to SQLite
    conn = sqlite3.connect(str(db_path))
    df.to_sql('orders_raw', conn, if_exists='replace', index=False)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS orders')
    cur.execute('''
    CREATE TABLE orders AS
    SELECT order_id, date(order_date) AS order_date, customer_id, region, product, units, unit_price, revenue
    FROM orders_raw;
    ''')
    conn.commit()
    total = cur.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    total_rev = cur.execute('SELECT ROUND(SUM(revenue),2) FROM orders').fetchone()[0]
    print(f'Wrote {total} orders to {db_path}. Total revenue: ${total_rev}')
    conn.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--db', required=True)
    args = p.parse_args()
    run(Path(args.input), Path(args.db))
