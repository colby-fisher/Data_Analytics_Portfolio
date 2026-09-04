from projects.revenue.src.analytics import load_orders, monthly_kpis, detect_monthly_anomalies
from pathlib import Path

def test_monthly_kpis_and_anomalies():
    db = Path(__file__).resolve().parents[1] / 'Data' / 'revenue.db'
    df = load_orders(db)
    kpi = monthly_kpis(df)
    assert 'revenue' in kpi.columns
    anoms = detect_monthly_anomalies(kpi)
    assert 'anomaly' in anoms.columns
