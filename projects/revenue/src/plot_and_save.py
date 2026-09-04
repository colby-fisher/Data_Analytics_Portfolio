"""Generate and save revenue visuals as PNG files for README."""
from pathlib import Path
import matplotlib.pyplot as plt
from projects.revenue.src.analytics import load_orders, monthly_kpis

OUT = Path(__file__).resolve().parents[1] / 'Visuals' / 'monthly_revenue.png'
DB = Path(__file__).resolve().parents[1] / 'Data' / 'revenue.db'

def main():
    df = load_orders(DB)
    kpi = monthly_kpis(df)
    plt.figure(figsize=(8,4))
    plt.plot(kpi['month'], kpi['revenue'], marker='o')
    plt.xlabel('Month')
    plt.ylabel('Revenue')
    plt.title('Monthly Revenue (sample)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT, dpi=150)
    print('Wrote', OUT)

if __name__ == '__main__':
    main()
