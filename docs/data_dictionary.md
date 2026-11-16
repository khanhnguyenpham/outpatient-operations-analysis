# Data dictionary

## Source and reporting view

| Column | Type | Definition |
|---|---|---|
| `appointment_id` | string | Unique synthetic appointment identifier |
| `patient_id` | string | Hashed synthetic patient identifier; not a real person |
| `appointment_date` | date | Local calendar date of the appointment |
| `department` | category | Outpatient specialty |
| `appointment_hour` | integer | Scheduled hour, from 07 to 16 |
| `weekday_name` | category | English weekday name derived from appointment date |
| `lead_days` | integer | Days between booking and appointment |
| `prior_no_shows` | integer | Synthetic count known before the appointment |
| `reminder_sent` | binary | 1 when a reminder was recorded, otherwise 0 |
| `outside_city` | binary | 1 for the synthetic outside-city group |
| `status` | category | `Completed`, `No-show`, or `Cancelled` |
| `no_show` | binary | 1 only when status is `No-show` |
| `wait_minutes` | decimal/null | Arrival-to-service interval for completed visits only |

## Warehouse tables

- `fact_appointment`: one row per appointment; stores measures, status and dimension keys.
- `dim_date`: calendar fields for every appointment date.
- `dim_department`: stable integer key and department name.
- `appointments`: analyst-facing view joining the fact table to both dimensions.

The model excludes patient names, phone numbers, addresses and clinical diagnoses because none are needed for the operational questions.

