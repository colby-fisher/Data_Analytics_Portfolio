from pathlib import Path

import pytest

from src.analytics import calculate_player_metrics, compare_players
from src.data_loader import load_shot_data


DATA_DIR = Path(__file__).resolve().parents[1] / "Data"


@pytest.fixture(scope="module")
def shots():
    return load_shot_data(DATA_DIR)


def test_player_metrics_are_calculated_from_raw_attempts(shots):
    metrics = calculate_player_metrics(shots, "Cooper Flagg")
    assert metrics["fga"] == 1194
    assert metrics["fgm"] == 559
    assert metrics["fg_pct"] == pytest.approx(559 / 1194)
    assert sum(zone["attempts"] for zone in metrics["zones"]) == 1194
    assert sum(zone["attempt_rate"] for zone in metrics["zones"]) == pytest.approx(1.0)


def test_comparison_differences_match_player_profiles(shots):
    comparison = compare_players(shots, "Cooper Flagg", "Dylan Harper")
    expected = comparison["player_b"]["fg_pct"] - comparison["player_a"]["fg_pct"]
    assert comparison["differences"]["fg_pct"] == pytest.approx(expected)
    assert comparison["difference_definition"] == "Dylan Harper minus Cooper Flagg"


def test_comparison_rejects_same_player(shots):
    with pytest.raises(ValueError, match="different players"):
        compare_players(shots, "Cooper Flagg", "Cooper Flagg")
