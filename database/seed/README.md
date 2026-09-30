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

### Primary accounts

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

### Scaled workforce (Phase 6)

Every organization is seeded with **6 supervisors, 16 workers, and 1
admin** (115 users total). The scaled accounts follow deterministic email
patterns — all use the same password `SecurePassword123!`:

| Organization | Supervisors | Workers |
|---|---|---|
| Acme Motors | `supervisor@amap.com`, `supervisor2@amap.com` … `supervisor6@amap.com` | `alex.worker@amap.com`, `jordan.worker@amap.com`, `maria.newhire@amap.com`, `worker4@amap.com` … `worker16@amap.com` |
| MediCare | `supervisor1@medicare-health.com` … `supervisor6@medicare-health.com` | `worker1@medicare-health.com` … `worker16@medicare-health.com` |
| Nexa Finance | `supervisor1@nexafinance.com` … `supervisor6@nexafinance.com` | `worker1@nexafinance.com` … `worker16@nexafinance.com` |
| LogiCore Logistics | `supervisor1@logicore-logistics.com` … `supervisor6@logicore-logistics.com` | `worker1@logicore-logistics.com` … `worker16@logicore-logistics.com` |
| BrightGrid Energy | `supervisor1@brightgrid-energy.com` … `supervisor6@brightgrid-energy.com` | `worker1@brightgrid-energy.com` … `worker16@brightgrid-energy.com` |

**Suspended demo accounts** (for demonstrating inactive-account behavior):
`supervisor6@…` and `worker16@…` in every organization are seeded with
status `suspended` — their login is blocked (401) until an admin
reactivates them through the worker/supervisor management panel or
`PUT /organizations/manage/workers/{id}`.

Seeded users are byte-for-byte equivalent to users created through the
CRUD invitation APIs (same tables, same PBKDF2 hashing format, same role
and readiness defaults) — verified field-by-field against an API-invited
user.

## Seeded sample datasets (synthetic)

Each organization owns one organization-scoped dataset in the `datasets`
table, with typed, interconnected records in `dataset_records` (foreign keys
to the dataset, the organization, and — where meaningful — a related record):

| Organization | Dataset | Records | Record types |
|---|---|---|---|
| Acme Motors | Powertrain Quality Tracer — Line 3 | 13 | production, inspection, maintenance, supply_chain, incident |
| MediCare Health Systems | Ward 4 Post-Operative Monitoring File | 8 | patient_vitals, medication_administration, lab_result, nursing_note, shift_handover, appointment, clinical_review, medication_reconciliation |
| Nexa Finance | Card Dispute & Fraud Alert File — NXC-4471 | 8 | transaction, fraud_alert, customer_profile, merchant_note, account, risk_review, customer_contact_log |
| LogiCore Logistics | Route 7 Exception File — Rotterdam Hub | 8 | shipment, scan_event, delay_incident, driver_report, customer_order, inventory_snapshot, carrier_schedule |
| BrightGrid Energy | Substation F-12 Feeder Monitoring File | 8 | sensor_reading, outage_ticket, maintenance_log, scada_alarm, service_ticket, infrastructure_asset, field_crew_dispatch |

Datasets are organization-owned and server-side scoped: admins can browse
their organization's datasets and records through
`GET /api/v1/organizations/manage/datasets` and
`GET /api/v1/organizations/manage/datasets/{id}/records` (Admin Studio →
Datasets tab). Cross-organization dataset access returns 404; workers and
supervisors do not have access to the management endpoints (workers see
their task's evidence through the task APIs).

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
