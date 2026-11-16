from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

DEPARTMENTS = {
    "Nội tổng quát": (0.30, 24),
    "Nhi": (0.22, 18),
    "Tim mạch": (0.16, 32),
    "Chấn thương chỉnh hình": (0.14, 28),
    "Mắt": (0.11, 20),
    "Nội tiết": (0.07, 26),
}
VALID_STATUSES = {"Hoàn thành", "Vắng hẹn", "Đã hủy"}


def generate_appointments(rows: int = 6500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2025-01-01")
    end = pd.Timestamp("2026-10-31")
    day_count = (end - start).days + 1
    dates = start + pd.to_timedelta(rng.integers(0, day_count, rows), unit="D")
    dates = pd.Series(dates)
    dates = dates.mask(dates.dt.dayofweek.eq(6), dates + pd.offsets.Day(1))
    departments = rng.choice(list(DEPARTMENTS), rows, p=[v[0] for v in DEPARTMENTS.values()])
    hours = rng.choice(range(7, 17), rows, p=[0.07, 0.13, 0.14, 0.13, 0.09, 0.07, 0.11, 0.11, 0.09, 0.06])
    lead_days = np.clip(rng.gamma(2.2, 5.0, rows).round().astype(int), 0, 60)
    prior_no_shows = np.clip(rng.poisson(0.25, rows), 0, 4)
    reminders = rng.binomial(1, np.where(lead_days > 1, 0.80, 0.35))
    outside_city = rng.binomial(1, 0.22, rows)
    log_odds = -2.25 + 0.045 * lead_days + 0.65 * prior_no_shows - 0.55 * reminders + 0.32 * outside_city
    probability = 1 / (1 + np.exp(-log_odds))
    no_show = rng.binomial(1, probability)
    cancelled = rng.binomial(1, np.clip(0.035 + 0.002 * lead_days, 0.03, 0.14))
    status = np.where(cancelled, "Đã hủy", np.where(no_show, "Vắng hẹn", "Hoàn thành"))
    no_show = (status == "Vắng hẹn").astype(int)
    peak = np.isin(hours, [9, 10, 14]) * 8
    base_wait = np.array([DEPARTMENTS[d][1] for d in departments])
    wait = np.clip(rng.normal(base_wait + peak, 11), 2, 100).round(1)
    wait = pd.Series(wait).mask(status != "Hoàn thành")
    patient_numbers = rng.integers(0, 1900, rows)
    patient_ids = [hashlib.sha256(f"synthetic-{n}".encode()).hexdigest()[:10] for n in patient_numbers]
    frame = pd.DataFrame(
        {
            "appointment_id": [f"APT-{i:06d}" for i in range(1, rows + 1)],
            "patient_id": patient_ids,
            "appointment_date": pd.to_datetime(dates).dt.date.astype(str),
            "department": departments,
            "appointment_hour": hours,
            "weekday_name": pd.to_datetime(dates).dt.day_name(),
            "lead_days": lead_days,
            "prior_no_shows": prior_no_shows,
            "reminder_sent": reminders,
            "outside_city": outside_city,
            "status": status,
            "no_show": no_show,
            "wait_minutes": wait,
        }
    )
    return frame.sort_values(["appointment_date", "appointment_hour"]).reset_index(drop=True)


def validate(frame: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = {
        "appointment_id",
        "patient_id",
        "appointment_date",
        "department",
        "appointment_hour",
        "weekday_name",
        "lead_days",
        "prior_no_shows",
        "reminder_sent",
        "outside_city",
        "status",
        "no_show",
        "wait_minutes",
    }
    missing = required - set(frame.columns)
    if missing:
        errors.append(f"Thiếu các cột bắt buộc: {sorted(missing)}")
        return errors
    if frame["appointment_id"].duplicated().any():
        errors.append("appointment_id phải là duy nhất")
    if frame[["appointment_id", "patient_id", "appointment_date", "department", "status"]].isna().any().any():
        errors.append("các trường khóa không được để trống")
    if pd.to_datetime(frame["appointment_date"], errors="coerce").isna().any():
        errors.append("appointment_date chứa ngày không hợp lệ")
    if not frame["appointment_hour"].between(7, 16).all():
        errors.append("appointment_hour phải nằm trong khoảng 7 đến 16")
    if (frame[["lead_days", "prior_no_shows"]] < 0).any().any():
        errors.append("lead_days và prior_no_shows không được âm")
    for column in ("reminder_sent", "outside_city", "no_show"):
        if not set(frame[column].dropna()).issubset({0, 1}):
            errors.append(f"{column} phải là biến nhị phân")
    if not set(frame["department"]).issubset(DEPARTMENTS):
        errors.append("department chứa giá trị ngoài danh mục")
    if not set(frame["status"]).issubset(VALID_STATUSES):
        errors.append("status chứa giá trị ngoài danh mục")
    if not frame.loc[frame["status"] == "Hoàn thành", "wait_minutes"].notna().all():
        errors.append("lượt khám hoàn thành phải có wait_minutes")
    if frame.loc[frame["status"] != "Hoàn thành", "wait_minutes"].notna().any():
        errors.append("lượt khám chưa hoàn thành không được có wait_minutes")
    if (frame["wait_minutes"].dropna() < 0).any():
        errors.append("wait_minutes không được âm")
    if not frame["no_show"].eq(frame["status"].eq("Vắng hẹn").astype(int)).all():
        errors.append("no_show không khớp với status")
    return errors


def build_dataset(output: Path, rows: int = 6500) -> pd.DataFrame:
    frame = generate_appointments(rows=rows)
    errors = validate(frame)
    if errors:
        raise ValueError("; ".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    return frame


def ensure_demo_dataset(output: Path, rows: int = 6500) -> bool:
    """Tạo lại dữ liệu mẫu khi tệp chưa có hoặc không còn đúng phiên bản."""
    if output.exists():
        try:
            current = pd.read_csv(output, usecols=["department", "status"])
            departments_ok = set(current["department"].dropna()).issubset(DEPARTMENTS)
            statuses_ok = set(current["status"].dropna()).issubset(VALID_STATUSES)
            if departments_ok and statuses_ok and len(current) == rows:
                return False
        except (OSError, ValueError, KeyError):
            pass
    build_dataset(output, rows=rows)
    return True
