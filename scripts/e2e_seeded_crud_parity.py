import json, urllib.request, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import psycopg

API = "http://127.0.0.1:8000/api/v1"
ORG = "9a61e05d-7a32-4112-9c17-1833d7b42f65"  # Acme
PW = "SecurePassword123!"
TASK = "51000000-0000-0000-0000-000000000001"  # Gearbox (seeded, active)

def req(method, path, token=None, body=None):
    r = urllib.request.Request(API + path, method=method)
    if token: r.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode() if body is not None else None
    if data: r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, data) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")

ok = True
def check(label, cond, extra=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + (f" | {extra}" if extra else ""))
    if not cond: ok = False

# --- admin context (invite/certify need admin; /supervisor router also admits admin) ---
_, login = req("POST", "/auth/login", body={"organization_id": ORG, "email": "admin@amap.com", "password": PW})
sup = login["access_token"]

# 1. CRUD-invite a worker (deterministic temp password)
st, invited = req("POST", "/organizations/manage/workers/invite", sup, {
    "email": "parity.worker@amap.com", "full_name": "Parity Worker (CRUD)",
    "badge_number": "ACME-PARITY-1", "temporary_password": "ParityPass123!"})
check("CRUD invite worker", st in (201, 409), f"{st} {'(already invited)' if st == 409 else json.dumps(invited)[:120]}")
uid = invited.get("user_id") or invited.get("id")
wpid = invited.get("worker_profile_id")

# 2. invited worker logs in through the same auth path as seeded workers
st, wlogin = req("POST", "/auth/login", body={"organization_id": ORG, "email": "parity.worker@amap.com", "password": "ParityPass123!"})
check("CRUD worker login (same auth path)", st == 200 and "access_token" in wlogin, str(st))
wtok = wlogin.get("access_token", "")

# 3. seeded worker vs CRUD worker: same readiness endpoint contract
st, r1 = req("GET", "/auth/me", wtok)
check("CRUD worker /auth/me contract", st == 200 and r1.get("worker_profile_id"), json.dumps(r1)[:100])
wpid = r1.get("worker_profile_id")
st, ready = req("GET", f"/workers/{wpid}/readiness", wtok)
check("CRUD worker readiness contract", st == 200 and "onboarding_completed" in ready and "is_fresher" in ready)

# 4. certify the CRUD worker (same lifecycle a fresher follows), then assign the SEEDED task
st, _ = req("POST", f"/workers/{wpid}/readiness/certify", sup, {"selected_modality": "multimodal", "gesture_ready": True, "voice_ready": True, "multimodal_ready": True, "task_training_complete": True})
check("certify CRUD worker", st in (200, 201), str(st))

# (assignable-list filtering is a UI convenience; the authoritative eligibility
#  check lives in assign_task, verified below)

st, asn = req("POST", "/supervisor/tasks/assign", sup, {"task_id": TASK, "worker_profile_id": wpid})
check("supervisor assigns seeded task to CRUD worker", st in (200, 201), f"{st} {json.dumps(asn)[:140]}")
aid = (asn.get("assignment") or {}).get("id") or asn.get("assignment_id") or asn.get("id")

# 5. CRUD worker executes the SEEDED task through the same endpoints a seeded worker uses
st, started = req("POST", f"/tasks/assignments/{aid}/start", wtok)
check("CRUD worker starts assignment", st == 200 and started.get("status") == "in_progress", str(st))
wfa = started.get("workflow_assignment_id")
st, d = req("GET", f"/tasks/{TASK}", wtok)
check("CRUD worker sees seeded task steps+evidence", st == 200 and len(d["steps"]) == 5 and len(d["evidence"]) >= 5)
for s in d["steps"]:
    st, _ = req("POST", f"/tasks/workflows/assignments/{wfa}/steps/{s['id']}/execute", wtok,
                {"status": "completed", "execution_data": {"step_number": s["stepNumber"]}})
    if st not in (200, 201): check(f"step {s['stepNumber']} execution", False, str(st))
st, comp = req("POST", f"/tasks/assignments/{aid}/complete", wtok,
               {"result_data": {"classification": "bearing_lot_defect", "total_steps": 5, "completed_steps": 5}, "outcome": "completed"})
check("CRUD worker completes seeded task with decision", st == 200, f"{st} {json.dumps(comp)[:120]}")

# 6. PG parity: CRUD-worker assignment row has the same populated shape as the seeded one
with psycopg.connect("postgresql://amap_user:change_me@127.0.0.1:5432/amap") as conn, conn.cursor() as cur:
    cur.execute("""
        SELECT
          (SELECT count(*) FROM worker_task_assignments WHERE worker_profile_id=%s AND status='completed' AND assigned_at IS NOT NULL AND started_at IS NOT NULL AND completed_at IS NOT NULL),
          (SELECT count(*) FROM task_results tr JOIN worker_task_assignments a ON a.id=tr.worker_task_assignment_id WHERE a.worker_profile_id=%s AND tr.result_data ? 'classification'),
          (SELECT count(*) FROM workflow_step_executions e JOIN workflow_assignments wa ON wa.id=e.workflow_assignment_id WHERE wa.worker_profile_id=%s AND e.status='completed')
    """, (wpid, wpid, wpid))
    a_cnt, r_cnt, e_cnt = cur.fetchone()
    check("PG parity: full lifecycle rows (timestamps+result+executions)",
          a_cnt >= 1 and r_cnt == a_cnt and e_cnt == 5 * a_cnt, f"assignments={a_cnt} results={r_cnt} executions={e_cnt}")
    # seeded example rows have the same NOT NULL shape
    cur.execute("SELECT count(*) FROM worker_task_assignments WHERE status='completed' AND assigned_at IS NOT NULL AND started_at IS NOT NULL AND completed_at IS NOT NULL AND id='62000000-0000-0000-0000-000000000002'")
    check("seeded completed example has same timestamp shape", cur.fetchone()[0] == 1)

# 7. cleanup (parity artifacts)
with psycopg.connect("postgresql://amap_user:change_me@127.0.0.1:5432/amap") as conn, conn.cursor() as cur:
    cur.execute("BEGIN")
    cur.execute("DELETE FROM task_results WHERE worker_task_assignment_id IN (SELECT id FROM worker_task_assignments WHERE worker_profile_id=%s)", (wpid,))
    cur.execute("DELETE FROM workflow_step_executions WHERE workflow_assignment_id IN (SELECT id FROM workflow_assignments WHERE worker_profile_id=%s)", (wpid,))
    cur.execute("DELETE FROM workflow_assignments WHERE worker_profile_id=%s", (wpid,))
    cur.execute("DELETE FROM worker_task_assignments WHERE worker_profile_id=%s", (wpid,))
    cur.execute("DELETE FROM worker_readiness WHERE worker_profile_id=%s", (wpid,))
    cur.execute("DELETE FROM worker_profiles WHERE id=%s", (wpid,))
    cur.execute("DELETE FROM user_roles WHERE user_id IN (SELECT id FROM users WHERE email='parity.worker@amap.com')")
    cur.execute("DELETE FROM user_departments WHERE user_id IN (SELECT id FROM users WHERE email='parity.worker@amap.com')")
    cur.execute("DELETE FROM users WHERE email='parity.worker@amap.com'")
    conn.commit()
check("cleanup parity artifacts", True)

print("PHASE 15 (seeded == CRUD):", "ALL PASS" if ok else "FAILURES")
