"""Generate and save churn visuals as PNG files for README.
"""
from pathlib import Path
import matplotlib.pyplot as plt
from projects.churn.src.analytics import load_customers, survival_by_tenure

OUT = Path(__file__).resolve().parents[1] / 'Visuals' / 'retention_curve.png'
DB = Path(__file__).resolve().parents[1] / 'Data' / 'churn.db'

def main():
    df = load_customers(DB)
    sv = survival_by_tenure(df)
    plt.figure(figsize=(8,4))
    plt.plot(sv['tenure'], sv['retention_pct'], marker='o')
    plt.xlabel('Tenure (months)')
    plt.ylabel('Percent retained')
    plt.title('Retention by Tenure (sample)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT, dpi=150)
    print('Wrote', OUT)

if __name__ == '__main__':
    main()
