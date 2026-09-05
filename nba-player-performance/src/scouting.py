"""LLM-backed scouting interpretation with a deterministic offline fallback."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Protocol

from .prompts import build_comparison_prompt, build_player_prompt


class TextGenerator(Protocol):
    """Small provider interface that keeps the scouting layer swappable."""

    def generate(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class ScoutingResult:
    content: str
    mode: str
    notice: str


class OpenAITextGenerator:
    """OpenAI Responses API adapter, imported only when an API key is used."""

    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(model=self.model, input=prompt)
        return response.output_text


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _top_zone(metrics: dict[str, Any], key: str) -> dict[str, Any]:
    eligible = [zone for zone in metrics["zones"] if zone["attempts"] >= 10]
    pool = eligible or metrics["zones"]
    return max(pool, key=lambda zone: zone[key])


def deterministic_player_report(metrics: dict[str, Any]) -> str:
    """Create a repeatable scouting interpretation without any external model."""
    volume_zone = _top_zone(metrics, "attempt_rate")
    efficient_zone = _top_zone(metrics, "points_per_attempt")
    low_value_zone = min(
        [zone for zone in metrics["zones"] if zone["attempts"] >= 10] or metrics["zones"],
        key=lambda zone: zone["points_per_attempt"],
    )
    name = metrics["player_name"]
    return f"""## Offensive Profile
**Calculated evidence:** {name} recorded {metrics['fga']:,} field-goal attempts, made {metrics['fgm']:,}, and produced {_pct(metrics['fg_pct'])} FG% in this dataset. Average shot distance was {metrics['average_shot_distance_ft']:.1f} feet.

**Interpretation:** The shot-location profile is best described by where the attempt volume is concentrated; it does not measure total offensive impact.

## Shot Selection
**Calculated evidence:** Three-pointers represented {_pct(metrics['three_point_attempt_rate'])} of attempts, restricted-area shots {_pct(metrics['restricted_area_attempt_rate'])}, and mid-range shots {_pct(metrics['mid_range_attempt_rate'])}. The largest zone was {volume_zone['zone']} at {_pct(volume_zone['attempt_rate'])} ({volume_zone['attempts']} attempts).

**Interpretation:** This distribution indicates the areas emphasized in the recorded shot diet, without explaining play type or defensive pressure.

## Scoring Efficiency
**Calculated evidence:** The player generated {metrics['points_per_attempt']:.3f} points per field-goal attempt. Among zones with at least 10 attempts, {efficient_zone['zone']} produced the highest value at {efficient_zone['points_per_attempt']:.3f} points per attempt.

**Interpretation:** Points per attempt adds shot value to FG%, but it is not a complete measure of offensive efficiency.

## Strengths
**Calculated evidence:** {efficient_zone['zone']} combined {efficient_zone['attempts']} attempts with {_pct(efficient_zone['fg_pct'])} FG%.

**Interpretation:** This is the clearest shot-location strength in the available sample and a useful starting point for film review.

## Development Areas
**Calculated evidence:** Among zones with at least 10 attempts, {low_value_zone['zone']} returned {low_value_zone['points_per_attempt']:.3f} points per attempt across {low_value_zone['attempts']} attempts.

**Interpretation:** This zone merits review for shot quality and decision context; the location data alone does not prove a player weakness.

## Overall Scouting Summary
**Interpretation:** {name}'s profile should be evaluated as a shot-selection and conversion snapshot. Pair these calculated results with film, role, lineup, free-throw, turnover, and passing context before making a personnel decision."""


def deterministic_comparison_report(comparison: dict[str, Any]) -> str:
    """Create a repeatable two-player comparison without an external model."""
    a = comparison["player_a"]
    b = comparison["player_b"]
    d = comparison["differences"]
    largest_zone_gap = max(comparison["zone_differences"], key=lambda row: abs(row["difference_b_minus_a"]))
    a_best = _top_zone(a, "points_per_attempt")
    b_best = _top_zone(b, "points_per_attempt")
    return f"""## Key Statistical Differences
**Calculated evidence:** {a['player_name']} recorded {a['fga']:,} attempts and {_pct(a['fg_pct'])} FG%; {b['player_name']} recorded {b['fga']:,} attempts and {_pct(b['fg_pct'])} FG%. The FG% difference ({b['player_name']} minus {a['player_name']}) was {d['fg_pct']:+.1%}, and the points-per-attempt difference was {d['points_per_attempt']:+.3f}.

## Shot Profile Differences
**Calculated evidence:** Three-point attempt rates were {_pct(a['three_point_attempt_rate'])} for {a['player_name']} and {_pct(b['three_point_attempt_rate'])} for {b['player_name']}. The largest zone-share gap was {largest_zone_gap['zone']}: {_pct(largest_zone_gap['player_a_attempt_rate'])} versus {_pct(largest_zone_gap['player_b_attempt_rate'])}.

**Interpretation:** The zone mix identifies a style difference in shot location, not a complete difference in offensive role.

## Player A Strengths
**Calculated evidence:** {a_best['zone']} produced {a_best['points_per_attempt']:.3f} points per attempt across {a_best['attempts']} attempts for {a['player_name']}.

## Player B Strengths
**Calculated evidence:** {b_best['zone']} produced {b_best['points_per_attempt']:.3f} points per attempt across {b_best['attempts']} attempts for {b['player_name']}.

## Style Comparison
**Interpretation:** {a['player_name']} and {b['player_name']} differ most clearly in their recorded shot-zone distributions and average distances ({a['average_shot_distance_ft']:.1f} feet versus {b['average_shot_distance_ft']:.1f} feet). This dataset cannot explain why those choices occurred.

## Overall Scouting Conclusion
**Interpretation:** Use this comparison to prioritize film questions, not as a stand-alone player ranking. It covers field-goal locations and outcomes but excludes defense, passing, turnovers, free throws, lineup context, and shot difficulty."""


def _configured_generator() -> TextGenerator | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
    return OpenAITextGenerator(api_key=api_key, model=model)


def generate_player_report(
    metrics: dict[str, Any], generator: TextGenerator | None = None
) -> ScoutingResult:
    """Use a configured LLM when available, otherwise return deterministic text."""
    try:
        selected = generator or _configured_generator()
        if selected is not None:
            return ScoutingResult(
                selected.generate(build_player_prompt(metrics)),
                "llm",
                "AI interpretation generated from the calculated statistical snapshot.",
            )
    except Exception as exc:  # The analytics product remains useful if the provider fails.
        notice = f"LLM unavailable ({type(exc).__name__}); showing deterministic analysis."
    else:
        notice = "No LLM API key configured; showing deterministic analysis."
    return ScoutingResult(deterministic_player_report(metrics), "deterministic", notice)


def generate_comparison_report(
    comparison: dict[str, Any], generator: TextGenerator | None = None
) -> ScoutingResult:
    """Use a configured LLM when available, otherwise return deterministic text."""
    try:
        selected = generator or _configured_generator()
        if selected is not None:
            return ScoutingResult(
                selected.generate(build_comparison_prompt(comparison)),
                "llm",
                "AI interpretation generated from the calculated comparison.",
            )
    except Exception as exc:
        notice = f"LLM unavailable ({type(exc).__name__}); showing deterministic analysis."
    else:
        notice = "No LLM API key configured; showing deterministic analysis."
    return ScoutingResult(deterministic_comparison_report(comparison), "deterministic", notice)
