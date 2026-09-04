import streamlit as st
from pathlib import Path
import sys
# Ensure repository root is on sys.path for imports on Streamlit Cloud
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from projects.experiment.src.analytics import load_results, summary_by_variant, ttest_conversion, power_proportion
except Exception as exc:
    print(f'Package import failed: {exc}')
    import importlib.util
    analytics_path = Path(__file__).resolve().parent / 'src' / 'analytics.py'
    spec = importlib.util.spec_from_file_location('projects.experiment.src.analytics', analytics_path)
    analytics = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analytics)
    load_results = analytics.load_results
    summary_by_variant = analytics.summary_by_variant
    ttest_conversion = analytics.ttest_conversion
    power_proportion = analytics.power_proportion
import pandas as pd

st.set_page_config(page_title='Experiment Analysis', layout='wide')
st.title('A/B Test Explorer')

project_dir = Path(__file__).resolve().parent
committed_db = project_dir / 'Data' / 'ab.db'
DB = committed_db if committed_db.exists() else Path('/tmp/ab.db')
if not DB.exists():
    st.info('Database not found in the deployed repository. Generating it from the committed sample CSV...')
    with st.spinner('Running ETL to create ab.db...'):
        import subprocess
        result = subprocess.run(
            [
                sys.executable,
                str(project_dir / 'src' / 'etl.py'),
                '--input',
                str(project_dir / 'Data' / 'sample_ab_test.csv'),
                '--db',
                str(DB),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            error = (result.stderr or result.stdout or 'ETL failed with unknown error')[:1500]
            st.error('ETL failed to create the database.')
            st.code(error)
            st.stop()

df = load_results(DB)
summary = summary_by_variant(df)
st.subheader('Variant summary')
st.dataframe(summary)

st.subheader('Conversion t-test (A vs B)')
tstat, p = ttest_conversion(df)
st.write(f't-statistic: {tstat:.4f}, p-value: {p:.4f}')

st.subheader('Power analysis (approximate)')
cols = st.columns(3)
p1 = cols[0].number_input('Baseline conversion (p1)', value=float(summary.loc[summary.variant=='A','conv_rate'].iloc[0]))
p2 = cols[1].number_input('Treatment conversion (p2)', value=float(summary.loc[summary.variant=='B','conv_rate'].iloc[0]))
n = cols[2].number_input('Sample size per group', value=int(summary['users'].mean()))
power = power_proportion(p1, p2, n)
st.write(f'Approx power: {power:.3f} (normal approx)')

st.markdown('**Notes:** This demo uses an approximate normal-approx power calc and t-test on binary outcomes for illustration. For production, use proportion tests and regression adjustment.')
