# Project status

## Completed

- Reproducible generator for 6,500 synthetic appointments.
- Row-level data validation and explicit operational rules.
- SQLite star schema with date and department dimensions.
- Source, fact and reporting-view reconciliation with orphan-key checks.
- Named SQL queries for monthly movement, wait distributions, operational pressure and reminder comparison.
- Streamlit dashboard with department/date filters, KPIs, trends and a demand heatmap.
- Decision report with recommendations, limitations and Wilson intervals.
- Ruff, pytest and GitHub Actions verification.
- Portable demo-data bootstrap for a new laptop or Streamlit deployment.

## Current verified reference

- Overall appointments: 6,500.
- No-show rate: 13.79%.
- Median wait: 27.7 minutes.
- P90 wait: 43.9 minutes.
- Local test suite: 7 tests passing.

## Safe next steps

1. Deploy `dashboard.py` on Streamlit Community Cloud and add the URL to `README.md`.
2. Add a screenshot of the deployed dashboard if its layout differs materially from the current preview.
3. Add a small sensitivity analysis for slice-size thresholds without changing the primary KPI definitions.

Do not add machine learning to this repository; keep that work in the AI Systems project.

