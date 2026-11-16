# Outpatient operations analysis

## Executive summary

This analysis uses 6,500 synthetic outpatient appointments from January 2025 through October 2026. It is a portfolio case study, not an assessment of a real hospital.

The main operational signal is waiting time, not attendance variation. Cardiology has a 35.9-minute median wait and a 50.5-minute P90, the highest of six departments. The most pressured stable slices are Cardiology at 09:00, 10:00 and 14:00, where P90 wait is between 54.1 and 56.7 minutes. Those slices should be reviewed first for arrival clustering, room availability and scheduling templates.

The overall no-show rate is 13.79%. Appointments with a recorded reminder have a 12.42% no-show rate versus 18.66% without one, a descriptive difference of 6.24 percentage points. This is not a causal estimate because reminder assignment in the synthetic process is related to booking lead time.

## Scope and method

- Grain: one row per outpatient appointment.
- Attendance denominator: completed plus no-show appointments; cancellations are excluded.
- Waiting-time population: completed visits only.
- Time statistics: median and P90 are reported to avoid hiding long waits behind an average.
- Stable slice rule: department-hour rankings require at least 50 completed visits.
- Storage: source rows are loaded to a star-schema SQLite database and exposed through a reporting view.

The pipeline validates identifiers, dates, categories, binary fields, wait-time rules and status/target consistency. It then reconciles 6,500 source rows to 6,500 fact rows and 6,500 reporting-view rows; both orphan-key checks return zero.

## Findings

### 1. Cardiology is the clearest waiting-time issue

| Department | Completed | Median wait | P90 wait | No-show rate |
|---|---:|---:|---:|---:|
| Cardiology | 885 | 35.9 min | 50.5 min | 13.74% |
| Orthopedics | 727 | 32.2 min | 45.8 min | 13.35% |
| Endocrinology | 362 | 29.4 min | 43.7 min | 14.01% |
| Internal Medicine | 1,608 | 27.7 min | 42.6 min | 13.78% |
| Ophthalmology | 559 | 22.7 min | 37.1 min | 14.00% |
| Pediatrics | 1,154 | 21.1 min | 35.8 min | 13.94% |

No-show rates are close across departments, while wait distributions differ materially. That makes a single organization-wide attendance intervention less targeted than a department-specific queue review.

### 2. Three Cardiology time slots lead the pressure ranking

| Department and hour | Completed visits | Average wait | P90 wait |
|---|---:|---:|---:|
| Cardiology 09:00 | 129 | 41.9 min | 56.7 min |
| Cardiology 10:00 | 112 | 40.4 min | 55.1 min |
| Cardiology 14:00 | 93 | 40.9 min | 54.1 min |
| Orthopedics 10:00 | 95 | 36.6 min | 52.2 min |
| Orthopedics 14:00 | 89 | 37.2 min | 52.2 min |

This ranking is more actionable than a weekday-wide average because it identifies a department and scheduling window. It still does not identify the root cause.

### 3. Reminder status is associated with attendance

| Reminder recorded | Eligible appointments | No-show rate | Wilson 95% interval |
|---|---:|---:|---:|
| No | 1,345 | 18.66% | 16.67%–20.83% |
| Yes | 4,797 | 12.42% | 11.52%–13.39% |

The intervals show a clear difference in this generated dataset, but the comparison is observational. A real decision would require adjustment for lead time and other selection factors or, preferably, a controlled rollout.

### 4. Monthly no-show variation should be monitored, not over-interpreted

Monthly no-show rate ranges from 9.66% to 18.55%. The largest single monthly increase is 6.78 percentage points. With synthetic data and roughly 250–340 appointments per month, this is a monitoring signal rather than proof of a structural change.

## Recommended next actions

1. Review Cardiology scheduling templates at 09:00, 10:00 and 14:00 before changing department-wide staffing.
2. Break the wait interval into check-in, rooming and clinician-start stages so the bottleneck can be located.
3. Audit reminder eligibility and delivery failures; do not interpret the current comparison as causal lift.
4. Add control limits and an annotation log to monthly monitoring so known operational events can be separated from noise.
5. Recalculate the metrics with real data only after agreeing definitions with registration and clinical operations staff.

## Limitations

- Every row is synthetic; results must not be used for staffing or patient-contact decisions.
- The generator intentionally encodes patterns, so discovering them does not validate performance on real data.
- Wait time has one start and end point and cannot locate the underlying process delay.
- No clinical outcomes, staffing roster or room-capacity data are included.
- Reminder assignment is not randomized.

