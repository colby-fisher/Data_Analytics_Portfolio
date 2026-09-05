from pathlib import Path

from src.analytics import calculate_player_metrics, compare_players
from src.data_loader import load_shot_data
from src.prompts import build_player_prompt
from src.scouting import generate_comparison_report, generate_player_report


DATA_DIR = Path(__file__).resolve().parents[1] / "Data"


class FakeGenerator:
    def generate(self, prompt: str) -> str:
        assert "CALCULATED_DATA" in prompt
        return "## Offensive Profile\nGrounded test output"


def test_deterministic_player_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    metrics = calculate_player_metrics(load_shot_data(DATA_DIR), "Dylan Harper")
    result = generate_player_report(metrics)
    assert result.mode == "deterministic"
    assert "No LLM API key" in result.notice
    assert "## Development Areas" in result.content
    assert f"{metrics['fga']:,}" in result.content


def test_deterministic_comparison_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    shots = load_shot_data(DATA_DIR)
    result = generate_comparison_report(compare_players(shots, "Cooper Flagg", "Kon Knueppel"))
    assert result.mode == "deterministic"
    assert "## Player A Strengths" in result.content
    assert "## Player B Strengths" in result.content


def test_provider_can_be_swapped_without_ui_changes():
    metrics = calculate_player_metrics(load_shot_data(DATA_DIR), "Kon Knueppel")
    result = generate_player_report(metrics, generator=FakeGenerator())
    assert result.mode == "llm"
    assert result.content.endswith("Grounded test output")


def test_prompt_contains_grounding_safeguards():
    metrics = calculate_player_metrics(load_shot_data(DATA_DIR), "Cooper Flagg")
    prompt = build_player_prompt(metrics)
    assert "Never add, estimate, or recall a statistic" in prompt
    assert "Every number in the response must appear" in prompt
    assert '"fga": 1194' in prompt
