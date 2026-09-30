# AMAP Seed Data & Demo Credentials

This document describes the seeded sample data and the demo accounts for the
five sample organizations. **All seeded data and accounts are synthetic
sample/demo data — this is NOT real company, patient, financial, shipment, or
grid data.**

Seeding is idempotent: every statement uses deterministic IDs with
`ON CONFLICT DO NOTHING`, so running the seed repeatedly never creates
duplicates.

```bash
# apply migrations (includes 053_org_datasets_and_task_evidence.sql)
python scripts/migrate.py

# seed (safe to run any number of times)
python scripts/seed.py
```

## Demo accounts

All demo accounts use the same deterministic development/demo password:
`SecurePassword123!`. Passwords are stored only as salted PBKDF2-SHA256
hashes (the project's existing authentication mechanism) — never in
plaintext. These are demo credentials for the capstone environment; do not
reuse them anywhere real.

Log in at the login page with the organization, email, and password below.

| Organization | Role | Email | Password |
|---|---|---|---|
| Acme Motors — Assembly Plant 1 | Admin | `admin@amap.com` | `SecurePassword123!` |
| Acme Motors — Assembly Plant 1 | Supervisor | `supervisor@amap.com` | `SecurePassword123!` |
| Acme Motors — Assembly Plant 1 | Worker (Alex Morgan) | `alex.worker@amap.com` | `SecurePassword123!` |
| MediCare Health Systems | Admin | `admin@medicare-health.com` | `SecurePassword123!` |
| MediCare Health Systems | Supervisor | `supervisor1@medicare-health.com` | `SecurePassword123!` |
| MediCare Health Systems | Worker | `worker1@medicare-health.com` | `SecurePassword123!` |
| Nexa Finance | Admin | `admin@nexafinance.com` | `SecurePassword123!` |
| Nexa Finance | Supervisor | `supervisor1@nexafinance.com` | `SecurePassword123!` |
| Nexa Finance | Worker | `worker1@nexafinance.com` | `SecurePassword123!` |
| LogiCore Logistics | Admin | `admin@logicore-logistics.com` | `SecurePassword123!` |
| LogiCore Logistics | Supervisor | `supervisor1@logicore-logistics.com` | `SecurePassword123!` |
| LogiCore Logistics | Worker | `worker1@logicore-logistics.com` | `SecurePassword123!` |
| BrightGrid Energy | Admin | `admin@brightgrid-energy.com` | `SecurePassword123!` |
| BrightGrid Energy | Supervisor | `supervisor1@brightgrid-energy.com` | `SecurePassword123!` |
| BrightGrid Energy | Worker | `worker1@brightgrid-energy.com` | `SecurePassword123!` |

Each organization also has a second supervisor (`supervisor2@…`) and two
more workers (`worker2@…`, `worker3@…`) with the same password.

## Seeded sample datasets (synthetic)

Each organization owns one organization-scoped dataset in the `datasets`
table, with typed, interconnected records in `dataset_records` (foreign keys
to the dataset, the organization, and — where meaningful — a related record):

| Organization | Dataset | Records | Record types |
|---|---|---|---|
| Acme Motors | Powertrain Quality Tracer — Line 3 | 13 | production, inspection, maintenance, supply_chain, incident |
| MediCare Health Systems | Ward 4 Post-Operative Monitoring File | 5 | patient_vitals, medication_administration, lab_result, nursing_note, shift_handover |
| Nexa Finance | Card Dispute & Fraud Alert File — NXC-4471 | 5 | transaction, fraud_alert, customer_profile, merchant_note |
| LogiCore Logistics | Route 7 Exception File — Rotterdam Hub | 5 | shipment, scan_event, delay_incident, driver_report |
| BrightGrid Energy | Substation F-12 Feeder Monitoring File | 5 | sensor_reading, outage_ticket, maintenance_log, scada_alarm |

## Seeded worker tasks (linked to the datasets above)

Every investigation task is a real `tasks` row with a workflow, workflow
steps, a `worker_task_assignments` row, and `task_evidence` links to the
dataset records the worker must investigate. Investigation tasks carry
`decision_prompt` / `decision_options`; the worker's classification is
validated server-side and persisted in `task_results.result_data`.

| Task | Organization | Assigned worker | Status |
|---|---|---|---|
| Gearbox Noise Investigation — Batch BR-2026-0917 | Acme Motors | alex.worker@amap.com | in_progress |
| Paint Adhesion Investigation — Batch PA-2026-0830 | Acme Motors | alex.worker@amap.com | completed (result persisted) |
| Post-Op Vitals Anomaly Review — Bed 7 | MediCare | worker1@medicare-health.com | assigned |
| Suspicious Transaction Review — NXC-4471 | Nexa Finance | worker1@nexafinance.com | assigned |
| Shipment Delay Root Cause — RTM-77412 | LogiCore | worker1@logicore-logistics.com | assigned |
| Feeder Voltage Anomaly Investigation — F-12 | BrightGrid | worker1@brightgrid-energy.com | assigned |

The Acme "Paint Adhesion Investigation" is a fully worked example: workflow
step executions, a completed assignment, and a persisted `task_results` row
(classification `pretreatment_contamination`, duration computed from the
stored timestamps).

## Timezone convention

Task/assignment/result timestamps are stored as timezone-aware UTC
(`TIMESTAMPTZ`) and returned as ISO-8601 UTC by the API. All user-facing
rendering displays IST (UTC+05:30), e.g. `29 Sep 2026, 11:42:18 AM IST`
(see `frontend/shared/utils/istTime.ts`).
