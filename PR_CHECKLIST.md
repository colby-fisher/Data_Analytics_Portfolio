PR reviewer checklist — Portfolio upgrade

- [ ] Read the recruiter 30s summaries for each project (NBA, Churn, Revenue, Experiment).
- [ ] Confirm ETL scripts run locally and produce SQLite DB artifacts.
- [ ] Run pytest: PYTHONPATH=. pytest -q (all tests should pass).
- [ ] Confirm Streamlit apps start locally (streamlit run <app-path>) and load without runtime errors.
- [ ] Verify README images render and captions match visuals.
- [ ] Review TECHNICAL_CASE_STUDY.md files for accuracy and limitations.
- [ ] Ensure no credentials or personal paths are committed.
- [ ] Approve and merge when CI is green.
