from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

DEPARTMENTS = {
    "Internal Medicine": (0.30, 24),
    "Pediatrics": (0.22, 18),
    "Cardiology": (0.16, 32),
    "Orthopedics": (0.14, 28),
    "Ophthalmology": (0.11, 20),
    "Endocrinology": (0.07, 26),
}
VALID_STATUSES = {"Completed", "No-show", "Cancelled"}


def generate_appointments(rows: int = 6500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2025-01-01")
    dates = start + pd.to_timedelta(rng.integers(0, 640, rows), unit="D")
    dates = pd.Series(dates)
    dates = dates.mask(dates.dt.dayofweek.eq(6), dates + pd.offsets.Day(1))
    departments = rng.choice(list(DEPARTMENTS), rows, p=[v[0] for v in DEPARTMENTS.values()])
    hours = rng.choice(range(7, 17), rows, p=[.07, .13, .14, .13, .09, .07, .11, .11, .09, .06])
    lead_days = np.clip(rng.gamma(2.2, 5.0, rows).round().astype(int), 0, 60)
    prior_no_shows = np.clip(rng.poisson(.25, rows), 0, 4)
    reminders = rng.binomial(1, np.where(lead_days > 1, .80, .35))
    outside_city = rng.binomial(1, .22, rows)
    log_odds = -2.25 + .045 * lead_days + .65 * prior_no_shows - .55 * reminders + .32 * outside_city
    probability = 1 / (1 + np.exp(-log_odds))
    no_show = rng.binomial(1, probability)
    cancelled = rng.binomial(1, np.clip(.035 + .002 * lead_days, .03, .14))
    status = np.where(cancelled, "Cancelled", np.where(no_show, "No-show", "Completed"))
    no_show = (status == "No-show").astype(int)
    peak = np.isin(hours, [9, 10, 14]) * 8
    base_wait = np.array([DEPARTMENTS[d][1] for d in departments])
    wait = np.clip(rng.normal(base_wait + peak, 11), 2, 100).round(1)
    wait = pd.Series(wait).mask(status != "Completed")
    patient_numbers = rng.integers(0, 1900, rows)
    patient_ids = [hashlib.sha256(f"synthetic-{n}".encode()).hexdigest()[:10] for n in patient_numbers]
    frame = pd.DataFrame({
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
    })
    return frame.sort_values(["appointment_date", "appointment_hour"]).reset_index(drop=True)


def validate(frame: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = {"appointment_id", "appointment_date", "department", "status", "no_show", "wait_minutes"}
    missing = required - set(frame.columns)
    if missing:
        errors.append(f"Missing columns: {sorted(missing)}")
        return errors
    if frame["appointment_id"].duplicated().any():
        errors.append("appointment_id must be unique")
    if not set(frame["status"]).issubset(VALID_STATUSES):
        errors.append("status contains an unexpected value")
    if not frame.loc[frame["status"] == "Completed", "wait_minutes"].notna().all():
        errors.append("completed visits must have wait_minutes")
    if (frame["wait_minutes"].dropna() < 0).any():
        errors.append("wait_minutes cannot be negative")
    if not frame["no_show"].eq(frame["status"].eq("No-show").astype(int)).all():
        errors.append("no_show does not match status")
    return errors


def build_dataset(output: Path, rows: int = 6500) -> pd.DataFrame:
    frame = generate_appointments(rows=rows)
    errors = validate(frame)
    if errors:
        raise ValueError("; ".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    return frame

