# revenue-analysis-crispdm

Revenue and customer analysis structured with the CRISP-DM methodology (Python, pandas, matplotlib).

This is a reproducible rebuild of my academic revenue-analysis project. The original data is not
public, so this version runs on a **synthetic dataset** generated with a fixed seed. The figures
below illustrate the method, not real business results.

## CRISP-DM phases in `analysis.py`

1. **Business understanding**: revenue trend, drivers by product and segment, customer concentration.
2. **Data understanding**: 4,000 synthetic orders (date, customer, segment, product, quantity, price).
3. **Data preparation**: remove duplicate rows and missing quantities, compute revenue and month.
4. **Modeling**: descriptive analysis and KPIs (total revenue, average order value, top-10% customer share, year-over-year change).
5. **Evaluation**: consistency checks (positive revenue, no duplicates, totals reconcile).
6. **Deployment**: charts and a KPI summary written to `reports/`.

## Run

```bash
pip install -r requirements.txt
python analysis.py
```

Outputs: `reports/monthly_revenue.png`, `reports/product_segment.png`, `reports/kpis.md`.
