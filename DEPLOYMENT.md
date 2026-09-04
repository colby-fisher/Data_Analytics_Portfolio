Deployment guide — Streamlit apps (portfolio)

This repository contains three Streamlit apps:
- nba-player-performance/app.py
- projects/churn/app_full.py
- projects/revenue/app.py
- projects/experiment/app.py

Streamlit Cloud (recommended for quick portfolio demos)
1. Sign in to https://streamlit.io/cloud with your GitHub account.
2. Create a new app and point it to the repository and branch (colby-fisher-portfolio-upgrade).
3. Select the app file path (for example: `nba-player-performance/app.py`) and deploy. Repeat to create separate apps for churn and revenue if desired.
4. No secrets are required for these demos; choose the Python environment matching requirements.txt. If the environment fails, set `pip install -r requirements.txt` in the advanced settings.

Render.com (alternative)
- Create a new web service from GitHub and set the build command to `pip install -r requirements.txt` and the start command to `streamlit run <app-path> --server.port $PORT`.

Local run (developer)
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r requirements.txt
- streamlit run <app-path>

Notes
- For production or larger datasets, use a managed database and add connection configuration via environment variables (use Streamlit Cloud secrets or Render environment variables). Do not commit credentials to the repo.
