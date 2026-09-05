# AI Basketball Scouting Assistant

An interactive, evidence-first scouting product that converts NBA shot-level data into player profiles, visual comparisons, and grounded AI interpretations. Built for the Handshake AI Showcase and as a data analytics portfolio case study.

> **Important data context:** The repository contains a static 2025–26 portfolio dataset. The application does not claim to provide live NBA statistics. Every number in the interface and scouting inputs is recalculated from the committed shot rows.

## Project Overview

This project analyzes 2,934 field-goal attempts for Cooper Flagg, Dylan Harper, and Kon Knueppel. A Streamlit application lets a user inspect one player's shot profile or compare two players, then generate a structured scouting interpretation. The interpretation is powered by an optional LLM when configured and a deterministic rules engine otherwise.

The product separates two responsibilities:

- **Calculated data:** validated pandas transformations produce attempts, makes, FG%, shot rates, distance, points per attempt, and zone breakdowns.
- **Interpretation:** an LLM or deterministic fallback explains those calculated results and their limitations.

## Problem

Shot data is detailed but difficult to scan quickly. A scout, coach, or analyst needs a concise answer to three questions: where does a player shoot, how efficiently does he convert, and what should be investigated next? A generic chatbot is unsafe for this task because it can recall stale facts or invent plausible-looking statistics.

## Who This Helps

- Scouting and player-development staff prioritizing film review
- Basketball analysts comparing shot-selection profiles
- Recruiters evaluating applied analytics, product thinking, and responsible AI implementation
- Students learning how deterministic analysis and generative AI can work together

## Solution

The assistant validates local shot records, computes a structured statistical profile, presents interactive evidence, and passes the same structure to a bounded interpretation layer. The user can:

- select any player in the dataset;
- inspect KPI cards, shot-zone distribution, zone efficiency, and shot locations;
- retain access to the original notebook-generated shot charts;
- generate a six-section individual scouting report;
- compare two players through a common metric table and grouped zone chart; and
- generate a structured comparison without requiring an API key.

## Key Features

- Centralized CSV discovery, schema validation, numeric coercion, and duplicate handling
- Reusable player and zone metric functions
- Individual player and two-player comparison modes
- Interactive Plotly visuals plus preserved Matplotlib notebook assets
- Grounded prompt templates kept outside UI code
- Swappable text-generation provider interface
- Environment-based credentials with no committed secrets
- Deterministic fallback for offline demos and provider failures
- Focused pytest coverage for validation, calculations, comparisons, selections, and scouting fallback

## Data

The source files in `Data/` contain one row per field-goal attempt and include NBA event identifiers, shot result, type, basic zone, distance, coordinates, and game date. The three player files contain 1,194, 656, and 1,084 attempts respectively. See [`docs/data_dictionary.md`](docs/data_dictionary.md) for field definitions.

The data was originally retrieved with `nba_api`, as documented in the notebook. The running application intentionally uses the committed CSVs so a recruiter can reproduce the analysis without relying on a rate-limited external endpoint.

## Methodology

1. Discover player shot files using the `*_shots.csv` naming convention.
2. Validate required columns and reject missing or malformed analytical values.
3. Preserve `GAME_ID` as text and remove repeated player/game/event keys.
4. Calculate each player's totals and shot-zone profile from the validated rows.
5. Calculate Player B minus Player A differences for comparisons.
6. Render the evidence before offering an interpretation.
7. Send only the structured calculated snapshot—not raw general knowledge—to the optional LLM.

Metric definitions and interpretation standards are documented in [`docs/methodology.md`](docs/methodology.md).

## Architecture

```text
nba-player-performance/
├── app.py                      # Streamlit presentation and interaction
├── Data/                       # committed shot-level source data
├── Notebooks/                  # original exploratory and clean analysis
├── Visuals/                    # original exported analysis visuals
├── docs/                       # data dictionary and methodology
├── src/
│   ├── data_loader.py          # discovery, validation, cleaning, selection
│   ├── analytics.py            # deterministic metrics and comparisons
│   ├── prompts.py              # grounded prompt templates
│   ├── scouting.py             # LLM adapter and deterministic fallback
│   └── build_summary.py        # optional reproducible zone export
├── tests/                      # focused unit and integration tests
├── .env.example
└── requirements.txt
```

The modules are deliberately small and direct: a junior analyst can follow data from CSV, through validation and calculation, to visualization and interpretation without a framework-heavy abstraction layer.

## AI Implementation

`src/scouting.py` exposes a minimal `TextGenerator` protocol. The included OpenAI adapter uses the Responses API, while application code depends only on the small `generate_*_report` functions. This makes a future provider swap localized.

If `OPENAI_API_KEY` is present, the app requests an LLM interpretation. `OPENAI_MODEL` optionally selects the model. If the key is missing or the request fails, a deterministic engine creates the same report sections from explicit thresholds and calculated values.

### How AI Is Grounded in Calculated Data

The prompt receives a JSON-serializable dictionary created by `analytics.py`. It does not receive an invitation to search memory for player statistics. Individual inputs contain totals, rates, average distance, points per attempt, and a complete zone table. Comparison inputs contain both profiles, signed differences, and zone-share differences.

