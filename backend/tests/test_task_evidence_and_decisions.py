"""
Data-backed worker task tests (time-critical data + task integration scope).

Focused coverage for:
- task details exposing linked evidence records + decision metadata
- evidence fetched organization-scoped (tenancy defense-in-depth)
- decision/classification enforcement on task completion (server-side)
- assignment timestamps (assigned/started/completed) exposed to workers
- route-level evidence exposure on GET /api/v1/tasks/{task_id}

Live PostgreSQL persistence (seed idempotency, real logins, seeded
evidence retrieval, result persistence) is verified against the running
stack in the integration verification for this scope.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import status
from starlette.testclient import TestClient

from app.dependencies import get_current_user
from app.main import app
from models.auth import AuthenticatedUserContext
from routes.tasks import get_task_service
from services.base import NotFoundError, UnauthorizedError, ValidationError
from services.task_service import TaskService

ORG_A_ID = UUID("9a61e05d-7a32-4112-9c17-1833d7b42f65")
ORG_B_ID = UUID("8b52d14c-6b21-4001-8b06-0722c6a31e54")
ADMIN_A_ID = UUID("c0000000-0000-0000-0000-000000000001")
WORKER_PROFILE_ID = UUID("d0000000-0000-0000-0000-000000000001")

NOW = datetime.now(timezone.utc)
client = TestClient(app)


# =============================================================================
# Fixtures / helpers
# =============================================================================

def _task_row(task_id, org_id, decision_prompt=None, decision_options=None):
    return {
        "id": task_id,
        "organization_id": org_id,
        "name": "Gearbox Noise Investigation — Batch BR-2026-0917",
        "description": "Investigate and classify.",
        "status": "active",
        "decision_prompt": decision_prompt,
        "decision_options": decision_options,
        "created_at": NOW,
        "updated_at": NOW,
    }


def _evidence_row(record_id, org_id, record_type="production"):
    return {
        "id": record_id,
        "dataset_id": uuid4(),
        "organization_id": org_id,
        "record_type": record_type,
        "title": f"Sample {record_type} record",
        "source_ref": "BR-2026-0917",
        "payload": {"result": "fail", "measured_avg_db": 84.4},
        "occurred_at": NOW,
        "related_record_id": None,
        "dataset_name": "Powertrain Quality Tracer — Line 3",
        "relevance": "Batch under investigation.",
    }


def _service(**overrides) -> TaskService:
    """TaskService with fully mocked repositories (no database access)."""
    deps: Dict[str, MagicMock] = {name: MagicMock() for name in (
        "tasks_repo", "task_assignments_repo", "task_results_repo",
        "task_workflows_repo", "workflows_repo", "workflow_steps_repo",
        "workflow_assignments_repo", "step_executions_repo",
        "task_evidence_repo",
    )}
    service = TaskService(**deps)
    service._mocks = deps  # type: ignore[attr-defined]
    for name, value in overrides.items():
        setattr(service, name, value)
    return service


def _assignment_row(assignment_id, task_id, status_="in_progress"):
    return {
        "id": assignment_id,
        "task_id": task_id,
        "worker_profile_id": WORKER_PROFILE_ID,
        "status": status_,
        "assigned_at": NOW,
        "started_at": NOW if status_ != "assigned" else None,
        "completed_at": NOW if status_ == "completed" else None,
        "created_at": NOW,
        "updated_at": NOW,
    }


# =============================================================================
# Task details: evidence + decision metadata
# =============================================================================

def test_task_details_includes_evidence_and_decision_metadata():
    task_id = uuid4()
    rec_id = uuid4()
    service = _service()
    service.tasks_repo.get_by_id.return_value = _task_row(
        task_id, ORG_A_ID,
        decision_prompt="Classify the root cause.",
        decision_options=["bearing_lot_defect", "no_fault_found"],
    )
    service.task_evidence_repo.list_by_task_id.return_value = [
        _evidence_row(rec_id, ORG_A_ID, "inspection")
    ]
    service.task_workflows_repo.list_by_task_id.return_value = []

    details = service.get_task_details(task_id, organization_id=ORG_A_ID)

    assert details["decision_prompt"] == "Classify the root cause."
    assert details["decision_options"] == ["bearing_lot_defect", "no_fault_found"]
    assert details["evidence_count"] == 1
    evidence = details["evidence"][0]
    assert evidence["id"] == str(rec_id)
    assert evidence["record_type"] == "inspection"
    assert evidence["dataset_name"] == "Powertrain Quality Tracer — Line 3"
    assert evidence["payload"]["result"] == "fail"
    assert evidence["relevance"] == "Batch under investigation."


def test_task_details_evidence_is_organization_scoped():
    """Evidence must be fetched with the task's organization id (tenant scoping)."""
    task_id = uuid4()
    service = _service()
    service.tasks_repo.get_by_id.return_value = _task_row(task_id, ORG_A_ID)
    service.task_evidence_repo.list_by_task_id.return_value = []
    service.task_workflows_repo.list_by_task_id.return_value = []

    service.get_task_details(task_id, organization_id=ORG_A_ID)

    service.task_evidence_repo.list_by_task_id.assert_called_once_with(
        task_id, organization_id=ORG_A_ID
    )


