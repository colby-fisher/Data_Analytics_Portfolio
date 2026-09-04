Technical case study — NBA Rookie Shot Selection

Problem statement
Compare where Cooper Flagg, Dylan Harper, and Kon Knueppel generate shot attempts and scoring value during the 2025–26 season to inform development and role decisions.

Stakeholders
Coaching or player-development staff; generalist data analyst reviewers.

Data
NBA shot-location records (one CSV per player). See Data/ and docs/data_dictionary.md for schema.

Analytical questions
- Which zones produce the most attempts and points?
- How does FG% and points-per-attempt vary by zone and player?
- Which zones represent development opportunities (high volume, low efficiency)?

Reproducibility
- build_summary.py standardizes inputs and writes Data/rookie_shot_selection_summary.csv
- SQL examples: sql/aggregation.sql
- Interactive comparator: app.py (Streamlit)

Validation
- Required-column checks, numeric coercion for SHOT_MADE_FLAG, duplicate-event removal when GAME_ID+GAME_EVENT_ID exist, and handling zero-attempt zones.

Limitations
- Location data does not capture defender proximity, play type, or context. Small zone samples may mislead.

Next steps
- Add play-type and lineup context; expand to rolling windows; pair with scouting film for prioritized review.