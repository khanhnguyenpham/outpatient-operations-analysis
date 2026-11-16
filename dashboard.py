from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ops_analysis.data import ensure_demo_dataset

DATA = ROOT / "data" / "generated" / "appointments.csv"

NAVY = "#17324D"
TEAL = "#0F766E"
AMBER = "#D97706"
BLUE = "#2563EB"
PLOT_CONFIG = {"displaylogo": False, "responsive": True}

st.set_page_config(page_title="Điều hành khám ngoại trú", page_icon="🏥", layout="wide")

st.markdown(
    """
    <style>
        .stApp { background: #F5F7FA; }
        .block-container { max-width: 1440px; padding-top: 1.7rem; padding-bottom: 3rem; }
        [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E2E8F0; }
        [data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
        .hero {
            background: linear-gradient(120deg, #17324D 0%, #124E5B 100%);
            border-radius: 18px; padding: 28px 32px; color: white; margin-bottom: 20px;
            box-shadow: 0 10px 28px rgba(15, 42, 67, 0.14);
        }
        .hero .eyebrow { font-size: 12px; letter-spacing: 1.5px; font-weight: 700; opacity: .78; }
        .hero h1 { color: white; font-size: 34px; line-height: 1.18; margin: 8px 0 8px; }
        .hero p { color: #DDEAF2; font-size: 15px; margin: 0; max-width: 900px; }
        .pill {
            display: inline-block; margin-top: 16px; padding: 5px 10px; border-radius: 999px;
            background: rgba(255,255,255,.13); color: #E6F4F1; font-size: 12px; font-weight: 600;
        }
        .metric-card {
            background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 18px 20px;
            min-height: 120px; box-shadow: 0 4px 14px rgba(15, 23, 42, .045);
        }
        .metric-card .label { color: #64748B; font-size: 13px; font-weight: 600; }
        .metric-card .value { color: #17324D; font-size: 29px; font-weight: 750; margin: 6px 0 2px; }
        .metric-card .note { color: #94A3B8; font-size: 12px; }
        .section-note {
            background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #0F766E;
            border-radius: 12px; padding: 18px 20px; color: #334155; line-height: 1.58;
        }
        .warning-note {
            background: #FFF8EB; border: 1px solid #FED7AA; border-radius: 12px;
            padding: 14px 16px; color: #854D0E; font-size: 13px; line-height: 1.55;
        }
        .quality-ok {
            background: #ECFDF3; border: 1px solid #ABEFC6; border-radius: 12px;
            padding: 16px; color: #067647; font-weight: 650;
        }
        h1, h2, h3 { color: #17324D; }
        div[data-testid="stTabs"] button { font-weight: 650; }
        div[data-testid="stDataFrame"] { border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden; }
        .footer { color: #94A3B8; font-size: 12px; text-align: center; margin-top: 28px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    ensure_demo_dataset(DATA)
    return pd.read_csv(DATA, parse_dates=["appointment_date"])


def style_chart(figure: go.Figure, height: int = 380) -> go.Figure:
    figure.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif", "color": "#334155", "size": 12},
        margin={"l": 12, "r": 12, "t": 52, "b": 12},
        hoverlabel={"bgcolor": "white", "font_size": 12},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    figure.update_xaxes(showgrid=False, linecolor="#CBD5E1")
    figure.update_yaxes(gridcolor="#E8EDF3", zeroline=False)
    return figure


def metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


data = load_data()

with st.sidebar:
    st.markdown("### BỘ LỌC BÁO CÁO")
    st.caption("Điều chỉnh phạm vi dữ liệu hiển thị")
    all_departments = sorted(data["department"].unique())
    departments = st.multiselect("Chuyên khoa", all_departments, default=all_departments)
    date_min = data["appointment_date"].min().date()
    date_max = data["appointment_date"].max().date()
    date_range = st.date_input(
        "Khoảng thời gian",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
        format="DD/MM/YYYY",
    )
    st.divider()
    st.markdown("**Phạm vi dữ liệu**")
    st.caption("01/01/2025 đến 31/10/2026")
    st.caption("6 chuyên khoa · Dữ liệu mô phỏng")

filtered = data[data["department"].isin(departments)].copy()
if len(date_range) == 2:
    filtered = filtered[filtered["appointment_date"].dt.date.between(date_range[0], date_range[1])]

eligible = filtered[filtered["status"] != "Đã hủy"].copy()
completed = filtered[filtered["status"] == "Hoàn thành"].copy()

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">PHÂN TÍCH VẬN HÀNH NGOẠI TRÚ</div>
        <h1>Bảng điều hành lịch hẹn và thời gian chờ</h1>
        <p>Theo dõi nhu cầu khám, tình trạng vắng hẹn và các khung giờ cần ưu tiên rà soát vận hành.</p>
        <span class="pill">DỮ LIỆU MÔ PHỎNG · KHÔNG PHẢI DỮ LIỆU BỆNH NHÂN THẬT</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("Không có dữ liệu trong phạm vi bộ lọc đã chọn.")
    st.stop()

if eligible.empty or completed.empty:
    st.warning("Phạm vi đã chọn chưa có đủ lượt hoàn thành để tính các chỉ số vận hành.")
    st.stop()

kpi_columns = st.columns(4)
with kpi_columns[0]:
    metric_card("Tổng lịch hẹn", f"{len(filtered):,}", "Bao gồm lịch đã hủy")
with kpi_columns[1]:
    metric_card("Tỷ lệ vắng hẹn", f"{eligible['no_show'].mean():.1%}", "Loại trừ lịch đã hủy")
with kpi_columns[2]:
    metric_card("Chờ trung vị", f"{completed['wait_minutes'].median():.1f} phút", "50% lượt khám chờ thấp hơn")
with kpi_columns[3]:
    metric_card(
        "Thời gian chờ P90", f"{completed['wait_minutes'].quantile(0.9):.1f} phút", "90% lượt khám chờ thấp hơn"
    )

overview_tab, wait_tab, no_show_tab, quality_tab = st.tabs(
    ["Tổng quan", "Thời gian chờ", "Vắng hẹn", "Kiểm soát dữ liệu"]
)

with overview_tab:
    st.subheader("Xu hướng nhu cầu khám")
    monthly = (
        filtered.assign(month=filtered["appointment_date"].dt.to_period("M"))
        .groupby("month", as_index=False)
        .agg(appointments=("appointment_id", "count"))
    )
    monthly["Tháng"] = monthly["month"].dt.strftime("%m/%Y")
    demand_figure = px.area(
        monthly,
        x="Tháng",
        y="appointments",
        markers=True,
        labels={"appointments": "Số lịch hẹn"},
        color_discrete_sequence=[BLUE],
    )
    demand_figure.update_traces(line={"width": 2.5}, fillcolor="rgba(37, 99, 235, 0.10)")
    st.plotly_chart(style_chart(demand_figure, 350), width="stretch", config=PLOT_CONFIG)

    pressure = (
        completed.groupby(["department", "appointment_hour"])["wait_minutes"]
        .agg(completed_visits="size", average_wait="mean", p90_wait=lambda values: values.quantile(0.90))
        .reset_index()
    )
    pressure = pressure[pressure["completed_visits"] >= 50].sort_values("p90_wait", ascending=False)
    if pressure.empty:
        top_pressure = None
    else:
        top_pressure = pressure.iloc[0]
    reminder_rates = eligible.groupby("reminder_sent")["no_show"].mean()
    reminder_difference = (reminder_rates.get(0, 0) - reminder_rates.get(1, 0)) * 100

    left, right = st.columns([1.45, 1])
    with left:
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        weekday_labels = {
            "Monday": "Thứ Hai",
            "Tuesday": "Thứ Ba",
            "Wednesday": "Thứ Tư",
            "Thursday": "Thứ Năm",
            "Friday": "Thứ Sáu",
            "Saturday": "Thứ Bảy",
        }
        heatmap_data = filtered.pivot_table(
            index="weekday_name", columns="appointment_hour", values="appointment_id", aggfunc="count", fill_value=0
        ).reindex([day for day in weekday_order if day in filtered["weekday_name"].unique()])
        heatmap_data.index = [weekday_labels[value] for value in heatmap_data.index]
        heatmap = px.imshow(
            heatmap_data,
            aspect="auto",
            color_continuous_scale=[[0, "#E8F1F8"], [1, NAVY]],
            labels={"x": "Giờ hẹn", "y": "Ngày trong tuần", "color": "Số lịch"},
            title="Mật độ lịch hẹn theo ngày và giờ",
        )
        st.plotly_chart(style_chart(heatmap, 360), width="stretch", config=PLOT_CONFIG)
    with right:
        st.markdown("### Điểm cần chú ý")
        pressure_note = (
            f"{top_pressure['department']} lúc {int(top_pressure['appointment_hour']):02d}:00 có P90 chờ "
            f"<b>{top_pressure['p90_wait']:.1f} phút</b> trên "
            f"{int(top_pressure['completed_visits'])} lượt khám hoàn thành."
            if top_pressure is not None
            else "Chưa có lát cắt nào đạt ngưỡng tối thiểu 50 lượt hoàn thành trong phạm vi đang chọn."
        )
        st.markdown(
            f"""
            <div class="section-note">
                <b>Khung giờ áp lực nhất</b><br>
                {pressure_note}
                <br><br>
                <b>Tín hiệu nhắc hẹn</b><br>
                Nhóm có ghi nhận gửi nhắc hẹn có tỷ lệ vắng thấp hơn
                <b>{reminder_difference:.2f} điểm phần trăm</b>. Đây chỉ là mối liên hệ mô tả.
            </div>
            """,
            unsafe_allow_html=True,
        )

with wait_tab:
    st.subheader("So sánh thời gian chờ theo chuyên khoa")
    department_wait = (
        completed.groupby("department")["wait_minutes"]
        .agg(
            completed_visits="size",
            average_wait="mean",
            median_wait="median",
            p90_wait=lambda values: values.quantile(0.90),
        )
        .reset_index()
        .sort_values("p90_wait", ascending=True)
    )
    wait_chart = go.Figure()
    wait_chart.add_bar(
        y=department_wait["department"],
        x=department_wait["p90_wait"],
        name="P90",
        orientation="h",
        marker_color="#9FB8CB",
    )
    wait_chart.add_bar(
        y=department_wait["department"],
        x=department_wait["median_wait"],
        name="Trung vị",
        orientation="h",
        marker_color=TEAL,
    )
    wait_chart.update_layout(barmode="overlay", title="Trung vị và P90 thời gian chờ", xaxis_title="Phút")
    st.plotly_chart(style_chart(wait_chart, 420), width="stretch", config=PLOT_CONFIG)

    st.subheader("Danh sách khung giờ ưu tiên rà soát")
    st.caption("Chỉ hiển thị lát cắt có ít nhất 50 lượt khám hoàn thành để hạn chế xếp hạng từ mẫu quá nhỏ.")
    pressure_display = pressure.head(12).copy()
    pressure_display["Khung giờ"] = pressure_display["appointment_hour"].map(lambda value: f"{int(value):02d}:00")
    pressure_display = pressure_display.rename(
        columns={
            "department": "Chuyên khoa",
            "completed_visits": "Lượt hoàn thành",
            "average_wait": "Chờ trung bình (phút)",
            "p90_wait": "P90 (phút)",
        }
    )[["Chuyên khoa", "Khung giờ", "Lượt hoàn thành", "Chờ trung bình (phút)", "P90 (phút)"]]
    st.dataframe(
        pressure_display.style.format({"Chờ trung bình (phút)": "{:.1f}", "P90 (phút)": "{:.1f}"}),
        width="stretch",
        hide_index=True,
    )

with no_show_tab:
    st.subheader("Phân tích tình trạng vắng hẹn")
    department_no_show = (
        eligible.groupby("department", as_index=False)
        .agg(eligible_appointments=("appointment_id", "count"), no_show_rate=("no_show", "mean"))
        .sort_values("no_show_rate")
    )
    left, right = st.columns(2)
    with left:
        no_show_chart = px.bar(
            department_no_show,
            x="no_show_rate",
            y="department",
            orientation="h",
            title="Tỷ lệ vắng hẹn theo chuyên khoa",
            labels={"no_show_rate": "Tỷ lệ vắng hẹn", "department": ""},
            color_discrete_sequence=[AMBER],
        )
        no_show_chart.update_xaxes(tickformat=".0%")
        st.plotly_chart(style_chart(no_show_chart, 390), width="stretch", config=PLOT_CONFIG)
    with right:
        reminder = (
            eligible.groupby("reminder_sent", as_index=False)
            .agg(eligible_appointments=("appointment_id", "count"), no_show_rate=("no_show", "mean"))
            .assign(reminder=lambda frame: frame["reminder_sent"].map({0: "Không ghi nhận", 1: "Đã gửi nhắc hẹn"}))
        )
        reminder_chart = px.bar(
            reminder,
            x="reminder",
            y="no_show_rate",
            title="Tỷ lệ vắng theo trạng thái nhắc hẹn",
            labels={"reminder": "", "no_show_rate": "Tỷ lệ vắng hẹn"},
            color="reminder",
            color_discrete_map={"Không ghi nhận": "#94A3B8", "Đã gửi nhắc hẹn": TEAL},
            text_auto=".1%",
        )
        reminder_chart.update_yaxes(tickformat=".0%")
        reminder_chart.update_layout(showlegend=False)
        st.plotly_chart(style_chart(reminder_chart, 390), width="stretch", config=PLOT_CONFIG)
    st.markdown(
        """
        <div class="warning-note">
            <b>Lưu ý phương pháp:</b> So sánh nhắc hẹn là phân tích mô tả, không chứng minh việc gửi nhắc hẹn
            trực tiếp làm giảm vắng hẹn. Trong dữ liệu mô phỏng, khả năng gửi nhắc hẹn
            có liên quan đến số ngày đặt trước.
        </div>
        """,
        unsafe_allow_html=True,
    )

with quality_tab:
    st.subheader("Kiểm soát chất lượng và phạm vi sử dụng")
    duplicate_ids = int(filtered["appointment_id"].duplicated().sum())
    missing_departments = int(filtered["department"].isna().sum())
    missing_wait = int(completed["wait_minutes"].isna().sum())
    quality_columns = st.columns(3)
    for column, label, value in zip(
        quality_columns,
        ["Mã lịch hẹn trùng", "Thiếu chuyên khoa", "Thiếu thời gian chờ"],
        [duplicate_ids, missing_departments, missing_wait],
        strict=True,
    ):
        with column:
            st.markdown(f'<div class="quality-ok">Đạt · {label}: {value}</div>', unsafe_allow_html=True)

    st.markdown("### Quy tắc tính KPI")
    definitions = pd.DataFrame(
        [
            ["Tỷ lệ vắng hẹn", "Vắng hẹn / (Hoàn thành + Vắng hẹn)", "Loại trừ lịch đã hủy"],
            ["Chờ trung vị", "Trung vị số phút từ đến nơi đến bắt đầu phục vụ", "Chỉ lượt hoàn thành"],
            ["P90 thời gian chờ", "Phân vị 90% của thời gian chờ", "Chỉ lượt hoàn thành"],
            ["Lát cắt ưu tiên", "Chuyên khoa theo khung giờ", "Tối thiểu 50 lượt hoàn thành"],
        ],
        columns=["Chỉ số", "Cách tính", "Phạm vi"],
    )
    st.dataframe(definitions, width="stretch", hide_index=True)

    st.markdown("### Tải dữ liệu theo bộ lọc")
    st.download_button(
        "Tải CSV mô phỏng",
        data=filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="du_lieu_ngoai_tru_mo_phong.csv",
        mime="text/csv",
    )
    st.caption("Tệp chỉ chứa dữ liệu mô phỏng, không có thông tin nhận dạng bệnh nhân thật.")

st.markdown(
    '<div class="footer">Đồ án phân tích dữ liệu · Python, SQL, SQLite và Streamlit · Dữ liệu mô phỏng</div>',
    unsafe_allow_html=True,
)
