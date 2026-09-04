"""Analytics helpers for churn project: retention and revenue-at-risk calculations."""
from pathlib import Path
import sqlite3
import pandas as pd


def load_customers(db_path: Path) -> pd.DataFrame:
    conn = sqlite3.connect(str(db_path))
    df = pd.read_sql('SELECT * FROM customers', conn)
    conn.close()
    return df


def survival_by_tenure(df: pd.DataFrame) -> pd.DataFrame:
    # For each tenure month, compute percent retained (not churned) among customers with that tenure
    grouped = (
        df.groupby('tenure')
        .agg(customers=('customerID','count'), churned=('Churn', lambda x: (x=='Yes').sum()))
        .reset_index()
    )
    grouped['retention_pct'] = 100 * (grouped['customers'] - grouped['churned']) / grouped['customers']
    return grouped.sort_values('tenure')


def retention_by_contract(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(['Contract','tenure'])
        .agg(customers=('customerID','count'), churned=('Churn', lambda x: (x=='Yes').sum()))
        .reset_index()
    )
    grouped['retention_pct'] = 100 * (grouped['customers'] - grouped['churned']) / grouped['customers']
    return grouped.sort_values(['Contract','tenure'])


def revenue_at_risk_by_segment(df: pd.DataFrame, seg_cols=('Contract','InternetService')) -> pd.DataFrame:
    g = (
        df.groupby(list(seg_cols))
        .agg(customers=('customerID','count'), avg_monthly_charges=('MonthlyCharges','mean'), churned=('Churn', lambda x: (x=='Yes').sum()))
        .reset_index()
    )
    g['est_monthly_revenue_lost'] = g['churned'] * g['avg_monthly_charges']
    return g.sort_values('est_monthly_revenue_lost', ascending=False)


if __name__ == '__main__':
    # Quick CLI smoke test when run directly
    import sys
    db = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'Data' / 'churn.db'
    print('Loading', db)
    df = load_customers(db)
    print('Customers loaded:', len(df))
    print('\nSurvival by tenure (top 5):')
    print(survival_by_tenure(df).head())
    print('\nRevenue at risk (top 5):')
    print(revenue_at_risk_by_segment(df).head())
