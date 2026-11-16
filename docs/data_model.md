# Data model

The generated SQLite database uses a small star schema rather than treating the source CSV as the reporting layer.

```text
dim_date ───────────┐
                    ├── fact_appointment ── appointments (reporting view)
dim_department ─────┘
```

`fact_appointment` stores one row per appointment and foreign keys to date and department dimensions. The `appointments` view exposes analyst-friendly names used by the SQL queries. The pipeline reconciles source, fact and view row counts and checks for orphan dimension keys every run.

This model is deliberately small. Patient details are not modeled because the project uses synthetic identifiers and the business questions do not require a patient dimension.

