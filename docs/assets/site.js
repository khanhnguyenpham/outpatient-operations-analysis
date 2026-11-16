const COLORS = {
  navy: "#173c56",
  navyLight: "#8da9bb",
  teal: "#0f766e",
  tealLight: "#b9e1dc",
  amber: "#d97706",
  amberLight: "#f4c47c",
  slate: "#687887",
  grid: "#e7edf2",
};

const WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const WEEKDAY_LABELS = {
  Monday: "Thứ Hai",
  Tuesday: "Thứ Ba",
  Wednesday: "Thứ Tư",
  Thursday: "Thứ Năm",
  Friday: "Thứ Sáu",
  Saturday: "Thứ Bảy",
};
const PLOT_CONFIG = { displayModeBar: false, responsive: true, scrollZoom: false };

const state = {
  records: [],
  departments: [],
  selectedDepartments: new Set(),
  minMonth: "2025-01",
  maxMonth: "2026-10",
};

const numberFormatter = new Intl.NumberFormat("vi-VN");
const decimalFormatter = new Intl.NumberFormat("vi-VN", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});
const percentFormatter = new Intl.NumberFormat("vi-VN", {
  style: "percent",
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

function quantile(values, probability) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const index = (sorted.length - 1) * probability;
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  if (lower === upper) return sorted[lower];
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (index - lower);
}

function percentileHigher(values, probability) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.max(0, Math.ceil(sorted.length * probability) - 1)];
}

function mean(values) {
  return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
}

function groupBy(items, keyFunction) {
  const groups = new Map();
  items.forEach((item) => {
    const key = keyFunction(item);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  });
  return groups;
}

function baseLayout(height = 360) {
  return {
    height,
    autosize: true,
    margin: { l: 54, r: 28, t: 22, b: 48 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: "Inter, Segoe UI, sans-serif", size: 11, color: "#3c4a57" },
    hoverlabel: { bgcolor: "#ffffff", bordercolor: "#dfe6ec", font: { color: "#17212b" } },
    legend: { orientation: "h", x: 0, y: 1.12, font: { size: 10 } },
    xaxis: { gridcolor: COLORS.grid, zeroline: false, linecolor: "#cbd5df" },
    yaxis: { gridcolor: COLORS.grid, zeroline: false, linecolor: "#cbd5df" },
  };
}

function emptyPlot(targetId, message) {
  const layout = baseLayout(300);
  layout.xaxis.visible = false;
  layout.yaxis.visible = false;
  layout.annotations = [
    {
      text: message,
      showarrow: false,
      font: { color: COLORS.slate, size: 12 },
    },
  ];
  Plotly.react(targetId, [], layout, PLOT_CONFIG);
}

function monthLabel(value) {
  const [year, month] = value.split("-");
  return `${month}/${year}`;
}

function getFilteredRecords() {
  const start = document.querySelector("#start-month").value;
  const end = document.querySelector("#end-month").value;
  return state.records.filter((record) => {
    const month = record.d.slice(0, 7);
    return state.selectedDepartments.has(record.p) && month >= start && month <= end;
  });
}

function calculateDepartmentWait(completed) {
  return [...groupBy(completed, (record) => record.p).entries()].map(([department, records]) => {
    const waits = records.map((record) => record.t).filter((value) => value !== null);
    return {
      department,
      completed: records.length,
      average: mean(waits),
      median: quantile(waits, 0.5),
      p90: percentileHigher(waits, 0.9),
    };
  });
}

function calculatePressure(completed, minimumVisits = 50) {
  return [...groupBy(completed, (record) => `${record.p}|${record.h}`).entries()]
    .map(([key, records]) => {
      const [department, hour] = key.split("|");
      const waits = records.map((record) => record.t).filter((value) => value !== null);
      return {
        department,
        hour: Number(hour),
        completed: records.length,
        average: mean(waits),
        p90: percentileHigher(waits, 0.9),
      };
    })
    .filter((row) => row.completed >= minimumVisits)
    .sort((a, b) => b.p90 - a.p90 || b.completed - a.completed);
}

