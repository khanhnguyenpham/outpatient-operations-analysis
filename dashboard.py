from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "generated" / "appointments.csv"

st.set_page_config(page_title="Outpatient Operations", layout="wide")
st.title("Outpatient operations dashboard")
st.caption("Synthetic portfolio data — descriptive analysis only")

if not DATA.exists():
    st.error("Run `python run_analysis.py` first.")
    st.stop()

frame = pd.read_csv(DATA, parse_dates=["appointment_date"])
departments = st.sidebar.multiselect("Department", sorted(frame.department.unique()), default=sorted(frame.department.unique()))
view = frame[frame.department.isin(departments)]
eligible = view[view.status != "Cancelled"]
completed = view[view.status == "Completed"]

cols = st.columns(4)
cols[0].metric("Appointments", f"{len(view):,}")
cols[1].metric("No-show rate", f"{eligible.no_show.mean():.1%}")
cols[2].metric("Median wait", f"{completed.wait_minutes.median():.1f} min")
cols[3].metric("P90 wait", f"{completed.wait_minutes.quantile(.9):.1f} min")

monthly = view.assign(month=view.appointment_date.dt.to_period("M").astype(str)).groupby("month", as_index=False).size()
st.plotly_chart(px.line(monthly, x="month", y="size", markers=True, labels={"size": "Appointments"}), use_container_width=True)

left, right = st.columns(2)
waits = completed.groupby("department", as_index=False).wait_minutes.median().sort_values("wait_minutes")
left.plotly_chart(px.bar(waits, x="wait_minutes", y="department", orientation="h", title="Median wait"), use_container_width=True)
rates = eligible.groupby("department", as_index=False).no_show.mean().sort_values("no_show")
right.plotly_chart(px.bar(rates, x="no_show", y="department", orientation="h", title="No-show rate"), use_container_width=True)

st.info("Reminder comparisons are associations, not proof that reminders caused the difference.")

