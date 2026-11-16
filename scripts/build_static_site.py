from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ops_analysis.data import generate_appointments, validate  # noqa: E402


def build_static_data(output: Path, rows: int = 6500) -> dict[str, object]:
    frame = generate_appointments(rows=rows, seed=42)
    errors = validate(frame)
    if errors:
        raise ValueError("; ".join(errors))

    records = []
    for item in frame.itertuples(index=False):
        records.append(
            {
                "d": item.appointment_date,
                "p": item.department,
                "h": int(item.appointment_hour),
                "w": item.weekday_name,
                "r": int(item.reminder_sent),
                "s": item.status,
                "n": int(item.no_show),
                "ci": None
                if item.checkin_wait_minutes != item.checkin_wait_minutes
                else float(item.checkin_wait_minutes),
                "rm": None if item.room_wait_minutes != item.room_wait_minutes else float(item.room_wait_minutes),
                "cl": None
                if item.clinician_wait_minutes != item.clinician_wait_minutes
                else float(item.clinician_wait_minutes),
                "t": None if item.wait_minutes != item.wait_minutes else float(item.wait_minutes),
            }
        )

    payload = {
        "metadata": {
            "title": "Phân tích vận hành khám ngoại trú",
            "synthetic": True,
            "seed": 42,
            "source": "Dữ liệu mô phỏng do mã Python trong repository tạo ra",
            "represents_real_hospital": False,
            "rows": len(records),
            "date_min": frame["appointment_date"].min(),
            "date_max": frame["appointment_date"].max(),
            "departments": sorted(frame["department"].unique()),
        },
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return payload


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    target = ROOT / "docs" / "assets" / "appointments.json"
    result = build_static_data(target)
    print(f"Đã tạo {result['metadata']['rows']:,} dòng tại {target.relative_to(ROOT)}")
