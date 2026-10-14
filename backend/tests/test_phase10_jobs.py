"""Phase 10 — medium-complexity digital jobs are genuinely differentiated.

Guards against the five organization jobs degenerating into cosmetic copies
of the Acme workflow. Runs against the seeded PostgreSQL database (same
convention as test_phase7_assignments.py) and asserts:

- every org's investigation job is multi-step (>= 5 steps) with durations
- safety-critical verification checkpoints exist exactly where the industry
  requires them (MediCare medication check, Nexa customer verification,
  BrightGrid field-crew coordination; Acme/LogiCore desk jobs have none)
- step titles are industry-specific (no cross-org title overlap)
- decision option sets are pairwise disjoint across organizations
- every job links real dataset evidence records
"""

import psycopg
import pytest

from app.config import get_settings

ACME_WF = "e1000000-0000-0000-0000-000000000001"      # Gearbox Noise Investigation
MEDICARE_WF = "e1200000-0000-0000-0000-000000000001"  # Post-Op Vitals Review
NEXA_WF = "e1300000-0000-0000-0000-000000000001"      # Suspicious Transaction Review
LOGICORE_WF = "e1400000-0000-0000-0000-000000000001"  # Shipment Delay Investigation
BRIGHTGRID_WF = "e1500000-0000-0000-0000-000000000001"  # Feeder Voltage Investigation

INVESTIGATION_WORKFLOWS = {
    "acme": ACME_WF,
    "medicare": MEDICARE_WF,
    "nexa": NEXA_WF,
    "logicore": LOGICORE_WF,
    "brightgrid": BRIGHTGRID_WF,
}

INVESTIGATION_TASKS = {
    "acme": "51000000-0000-0000-0000-000000000001",
    "medicare": "51200000-0000-0000-0000-000000000001",
    "nexa": "51300000-0000-0000-0000-000000000001",
    "logicore": "51400000-0000-0000-0000-000000000001",
    "brightgrid": "51500000-0000-0000-0000-000000000001",
}


def _pg(sql, params=None):
    with psycopg.connect(get_settings().database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def _steps(workflow_id):
    rows = _pg(
        """
        SELECT step_order, name, description, is_safety_critical,
               expected_duration_seconds
        FROM workflow_steps
        WHERE workflow_id = %s AND status = 'active'
        ORDER BY step_order
        """,
        (workflow_id,),
    )
    return [
        {
            "order": r[0],
            "name": r[1],
            "description": r[2],
            "safety": r[3],
            "duration": r[4],
        }
        for r in rows
    ]


def test_every_job_is_multi_step_with_durations():
    """Each org's job requires multiple investigation/decision steps."""
    for org, wf_id in INVESTIGATION_WORKFLOWS.items():
        steps = _steps(wf_id)
        assert len(steps) >= 5, f"{org}: expected >= 5 steps, got {len(steps)}"
        for s in steps:
            assert s["name"] and s["name"].strip(), f"{org}: empty step name"
            assert s["description"] and len(s["description"]) > 20, (
                f"{org} step {s['order']}: description too thin"
            )
            assert s["duration"] and s["duration"] > 0, (
                f"{org} step {s['order']}: expected_duration_seconds missing"
            )


def test_safety_critical_checkpoints_match_industry_requirements():
    """Verification checkpoints exist exactly where the industry demands them."""
    medicare = _steps(MEDICARE_WF)
    nexa = _steps(NEXA_WF)
    brightgrid = _steps(BRIGHTGRID_WF)
    acme = _steps(ACME_WF)
    logicore = _steps(LOGICORE_WF)

    mc_safety = [s for s in medicare if s["safety"]]
    assert len(mc_safety) == 1 and mc_safety[0]["order"] == 2, (
        "MediCare job must have exactly one safety-critical medication check at step 2"
    )
    assert "medication" in mc_safety[0]["name"].lower()

    nx_safety = [s for s in nexa if s["safety"]]
    assert len(nx_safety) == 1 and nx_safety[0]["order"] == 2, (
        "Nexa job must have exactly one compliance-critical customer verification at step 2"
    )
    assert "verify" in nx_safety[0]["name"].lower()

    bg_safety = [s for s in brightgrid if s["safety"]]
    assert len(bg_safety) == 1 and bg_safety[0]["order"] == 3, (
        "BrightGrid job must have exactly one safety-critical field-crew coordination at step 3"
    )
    assert "crew" in bg_safety[0]["name"].lower()

    assert not any(s["safety"] for s in acme), "Acme desk investigation has no safety checkpoint"
    assert not any(s["safety"] for s in logicore), "LogiCore desk investigation has no safety checkpoint"


def test_step_titles_are_industry_specific_not_copies():
    """No step title is shared across organizations (beyond the shared engine)."""
    title_sets = {
        org: {s["name"] for s in _steps(wf_id)}
        for org, wf_id in INVESTIGATION_WORKFLOWS.items()
    }
    orgs = list(title_sets)
    for i in range(len(orgs)):
        for j in range(i + 1, len(orgs)):
            overlap = title_sets[orgs[i]] & title_sets[orgs[j]]
            assert not overlap, (
                f"cosmetic copy detected: {orgs[i]} and {orgs[j]} share step titles {overlap}"
            )


def test_decision_options_are_pairwise_disjoint():
    """Each industry's classification vocabulary is its own."""
    option_sets = {}
    for org, task_id in INVESTIGATION_TASKS.items():
        rows = _pg(
            "SELECT decision_options FROM tasks WHERE id = %s", (task_id,)
        )
        assert rows and rows[0][0], f"{org}: task has no decision options"
        option_sets[org] = set(rows[0][0])

    orgs = list(option_sets)
    for i in range(len(orgs)):
        for j in range(i + 1, len(orgs)):
            overlap = option_sets[orgs[i]] & option_sets[orgs[j]]
            assert not overlap, (
                f"decision vocabularies overlap between {orgs[i]} and {orgs[j]}: {overlap}"
            )


def test_every_job_links_real_evidence_records():
    """Each investigation task references actual dataset records."""
    for org, task_id in INVESTIGATION_TASKS.items():
        rows = _pg(
            """
            SELECT count(*) FROM task_evidence te
            JOIN dataset_records dr ON dr.id = te.record_id
            JOIN tasks t ON t.id = te.task_id
            WHERE te.task_id = %s AND t.organization_id = dr.organization_id
            """,
            (task_id,),
        )
        assert rows[0][0] >= 5, (
            f"{org}: investigation task links only {rows[0][0]} evidence records"
        )


def test_jobs_have_distinct_evidence_record_types():
    """The evidence behind each job draws on industry-specific record types."""
    for org, task_id in INVESTIGATION_TASKS.items():
        rows = _pg(
            """
            SELECT DISTINCT dr.record_type
            FROM task_evidence te
            JOIN dataset_records dr ON dr.id = te.record_id
            WHERE te.task_id = %s
            """,
            (task_id,),
        )
        types = {r[0] for r in rows}
        assert len(types) >= 4, f"{org}: evidence draws on only {len(types)} record types"
