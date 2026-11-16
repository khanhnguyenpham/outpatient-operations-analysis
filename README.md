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
synthetic source -> validation -> star-schema SQLite -> SQL analysis -> report/dashboard
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

Each named SQL query is also exported to `reports/generated/query_results/`, making the SQL output easy to inspect without opening SQLite manually.

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

## Review the result

- [Analysis report](reports/analysis_report.md) — findings, recommendations and limitations.
- [Metric definitions](docs/metrics.md) — exact KPI denominators.
- [Data model](docs/data_model.md) — fact/dimension design and reconciliation.
- [Data dictionary](docs/data_dictionary.md) — field-level meanings.
- [SQL analysis](sql/analysis.sql) — named queries with window functions for trends, median and P90.
- [Laptop workflow](docs/laptop_workflow.md) — clone, branch, test and synchronize safely between computers.

## Hosted demo

The Streamlit app creates its reproducible synthetic dataset automatically when no generated CSV exists. This keeps both Community Cloud and a newly cloned laptop setup independent of local files.

## Analytical choices

- Median wait is reported alongside the 90th percentile because averages hide long queues.
- Cancelled appointments are excluded from the no-show denominator.
- Reminder results are descriptive, not causal: reminder assignment may depend on lead time.
- Department-hour rankings require at least 50 completed visits; weekday-hour summaries require at least 30 appointments.
- Source, fact-table and reporting-view row counts are reconciled on every run.

## Reproducible reference run

With seed 42 and 6,500 appointments, the pipeline reports a 13.79% no-show rate, 27.7-minute median wait and 43.9-minute P90 wait. These values are outputs of the generator, not claims about any real hospital.

![Median wait by department](docs/assets/median_wait_by_department.png)

## Limits

Synthetic patterns make the project reproducible, but they cannot justify real staffing decisions. With production data I would confirm operational definitions, validate timestamps with front-desk staff, document missingness, and add privacy and access controls.