function calculateStageSummary(completed) {
  return [...groupBy(completed, (record) => record.p).entries()].map(([department, records]) => ({
    department,
    checkin: mean(records.map((record) => record.ci).filter((value) => value !== null)),
    room: mean(records.map((record) => record.rm).filter((value) => value !== null)),
    clinician: mean(records.map((record) => record.cl).filter((value) => value !== null)),
    total: mean(records.map((record) => record.t).filter((value) => value !== null)),
  }));
}

function renderDepartmentFilters() {
  const container = document.querySelector("#department-options");
  container.innerHTML = "";
  state.departments.forEach((department) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "filter-chip";
    button.textContent = department;
    button.dataset.department = department;
    button.setAttribute("aria-pressed", "true");
    button.addEventListener("click", () => {
      if (state.selectedDepartments.has(department)) {
        if (state.selectedDepartments.size === 1) return;
        state.selectedDepartments.delete(department);
        button.setAttribute("aria-pressed", "false");
      } else {
        state.selectedDepartments.add(department);
        button.setAttribute("aria-pressed", "true");
      }
      renderDashboard();
    });
    container.append(button);
  });
}

function renderKpis(records, eligible, completed) {
  const waits = completed.map((record) => record.t).filter((value) => value !== null);
  const noShowRate = eligible.length ? eligible.reduce((sum, record) => sum + record.n, 0) / eligible.length : 0;
  const median = quantile(waits, 0.5);
  const p90 = percentileHigher(waits, 0.9);

  document.querySelector("#kpi-appointments").textContent = numberFormatter.format(records.length);
  document.querySelector("#kpi-no-show").textContent = percentFormatter.format(noShowRate);
  document.querySelector("#kpi-median").textContent = `${decimalFormatter.format(median)} phút`;
  document.querySelector("#kpi-p90").textContent = `${decimalFormatter.format(p90)} phút`;
}

function renderMonthlyChart(records) {
  const monthly = [...groupBy(records, (record) => record.d.slice(0, 7)).entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([month, rows]) => {
      const eligible = rows.filter((record) => record.s !== "Đã hủy");
      return {
        month,
        appointments: rows.length,
        noShowRate: eligible.reduce((sum, record) => sum + record.n, 0) / eligible.length,
      };
    });

  const layout = baseLayout(350);
  layout.margin.r = 56;
  layout.xaxis = { type: "category", tickangle: -35, showgrid: false, linecolor: "#cbd5df" };
  layout.yaxis = { title: "Số lịch hẹn", gridcolor: COLORS.grid, rangemode: "tozero" };
  layout.yaxis2 = {
    title: "Tỷ lệ vắng",
    overlaying: "y",
    side: "right",
    tickformat: ".0%",
    showgrid: false,
    rangemode: "tozero",
  };

  Plotly.react(
    "monthly-chart",
    [
      {
        type: "bar",
        name: "Lịch hẹn",
        x: monthly.map((row) => monthLabel(row.month)),
        y: monthly.map((row) => row.appointments),
        marker: { color: COLORS.navyLight },
        hovertemplate: "%{x}<br><b>%{y}</b> lịch hẹn<extra></extra>",
      },
      {
        type: "scatter",
        mode: "lines+markers",
        name: "Tỷ lệ vắng",
        x: monthly.map((row) => monthLabel(row.month)),
        y: monthly.map((row) => row.noShowRate),
        yaxis: "y2",
        line: { color: COLORS.amber, width: 2.5 },
        marker: { color: COLORS.amber, size: 5 },
        hovertemplate: "%{x}<br><b>%{y:.1%}</b> vắng hẹn<extra></extra>",
      },
    ],
    layout,
    PLOT_CONFIG,
  );
}

