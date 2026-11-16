from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ops_analysis.analysis import create_report, load_sqlite, validate_warehouse
from ops_analysis.data import build_dataset
from ops_analysis.sql_runner import run_queries


def main() -> None:
    csv_path = ROOT / "data" / "generated" / "appointments.csv"
    db_path = ROOT / "data" / "generated" / "operations.db"
    frame = build_dataset(csv_path)
    load_sqlite(frame, db_path)
    warehouse_checks = validate_warehouse(db_path, expected_rows=len(frame))
    kpis = create_report(frame, ROOT / "reports" / "generated")
    query_rows = run_queries(db_path, ROOT / "sql" / "analysis.sql", ROOT / "reports" / "generated" / "query_results")
    print(json.dumps({"kpis": kpis, "warehouse_checks": warehouse_checks, "query_rows": query_rows}, indent=2))


if __name__ == "__main__":
    main()
