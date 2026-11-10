"""
HTTP contract tests for the work-session routes (routes/sessions.py).

The happy-path lifecycle (start/active/pause/resume/end) is covered in
test_api_routes.py. This file closes the remaining gaps: the heartbeat
endpoint (all three of its branches) and every service-exception ->
HTTP-status mapping (404/403/409/400) on the lifecycle endpoints.

All tests mock WorkSessionService via FastAPI dependency overrides —
no database, no network, pure HTTP-contract verification.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock
import uuid

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_current_active_worker, get_current_user
from app.main import app
from models.auth import AuthenticatedUserContext
from models.session import WorkSessionRead
from routes.sessions import get_work_session_service
from services.base import ConflictError, NotFoundError, UnauthorizedError, ValidationError


@pytest.fixture
def mock_worker_context():
    return AuthenticatedUserContext(
        user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        email="worker@amap.org",
        full_name="AMAP Worker",
        status="active",
        roles=["worker"],
        permissions=["session:read", "session:write"],
        worker_profile_id=uuid.uuid4(),
    )


@pytest.fixture
def client(mock_worker_context):
    app.dependency_overrides[get_current_user] = lambda: mock_worker_context
    app.dependency_overrides[get_current_active_worker] = lambda: mock_worker_context
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_service():
    service = MagicMock()
    app.dependency_overrides[get_work_session_service] = lambda: service
    return service


def _session_read(session_id, worker_profile_id, status="active"):
    now = datetime.now(timezone.utc)
    return WorkSessionRead(
        id=session_id,
        worker_profile_id=worker_profile_id,
        status=status,
        started_at=now,
        ended_at=None,
        created_at=now,
        updated_at=now,
    )


# ======================================================================
# Heartbeat endpoint (POST /sessions/heartbeat)
# ======================================================================

def test_heartbeat_with_explicit_session_id(client, mock_service, mock_worker_context):
    session_id = uuid.uuid4()
    mock_service.heartbeat.return_value = _session_read(session_id, mock_worker_context.worker_profile_id)

    resp = client.post("/api/v1/sessions/heartbeat", json={"work_session_id": str(session_id)})

    assert resp.status_code == 200
    assert resp.json()["id"] == str(session_id)
    mock_service.heartbeat.assert_called_once_with(
        work_session_id=session_id,
        worker_profile_id=mock_worker_context.worker_profile_id,
    )
    # Explicit id must not trigger an active-session lookup.
    mock_service.get_active_session.assert_not_called()


def test_heartbeat_implicit_resolves_active_session(client, mock_service, mock_worker_context):
    """Without a payload id, the worker's active session id is used."""
    active_id = uuid.uuid4()
    mock_service.get_active_session.return_value = _session_read(active_id, mock_worker_context.worker_profile_id)
    mock_service.heartbeat.return_value = _session_read(active_id, mock_worker_context.worker_profile_id)

    resp = client.post("/api/v1/sessions/heartbeat")

    assert resp.status_code == 200
    mock_service.get_active_session.assert_called_once_with(
        worker_profile_id=mock_worker_context.worker_profile_id
    )
    mock_service.heartbeat.assert_called_once_with(
        work_session_id=active_id,
        worker_profile_id=mock_worker_context.worker_profile_id,
    )


def test_heartbeat_without_active_session_returns_null(client, mock_service):
    """No payload id + no live session -> 200 with null body (liveness miss)."""
    mock_service.get_active_session.return_value = None

    resp = client.post("/api/v1/sessions/heartbeat")

    assert resp.status_code == 200
    assert resp.json() is None
    mock_service.heartbeat.assert_not_called()


def test_heartbeat_payload_with_null_id_falls_back_to_active(client, mock_service, mock_worker_context):
    """A payload whose work_session_id is null behaves like no payload."""
    active_id = uuid.uuid4()
    mock_service.get_active_session.return_value = _session_read(active_id, mock_worker_context.worker_profile_id)
    mock_service.heartbeat.return_value = _session_read(active_id, mock_worker_context.worker_profile_id)

    resp = client.post("/api/v1/sessions/heartbeat", json={"work_session_id": None})

    assert resp.status_code == 200
    assert resp.json()["id"] == str(active_id)


