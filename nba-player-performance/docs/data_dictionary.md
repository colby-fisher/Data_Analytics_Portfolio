# Data dictionary

This dictionary documents the fields used by the cleaned analysis. NBA API responses can contain additional source columns; only the analytical fields below are required for the portfolio workflow.

| Field | Type | Description | Validation |
|---|---|---|---|
| `PLAYER_NAME` | text | Display name of the shooter | Non-null; standardized during ingestion |
| `GAME_ID` | text | NBA game identifier | Stored as text to preserve leading zeros |
| `GAME_EVENT_ID` | integer | Event identifier within a game | Used with `GAME_ID` to detect duplicates |
| `GAME_DATE` | date | Date of the game | Parsed to a date when used |
| `PERIOD` | integer | Game period in which the attempt occurred | Expected to be 1 or greater |
| `MINUTES_REMAINING` | integer | Whole minutes left in the period | Expected range: 0–11 in regulation periods |
| `SECONDS_REMAINING` | integer | Additional seconds left in the minute | Expected range: 0–59 |
| `SHOT_MADE_FLAG` | integer | Shot result: 1 made, 0 missed | Must be 0 or 1 |
| `SHOT_TYPE` | text | Two-point or three-point field goal | Non-null for shot attempts |
| `ACTION_TYPE` | text | NBA description of the shot action | Retained for drill-down analysis |
| `SHOT_ZONE_BASIC` | text | Broad NBA-defined court zone | Primary grouping field in the summary |
| `SHOT_ZONE_AREA` | text | Court side or central area | Optional secondary segmentation |
| `SHOT_ZONE_RANGE` | text | NBA-defined distance band | Optional secondary segmentation |
| `SHOT_DISTANCE` | numeric | Distance from the basket in feet | Expected to be nonnegative |
| `LOC_X` | numeric | Horizontal shot coordinate | Used for shot-chart visualization |
| `LOC_Y` | numeric | Vertical shot coordinate | Used for shot-chart visualization |

## Derived metrics

| Metric | Formula | Purpose |
|---|---|---|
| Attempts | Count of shot records | Measures shot volume |
| Makes | Sum of `SHOT_MADE_FLAG` | Measures successful attempts |
| FG% | Makes / attempts | Measures conversion efficiency |
| Shot share | Zone attempts / player attempts | Measures shot-selection distribution |
| Points per attempt | Estimated points / attempts | Compares scoring value across shot types |

