"""ETL for experiment A/B sample: load CSV and write SQLite DB."""
import argparse
from pathlib import Path
import sqlite3
import pandas as pd


def run(input_csv: Path, db_path: Path):
    df = pd.read_csv(input_csv)
    # Basic validation
    required = ['user_id','variant','converted','revenue']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f'Missing required columns: {missing}')

    conn = sqlite3.connect(str(db_path))
    df.to_sql('ab_results', conn, if_exists='replace', index=False)
    cur = conn.cursor()
    total = cur.execute('SELECT COUNT(*) FROM ab_results').fetchone()[0]
    print(f'Wrote {total} rows to {db_path}')
    conn.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--db', required=True)
    args = p.parse_args()
    run(Path(args.input), Path(args.db))