def test_task_details_tenancy_still_enforced_before_evidence():
    """Cross-organization access must fail before any evidence is fetched."""
    task_id = uuid4()
    service = _service()
    service.tasks_repo.get_by_id.return_value = _task_row(task_id, ORG_B_ID)

    with pytest.raises(UnauthorizedError):
        service.get_task_details(task_id, organization_id=ORG_A_ID)
    service.task_evidence_repo.list_by_task_id.assert_not_called()


def test_task_details_plain_task_has_empty_evidence_and_options():
    """Assembly tasks without decision metadata keep working unchanged."""
    task_id = uuid4()
    service = _service()
    service.tasks_repo.get_by_id.return_value = _task_row(task_id, ORG_A_ID)
    service.task_evidence_repo.list_by_task_id.return_value = []
    service.task_workflows_repo.list_by_task_id.return_value = []

    details = service.get_task_details(task_id, organization_id=ORG_A_ID)

    assert details["evidence"] == []
    assert details["evidence_count"] == 0
    assert details["decision_options"] == []
    assert details["decision_prompt"] is None


# =============================================================================
# Decision enforcement on completion (server-side)
# =============================================================================

def _completion_service(task_row):
    service = _service()
    service.tasks_repo.get_by_id.return_value = task_row
    service.task_workflows_repo.list_by_task_id.return_value = []
    return service


def test_completion_requires_classification_for_decision_tasks():
    assignment_id, task_id = uuid4(), uuid4()
    service = _completion_service(_task_row(
        task_id, ORG_A_ID, decision_prompt="Classify.", decision_options=["a", "b"]
    ))
    service.task_assignments_repo.get_by_id.return_value = _assignment_row(assignment_id, task_id)

    with pytest.raises(ValidationError) as exc:
        service.complete_task_assignment(assignment_id, worker_profile_id=WORKER_PROFILE_ID)
    assert "classification" in str(exc.value).lower()
    service.task_results_repo.create.assert_not_called()


def test_completion_rejects_invalid_classification():
    assignment_id, task_id = uuid4(), uuid4()
    service = _completion_service(_task_row(
        task_id, ORG_A_ID, decision_prompt="Classify.", decision_options=["a", "b"]
    ))
    service.task_assignments_repo.get_by_id.return_value = _assignment_row(assignment_id, task_id)

    with pytest.raises(ValidationError) as exc:
        service.complete_task_assignment(
            assignment_id, worker_profile_id=WORKER_PROFILE_ID,
            result_data={"classification": "totally_made_up"},
        )
    assert "invalid classification" in str(exc.value).lower()
    service.task_results_repo.create.assert_not_called()


def test_completion_persists_valid_classification_in_result_data():
    assignment_id, task_id = uuid4(), uuid4()
    service = _completion_service(_task_row(
        task_id, ORG_A_ID, decision_prompt="Classify.", decision_options=["a", "b"]
    ))
    service.task_assignments_repo.get_by_id.return_value = _assignment_row(assignment_id, task_id)
    service.task_results_repo.get_by_worker_task_assignment_id.return_value = None
    service.task_results_repo.create.return_value = {
        "id": uuid4(), "worker_task_assignment_id": assignment_id,
        "outcome": "completed", "result_data": {}, "notes": None,
        "recorded_at": NOW, "created_at": NOW, "updated_at": NOW,
    }

    service.complete_task_assignment(
        assignment_id, worker_profile_id=WORKER_PROFILE_ID,
        outcome="completed", result_data={"classification": "b"},
        notes="Evidence reviewed.",
    )

    create_kwargs = service.task_results_repo.create.call_args.kwargs
    assert create_kwargs["result_data"]["classification"] == "b"
    assert create_kwargs["outcome"] == "completed"
    # Server-computed stats are still merged in.
    assert create_kwargs["result_data"]["outcome"] == "completed"


