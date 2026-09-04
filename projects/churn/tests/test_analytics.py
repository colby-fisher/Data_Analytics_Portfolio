import pathlib
import pandas as pd
from projects.churn.src.analytics import load_customers, survival_by_tenure, revenue_at_risk_by_segment


def test_survival_retention_pct_range():
    db = pathlib.Path(__file__).resolve().parents[1] / 'Data' / 'churn.db'
    df = load_customers(db)
    sv = survival_by_tenure(df)
    assert 'retention_pct' in sv.columns
    # retention percent should be between 0 and 100
    assert sv['retention_pct'].between(0,100).all()


def test_revenue_at_risk_nonnegative():
    db = pathlib.Path(__file__).resolve().parents[1] / 'Data' / 'churn.db'
    df = load_customers(db)
    rev = revenue_at_risk_by_segment(df)
    assert 'est_monthly_revenue_lost' in rev.columns
    assert (rev['est_monthly_revenue_lost'] >= 0).all()
