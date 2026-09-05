"""Prompt construction for scouting interpretations grounded in app metrics."""

from __future__ import annotations

import json
from typing import Any


GROUNDING_RULES = """You are an NBA scouting analyst interpreting a supplied statistical snapshot.
Use only the statistics in CALCULATED_DATA. Never add, estimate, or recall a statistic.
Clearly distinguish observed evidence from interpretation. Treat small zone samples cautiously.
Do not make claims about defense, athleticism, passing, role, injuries, or film that the data does not measure.
Every number in the response must appear in CALCULATED_DATA. If evidence is unavailable, say so.
Write concise Markdown for a basketball or analytics audience."""


def build_player_prompt(metrics: dict[str, Any]) -> str:
    """Build an individual scouting prompt from calculated structured data."""
    return f"""{GROUNDING_RULES}

Produce exactly these headings:
## Offensive Profile
## Shot Selection
## Scoring Efficiency
## Strengths
## Development Areas
## Overall Scouting Summary

CALCULATED_DATA:
{json.dumps(metrics, indent=2, sort_keys=True)}
"""


def build_comparison_prompt(comparison: dict[str, Any]) -> str:
    """Build a two-player comparison prompt from calculated structured data."""
    return f"""{GROUNDING_RULES}

The supplied differences are explicitly Player B minus Player A. Do not reverse their sign.
Produce exactly these headings:
## Key Statistical Differences
## Shot Profile Differences
## Player A Strengths
## Player B Strengths
## Style Comparison
## Overall Scouting Conclusion

CALCULATED_DATA:
{json.dumps(comparison, indent=2, sort_keys=True)}
"""
