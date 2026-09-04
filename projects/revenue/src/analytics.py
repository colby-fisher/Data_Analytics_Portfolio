"""Analytics helpers for revenue dashboard."""
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np


def load_orders(db_path: Path) -> pd.DataFrame:
    conn = sqlite3.connect(str(db_path))
    df = pd.read_sql('SELECT * FROM orders', conn, parse_dates=['order_date'])
    conn.close()
    return df


def monthly_kpis(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['month'] = df['order_date'].dt.to_period('M').dt.to_timestamp()
    g = df.groupby('month').agg(orders=('order_id','count'), revenue=('revenue','sum'))
    g['avg_order_value'] = g['revenue'] / g['orders']
    return g.reset_index()


def top_products(df: pd.DataFrame, n=5) -> pd.DataFrame:
    return df.groupby('product').agg(units_sold=('units','sum'), revenue=('revenue','sum')).reset_index().sort_values('revenue', ascending=False).head(n)


def region_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby('region').agg(orders=('order_id','count'), revenue=('revenue','sum')).reset_index().sort_values('revenue', ascending=False)


def detect_monthly_anomalies(kpi_df: pd.DataFrame, z_thresh=2.0) -> pd.DataFrame:
    df = kpi_df.copy()
    if 'revenue' not in df.columns:
        raise ValueError('kpi_df must include revenue column')
    mean = df['revenue'].mean()
    std = df['revenue'].std(ddof=0) if df['revenue'].std(ddof=0) > 0 else 1.0
    df['z'] = (df['revenue'] - mean) / std
    df['anomaly'] = df['z'].abs() > z_thresh
    return df


if __name__ == '__main__':
    import sys
    db = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'Data' / 'revenue.db'
    df = load_orders(db)
    print('Orders:', len(df))
    print(monthly_kpis(df))
