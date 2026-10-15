# revenue-analysis-crispdm

Revenue and sales analysis structured along the six CRISP-DM phases. It is a reproducible version of
the analysis project done during my Business Information Systems degree at Esprit School of Business.

The dataset is **synthetic** (generated with a fixed seed) so the project runs anywhere and exposes
no real customer data.

## CRISP-DM mapping

| Phase | Where in `analysis.py` | What it does |
|-------|------------------------|--------------|
| Business understanding | header comment | Revenue trend, drivers, dependence on top customers |
| Data understanding | `generate_dataset` | 4,000 orders, with injected duplicates and missing values |
| Data preparation | `prepare` | Deduplicate, drop missing revenue, add month |
| Modeling | `kpis`, `make_charts` | KPIs, monthly trend, product × segment breakdown |
| Evaluation | `evaluate` | Rows removed and why, data-quality summary |
| Deployment | `main` | CSV and PNG outputs in `outputs/` |

## KPIs produced

Total revenue, number of orders, average order value, active customers, and the share of revenue
from the top 20 % of customers.

## Run

```bash
pip install -r requirements.txt
python analysis.py
```

Outputs are written to `outputs/` (`clean_sales.csv`, `summary.csv`, two charts).
