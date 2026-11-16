from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_sqlite(frame: pd.DataFrame, database: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        legacy_object = connection.execute("SELECT type FROM sqlite_master WHERE name = 'appointments'").fetchone()
        if legacy_object:
            connection.execute(f"DROP {legacy_object[0].upper()} appointments")
        connection.executescript("""
            DROP TABLE IF EXISTS fact_appointment;
            DROP TABLE IF EXISTS dim_date;
            DROP TABLE IF EXISTS dim_department;

            CREATE TABLE dim_department (
                department_key INTEGER PRIMARY KEY,
                department_name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE dim_date (
                date_key INTEGER PRIMARY KEY,
                date_value TEXT NOT NULL UNIQUE,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                month_name TEXT NOT NULL,
                weekday_number INTEGER NOT NULL,
                weekday_name TEXT NOT NULL,
                is_weekend INTEGER NOT NULL CHECK (is_weekend IN (0, 1))
            );

            CREATE TABLE fact_appointment (
                appointment_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
                department_key INTEGER NOT NULL REFERENCES dim_department(department_key),
                appointment_hour INTEGER NOT NULL CHECK (appointment_hour BETWEEN 7 AND 16),
                lead_days INTEGER NOT NULL CHECK (lead_days >= 0),
                prior_no_shows INTEGER NOT NULL CHECK (prior_no_shows >= 0),
                reminder_sent INTEGER NOT NULL CHECK (reminder_sent IN (0, 1)),
                outside_city INTEGER NOT NULL CHECK (outside_city IN (0, 1)),
                status TEXT NOT NULL CHECK (status IN ('Hoàn thành', 'Vắng hẹn', 'Đã hủy')),
                no_show INTEGER NOT NULL CHECK (no_show IN (0, 1)),
                wait_minutes REAL
            );

            CREATE INDEX idx_fact_date ON fact_appointment(date_key);
            CREATE INDEX idx_fact_department ON fact_appointment(department_key);

            CREATE VIEW appointments AS
            SELECT
                f.appointment_id,
                f.patient_id,
                d.date_value AS appointment_date,
                dep.department_name AS department,
                f.appointment_hour,
                d.weekday_name,
                f.lead_days,
                f.prior_no_shows,
                f.reminder_sent,
                f.outside_city,
                f.status,
                f.no_show,
                f.wait_minutes
            FROM fact_appointment f
            JOIN dim_date d ON d.date_key = f.date_key
            JOIN dim_department dep ON dep.department_key = f.department_key;
        """)

        departments = {name: index for index, name in enumerate(sorted(frame["department"].unique()), start=1)}
        connection.executemany(
            "INSERT INTO dim_department VALUES (?, ?)",
            [(key, name) for name, key in departments.items()],
        )
        dates = pd.to_datetime(frame["appointment_date"]).drop_duplicates().sort_values()
        connection.executemany(
            "INSERT INTO dim_date VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    int(value.strftime("%Y%m%d")),
                    value.strftime("%Y-%m-%d"),
                    value.year,
                    value.month,
                    value.month_name(),
                    value.dayofweek,
                    value.day_name(),
                    int(value.dayofweek >= 5),
                )
                for value in dates
            ],
        )
        rows = []
        for item in frame.itertuples(index=False):
            rows.append(
                (
                    item.appointment_id,
                    item.patient_id,
                    int(pd.Timestamp(item.appointment_date).strftime("%Y%m%d")),
                    departments[item.department],
                    int(item.appointment_hour),
                    int(item.lead_days),
                    int(item.prior_no_shows),
                    int(item.reminder_sent),
                    int(item.outside_city),
                    item.status,
                    int(item.no_show),
                    None if pd.isna(item.wait_minutes) else float(item.wait_minutes),
                )
            )
        connection.executemany("INSERT INTO fact_appointment VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)


def validate_warehouse(database: Path, expected_rows: int) -> dict[str, int]:
    with sqlite3.connect(database) as connection:
        fact_rows = connection.execute("SELECT COUNT(*) FROM fact_appointment").fetchone()[0]
        view_rows = connection.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
        orphan_dates = connection.execute(
            """SELECT COUNT(*)
               FROM fact_appointment f
               LEFT JOIN dim_date d ON d.date_key = f.date_key
               WHERE d.date_key IS NULL"""
        ).fetchone()[0]
        orphan_departments = connection.execute(
            """SELECT COUNT(*)
               FROM fact_appointment f
               LEFT JOIN dim_department d ON d.department_key = f.department_key
               WHERE d.department_key IS NULL"""
        ).fetchone()[0]
    checks = {
        "fact_rows": fact_rows,
        "view_rows": view_rows,
        "orphan_dates": orphan_dates,
        "orphan_departments": orphan_departments,
    }
    if fact_rows != expected_rows or view_rows != expected_rows or orphan_dates or orphan_departments:
        raise ValueError(f"Đối soát kho dữ liệu không đạt: {checks}")
    return checks


def calculate_kpis(frame: pd.DataFrame) -> dict[str, float | int]:
    eligible = frame[frame["status"] != "Đã hủy"]
    completed = frame[frame["status"] == "Hoàn thành"]
    return {
        "appointments": len(frame),
        "completion_rate_pct": round(100 * len(completed) / len(eligible), 2),
        "no_show_rate_pct": round(100 * eligible["no_show"].mean(), 2),
        "median_wait_minutes": round(float(completed["wait_minutes"].median()), 1),
        "p90_wait_minutes": round(float(completed["wait_minutes"].quantile(0.90)), 1),
    }


def create_report(frame: pd.DataFrame, report_dir: Path) -> dict[str, float | int]:
    report_dir.mkdir(parents=True, exist_ok=True)
    preview_dir = report_dir.parents[1] / "docs" / "assets"
    preview_dir.mkdir(parents=True, exist_ok=True)
    kpis = calculate_kpis(frame)
    completed = frame[frame["status"] == "Hoàn thành"]
    wait_by_department = completed.groupby("department")["wait_minutes"].median().sort_values(ascending=False)
    no_show_by_department = (
        frame[frame["status"] != "Đã hủy"].groupby("department")["no_show"].mean().mul(100).sort_values(ascending=False)
    )
    data_quality = {
        "duplicate_appointment_ids": int(frame["appointment_id"].duplicated().sum()),
        "missing_department": int(frame["department"].isna().sum()),
        "missing_wait_completed": int(completed["wait_minutes"].isna().sum()),
    }

    ax = wait_by_department.sort_values().plot.barh(figsize=(8, 4), color="#2563eb")
    ax.set(title="Thời gian chờ trung vị theo chuyên khoa", xlabel="Phút", ylabel="")
    plt.tight_layout()
    plt.savefig(report_dir / "median_wait_by_department.png", dpi=150)
    plt.savefig(preview_dir / "median_wait_by_department.png", dpi=150)
    plt.close()

    lines = [
        "# Tóm tắt phân tích được tạo tự động",
        "",
        "Báo cáo được tạo bởi `run_analysis.py` từ bộ dữ liệu mô phỏng.",
        "",
        "## KPI tổng quan",
        "",
        f"- Tổng lịch hẹn: {kpis['appointments']:,}",
        f"- Tỷ lệ hoàn thành: {kpis['completion_rate_pct']}%",
        f"- Tỷ lệ vắng hẹn: {kpis['no_show_rate_pct']}%",
        f"- Thời gian chờ trung vị: {kpis['median_wait_minutes']} phút",
        f"- Thời gian chờ P90: {kpis['p90_wait_minutes']} phút",
        "",
        "## Nội dung cần rà soát",
        "",
        f"- Chờ trung vị cao nhất: {wait_by_department.index[0]} ({wait_by_department.iloc[0]:.1f} phút).",
        f"- Tỷ lệ vắng hẹn cao nhất: {no_show_by_department.index[0]} ({no_show_by_department.iloc[0]:.1f}%).",
        "- Đây là tín hiệu mô tả để bắt đầu rà soát vận hành, không phải căn cứ tự động điều chỉnh nhân sự.",
        "",
        "## Kiểm tra chất lượng dữ liệu",
        "",
        f"- Mã lịch hẹn trùng: {data_quality['duplicate_appointment_ids']}",
        f"- Thiếu chuyên khoa: {data_quality['missing_department']}",
        f"- Lượt khám hoàn thành thiếu thời gian chờ: {data_quality['missing_wait_completed']}",
        "",
    ]
    (report_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    return kpis