### Safeguards Against Fabricated Statistics

- The model is explicitly told to use only `CALCULATED_DATA`.
- It is forbidden from adding, estimating, recalling, or inventing a statistic.
- Every response number must appear in the supplied structure.
- Prompts require evidence to be distinguished from interpretation.
- Unsupported claims about defense, athleticism, passing, injuries, role, and film are prohibited.
- The UI visibly separates calculated data from the interpretation layer.
- The offline fallback uses no generative model.
- Tests verify that grounding instructions and calculated data are included in prompts.

These controls reduce hallucination risk; they do not make model output infallible. Production use should add output-schema validation and human review.

## Key Findings

The following values are calculated from the committed shot rows:

- Cooper Flagg recorded 1,194 FGA, 46.8% FG, a 20.4% three-point attempt rate, a 20.3% mid-range attempt rate, and 11.0-foot average shot distance.
- Dylan Harper recorded 656 FGA and the highest FG% in this three-player dataset at 50.5%; 45.6% of his attempts came from the restricted area.
- Kon Knueppel recorded 1,084 FGA, a 59.2% three-point attempt rate, 17.4-foot average shot distance, and 1.202 points per field-goal attempt.
- The clearest style contrast is location: Harper's recorded profile is more restricted-area-oriented, while Knueppel's is substantially more perimeter-oriented. Flagg has the largest mid-range share of the three.

These are descriptive shot-profile findings, not complete rankings. Free throws, turnovers, passing, defense, lineup context, defender distance, and play type are outside the dataset.

## Technologies Used

Python, pandas, NumPy, Streamlit, Plotly, Matplotlib, Seaborn, `nba_api`, OpenAI Responses API, pytest, SQL, and Jupyter Notebook.

## How to Run Locally

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r nba-player-performance/requirements.txt
streamlit run nba-player-performance/app.py
```

The app works immediately in deterministic mode. To enable LLM interpretation, copy the example configuration and set your own secret locally:

```bash
cp nba-player-performance/.env.example nba-player-performance/.env
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4.1-mini"
streamlit run nba-player-performance/app.py
```

The application reads environment variables; it does not load or commit `.env`. Never add a real key to source control.

Run tests from the repository root:

```bash
python -m pytest -q nba-player-performance/tests
```

Regenerate the optional zone summary with:

```bash
python nba-player-performance/src/build_summary.py
```

## Deployment

For Streamlit Community Cloud:

1. Choose this GitHub repository and set the entry point to `nba-player-performance/app.py`.
2. The project-local `requirements.txt` includes every application and test dependency.
3. Deploy without a secret for deterministic mode, or add `OPENAI_API_KEY` and optional `OPENAI_MODEL` through Streamlit's encrypted secrets settings.
4. Do not commit `.env` or `.streamlit/secrets.toml`; `.env` is already ignored by the repository.

All runtime file paths are derived from `app.py`, so the app does not depend on a developer's working directory. The committed data and visuals remove runtime network dependencies except optional LLM generation.

## Handshake AI Showcase

**Problem being solved:** scouting data is too granular for quick evaluation, while ungrounded chatbots can produce convincing but unreliable sports claims.

**Intended users:** basketball scouts, player-development staff, analysts, and decision-makers who need a fast statistical orientation before deeper film review.

**How AI is used:** AI translates a calculated statistical object into a consistent scouting narrative and comparison. It does not calculate or retrieve the statistics.

**Why AI adds value:** deterministic charts answer “what happened”; the interpretation layer organizes that evidence into strengths, development questions, style differences, and limitations that are faster to consume.

**How it remains grounded:** the model receives only application-calculated data and strict evidence rules. The product visibly labels the source data and generated interpretation, and remains fully usable without a model.

**My contribution:** I designed the product workflow; modularized ingestion, validation, analytics, comparison, prompts, and provider logic; built the Streamlit experience; preserved and integrated the original analysis assets; added tests and failure handling; and documented responsible AI boundaries and deployment.

**Expected real-world value:** the assistant can shorten the first pass of shot-profile review, make comparisons consistent, and give staff targeted questions for film study while keeping numerical evidence auditable.

## Limitations

- The dataset is a static snapshot and is not refreshed in the application.
- Only field-goal attempts are included; points per attempt is not true shooting percentage.
- Shot location does not measure difficulty, defensive pressure, play design, or decision quality.
- Zone percentages can be unstable in small samples.
- Generated interpretation still requires human review.
- The current LLM response is free-form Markdown rather than a validated structured schema.

## Future Improvements

- Add retrieval timestamps and automated, versioned data refreshes.
- Add game-level and rolling-window filters.
- Incorporate play type, defender distance, assisted rate, lineup, and possession context.
- Validate LLM output against an allowed-number ledger before display.
- Add exportable PDF reports and saved scouting sessions.
- Expand accessibility and mobile interface testing.

## What I Personally Built

I built the end-to-end analytical product: data-quality controls, reproducible metric functions, comparison logic, interactive Streamlit interface, optional LLM integration, prompt safeguards, deterministic fallback, automated tests, deployment configuration, and recruiter-facing case-study documentation. The original notebooks and visuals remain in the project to show the exploratory path that informed the production application.
