import sqlite3
from pathlib import Path

from ops_analysis.analysis import load_sqlite, validate_warehouse
from ops_analysis.data import generate_appointments
from ops_analysis.sql_runner import run_queries


def test_warehouse_reconciles_source_rows(tmp_path):
    frame = generate_appointments(rows=200, seed=11)
    database = tmp_path / "operations.db"
    load_sqlite(frame, database)
    checks = validate_warehouse(database, expected_rows=200)
    assert checks["orphan_dates"] == 0
    assert checks["orphan_departments"] == 0
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM dim_department").fetchone()[0] == 6


def test_every_business_query_executes(tmp_path):
    frame = generate_appointments(rows=500, seed=12)
    database = tmp_path / "operations.db"
    load_sqlite(frame, database)
    sql_file = tmp_path / "analysis.sql"
    project_sql = Path(__file__).parents[1] / "sql" / "analysis.sql"
    sql_file.write_text(project_sql.read_text(encoding="utf-8"), encoding="utf-8")
    counts = run_queries(database, sql_file, tmp_path / "results")
    assert counts["department_performance"] == 6
    assert counts["reminder_comparison"] == 2
