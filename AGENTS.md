# Project guidance for Codex

## Purpose

This repository is a Data Analyst portfolio case study about fictional outpatient operations in Buon Ma Thuot. Keep it focused on SQL, data quality, KPI definitions, operational analysis and dashboard communication. Predictive modeling belongs in the separate AI Systems repository.

## Data and claims

- All appointment and patient records are synthetic.
- Never describe findings as results from a real hospital.
- Do not add names, phone numbers, addresses, medical records or other personal data.
- Treat reminder comparisons as descriptive associations, not causal effects.
- Preserve the KPI definitions in `docs/metrics.md` unless the report, SQL and tests are updated together.

## Standard verification

Run these commands before committing:

```powershell
ruff check .
ruff format --check .
pytest
python run_analysis.py
```

When the generator, KPI logic or SQL changes, reconcile the generated results with `reports/analysis_report.md` and the reference values in `README.md`.

## Repository hygiene

- Do not commit `.venv`, generated CSV/SQLite files, query exports or secrets.
- Keep `main` deployable; make non-trivial changes on a short-lived branch.
- Prefer small commits with messages that describe the analytical or engineering outcome.
- Update tests when adding a validation rule, warehouse table, KPI or business query.

## Important entry points

- `run_analysis.py`: reproducible end-to-end pipeline.
- `dashboard.py`: Streamlit demo; creates demo data when the generated CSV is absent.
- `sql/analysis.sql`: named business queries executed by the pipeline.
- `reports/analysis_report.md`: recruiter-facing decision report.
- `docs/project_status.md`: current state and safe next steps.

