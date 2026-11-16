-- name: monthly_trend
-- Số lịch hẹn và tỷ lệ vắng theo tháng
WITH monthly AS (
    SELECT
        substr(appointment_date, 1, 7) AS month,
        COUNT(*) AS appointments,
        100.0 * SUM(no_show) / NULLIF(SUM(CASE WHEN status != 'Đã hủy' THEN 1 ELSE 0 END), 0) AS no_show_rate_pct
    FROM appointments
    GROUP BY substr(appointment_date, 1, 7)
)
SELECT
    month,
    appointments,
    ROUND(no_show_rate_pct, 2) AS no_show_rate_pct,
    ROUND(no_show_rate_pct - LAG(no_show_rate_pct) OVER (ORDER BY month), 2) AS no_show_change_pp
FROM monthly
ORDER BY month;

-- name: department_performance
-- Hiệu quả phục vụ theo chuyên khoa
WITH wait_distribution AS (
    SELECT
        department,
        wait_minutes,
        CUME_DIST() OVER (PARTITION BY department ORDER BY wait_minutes) AS cumulative_share
    FROM appointments
    WHERE status = 'Hoàn thành'
),
wait_summary AS (
    SELECT
        department,
        COUNT(*) AS completed_visits,
        ROUND(AVG(wait_minutes), 1) AS average_wait_minutes,
        ROUND(MIN(CASE WHEN cumulative_share >= 0.50 THEN wait_minutes END), 1) AS median_wait_minutes,
        ROUND(MIN(CASE WHEN cumulative_share >= 0.90 THEN wait_minutes END), 1) AS p90_wait_minutes
    FROM wait_distribution
    GROUP BY department
),
attendance AS (
    SELECT
        department,
        ROUND(100.0 * SUM(no_show) / NULLIF(SUM(CASE WHEN status != 'Đã hủy' THEN 1 ELSE 0 END), 0), 2) AS no_show_rate_pct
    FROM appointments
    GROUP BY department
)
SELECT w.*, a.no_show_rate_pct
FROM wait_summary w
JOIN attendance a USING (department)
ORDER BY w.p90_wait_minutes DESC;

-- name: pressure_by_weekday_hour
-- Áp lực vận hành theo thứ và giờ
SELECT
    weekday_name,
    appointment_hour,
    COUNT(*) AS appointments,
    ROUND(AVG(CASE WHEN status = 'Hoàn thành' THEN wait_minutes END), 1) AS average_wait_minutes
FROM appointments
GROUP BY weekday_name, appointment_hour
HAVING COUNT(*) >= 30
ORDER BY average_wait_minutes DESC, appointments DESC;

-- name: department_hour_pressure
-- Lát cắt chuyên khoa - khung giờ có đủ lượt hoàn thành để rà soát ổn định
WITH completed AS (
    SELECT
        department,
        appointment_hour,
        wait_minutes,
        CUME_DIST() OVER (
            PARTITION BY department, appointment_hour
            ORDER BY wait_minutes
        ) AS cumulative_share
    FROM appointments
    WHERE status = 'Hoàn thành'
)
SELECT
    department,
    appointment_hour,
    COUNT(*) AS completed_visits,
    ROUND(AVG(wait_minutes), 1) AS average_wait_minutes,
    ROUND(MIN(CASE WHEN cumulative_share >= 0.90 THEN wait_minutes END), 1) AS p90_wait_minutes
FROM completed
GROUP BY department, appointment_hour
HAVING COUNT(*) >= 50
ORDER BY p90_wait_minutes DESC, completed_visits DESC;

-- name: reminder_comparison
-- So sánh mô tả theo trạng thái nhắc hẹn, không phải ước lượng nhân quả
SELECT
    reminder_sent,
    COUNT(*) AS eligible_appointments,
    ROUND(100.0 * AVG(no_show), 2) AS no_show_rate_pct
FROM appointments
WHERE status != 'Đã hủy'
GROUP BY reminder_sent;

