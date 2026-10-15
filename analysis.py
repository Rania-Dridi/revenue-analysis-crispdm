"""Revenue analysis following the CRISP-DM methodology.

Runs on a synthetic sales dataset generated with a fixed seed, so every result is reproducible.
Usage: python analysis.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).parent / "reports"
OUT.mkdir(exist_ok=True)


# 1. Business understanding ------------------------------------------------------------
# Questions: how does revenue evolve, which products and customer segments drive it,
# and where is the risk of dependence on a few customers?


# 2. Data understanding ----------------------------------------------------------------
def generate_data(seed: int = 42, n: int = 4000) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    products = {"Starter": 49, "Pro": 149, "Enterprise": 499, "Support plan": 99}
    segments = ["Retail", "Education", "Services", "Industry"]
    dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 730, n), unit="D")
    df = pd.DataFrame(
        {
            "order_date": dates,
            "customer_id": rng.integers(1, 400, n),
            "segment": rng.choice(segments, n, p=[0.35, 0.25, 0.25, 0.15]),
            "product": rng.choice(list(products), n, p=[0.4, 0.3, 0.1, 0.2]),
            "quantity": rng.integers(1, 6, n),
        }
    )
    df["unit_price"] = df["product"].map(products)
    # Inject a few data-quality problems to be cleaned in the next phase.
    df.loc[rng.choice(n, 40, replace=False), "quantity"] = np.nan
    df = pd.concat([df, df.sample(25, random_state=seed)], ignore_index=True)
    return df


# 3. Data preparation ------------------------------------------------------------------
def prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates().dropna(subset=["quantity"]).copy()
    df["quantity"] = df["quantity"].astype(int)
    df["revenue"] = df["quantity"] * df["unit_price"]
    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    return df


# 4. Modeling (descriptive analysis and KPIs) ------------------------------------------
def kpis(df: pd.DataFrame) -> dict:
    by_customer = df.groupby("customer_id")["revenue"].sum().sort_values(ascending=False)
    top10_share = by_customer.head(max(1, len(by_customer) // 10)).sum() / by_customer.sum()
    monthly = df.groupby("month")["revenue"].sum()
    return {
        "total_revenue": float(df["revenue"].sum()),
        "orders": int(len(df)),
        "average_order_value": float(df["revenue"].mean()),
        "active_customers": int(df["customer_id"].nunique()),
        "top_10pct_customers_share": float(top10_share),
        "last_12m_vs_previous_12m": float(monthly.iloc[-12:].sum() / monthly.iloc[-24:-12].sum() - 1),
    }


# 5. Evaluation ------------------------------------------------------------------------
def evaluate(df: pd.DataFrame, k: dict) -> None:
    assert (df["revenue"] > 0).all(), "revenue must be positive"
    assert df.duplicated().sum() == 0, "duplicates remain"
    assert abs(df.groupby("product")["revenue"].sum().sum() - k["total_revenue"]) < 1e-6


# 6. Deployment (charts and report) ----------------------------------------------------
def report(df: pd.DataFrame, k: dict) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.5))
    df.groupby("month")["revenue"].sum().plot(ax=ax, color="#6d3fc0", marker="o")
    ax.set_title("Monthly revenue")
    ax.set_ylabel("Revenue")
    fig.tight_layout()
    fig.savefig(OUT / "monthly_revenue.png", dpi=130)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
    df.groupby("product")["revenue"].sum().sort_values().plot.barh(ax=axes[0], color="#6d3fc0")
    axes[0].set_title("Revenue by product")
    df.groupby("segment")["revenue"].sum().sort_values().plot.barh(ax=axes[1], color="#a88af0")
    axes[1].set_title("Revenue by segment")
    fig.tight_layout()
    fig.savefig(OUT / "product_segment.png", dpi=130)
    plt.close(fig)

    lines = [
        "# KPI summary",
        "",
        f"- Total revenue: {k['total_revenue']:,.0f}",
        f"- Orders: {k['orders']:,}",
        f"- Average order value: {k['average_order_value']:,.1f}",
        f"- Active customers: {k['active_customers']}",
        f"- Share of revenue from the top 10% of customers: {k['top_10pct_customers_share']:.1%}",
        f"- Last 12 months vs previous 12 months: {k['last_12m_vs_previous_12m']:+.1%}",
    ]
    (OUT / "kpis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    raw = generate_data()
    df = prepare(raw)
    k = kpis(df)
    evaluate(df, k)
    report(df, k)
    print(f"raw rows: {len(raw)}, clean rows: {len(df)}")
    for name, value in k.items():
        print(f"{name}: {value:,.3f}")


if __name__ == "__main__":
    main()
