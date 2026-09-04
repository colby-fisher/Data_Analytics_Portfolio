Experiment / A-B Test Analysis

Executive summary

This project demonstrates a reproducible experiment analysis pipeline: ETL -> summary statistics -> t-test & approximate power calculation -> interactive explorer.

How to run
1. Run ETL:
   python3 projects/experiment/src/etl.py --input projects/experiment/Data/sample_ab_test.csv --db projects/experiment/Data/ab.db
2. Run app:
   streamlit run projects/experiment/app.py

Notes
- Sample data is synthetic and labeled. The power calculation is an approximation for demo purposes.

**Live demo:** Add the Streamlit URL here after deployment.
