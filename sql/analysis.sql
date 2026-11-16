-- 1. Monthly appointment volume and no-show rate
SELECT
    substr(appointment_date, 1, 7) AS month,
    COUNT(*) AS appointments,
    ROUND(100.0 * SUM(no_show) / NULLIF(SUM(CASE WHEN status != 'Cancelled' THEN 1 ELSE 0 END), 0), 2) AS no_show_rate_pct
FROM appointments
GROUP BY month
ORDER BY month;

-- 2. Department service performance
SELECT
    department,
    COUNT(CASE WHEN status = 'Completed' THEN 1 END) AS completed_visits,
    ROUND(AVG(CASE WHEN status = 'Completed' THEN wait_minutes END), 1) AS average_wait_minutes,
    ROUND(100.0 * SUM(no_show) / NULLIF(SUM(CASE WHEN status != 'Cancelled' THEN 1 ELSE 0 END), 0), 2) AS no_show_rate_pct
FROM appointments
GROUP BY department
ORDER BY average_wait_minutes DESC;

-- 3. Operational pressure by weekday and hour
SELECT
    weekday_name,
    appointment_hour,
    COUNT(*) AS appointments,
    ROUND(AVG(CASE WHEN status = 'Completed' THEN wait_minutes END), 1) AS average_wait_minutes
FROM appointments
GROUP BY weekday_name, appointment_hour
HAVING COUNT(*) >= 30
ORDER BY average_wait_minutes DESC, appointments DESC;

-- 4. Descriptive reminder comparison (not a causal estimate)
SELECT
    reminder_sent,
    COUNT(*) AS eligible_appointments,
    ROUND(100.0 * AVG(no_show), 2) AS no_show_rate_pct
FROM appointments
WHERE status != 'Cancelled'
GROUP BY reminder_sent;

