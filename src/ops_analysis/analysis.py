from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_sqlite(frame: pd.DataFrame, database: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as connection:
        frame.to_sql("appointments", connection, if_exists="replace", index=False)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_appointment_date ON appointments(appointment_date)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_department ON appointments(department)")


def calculate_kpis(frame: pd.DataFrame) -> dict[str, float | int]:
    eligible = frame[frame["status"] != "Cancelled"]
    completed = frame[frame["status"] == "Completed"]
    return {
        "appointments": int(len(frame)),
        "completion_rate_pct": round(100 * len(completed) / len(eligible), 2),
        "no_show_rate_pct": round(100 * eligible["no_show"].mean(), 2),
        "median_wait_minutes": round(float(completed["wait_minutes"].median()), 1),
        "p90_wait_minutes": round(float(completed["wait_minutes"].quantile(.90)), 1),
    }


def create_report(frame: pd.DataFrame, report_dir: Path) -> dict[str, float | int]:
    report_dir.mkdir(parents=True, exist_ok=True)
    kpis = calculate_kpis(frame)
    completed = frame[frame["status"] == "Completed"]
    wait_by_department = completed.groupby("department")["wait_minutes"].median().sort_values(ascending=False)
    no_show_by_department = frame[frame["status"] != "Cancelled"].groupby("department")["no_show"].mean().mul(100).sort_values(ascending=False)

    ax = wait_by_department.sort_values().plot.barh(figsize=(8, 4), color="#2563eb")
    ax.set(title="Median wait by department", xlabel="Minutes", ylabel="")
    plt.tight_layout()
    plt.savefig(report_dir / "median_wait_by_department.png", dpi=150)
    plt.close()

    lines = [
        "# Generated analysis summary", "",
        "This report is produced by `run_analysis.py` from the synthetic dataset.", "",
        "## Overall KPIs", "",
        f"- Appointments: {kpis['appointments']:,}",
        f"- Completion rate: {kpis['completion_rate_pct']}%",
        f"- No-show rate: {kpis['no_show_rate_pct']}%",
        f"- Median wait: {kpis['median_wait_minutes']} minutes",
        f"- P90 wait: {kpis['p90_wait_minutes']} minutes", "",
        "## Areas to review", "",
        f"- Highest median wait: {wait_by_department.index[0]} ({wait_by_department.iloc[0]:.1f} minutes).",
        f"- Highest no-show rate: {no_show_by_department.index[0]} ({no_show_by_department.iloc[0]:.1f}%).",
        "- These are descriptive signals. They should start an operational review, not automatically change staffing.", "",
    ]
    (report_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    return kpis