def test_completion_without_decision_options_needs_no_classification():
    """Plain assembly tasks complete exactly as before (no classification)."""
    assignment_id, task_id = uuid4(), uuid4()
    service = _completion_service(_task_row(task_id, ORG_A_ID))
    service.task_assignments_repo.get_by_id.return_value = _assignment_row(assignment_id, task_id)
    service.task_results_repo.get_by_worker_task_assignment_id.return_value = None
    service.task_results_repo.create.return_value = {
        "id": uuid4(), "worker_task_assignment_id": assignment_id,
        "outcome": "completed", "result_data": {}, "notes": None,
        "recorded_at": NOW, "created_at": NOW, "updated_at": NOW,
    }

    result = service.complete_task_assignment(
        assignment_id, worker_profile_id=WORKER_PROFILE_ID, outcome="completed",
    )
    assert result is not None
    service.task_results_repo.create.assert_called_once()


# =============================================================================
# Assignment timestamps exposed to the worker
# =============================================================================

def test_worker_assignments_expose_timestamps():
    service = _service()
    assignment_id, task_id = uuid4(), uuid4()
    row = _assignment_row(assignment_id, task_id, status_="in_progress")
    service.task_assignments_repo.list_by_worker_profile_id.return_value = [row]
    service.workflow_assignments_repo.list_by_worker_profile_id.return_value = []
    service.task_workflows_repo.list_by_task_id.return_value = []

    assignments: List[Any] = service.get_worker_assignments(WORKER_PROFILE_ID)

    assert len(assignments) == 1
    assert assignments[0].assigned_at == row["assigned_at"]
    assert assignments[0].started_at == row["started_at"]
    assert assignments[0].completed_at is None


# =============================================================================
# Route-level exposure (GET /api/v1/tasks/{task_id})
# =============================================================================

def test_task_details_route_returns_evidence():
    task_id = uuid4()
    mock_service = MagicMock()
    mock_service.get_task_details.return_value = {
        "id": str(task_id),
        "organization_id": str(ORG_A_ID),
        "name": "Gearbox Noise Investigation",
        "description": "Investigate.",
        "status": "active",
        "workflow_id": None,
        "total_steps": 0,
        "steps": [],
        "evidence": [{
            "id": str(uuid4()),
            "dataset_name": "Powertrain Quality Tracer — Line 3",
            "record_type": "inspection",
            "title": "Final Noise & Vibration Gate — BR-2026-0917",
            "source_ref": "INSP-NV-0917",
            "payload": {"result": "fail"},
            "occurred_at": NOW.isoformat(),
            "related_record_id": None,
            "relevance": "Failed noise gate that triggered the investigation.",
        }],
        "evidence_count": 1,
        "decision_prompt": "Classify the root cause.",
        "decision_options": ["bearing_lot_defect", "no_fault_found"],
    }
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUserContext(
        user_id=ADMIN_A_ID,
        organization_id=ORG_A_ID,
        email="admin@amap.com",
        full_name="Sarah Jenkins",
        status="active",
        roles=["admin", "organization_admin"],
        is_active=True,
    )
    app.dependency_overrides[get_task_service] = lambda: mock_service
    try:
        res = client.get(f"/api/v1/tasks/{task_id}")
        assert res.status_code == status.HTTP_200_OK, res.text
        body = res.json()
        assert body["evidence_count"] == 1
        assert body["evidence"][0]["record_type"] == "inspection"
        assert body["evidence"][0]["source_ref"] == "INSP-NV-0917"
        assert body["decision_options"] == ["bearing_lot_defect", "no_fault_found"]
        mock_service.get_task_details.assert_called_once_with(
            task_id=task_id, organization_id=ORG_A_ID
        )
    finally:
        app.dependency_overrides.clear()


def test_task_details_route_cross_org_403():
    task_id = uuid4()
    mock_service = MagicMock()
    mock_service.get_task_details.side_effect = UnauthorizedError(
        "Task does not belong to user's organization."
    )
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUserContext(
        user_id=ADMIN_A_ID,
        organization_id=ORG_A_ID,
        email="admin@amap.com",
        full_name="Sarah Jenkins",
        status="active",
        roles=["admin", "organization_admin"],
        is_active=True,
    )
    app.dependency_overrides[get_task_service] = lambda: mock_service
    try:
        res = client.get(f"/api/v1/tasks/{task_id}")
        assert res.status_code == status.HTTP_403_FORBIDDEN
    finally:
        app.dependency_overrides.clear()
