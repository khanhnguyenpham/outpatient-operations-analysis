# Outpatient Operations Analysis

An end-to-end data analysis project for a fictional outpatient clinic in Buon Ma Thuot. The goal is to help an operations team understand patient demand, waiting time and missed appointments before discussing staffing changes.

The dataset is synthetic and contains no real patient information.

## Questions answered

1. When is outpatient demand highest?
2. Which departments have the longest median waiting time?
3. Where are no-shows concentrated?
4. Is reminder delivery associated with a lower no-show rate?
5. Which department-hour combinations should be reviewed first?

## Workflow

```text
synthetic source -> validation -> SQLite -> SQL analysis -> report/dashboard
```

This repository is intentionally focused on analysis. Prediction and model serving live in a separate AI Systems project.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_analysis.py
streamlit run dashboard.py
```

The first command creates a reproducible dataset, validates it, loads SQLite, runs the queries in `sql/analysis.sql`, saves charts and writes `reports/generated/summary.md`.

## Repository structure

```text
data/                 generated CSV and SQLite files
docs/                 metric definitions and limitations
sql/analysis.sql      reusable business queries
src/ops_analysis/     generation, validation and analysis code
tests/                data-quality and KPI tests
dashboard.py          interactive Streamlit dashboard
run_analysis.py       one-command workflow
```

## Analytical choices

- Median wait is reported alongside the 90th percentile because averages hide long queues.
- Cancelled appointments are excluded from the no-show denominator.
- Reminder results are descriptive, not causal: reminder assignment may depend on lead time.
- Departments with fewer than 30 completed appointments in a slice are suppressed from ranking.

## Limits

Synthetic patterns make the project reproducible, but they cannot justify real staffing decisions. With production data I would confirm operational definitions, validate timestamps with front-desk staff, document missingness, and add privacy and access controls.