function renderHeatmap(records) {
  const hours = Array.from({ length: 10 }, (_, index) => index + 7);
  const matrix = WEEKDAYS.map((weekday) =>
    hours.map(
      (hour) => records.filter((record) => record.w === weekday && record.h === hour).length,
    ),
  );
  const layout = baseLayout(350);
  layout.margin = { l: 78, r: 20, t: 22, b: 42 };
  layout.xaxis = { title: "Giờ hẹn", dtick: 1, showgrid: false };
  layout.yaxis = { autorange: "reversed", showgrid: false };

  Plotly.react(
    "heatmap-chart",
    [
      {
        type: "heatmap",
        x: hours,
        y: WEEKDAYS.map((day) => WEEKDAY_LABELS[day]),
        z: matrix,
        colorscale: [
          [0, "#eef5f7"],
          [0.5, "#82bbb5"],
          [1, COLORS.navy],
        ],
        colorbar: { title: "Lịch", thickness: 10, len: 0.75 },
        hovertemplate: "%{y}, %{x}:00<br><b>%{z}</b> lịch hẹn<extra></extra>",
      },
    ],
    layout,
    PLOT_CONFIG,
  );
}

function renderWaitChart(departmentWait) {
  const rows = [...departmentWait].sort((a, b) => a.p90 - b.p90);
  if (!rows.length) {
    emptyPlot("wait-chart", "Chưa có lượt hoàn thành trong phạm vi lựa chọn.");
    return;
  }
  const layout = baseLayout(430);
  layout.barmode = "group";
  layout.margin = { l: 150, r: 24, t: 26, b: 48 };
  layout.xaxis = { title: "Phút", gridcolor: COLORS.grid, rangemode: "tozero" };
  layout.yaxis = { showgrid: false };

  Plotly.react(
    "wait-chart",
    [
      {
        type: "bar",
        name: "Trung vị",
        orientation: "h",
        y: rows.map((row) => row.department),
        x: rows.map((row) => row.median),
        marker: { color: COLORS.teal },
        hovertemplate: "%{y}<br>Trung vị: <b>%{x:.1f} phút</b><extra></extra>",
      },
      {
        type: "bar",
        name: "P90",
        orientation: "h",
        y: rows.map((row) => row.department),
        x: rows.map((row) => row.p90),
        marker: { color: COLORS.navyLight },
        hovertemplate: "%{y}<br>P90: <b>%{x:.1f} phút</b><extra></extra>",
      },
    ],
    layout,
    PLOT_CONFIG,
  );
}

function renderStageChart(completed) {
  const rows = calculateStageSummary(completed).sort((a, b) => a.total - b.total);
  const layout = baseLayout(430);
  layout.barmode = "stack";
  layout.margin = { l: 150, r: 24, t: 30, b: 48 };
  layout.xaxis = { title: "Phút trung bình", gridcolor: COLORS.grid, rangemode: "tozero" };
  layout.yaxis = { showgrid: false };

  Plotly.react(
    "stage-chart",
    [
      {
        type: "bar",
        name: "Tiếp nhận",
        orientation: "h",
        y: rows.map((row) => row.department),
        x: rows.map((row) => row.checkin),
        marker: { color: COLORS.tealLight },
        hovertemplate: "%{y}<br>Tiếp nhận: <b>%{x:.1f} phút</b><extra></extra>",
      },
      {
        type: "bar",
        name: "Chờ vào phòng",
        orientation: "h",
        y: rows.map((row) => row.department),
        x: rows.map((row) => row.room),
        marker: { color: COLORS.navyLight },
        hovertemplate: "%{y}<br>Chờ vào phòng: <b>%{x:.1f} phút</b><extra></extra>",
      },
      {
        type: "bar",
        name: "Chờ bắt đầu khám",
        orientation: "h",
        y: rows.map((row) => row.department),
        x: rows.map((row) => row.clinician),
        marker: { color: COLORS.navy },
        hovertemplate: "%{y}<br>Chờ bắt đầu khám: <b>%{x:.1f} phút</b><extra></extra>",
      },
    ],
    layout,
    PLOT_CONFIG,
  );
}