# ======================================================================
# Start endpoint error mapping (POST /sessions/start)
# ======================================================================

def test_start_session_conflict_maps_to_409(client, mock_service):
    mock_service.start_session.side_effect = ConflictError("Worker already has an active session.")

    resp = client.post("/api/v1/sessions/start")

    assert resp.status_code == 409
    assert "active session" in resp.json()["error"]


def test_get_active_session_none_returns_null_body(client, mock_service):
    mock_service.get_active_session.return_value = None

    resp = client.get("/api/v1/sessions/active")

    assert resp.status_code == 200
    assert resp.json() is None


# ======================================================================
# Pause / Resume error mappings
# ======================================================================

@pytest.mark.parametrize("endpoint", ["pause", "resume"])
def test_pause_resume_not_found_maps_to_404(client, mock_service, endpoint):
    getattr(mock_service, f"{endpoint}_session").side_effect = NotFoundError("Work session not found.")

    resp = client.post(f"/api/v1/sessions/{uuid.uuid4()}/{endpoint}")

    assert resp.status_code == 404
    assert "not found" in resp.json()["error"]


@pytest.mark.parametrize("endpoint", ["pause", "resume"])
def test_pause_resume_unauthorized_maps_to_403(client, mock_service, endpoint):
    getattr(mock_service, f"{endpoint}_session").side_effect = UnauthorizedError(
        "Session belongs to another worker."
    )

    resp = client.post(f"/api/v1/sessions/{uuid.uuid4()}/{endpoint}")

    assert resp.status_code == 403


@pytest.mark.parametrize("endpoint", ["pause", "resume"])
def test_pause_resume_validation_error_maps_to_400(client, mock_service, endpoint):
    getattr(mock_service, f"{endpoint}_session").side_effect = ValidationError(
        "Only active sessions can be paused."
    )

    resp = client.post(f"/api/v1/sessions/{uuid.uuid4()}/{endpoint}")

    assert resp.status_code == 400


# ======================================================================
# End endpoint: status query, default, and error mappings
# ======================================================================

def test_end_session_default_status_is_completed(client, mock_service, mock_worker_context):
    session_id = uuid.uuid4()
    mock_service.end_session.return_value = _session_read(
        session_id, mock_worker_context.worker_profile_id, status="completed"
    )

    resp = client.post(f"/api/v1/sessions/{session_id}/end")

    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    mock_service.end_session.assert_called_once_with(
        work_session_id=session_id,
        worker_profile_id=mock_worker_context.worker_profile_id,
        status="completed",
    )


def test_end_session_cancelled_status_accepted(client, mock_service, mock_worker_context):
    session_id = uuid.uuid4()
    mock_service.end_session.return_value = _session_read(
        session_id, mock_worker_context.worker_profile_id, status="cancelled"
    )

    resp = client.post(f"/api/v1/sessions/{session_id}/end?status=cancelled")

    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"
    assert mock_service.end_session.call_args.kwargs["status"] == "cancelled"


def test_end_session_invalid_status_rejected_422(client, mock_service):
    resp = client.post(f"/api/v1/sessions/{uuid.uuid4()}/end?status=abandoned")

    assert resp.status_code == 422
    mock_service.end_session.assert_not_called()


def test_end_session_not_found_maps_to_404(client, mock_service):
    mock_service.end_session.side_effect = NotFoundError("Work session not found.")

    resp = client.post(f"/api/v1/sessions/{uuid.uuid4()}/end")

    assert resp.status_code == 404


def test_end_session_unauthorized_maps_to_403(client, mock_service):
    mock_service.end_session.side_effect = UnauthorizedError("Session belongs to another worker.")

    resp = client.post(f"/api/v1/sessions/{uuid.uuid4()}/end")

    assert resp.status_code == 403


def test_end_session_conflict_maps_to_409(client, mock_service):
    mock_service.end_session.side_effect = ConflictError("Session already ended.")

    resp = client.post(f"/api/v1/sessions/{uuid.uuid4()}/end")

    assert resp.status_code == 409


def test_end_session_validation_error_maps_to_400(client, mock_service):
    mock_service.end_session.side_effect = ValidationError("Invalid transition.")

    resp = client.post(f"/api/v1/sessions/{uuid.uuid4()}/end")

    assert resp.status_code == 400
