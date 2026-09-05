"""Deterministic basketball calculations used by the app and AI layer."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .data_loader import get_player_shots


def _safe_rate(numerator: int | float, denominator: int | float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def calculate_zone_metrics(player_shots: pd.DataFrame) -> pd.DataFrame:
    """Calculate makes, attempts, efficiency, share, and value for each zone."""
    frame = player_shots.copy()
    frame["POINT_VALUE"] = np.where(frame["SHOT_TYPE"].eq("3PT Field Goal"), 3, 2)
    frame["POINTS"] = frame["SHOT_MADE_FLAG"] * frame["POINT_VALUE"]
    zones = (
        frame.groupby("SHOT_ZONE_BASIC", dropna=False)
        .agg(
            attempts=("SHOT_MADE_FLAG", "size"),
            makes=("SHOT_MADE_FLAG", "sum"),
            points=("POINTS", "sum"),
            average_distance_ft=("SHOT_DISTANCE", "mean"),
        )
        .reset_index()
        .rename(columns={"SHOT_ZONE_BASIC": "zone"})
    )
    total_attempts = int(zones["attempts"].sum())
    zones["fg_pct"] = zones["makes"] / zones["attempts"]
    zones["attempt_rate"] = zones["attempts"] / total_attempts
    zones["points_per_attempt"] = zones["points"] / zones["attempts"]
    return zones.sort_values(["attempts", "zone"], ascending=[False, True]).reset_index(drop=True)


def calculate_player_metrics(shots: pd.DataFrame, player_name: str) -> dict[str, Any]:
    """Return JSON-safe player totals and zone distribution from shot-level data."""
    player = get_player_shots(shots, player_name)
    attempts = len(player)
    makes = int(player["SHOT_MADE_FLAG"].sum())
    is_three = player["SHOT_TYPE"].eq("3PT Field Goal")
    point_values = np.where(is_three, 3, 2)
    points = int((player["SHOT_MADE_FLAG"] * point_values).sum())
    zones = calculate_zone_metrics(player)

    def zone_rate(zone: str) -> float:
        return float(player["SHOT_ZONE_BASIC"].eq(zone).mean())

    zone_records = []
    for row in zones.itertuples(index=False):
        zone_records.append(
            {
                "zone": str(row.zone),
                "attempts": int(row.attempts),
                "makes": int(row.makes),
                "fg_pct": float(row.fg_pct),
                "attempt_rate": float(row.attempt_rate),
                "points_per_attempt": float(row.points_per_attempt),
                "average_distance_ft": float(row.average_distance_ft),
            }
        )

    return {
        "player_name": player_name,
        "fga": int(attempts),
        "fgm": makes,
        "fg_pct": _safe_rate(makes, attempts),
        "three_point_attempts": int(is_three.sum()),
        "three_point_attempt_rate": float(is_three.mean()),
        "restricted_area_attempt_rate": zone_rate("Restricted Area"),
        "mid_range_attempt_rate": zone_rate("Mid-Range"),
        "average_shot_distance_ft": float(player["SHOT_DISTANCE"].mean()),
        "points_from_field_goals": points,
        "points_per_attempt": _safe_rate(points, attempts),
        "zones": zone_records,
    }


def compare_players(
    shots: pd.DataFrame, player_a: str, player_b: str
) -> dict[str, Any]:
    """Calculate two profiles and signed Player B minus Player A differences."""
    if player_a == player_b:
        raise ValueError("Select two different players for comparison")
    a = calculate_player_metrics(shots, player_a)
    b = calculate_player_metrics(shots, player_b)
    metric_names = [
        "fga",
        "fg_pct",
        "three_point_attempt_rate",
        "restricted_area_attempt_rate",
        "mid_range_attempt_rate",
        "average_shot_distance_ft",
        "points_per_attempt",
    ]
    differences = {name: float(b[name] - a[name]) for name in metric_names}

    zone_names = sorted({z["zone"] for z in a["zones"]} | {z["zone"] for z in b["zones"]})
    a_zones = {z["zone"]: z for z in a["zones"]}
    b_zones = {z["zone"]: z for z in b["zones"]}
    zone_differences = []
    for zone in zone_names:
        a_rate = float(a_zones.get(zone, {}).get("attempt_rate", 0.0))
        b_rate = float(b_zones.get(zone, {}).get("attempt_rate", 0.0))
        zone_differences.append(
            {
                "zone": zone,
                "player_a_attempt_rate": a_rate,
                "player_b_attempt_rate": b_rate,
                "difference_b_minus_a": b_rate - a_rate,
            }
        )
    return {
        "player_a": a,
        "player_b": b,
        "difference_definition": f"{player_b} minus {player_a}",
        "differences": differences,
        "zone_differences": zone_differences,
    }
