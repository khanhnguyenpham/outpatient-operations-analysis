from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ops_analysis.analysis import create_report, load_sqlite
from ops_analysis.data import build_dataset


def main() -> None:
    csv_path = ROOT / "data" / "generated" / "appointments.csv"
    db_path = ROOT / "data" / "generated" / "operations.db"
    frame = build_dataset(csv_path)
    load_sqlite(frame, db_path)
    kpis = create_report(frame, ROOT / "reports" / "generated")
    print(json.dumps(kpis, indent=2))


if __name__ == "__main__":
    main()

