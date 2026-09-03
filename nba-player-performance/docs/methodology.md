# Methodology

## Scope

The comparison should use the same NBA season, season type, and endpoint parameters for Cooper Flagg, Dylan Harper, and Kon Knueppel. Record the exact retrieval date in the notebook because API data can be corrected after games are played.

## Cleaning rules

1. Add or standardize `PLAYER_NAME` before concatenating files.
2. Preserve identifiers such as `GAME_ID` as text.
3. Convert `SHOT_MADE_FLAG` to numeric and reject values outside 0 and 1.
4. Remove exact duplicate shot events only when `GAME_ID` and `GAME_EVENT_ID` identify the same event for the same player.
5. Retain missing optional location fields for review; do not silently convert them to zero.
6. Use the same zone definitions for every player.

## Metrics

- **Attempts:** number of valid shot records.
- **Makes:** sum of `SHOT_MADE_FLAG`.
- **FG%:** makes divided by attempts.
- **Shot share:** attempts in a zone divided by all attempts for that player.
- **Points per attempt:** estimated points scored divided by attempts. A made three-point attempt receives three points; other made field goals receive two.

## Interpretation standard

Describe observed patterns rather than claiming causation. A poor percentage may reflect shot difficulty, role, injury, defensive attention, or a small sample. Recommendations should therefore point to follow-up analysis or film review instead of making definitive personnel judgments.

