"""Analytics for experiment A/B sample: power calc and significance tests."""
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
from scipy import stats


def load_results(db_path: Path) -> pd.DataFrame:
    conn = sqlite3.connect(str(db_path))
    df = pd.read_sql('SELECT * FROM ab_results', conn)
    conn.close()
    return df


def summary_by_variant(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby('variant').agg(users=('user_id','count'), conversions=('converted','sum'), revenue=('revenue','sum')).reset_index()
    g['conv_rate'] = g['conversions'] / g['users']
    g['avg_revenue_per_user'] = g['revenue'] / g['users']
    return g


def ttest_conversion(df: pd.DataFrame):
    a = df[df['variant']=='A']['converted']
    b = df[df['variant']=='B']['converted']
    # two-sample proportion test via t-test on binary; fine for small demo
    tstat, p = stats.ttest_ind(a, b, equal_var=False)
    return tstat, p


def power_proportion(p1, p2, n_per_group, alpha=0.05):
    # approximate power for two-sample proportion using normal approximation
    p_pool = (p1 + p2) / 2
    se = np.sqrt(2 * p_pool * (1 - p_pool) / n_per_group)
    z = abs((p2 - p1) / se)
    z_alpha = stats.norm.ppf(1 - alpha/2)
    power = stats.norm.cdf(z - z_alpha)
    return power


if __name__ == '__main__':
    import sys
    db = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'Data' / 'ab.db'
    df = load_results(db)
    print(summary_by_variant(df))
    t, p = ttest_conversion(df)
    print('tstat, p:', t, p)
