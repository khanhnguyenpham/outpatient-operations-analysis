import pandas as pd

from ops_analysis.analysis import calculate_kpis
from ops_analysis.data import ensure_demo_dataset, generate_appointments, validate
from ops_analysis.sql_runner import parse_named_queries


def test_generated_data_passes_validation():
    frame = generate_appointments(rows=400, seed=7)
    assert validate(frame) == []
    assert frame["appointment_id"].is_unique


def test_wait_stages_reconcile_to_total_wait():
    frame = generate_appointments(rows=400, seed=9)
    completed = frame[frame["status"] == "Hoàn thành"]
    stage_total = completed[["checkin_wait_minutes", "room_wait_minutes", "clinician_wait_minutes"]].sum(axis=1)
    assert (stage_total - completed["wait_minutes"]).abs().max() <= 0.11


def test_no_show_denominator_excludes_cancellations():
    frame = pd.DataFrame(
        {
            "status": ["Hoàn thành", "Vắng hẹn", "Đã hủy"],
            "no_show": [0, 1, 0],
            "wait_minutes": [10.0, None, None],
        }
    )
    result = calculate_kpis(frame)
    assert result["no_show_rate_pct"] == 50.0


def test_named_sql_queries_are_discovered():
    sql = "-- name: first\nSELECT 1;\n-- name: second\nSELECT 2;"
    queries = parse_named_queries(sql)
    assert [name for name, _ in queries] == ["first", "second"]


def test_invalid_operational_values_are_reported():
    frame = generate_appointments(rows=100, seed=3)
    frame.loc[0, "appointment_hour"] = 23
    frame.loc[1, "reminder_sent"] = 4
    errors = validate(frame)
    assert "appointment_hour phải nằm trong khoảng 7 đến 16" in errors
    assert "reminder_sent phải là biến nhị phân" in errors


def test_invalid_wait_stage_total_is_reported():
    frame = generate_appointments(rows=100, seed=4)
    completed_index = frame.index[frame["status"] == "Hoàn thành"][0]
    frame.loc[completed_index, "clinician_wait_minutes"] += 5
    errors = validate(frame)
    assert "tổng thời gian chờ theo công đoạn không khớp wait_minutes" in errors


def test_demo_dataset_is_created_once(tmp_path):
    output = tmp_path / "appointments.csv"
    assert ensure_demo_dataset(output, rows=50) is True
    first_bytes = output.read_bytes()
    assert ensure_demo_dataset(output, rows=50) is False
    assert output.read_bytes() == first_bytes


def test_demo_dataset_is_upgraded_when_categories_are_outdated(tmp_path):
    output = tmp_path / "appointments.csv"
    output.write_text("department,status\nCardiology,Completed\n", encoding="utf-8")
    assert ensure_demo_dataset(output, rows=50) is True
    upgraded = pd.read_csv(output)
    assert set(upgraded["status"]).issubset({"Hoàn thành", "Vắng hẹn", "Đã hủy"})
    assert len(upgraded) == 50
