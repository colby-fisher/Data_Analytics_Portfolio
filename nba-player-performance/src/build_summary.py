"""Build the optional zone-summary export from validated shot-level data."""

from pathlib import Path
import sys

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from src.analytics import calculate_zone_metrics  # noqa: E402
from src.data_loader import load_shot_data  # noqa: E402

DATA_DIR = PROJECT_DIR / "Data"
OUTPUT_PATH = DATA_DIR / "rookie_shot_selection_summary.csv"

def build_summary(shots: pd.DataFrame) -> pd.DataFrame:
    """Aggregate player-zone volume, efficiency, and scoring value metrics."""
    summaries = []
    for player_name, player_shots in shots.groupby("PLAYER_NAME", sort=True):
        zones = calculate_zone_metrics(player_shots).rename(
            columns={"zone": "SHOT_ZONE_BASIC", "attempt_rate": "shot_share"}
        )
        zones.insert(0, "PLAYER_NAME", player_name)
        summaries.append(zones)
    return pd.concat(summaries, ignore_index=True)[
        ["PLAYER_NAME", "SHOT_ZONE_BASIC", "attempts", "makes", "points", "fg_pct", "shot_share", "points_per_attempt"]
    ]


def main() -> None:
    shots = load_shot_data(DATA_DIR)
    summary = build_summary(shots)
    summary.to_csv(OUTPUT_PATH, index=False, float_format="%.4f")

    print(f"Validated {len(shots):,} shots across {shots['PLAYER_NAME'].nunique()} players.")
    print(f"Wrote {len(summary):,} summary rows to {OUTPUT_PATH}.")


if __name__ == "__main__":
    main()
