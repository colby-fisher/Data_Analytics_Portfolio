from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import REQUIRED_COLUMNS, ShotDataError, get_player_shots, load_shot_data, validate_shot_data


DATA_DIR = Path(__file__).resolve().parents[1] / "Data"


def test_loads_all_project_shot_files():
    shots = load_shot_data(DATA_DIR)
    assert len(shots) == 2934
    assert set(shots["PLAYER_NAME"].unique()) == {"Cooper Flagg", "Dylan Harper", "Kon Knueppel"}


def test_required_column_validation_reports_missing_field():
    frame = pd.DataFrame(columns=sorted(REQUIRED_COLUMNS - {"SHOT_TYPE"}))
    with pytest.raises(ShotDataError, match="SHOT_TYPE"):
        validate_shot_data(frame)


def test_malformed_result_is_rejected():
    row = {column: 1 for column in REQUIRED_COLUMNS}
    row.update({"PLAYER_NAME": "Test Player", "GAME_ID": "001", "SHOT_TYPE": "2PT Field Goal", "SHOT_ZONE_BASIC": "Mid-Range", "SHOT_MADE_FLAG": "bad"})
    with pytest.raises(ShotDataError, match="SHOT_MADE_FLAG"):
        validate_shot_data(pd.DataFrame([row]))


def test_invalid_player_selection_has_useful_error():
    shots = load_shot_data(DATA_DIR)
    with pytest.raises(ShotDataError, match="Available players"):
        get_player_shots(shots, "Not A Player")
