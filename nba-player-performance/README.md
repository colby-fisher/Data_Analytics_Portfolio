# Rookie Shot Selection Analysis

## Cooper Flagg vs. Dylan Harper vs. Kon Knueppel

This project analyzes and compares the shot-selection profiles of Cooper Flagg, Dylan Harper, and Kon Knueppel during the 2025-26 NBA regular season.

Using shot-level data from NBA.com Stats, the analysis examines where each rookie attempted shots, how efficiently they scored from different areas of the court, and how their offensive styles differed.

## Project Questions

- Where does each player take the majority of his shots?
- How frequently does each player attack the rim, shoot from mid-range, or attempt three-pointers?
- How efficient is each player from different areas of the court?
- How do their average shot distances compare?
- Which player generates the most points per field goal attempt?

## Tools Used

- Python
- pandas
- Matplotlib
- nba_api
- Jupyter Notebook / VS Code
- Git & GitHub

## Data

Shot-level data was collected from NBA.com Stats using the `nba_api` Python package.

The dataset includes:

- Shot coordinates
- Shot zones
- Shot distance
- Shot type
- Makes and misses
- Game dates

The analysis covers the 2025-26 NBA regular season.

## Key Findings

### Cooper Flagg — Balanced Scoring Profile

Flagg displayed the most balanced shot distribution of the three rookies.

- 31.6% of attempts came from the non-restricted paint
- 20.3% came from mid-range
- 20.4% of attempts were three-pointers
- Average shot distance: 11.0 feet
- Points per field goal attempt: 0.997

His shot profile shows significant usage in both the interior and intermediate areas of the court.

### Dylan Harper — Rim-Oriented Attacker

Harper had the strongest rim-oriented shot profile.

- 45.6% of attempts came from the restricted area
- Only 9.9% came from mid-range
- Average shot distance: 10.2 feet
- Points per field goal attempt: 1.102

His shot distribution reflects an offensive style centered heavily around attacking the basket.

### Kon Knueppel — Perimeter-Oriented Shooter

Knueppel had the strongest perimeter-oriented profile.

- 59.2% of attempts were three-pointers
- 45.9% came from above-the-break three
- Average shot distance: 17.4 feet
- Points per field goal attempt: 1.202

Knueppel generated the highest points per field goal attempt of the three players, demonstrating the value created by his combination of three-point volume and efficiency.

## Shot Selection Comparison

![Shot Selection by Zone](Visuals/shot_selection_by_zone.png)

The chart highlights three distinctly different offensive profiles: Flagg's balanced interior and mid-range game, Harper's heavy concentration around the rim, and Knueppel's high-volume perimeter shooting.

## Shot Charts

### Cooper Flagg

![Cooper Flagg Shot Chart](Visuals/cooper_flagg_shot_chart.png)

### Dylan Harper

![Dylan Harper Shot Chart](Visuals/dylan_harper_shot_chart.png)

### Kon Knueppel

![Kon Knueppel Shot Chart](Visuals/kon_knueppel_shot_chart.png)

## Project Structure

- `Data/` — Raw shot data and summary statistics
- `Notebooks/` — Jupyter notebook containing the complete analysis
- `Visuals/` — Shot charts and comparison visualizations
- `README.md` — Project overview and key findings

## Limitations

This analysis focuses exclusively on field goal attempts and does not account for free throws, turnovers, assists, or other aspects of offensive performance.

Some shot zones also contain relatively small sample sizes, so zone-level shooting percentages should be interpreted alongside attempt volume.

Points per shot in this project represents points generated from field goal attempts only and should not be interpreted as true shooting percentage or overall offensive efficiency.
