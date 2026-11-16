import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ops_analysis.data import ensure_demo_dataset

DATA = ROOT / "data" / "generated" / "appointments.csv"

st.set_page_config(page_title="Outpatient Operations", layout="wide")
st.title("Outpatient operations dashboard")
st.caption("Synthetic portfolio data — descriptive analysis only")

if not DATA.exists():
    with st.spinner("Preparing reproducible demo data..."):
        ensure_demo_dataset(DATA)

frame = pd.read_csv(DATA, parse_dates=["appointment_date"])
departments = st.sidebar.multiselect(
    "Department", sorted(frame.department.unique()), default=sorted(frame.department.unique())
)
date_min, date_max = frame.appointment_date.min().date(), frame.appointment_date.max().date()
date_range = st.sidebar.date_input("Date range", value=(date_min, date_max), min_value=date_min, max_value=date_max)
view = frame[frame.department.isin(departments)]
if len(date_range) == 2:
    view = view[view.appointment_date.dt.date.between(date_range[0], date_range[1])]
eligible = view[view.status != "Cancelled"]
completed = view[view.status == "Completed"]

cols = st.columns(4)
cols[0].metric("Appointments", f"{len(view):,}")
cols[1].metric("No-show rate", f"{eligible.no_show.mean():.1%}")
cols[2].metric("Median wait", f"{completed.wait_minutes.median():.1f} min")
cols[3].metric("P90 wait", f"{completed.wait_minutes.quantile(0.9):.1f} min")

monthly = view.assign(month=view.appointment_date.dt.to_period("M").astype(str)).groupby("month", as_index=False).size()
st.plotly_chart(px.line(monthly, x="month", y="size", markers=True, labels={"size": "Appointments"}), width="stretch")

left, right = st.columns(2)
waits = completed.groupby("department", as_index=False).wait_minutes.median().sort_values("wait_minutes")
left.plotly_chart(
    px.bar(waits, x="wait_minutes", y="department", orientation="h", title="Median wait"), width="stretch"
)
rates = eligible.groupby("department", as_index=False).no_show.mean().sort_values("no_show")
right.plotly_chart(px.bar(rates, x="no_show", y="department", orientation="h", title="No-show rate"), width="stretch")

st.subheader("Demand pressure by weekday and hour")
pressure = view.pivot_table(
    index="weekday_name", columns="appointment_hour", values="appointment_id", aggfunc="count", fill_value=0
)
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
pressure = pressure.reindex([day for day in weekday_order if day in pressure.index])
st.plotly_chart(
    px.imshow(pressure, aspect="auto", color_continuous_scale="Blues", labels={"color": "Appointments"}),
    width="stretch",
)

st.info("Reminder comparisons are associations, not proof that reminders caused the difference.")
