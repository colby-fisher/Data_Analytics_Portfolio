import streamlit as st
from pathlib import Path
import sys
# Ensure repository root is on sys.path for imports on Streamlit Cloud
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from projects.experiment.src.analytics import load_results, summary_by_variant, ttest_conversion, power_proportion
import pandas as pd

st.set_page_config(page_title='Experiment Analysis', layout='wide')
st.title('A/B Test Explorer')

DB = Path(__file__).resolve().parents[1] / 'Data' / 'ab.db'
if not DB.exists():
    st.error('Database not found. Run ETL: projects/experiment/src/etl.py')
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
