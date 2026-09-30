# AMAP Demo Scenarios (Phase 17)

All three demos run against the live stack (backend `:8000`, frontend `:3000`)
with the seeded PostgreSQL database. All passwords are deterministic
development-only credentials (`SecurePassword123!` unless noted), stored only
as bcrypt hashes. User-facing timestamps render in IST (UTC+05:30); storage is
timezone-aware UTC.

Full credential matrix: `database/seed/README.md`.

---

## Demo 1 — Acme Motors worker journey (manufacturing root-cause investigation)

| Item | Value |
|---|---|
| Organization | Acme Motors — Assembly Plant 1 (`9a61e05d-7a32-4112-9c17-1833d7b42f65`) |
| Worker | `alex.worker@amap.com` / `SecurePassword123!` (certified, ready) |
| Workflow | Gearbox Noise Investigation Workflow (`e1000000-…-0001`), 5 steps |
| Task | Gearbox Noise Investigation — Batch BR-2026-0917 (`51000000-…-0001`) |
| Dataset | Assembly Plant 1 Production File (`ba100000-…-0001`) — 13 records: production, inspection, maintenance, supply_chain, incident |
| Decision | Classify root cause: machining_tolerance_deviation / bearing_lot_defect / lubrication_underfill / assembly_torque_error / no_fault_found |

**Journey** (verified live, real browser):
login → routed to `/worker` → assignment auto-starts (`assigned → in_progress`)
→ 5-step investigation (batch comparison → quality gates → maintenance →
incidents → classification) with per-step durations → open the evidence panel
("Show Records", voice: *"show evidence"*) and inspect the 10 linked production
records with record-type filter chips → select classification → **End Work** →
completion dialog with server-computed duration.

**Result:** `worker_task_assignments` row with `assigned_at` / `started_at` /
`completed_at` (UTC), 5 `workflow_step_executions` rows, and a
`task_results` row with `result_data.classification` — all visible in the
supervisor monitor and admin dashboard (completion rate, recent activity, IST).

---

## Demo 2 — MediCare Health Systems worker journey (genuinely different, clinical)

| Item | Value |
|---|---|
| Organization | MediCare Health Systems (`aa100000-…-0002`) |
| Worker | `worker1@medicare-health.com` / `SecurePassword123!` (certified, ready) |
| Workflow | Post-Op Vitals Review Workflow (`e1200000-…-0001`), 5 steps, **different structure from Acme** |
| Task | Post-Op Vitals Anomaly Review — Bed 7 (`51200000-…-0001`) |
| Dataset | Ward 4 Post-Operative Monitoring File (`ba200000-…-0001`) — patient_vitals, medication_administration, lab_result, nursing_note, shift_handover |
| Safety checkpoint | Step 2 **Verify Medication Record** is `is_safety_critical` — the worker UI renders a prominent `⚠️ SAFETY CRITICAL — Verify Before Proceeding` badge (cross-check MAR against pharmacy reconciliation before interpreting the trend) |
| Decision | Classify clinical response: surgical_site_infection_escalation / adverse_medication_reaction / monitoring_device_artifact / pain_induced_response / stable_monitor_only |

**Journey** (verified live, real browser): login (organization selector →
MediCare) → `/worker` → clinical triage workflow: vitals triage →
**safety-critical medication verification (badge shown)** → lab panel
interpretation → notes/handover cross-check → escalation decision — with the
MediCare evidence records (vitals/meds/labs/notes/handover), zero Acme content
visible (org isolation enforced server-side, 403 on cross-org reads).

---

## Demo 3 — Admin-created scenario (CRUD path, seeded parity)

| Item | Value |
|---|---|
| Organization | Acme Motors — Assembly Plant 1 |
| Admin | `admin@amap.com` / `SecurePassword123!` |
| Supervisor | `supervisor@amap.com` / `SecurePassword123!` |
| Created worker | e.g. `parity.worker@amap.com` / `ParityPass123!` (admin-invited, temp password, hashed at rest) |
| Workflow/Task | Same seeded Gearbox investigation (the CRUD path accepts any org task/workflow) |

**Journey** (verified live — `scripts/e2e_seeded_crud_parity.py`, ALL PASS):
admin invites a worker (`POST /organizations/manage/workers/invite`) → worker
logs in through the same auth path → readiness certify
(`POST /workers/{id}/readiness/certify`) → supervisor assigns the task
(`POST /supervisor/tasks/assign`, eligibility enforced) → worker starts,
executes all 5 steps, classifies, completes → PostgreSQL rows are identical in
shape to the seeded example (timestamps, result with classification, 5
executions). Artifacts are cleaned up afterwards, proving the seeded demo
state is never dependent on CRUD-created rows (and vice versa).

---

## Verification artifacts

- `scripts/e2e_browser_journey.py`-style API journey: `scripts/e2e_worker_journey.py`
- Real-browser suite (27 checks, ALL PASS): `scripts/e2e_browser_journey.js`
- Seeded==CRUD parity check: `scripts/e2e_seeded_crud_parity.py`
- Backend regression: 802/802 passed; frontend typecheck + lint + production build green.
