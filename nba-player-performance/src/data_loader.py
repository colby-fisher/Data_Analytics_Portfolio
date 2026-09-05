"""Validated loading for the project's shot-level CSV data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_DIR / "Data"

REQUIRED_COLUMNS = {
    "PLAYER_NAME",
    "GAME_ID",
    "GAME_EVENT_ID",
    "SHOT_MADE_FLAG",
    "SHOT_TYPE",
    "SHOT_ZONE_BASIC",
    "SHOT_DISTANCE",
    "LOC_X",
    "LOC_Y",
}
NUMERIC_COLUMNS = {
    "GAME_EVENT_ID",
    "SHOT_MADE_FLAG",
    "SHOT_DISTANCE",
    "LOC_X",
    "LOC_Y",
}


class ShotDataError(ValueError):
    """Raised when the project data cannot be safely used for analysis."""


def validate_shot_data(frame: pd.DataFrame, source: str = "shot data") -> pd.DataFrame:
    """Validate and normalize one shot-level dataframe.

    Invalid required numeric values are reported instead of silently becoming
    zero. Duplicate NBA game events are removed because they represent the same
    recorded attempt, not additional volume.
    """
    missing = sorted(REQUIRED_COLUMNS.difference(frame.columns))
    if missing:
        raise ShotDataError(f"{source} is missing required columns: {', '.join(missing)}")

    cleaned = frame.copy()
    for column in NUMERIC_COLUMNS:
        converted = pd.to_numeric(cleaned[column], errors="coerce")
        invalid_count = int(converted.isna().sum())
        if invalid_count:
            raise ShotDataError(
                f"{source} has {invalid_count} missing or malformed value(s) in {column}"
            )
        cleaned[column] = converted

    text_columns = ["PLAYER_NAME", "SHOT_TYPE", "SHOT_ZONE_BASIC"]
    for column in text_columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()
        empty = cleaned[column].isna() | cleaned[column].eq("")
        if empty.any():
            raise ShotDataError(f"{source} has {int(empty.sum())} empty value(s) in {column}")

    invalid_results = ~cleaned["SHOT_MADE_FLAG"].isin([0, 1])
    if invalid_results.any():
        raise ShotDataError(
            f"{source} has {int(invalid_results.sum())} SHOT_MADE_FLAG value(s) outside 0 or 1"
        )
    if (cleaned["SHOT_DISTANCE"] < 0).any():
        raise ShotDataError(f"{source} contains a negative SHOT_DISTANCE")

    cleaned["GAME_ID"] = cleaned["GAME_ID"].astype("string").str.strip()
    cleaned = cleaned.drop_duplicates(
        subset=["PLAYER_NAME", "GAME_ID", "GAME_EVENT_ID"], keep="first"
    )
    cleaned["SHOT_MADE_FLAG"] = cleaned["SHOT_MADE_FLAG"].astype("int8")
    return cleaned.reset_index(drop=True)


def load_shot_data(data_dir: Path | str = DEFAULT_DATA_DIR) -> pd.DataFrame:
    """Load, combine, and validate all player shot files in a directory."""
    directory = Path(data_dir)
    if not directory.exists():
        raise ShotDataError(f"Data directory does not exist: {directory}")

    paths = sorted(directory.glob("*_shots.csv"))
    if not paths:
        raise ShotDataError(f"No player shot CSV files were found in {directory}")

    frames: list[pd.DataFrame] = []
    for path in paths:
        try:
            raw = pd.read_csv(path, dtype={"GAME_ID": "string"})
        except (OSError, pd.errors.ParserError) as exc:
            raise ShotDataError(f"Could not read {path.name}: {exc}") from exc
        frames.append(validate_shot_data(raw, path.name))

    combined = pd.concat(frames, ignore_index=True)
    duplicate_player_events = combined.duplicated(
        ["PLAYER_NAME", "GAME_ID", "GAME_EVENT_ID"]
    )
    combined = combined.loc[~duplicate_player_events].reset_index(drop=True)
    if combined.empty:
        raise ShotDataError("The loaded shot dataset is empty")
    return combined


def list_players(shots: pd.DataFrame) -> list[str]:
    """Return sorted player names from validated shot data."""
    return sorted(shots["PLAYER_NAME"].dropna().astype(str).unique().tolist())


def get_player_shots(shots: pd.DataFrame, player_name: str) -> pd.DataFrame:
    """Return one player's attempts or raise a useful selection error."""
    player_frame = shots.loc[shots["PLAYER_NAME"] == player_name].copy()
    if player_frame.empty:
        available = ", ".join(list_players(shots)) or "none"
        raise ShotDataError(
            f"Player '{player_name}' was not found. Available players: {available}"
        )
    return player_frame.reset_index(drop=True)
