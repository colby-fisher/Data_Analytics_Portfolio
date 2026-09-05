"""Streamlit interface for the AI Basketball Scouting Assistant."""

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from src.analytics import calculate_player_metrics, compare_players  # noqa: E402
from src.data_loader import ShotDataError, get_player_shots, list_players, load_shot_data  # noqa: E402
from src.scouting import generate_comparison_report, generate_player_report  # noqa: E402

st.set_page_config(page_title="AI Basketball Scouting Assistant", page_icon="🏀", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 2rem;}
[data-testid="stMetric"] {background: #f7f8fa; border: 1px solid #e5e7eb; padding: 1rem; border-radius: .7rem;}
.eyebrow {color: #c45116; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: .8rem;}
.source-box {border-left: 4px solid #c45116; padding: .15rem 1rem; color: #4b5563;}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_project_data() -> pd.DataFrame:
    return load_shot_data(PROJECT_DIR / "Data")


def format_pct(value: float) -> str:
    return f"{value:.1%}"


def metrics_frame(metrics: dict) -> pd.DataFrame:
    return pd.DataFrame(metrics["zones"])


def show_metric_cards(metrics: dict) -> None:
    values = [
        ("FGA", f"{metrics['fga']:,}"), ("FG%", format_pct(metrics["fg_pct"])),
        ("3PT attempt rate", format_pct(metrics["three_point_attempt_rate"])),
        ("Restricted-area rate", format_pct(metrics["restricted_area_attempt_rate"])),
        ("Mid-range rate", format_pct(metrics["mid_range_attempt_rate"])),
        ("Avg. shot distance", f"{metrics['average_shot_distance_ft']:.1f} ft"),
    ]
    for column, (label, value) in zip(st.columns(6), values):
        column.metric(label, value)


def show_zone_profile(metrics: dict) -> None:
    zones = metrics_frame(metrics)
    zones["Attempt rate (%)"] = zones["attempt_rate"] * 100
    zones["FG%"] = zones["fg_pct"] * 100
    chart = px.bar(
        zones.sort_values("attempt_rate", ascending=False), x="zone", y="Attempt rate (%)", color="FG%",
        color_continuous_scale="Blues", labels={"zone": "Shot zone"},
        hover_data={"attempts": True, "makes": True, "points_per_attempt": ":.3f"},
    )
    chart.update_layout(height=420, xaxis_tickangle=-30)
    st.plotly_chart(chart, width="stretch")


def show_shot_map(player_shots: pd.DataFrame, player_name: str) -> None:
    plot_data = player_shots.copy()
    plot_data["Result"] = plot_data["SHOT_MADE_FLAG"].map({1: "Made", 0: "Missed"})
    chart = px.scatter(
        plot_data, x="LOC_X", y="LOC_Y", color="Result", opacity=0.62,
        color_discrete_map={"Made": "#16836b", "Missed": "#c7cbd1"},
        hover_data=["SHOT_ZONE_BASIC", "SHOT_DISTANCE", "SHOT_TYPE"], title=f"{player_name} shot locations",
    )
    chart.update_yaxes(scaleanchor="x", scaleratio=1)
    chart.update_layout(height=560, legend_title_text="Result")
    st.plotly_chart(chart, width="stretch")


def show_zone_table(metrics: dict) -> None:
    zones = metrics_frame(metrics).rename(columns={
        "zone": "Zone", "attempts": "Attempts", "makes": "Makes", "fg_pct": "FG%",
        "attempt_rate": "Attempt rate", "points_per_attempt": "Points / attempt",
        "average_distance_ft": "Avg. distance (ft)",
    })
    st.dataframe(zones.style.format({
        "FG%": "{:.1%}", "Attempt rate": "{:.1%}", "Points / attempt": "{:.3f}", "Avg. distance (ft)": "{:.1f}"
    }), width="stretch", hide_index=True)


def show_report(result) -> None:
    (st.success if result.mode == "llm" else st.info)(result.notice, icon="✨" if result.mode == "llm" else "🧮")
    st.markdown("**Interpretation layer** — narrative derived from the calculated snapshot above")
    st.markdown(result.content)


st.markdown('<div class="eyebrow">Handshake AI Showcase · Data Analytics Portfolio</div>', unsafe_allow_html=True)
st.title("AI Basketball Scouting Assistant")
st.write("Turn shot-level data into explainable scouting evidence. The application calculates every statistic first, then uses either a grounded LLM or a transparent rules-based fallback to interpret the results.")
st.markdown('<div class="source-box"><strong>Data boundary:</strong> This is a static 2025–26 portfolio dataset. It evaluates field-goal locations and outcomes only—not complete player value or live NBA performance.</div>', unsafe_allow_html=True)

try:
    shots = load_project_data()
except ShotDataError as exc:
    st.error(f"The scouting dataset could not be loaded: {exc}")
    st.stop()

players = list_players(shots)
individual_tab, comparison_tab, methodology_tab = st.tabs(["Player scouting report", "Player comparison", "How it works"])

with individual_tab:
    st.subheader("Individual player profile")
    player = st.selectbox("Select a player", players, key="individual_player")
    player_metrics = calculate_player_metrics(shots, player)
    player_shots = get_player_shots(shots, player)
    st.markdown("### Calculated data")
    st.caption("Every value below is calculated directly from the selected player's shot rows.")
    show_metric_cards(player_metrics)
    zone_tab, location_tab, existing_tab = st.tabs(["Shot profile", "Interactive locations", "Existing analysis visual"])
    with zone_tab:
        show_zone_profile(player_metrics)
        show_zone_table(player_metrics)
    with location_tab:
        show_shot_map(player_shots, player)
    with existing_tab:
        image_path = PROJECT_DIR / "Visuals" / (player.lower().replace(" ", "_") + "_shot_chart.png")
        if image_path.exists():
            st.image(str(image_path), caption=f"Existing notebook-generated shot chart for {player}", width="stretch")
        else:
            st.info("No existing exported shot chart is available for this player.")
    st.markdown("### Scouting report")
    if st.button("Generate scouting report", type="primary", key="player_report_button"):
        with st.spinner("Interpreting the calculated profile..."):
            st.session_state["player_report"] = (player, generate_player_report(player_metrics))
    stored = st.session_state.get("player_report")
    if stored and stored[0] == player:
        show_report(stored[1])
    else:
        st.caption("Generate a report to interpret the calculated evidence. No API key is required.")

with comparison_tab:
    st.subheader("Side-by-side scouting comparison")
    selector_a, selector_b = st.columns(2)
    player_a = selector_a.selectbox("Player A", players, index=0, key="player_a")
    player_b = selector_b.selectbox("Player B", players, index=1 if len(players) > 1 else 0, key="player_b")
    if player_a == player_b:
        st.warning("Select two different players to calculate a comparison.")
    else:
        comparison = compare_players(shots, player_a, player_b)
        a, b = comparison["player_a"], comparison["player_b"]
        st.markdown("### Calculated data")
        rows = [
            ("FGA", f"{a['fga']:,}", f"{b['fga']:,}"), ("FG%", format_pct(a["fg_pct"]), format_pct(b["fg_pct"])),
            ("3PT attempt rate", format_pct(a["three_point_attempt_rate"]), format_pct(b["three_point_attempt_rate"])),
            ("Restricted-area rate", format_pct(a["restricted_area_attempt_rate"]), format_pct(b["restricted_area_attempt_rate"])),
            ("Mid-range rate", format_pct(a["mid_range_attempt_rate"]), format_pct(b["mid_range_attempt_rate"])),
            ("Average shot distance", f"{a['average_shot_distance_ft']:.1f} ft", f"{b['average_shot_distance_ft']:.1f} ft"),
            ("Points per attempt", f"{a['points_per_attempt']:.3f}", f"{b['points_per_attempt']:.3f}"),
        ]
        st.dataframe(pd.DataFrame(rows, columns=["Metric", player_a, player_b]), width="stretch", hide_index=True)
        zone_data = []
        for label, profile in [(player_a, a), (player_b, b)]:
            zone_data.extend({"Player": label, "Zone": z["zone"], "Attempt rate (%)": z["attempt_rate"] * 100} for z in profile["zones"])
        chart = px.bar(pd.DataFrame(zone_data), x="Zone", y="Attempt rate (%)", color="Player", barmode="group", color_discrete_sequence=["#c45116", "#315b7d"], title="Shot-zone distribution")
        chart.update_layout(height=430, xaxis_tickangle=-30)
        st.plotly_chart(chart, width="stretch")
        st.markdown("### AI-assisted comparison")
        if st.button("Generate player comparison", type="primary", key="comparison_report_button"):
            with st.spinner("Interpreting the calculated differences..."):
                st.session_state["comparison_report"] = (player_a, player_b, generate_comparison_report(comparison))
        stored_comparison = st.session_state.get("comparison_report")
        if stored_comparison and stored_comparison[:2] == (player_a, player_b):
            show_report(stored_comparison[2])
        else:
            st.caption("Generate a comparison to interpret the calculated differences. No API key is required.")

with methodology_tab:
    st.subheader("Evidence first, interpretation second")
    st.markdown("""
1. **Validated source data:** local shot-level CSVs are checked for required columns, numeric values, valid make/miss flags, and duplicate event keys.
2. **Deterministic analytics:** pandas functions calculate totals, rates, distances, zone distributions, and player-to-player differences.
3. **Bounded interpretation:** the optional LLM receives only the calculated structure and instructions forbidding invented statistics.
4. **Resilient fallback:** if no API key is configured—or a provider call fails—the same evidence is interpreted by transparent rules.

The analysis does not include defense, assists, turnovers, free throws, defender distance, play type, lineup context, or film grades. It should support scouting questions, not replace film or holistic evaluation.
""")
