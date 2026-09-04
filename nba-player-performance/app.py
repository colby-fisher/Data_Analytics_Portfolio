import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
# Ensure repository root on sys.path for Streamlit Cloud
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title='NBA Rookie Shot Selection', layout='wide')
st.title('NBA Rookie Shot Selection — Player Comparison')

DATA = Path(__file__).resolve().parents[1] / 'Data' / 'rookie_shot_selection_summary.csv'

if not DATA.exists():
    st.error('Summary CSV not found. Run nba-player-performance/src/build_summary.py first.')
    st.stop()

summary = pd.read_csv(DATA)

players = summary['PLAYER_NAME'].unique().tolist()
player = st.selectbox('Player', options=players)

player_df = summary[summary['PLAYER_NAME'] == player].copy()

# KPI cards
col1, col2, col3 = st.columns(3)
col1.metric('Total zones', f"{player_df['SHOT_ZONE_BASIC'].nunique()}")
col2.metric('Total attempts', int(player_df['attempts'].sum()))
# Weighted FG% (by attempts)
wg = (player_df['fg_pct'] * player_df['attempts']).sum() / player_df['attempts'].sum()
col3.metric('Weighted FG%', f"{wg:.2%}")

st.markdown('---')

st.subheader('Attempts and FG% by zone')
fig = px.bar(
    player_df.sort_values('attempts', ascending=False),
    x='SHOT_ZONE_BASIC', y='attempts', color='fg_pct',
    color_continuous_scale='Viridis',  # colorblind-friendly

    labels={'SHOT_ZONE_BASIC':'Zone', 'attempts':'Attempts', 'fg_pct':'FG%'}
)
fig.update_layout(xaxis_tickangle=-45, height=450)
st.plotly_chart(fig, use_container_width=True)

st.subheader('Points per attempt by zone')
fig2 = px.bar(
    player_df.sort_values('points_per_attempt', ascending=False),
    x='SHOT_ZONE_BASIC', y='points_per_attempt', color='points_per_attempt',
    color_continuous_scale='Cividis', labels={'points_per_attempt':'Points per attempt'}  # colorblind-friendly
)
fig2.update_layout(xaxis_tickangle=-45, height=380)
st.plotly_chart(fig2, use_container_width=True)

st.subheader('Zone table')
st.dataframe(player_df[['SHOT_ZONE_BASIC','attempts','makes','fg_pct','shot_share','points_per_attempt']].sort_values('attempts', ascending=False).reset_index(drop=True))

st.markdown('**Notes:** Weighted FG% is calculated by zone FG% weighted by attempts. Small samples may inflate FG% and points per attempt. See project README for methodology and limitations.')
