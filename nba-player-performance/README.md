# NBA Rookie Shot Selection Analysis

## Executive summary

This project compares the 2025–26 shot profiles of Cooper Flagg, Dylan Harper, and Kon Knueppel. The analysis converts play-by-play shot records into a consistent set of location and efficiency metrics, then uses those metrics to describe each player's offensive tendencies.

5. Calculate attempts, makes, field-goal percentage, shot share, and points per attempt.
6. Compare player profiles visually and summarize decision-relevant takeaways.

## Key findings

Replace the bracketed text below with exact values produced by the notebook. Keep this section to three or four evidence-backed bullets.

- **Shot distribution:** Kon Knueppel had the most perimeter-oriented profile, with 59.2% of his attempts coming from three-point range and an average shot distance of 17.4 feet.
- **Overall efficiency:** Dylan Harper recorded the highest field-goal percentage at 50.5%, despite having the smallest sample of the three players at 656 attempts.
- **Profile difference:** Knueppel's three-point rate was 38.8 percentage points higher than Cooper Flagg's, while Harper's restricted-area rate was 18.0 percentage points higher than Flagg's.
- **Development opportunity:** Flagg took 20.3% of his shots from mid-range—the highest rate in the group—while posting the lowest overall field-goal percentage at 46.8%. This makes his mid-range shot selection a useful area for additional film and efficiency analysis.
## Recommendations

- Use both volume and efficiency when evaluating a shot zone; high percentage on a very small sample should not drive a decision by itself.
- Review film and lineup context for the largest differences. Shot data describes outcomes and locations, but not defensive pressure, play type, or teammate spacing.
- Track the same metrics over multiple seasons or rolling intervals to determine whether early patterns remain stable.
- Pair this work with possession, play-type, and lineup data before making personnel conclusions.

## Data quality checks

The reproducible summary script checks for:

- required columns;
- missing or invalid `SHOT_MADE_FLAG` values;
- duplicate shot events when event identifiers are available;
- consistent player labels; and
- valid output calculations when a zone contains zero attempts.

## Limitations

- A single season may contain small samples, especially within individual zones.
- Field-goal percentage does not fully capture shot difficulty or offensive value.
- Location data alone does not explain defender distance, play type, lineup context, or late-clock situations.
- Results depend on the completeness and availability of NBA API data.

## How to reproduce

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r nba-player-performance/requirements.txt
python nba-player-performance/src/build_summary.py
jupyter notebook nba-player-performance/Notebooks/rookie_shot_selection_analysis.ipynb
```

On Windows, activate the environment with `.venv\Scripts\activate`.

## Next steps

- Add a SQL version of the aggregation workflow.
- Build an interactive dashboard with filters for player and shot zone.
- Extend the analysis with play type, assisted-shot rate, or lineup context.