function renderSensitivity(completed) {
  const thresholds = [30, 50, 70];
  const results = thresholds.map((threshold) => ({
    threshold,
    rows: calculatePressure(completed, threshold).slice(0, 3),
  }));
  const container = document.querySelector("#sensitivity-grid");
  container.innerHTML = results
    .map(({ threshold, rows }) => {
      const ranking = rows.length
        ? rows
            .map(
              (row, index) =>
                `<li><span>${index + 1}</span>${row.department} · ${String(row.hour).padStart(2, "0")}:00</li>`,
            )
            .join("")
        : "<li>Chưa có lát cắt đủ mẫu</li>";
      return `
        <article class="sensitivity-card">
          <p>NGƯỠNG TỐI THIỂU</p>
          <strong>${threshold} lượt</strong>
          <ol>${ranking}</ol>
        </article>
      `;
    })
    .join("");

  const signatures = results.map(({ rows }) => rows.map((row) => `${row.department}|${row.hour}`).join(","));
  const enoughData = results.every(({ rows }) => rows.length === 3);
  const stable = enoughData && signatures.every((signature) => signature === signatures[0]);
  document.querySelector("#sensitivity-conclusion").textContent = !enoughData
    ? "Phạm vi đang chọn chưa đủ ba lát cắt ở mọi ngưỡng để đánh giá độ bền kết luận."
    : stable
      ? "Kết luận ổn định: ba vị trí đầu không thay đổi ở cả ba ngưỡng."
      : "Thứ hạng thay đổi theo ngưỡng; cần diễn giải thận trọng khi ưu tiên lát cắt.";
}

