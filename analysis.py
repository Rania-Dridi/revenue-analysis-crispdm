"""Revenue analysis following the CRISP-DM phases.

Usage:
    python analysis.py            # generates data, runs the analysis, writes outputs/
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


# 1. Business understanding ---------------------------------------------------
# Questions: how does revenue evolve, which segments and products drive it,
# and where is the risk of dependence on a few customers?


# 2. Data understanding -------------------------------------------------------
def generate_dataset(seed: int = 42) -> pd.DataFrame:
    """Synthetic sales data (no real customer data is used)."""
    rng = np.random.default_rng(seed)
    n = 4000
    dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 730, n), unit="D")
    df = pd.DataFrame(
        {
            "order_id": np.arange(1, n + 1),
            "date": dates,
            "customer_id": rng.integers(1, 401, n),
            "segment": rng.choice(["Particulier", "PME", "Grand compte"], n, p=[0.55, 0.3, 0.15]),
            "product": rng.choice(["Abonnement", "Formation", "Support", "Licence"], n, p=[0.4, 0.2, 0.25, 0.15]),
            "quantity": rng.integers(1, 6, n),
        }
    )
    unit_price = df["product"].map({"Abonnement": 40, "Formation": 120, "Support": 60, "Licence": 200})
    uplift = df["segment"].map({"Particulier": 1.0, "PME": 1.2, "Grand compte": 1.5})
    df["revenue"] = (df["quantity"] * unit_price * uplift * rng.normal(1, 0.08, n)).round(2)
    # inject quality issues to be cleaned in the next phase
    df.loc[rng.choice(n, 40, replace=False), "revenue"] = np.nan
    df = pd.concat([df, df.sample(25, random_state=seed)], ignore_index=True)
    return df


# 3. Data preparation ---------------------------------------------------------
def prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset="order_id").copy()
    df = df.dropna(subset=["revenue"])
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


# 4. Modeling (descriptive analysis and KPIs) ---------------------------------
def kpis(df: pd.DataFrame) -> dict:
    by_customer = df.groupby("customer_id")["revenue"].sum().sort_values(ascending=False)
    top_20pct = by_customer.head(max(1, int(len(by_customer) * 0.2))).sum() / by_customer.sum()
    return {
        "total_revenue": round(df["revenue"].sum(), 2),
        "orders": int(len(df)),
        "average_order_value": round(df["revenue"].mean(), 2),
        "active_customers": int(df["customer_id"].nunique()),
        "revenue_share_top_20pct_customers": round(float(top_20pct), 3),
    }


def make_charts(df: pd.DataFrame) -> None:
    monthly = df.groupby("month")["revenue"].sum()
    fig, ax = plt.subplots(figsize=(8, 4))
    monthly.plot(ax=ax, marker="o", color="#6d3fc0")
    ax.set_title("Monthly revenue")
    ax.set_ylabel("Revenue")
    fig.tight_layout()
    fig.savefig(OUT / "monthly_revenue.png", dpi=120)
    plt.close(fig)

    pivot = df.pivot_table(index="product", columns="segment", values="revenue", aggfunc="sum")
    ax = pivot.plot(kind="bar", stacked=True, figsize=(8, 4), colormap="Purples")
    ax.set_title("Revenue by product and segment")
    ax.figure.tight_layout()
    ax.figure.savefig(OUT / "revenue_by_product_segment.png", dpi=120)
    plt.close(ax.figure)


# 5. Evaluation ---------------------------------------------------------------
def evaluate(raw: pd.DataFrame, clean: pd.DataFrame) -> dict:
    return {
        "rows_raw": len(raw),
        "rows_clean": len(clean),
        "duplicates_removed": int(raw.duplicated(subset="order_id").sum()),
        "missing_revenue_removed": int(raw.drop_duplicates(subset="order_id")["revenue"].isna().sum()),
    }


# 6. Deployment (reporting) ---------------------------------------------------
def main() -> None:
    raw = generate_dataset()
    raw.to_csv(OUT / "raw_sales.csv", index=False)
    clean = prepare(raw)
    clean.to_csv(OUT / "clean_sales.csv", index=False)
    make_charts(clean)

    k, q = kpis(clean), evaluate(raw, clean)
    pd.Series({**k, **q}).to_csv(OUT / "summary.csv", header=["value"])
    print("Data quality:", q)
    print("KPIs:", k)
    seg = clean.groupby("segment")["revenue"].sum().sort_values(ascending=False)
    print("Revenue by segment:\n", seg.round(0).to_string())


if __name__ == "__main__":
    main()
