from pathlib import Path
from projects.experiment.src.analytics import load_results, summary_by_variant, ttest_conversion


def test_experiment_summary_and_ttest():
    db = Path(__file__).resolve().parents[1] / 'Data' / 'ab.db'
    df = load_results(db)
    s = summary_by_variant(df)
    assert 'conv_rate' in s.columns
    t, p = ttest_conversion(df)
    assert p >= 0 and p <= 1