function renderPressureTable(pressure) {
  const body = document.querySelector("#pressure-table");
  body.innerHTML = "";
  if (!pressure.length) {
    const row = document.createElement("tr");
    row.className = "empty-row";
    row.innerHTML = '<td colspan="4">Chưa có lát cắt đạt ngưỡng 50 lượt hoàn thành.</td>';
    body.append(row);
    return;
  }
  pressure.slice(0, 8).forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.department}</td>
      <td>${String(item.hour).padStart(2, "0")}:00</td>
      <td>${numberFormatter.format(item.completed)}</td>
      <td><strong>${decimalFormatter.format(item.p90)}′</strong></td>
    `;
    body.append(row);
  });
}

function renderNoShowChart(eligible) {
  const rows = [...groupBy(eligible, (record) => record.p).entries()]
    .map(([department, records]) => ({
      department,
      rate: records.reduce((sum, record) => sum + record.n, 0) / records.length,
    }))
    .sort((a, b) => a.rate - b.rate);
  const layout = baseLayout(350);
  layout.margin = { l: 150, r: 30, t: 24, b: 44 };
  layout.xaxis = { tickformat: ".0%", gridcolor: COLORS.grid, rangemode: "tozero" };
  layout.yaxis = { showgrid: false };

  Plotly.react(
    "no-show-chart",
    [
      {
        type: "bar",
        orientation: "h",
        x: rows.map((row) => row.rate),
        y: rows.map((row) => row.department),
        marker: { color: COLORS.amber },
        hovertemplate: "%{y}<br><b>%{x:.1%}</b><extra></extra>",
      },
    ],
    layout,
    PLOT_CONFIG,
  );
}

function renderReminderChart(eligible) {
  const groups = [0, 1].map((value) => {
    const rows = eligible.filter((record) => record.r === value);
    return {
      label: value === 1 ? "Đã gửi nhắc hẹn" : "Không ghi nhận",
      rate: rows.length ? rows.reduce((sum, record) => sum + record.n, 0) / rows.length : 0,
    };
  });
  const layout = baseLayout(350);
  layout.margin = { l: 58, r: 24, t: 24, b: 76 };
  layout.xaxis = { showgrid: false };
  layout.yaxis = { tickformat: ".0%", gridcolor: COLORS.grid, rangemode: "tozero" };

  Plotly.react(
    "reminder-chart",
    [
      {
        type: "bar",
        x: groups.map((row) => row.label),
        y: groups.map((row) => row.rate),
        text: groups.map((row) => percentFormatter.format(row.rate)),
        textposition: "outside",
        marker: { color: [COLORS.navyLight, COLORS.teal] },
        hovertemplate: "%{x}<br><b>%{y:.1%}</b><extra></extra>",
      },
    ],
    layout,
    PLOT_CONFIG,
  );
}

function renderControlChart(eligible) {
  const monthly = [...groupBy(eligible, (record) => record.d.slice(0, 7)).entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([month, rows]) => ({
      month,
      n: rows.length,
      rate: rows.reduce((sum, record) => sum + record.n, 0) / rows.length,
    }));
  const overall = eligible.reduce((sum, record) => sum + record.n, 0) / eligible.length;
  monthly.forEach((row) => {
    const sigma = Math.sqrt((overall * (1 - overall)) / row.n);
    row.ucl = Math.min(1, overall + 3 * sigma);
    row.lcl = Math.max(0, overall - 3 * sigma);
    row.signal = row.rate > row.ucl || row.rate < row.lcl;
  });
  const labels = monthly.map((row) => monthLabel(row.month));
  const signalCount = monthly.filter((row) => row.signal).length;
  const layout = baseLayout(390);
  layout.margin = { l: 60, r: 26, t: 30, b: 62 };
  layout.xaxis = { type: "category", tickangle: -35, showgrid: false };
  layout.yaxis = { title: "Tỷ lệ vắng hẹn", tickformat: ".0%", gridcolor: COLORS.grid, rangemode: "tozero" };

  Plotly.react(
    "control-chart",
    [
      {
        type: "scatter",
        mode: "lines+markers",
        name: "Tỷ lệ theo tháng",
        x: labels,
        y: monthly.map((row) => row.rate),
        line: { color: COLORS.amber, width: 2.5 },
        marker: {
          size: 7,
          color: monthly.map((row) => (row.signal ? "#b42318" : COLORS.amber)),
        },
        hovertemplate: "%{x}<br><b>%{y:.1%}</b><extra></extra>",
      },
      {
        type: "scatter",
        mode: "lines",
        name: "Giới hạn trên",
        x: labels,
        y: monthly.map((row) => row.ucl),
        line: { color: COLORS.navyLight, dash: "dash", width: 1.5 },
        hovertemplate: "%{x}<br>UCL: %{y:.1%}<extra></extra>",
      },
      {
        type: "scatter",
        mode: "lines",
        name: "Đường trung tâm",
        x: labels,
        y: monthly.map(() => overall),
        line: { color: COLORS.teal, width: 1.5 },
        hovertemplate: "Tỷ lệ chung: %{y:.1%}<extra></extra>",
      },
      {
        type: "scatter",
        mode: "lines",
        name: "Giới hạn dưới",
        x: labels,
        y: monthly.map((row) => row.lcl),
        line: { color: COLORS.navyLight, dash: "dash", width: 1.5 },
        hovertemplate: "%{x}<br>LCL: %{y:.1%}<extra></extra>",
      },
    ],
    layout,
    PLOT_CONFIG,
  );

  document.querySelector("#control-conclusion").textContent = signalCount
    ? `${signalCount} tháng nằm ngoài giới hạn kiểm soát và cần được đối chiếu với sự kiện vận hành.`
    : "Không có tháng nào vượt giới hạn ba sigma; biến động hiện tại phù hợp với nhiễu nguyên nhân chung.";
}

function renderInsights(departmentWait, pressure, completed) {
  const container = document.querySelector("#dynamic-insights");
  const worstDepartment = [...departmentWait].sort((a, b) => b.p90 - a.p90)[0];
  const topPressure = pressure[0];
  const worstStage = calculateStageSummary(completed).sort((a, b) => b.total - a.total)[0];

  const insights = [
    {
      label: "CHUYÊN KHOA",
      value: `${worstDepartment.department} có P90 ${decimalFormatter.format(worstDepartment.p90)} phút, cao nhất phạm vi đang chọn.`,
    },
    {
      label: "KHUNG GIỜ",
      value: topPressure
        ? `${topPressure.department} lúc ${String(topPressure.hour).padStart(2, "0")}:00 đứng đầu bảng áp lực ổn định.`
        : "Chưa có tổ hợp chuyên khoa – khung giờ đạt tối thiểu 50 lượt hoàn thành.",
    },
    {
      label: "CÔNG ĐOẠN",
      value: `Tại ${worstStage.department}, chờ bắt đầu khám chiếm ${decimalFormatter.format(worstStage.clinician)} trên ${decimalFormatter.format(worstStage.total)} phút trung bình.`,
    },
  ];

  container.innerHTML = insights
    .map(
      (item) => `
        <div class="insight-item">
          <span>${item.label}</span>
          <strong>${item.value}</strong>
        </div>
      `,
    )
    .join("");

  document.querySelector("#hero-department").textContent = worstDepartment.department;
  document.querySelector("#hero-p90").textContent = decimalFormatter.format(worstDepartment.p90);
  document.querySelector("#hero-finding-copy").textContent = "có P90 thời gian chờ cao nhất trong phạm vi đang chọn.";
}

function renderDashboard() {
  const status = document.querySelector("#status-message");
  const records = getFilteredRecords();
  const eligible = records.filter((record) => record.s !== "Đã hủy");
  const completed = records.filter((record) => record.s === "Hoàn thành");
  const start = document.querySelector("#start-month").value;
  const end = document.querySelector("#end-month").value;

  document.querySelector("#filter-summary").textContent = `${numberFormatter.format(records.length)} lịch hẹn · ${state.selectedDepartments.size} chuyên khoa · ${monthLabel(start)} đến ${monthLabel(end)}`;

  if (!records.length || !completed.length) {
    status.hidden = false;
    status.className = "status-message error";
    status.textContent = "Phạm vi lựa chọn chưa có đủ dữ liệu hoàn thành để tính các chỉ số.";
    document.querySelector("#kpi-grid").hidden = true;
    return;
  }

  status.hidden = true;
  document.querySelector("#kpi-grid").hidden = false;
  const departmentWait = calculateDepartmentWait(completed);
  const pressure = calculatePressure(completed);

  renderKpis(records, eligible, completed);
  renderMonthlyChart(records);
  renderHeatmap(records);
  renderWaitChart(departmentWait);
  renderStageChart(completed);
  renderPressureTable(pressure);
  renderSensitivity(completed);
  renderNoShowChart(eligible);
  renderReminderChart(eligible);
  renderControlChart(eligible);
  renderInsights(departmentWait, pressure, completed);
}

function bindControls() {
  const startInput = document.querySelector("#start-month");
  const endInput = document.querySelector("#end-month");

  startInput.addEventListener("change", () => {
    if (startInput.value > endInput.value) endInput.value = startInput.value;
    renderDashboard();
  });
  endInput.addEventListener("change", () => {
    if (endInput.value < startInput.value) startInput.value = endInput.value;
    renderDashboard();
  });
  document.querySelector("#reset-filters").addEventListener("click", () => {
    state.selectedDepartments = new Set(state.departments);
    startInput.value = state.minMonth;
    endInput.value = state.maxMonth;
    document.querySelectorAll(".filter-chip").forEach((button) => button.setAttribute("aria-pressed", "true"));
    renderDashboard();
  });
}

async function initialize() {
  const status = document.querySelector("#status-message");
  try {
    const response = await fetch("assets/appointments.json");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    state.records = payload.records;
    state.departments = payload.metadata.departments;
    state.selectedDepartments = new Set(state.departments);
    state.minMonth = payload.metadata.date_min.slice(0, 7);
    state.maxMonth = payload.metadata.date_max.slice(0, 7);

    document.querySelector("#start-month").value = state.minMonth;
    document.querySelector("#end-month").value = state.maxMonth;
    renderDepartmentFilters();
    bindControls();
    renderDashboard();
  } catch (error) {
    status.className = "status-message error";
    status.textContent = "Không thể tải dữ liệu dashboard. Vui lòng thử tải lại trang.";
    console.error("Lỗi tải dữ liệu:", error);
  }
}

initialize();
