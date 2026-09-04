"""Build a validated rookie shot-selection summary from player CSV files."""

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "Data"
OUTPUT_PATH = DATA_DIR / "rookie_shot_selection_summary.csv"

PLAYER_FILES = {
    "Cooper Flagg": "cooper_flagg_shots.csv",
    "Dylan Harper": "dylan_harper_shots.csv",
    "Kon Knueppel": "kon_knueppel_shots.csv",
}

REQUIRED_COLUMNS = {"SHOT_MADE_FLAG", "SHOT_TYPE", "SHOT_ZONE_BASIC"}


def load_player_file(player_name: str, filename: str) -> pd.DataFrame:
    """Load one player file, validate core fields, and add a standard label."""
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")

    frame = pd.read_csv(path, dtype={"GAME_ID": "string"})
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"{filename} is missing columns: {sorted(missing)}")

    frame = frame.copy()
    frame["PLAYER_NAME"] = player_name
    frame["SHOT_MADE_FLAG"] = pd.to_numeric(
        frame["SHOT_MADE_FLAG"], errors="coerce"
    )

    invalid_results = ~frame["SHOT_MADE_FLAG"].isin([0, 1])
    if invalid_results.any():
        count = int(invalid_results.sum())
        raise ValueError(f"{filename} contains {count} invalid shot results")

    duplicate_keys = [
        column
        for column in ["PLAYER_NAME", "GAME_ID", "GAME_EVENT_ID"]
        if column in frame.columns
    ]
    if len(duplicate_keys) == 3:
        frame = frame.drop_duplicates(subset=duplicate_keys, keep="first")

    return frame


def build_summary(shots: pd.DataFrame) -> pd.DataFrame:
    """Aggregate player-zone volume, efficiency, and scoring value metrics."""
    shots = shots.copy()
    is_three = shots["SHOT_TYPE"].astype("string").str.contains("3PT", na=False)
    shots["POINT_VALUE"] = np.where(is_three, 3, 2)
    shots["POINTS"] = shots["SHOT_MADE_FLAG"] * shots["POINT_VALUE"]

    summary = (
        shots.groupby(["PLAYER_NAME", "SHOT_ZONE_BASIC"], dropna=False)
        .agg(
            attempts=("SHOT_MADE_FLAG", "size"),
            makes=("SHOT_MADE_FLAG", "sum"),
            points=("POINTS", "sum"),
        )
        .reset_index()
    )

    player_attempts = summary.groupby("PLAYER_NAME")["attempts"].transform("sum")
    summary["fg_pct"] = summary["makes"].div(summary["attempts"])
    summary["shot_share"] = summary["attempts"].div(player_attempts)
    summary["points_per_attempt"] = summary["points"].div(summary["attempts"])

    return summary.sort_values(
        ["PLAYER_NAME", "attempts"], ascending=[True, False]
    ).reset_index(drop=True)


def main() -> None:
    frames = [
        load_player_file(player_name, filename)
        for player_name, filename in PLAYER_FILES.items()
    ]
    shots = pd.concat(frames, ignore_index=True)
    summary = build_summary(shots)
    summary.to_csv(OUTPUT_PATH, index=False, float_format="%.4f")

    print(f"Validated {len(shots):,} shots across {shots['PLAYER_NAME'].nunique()} players.")
    print(f"Wrote {len(summary):,} summary rows to {OUTPUT_PATH}.")


if __name__ == "__main__":
    main()

