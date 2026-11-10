"""
Unit tests for the AssistanceService business-logic layer
(services/assistance_service.py).

Repositories are replaced with MagicMocks, so these tests verify the
service contract in isolation: correct field pass-through on create/send,
tenant and recipient ownership guards on acknowledge/resolve/mark-read,
and the NotFoundError / UnauthorizedError failure modes — no database
required.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock
import uuid

import pytest

from models.assistance import (
    AssistancePriority,
    AssistanceRequestCreate,
    AssistanceRequestRead,
    NotificationCreate,
    NotificationRead,
)
from services.assistance_service import AssistanceService
from services.base import NotFoundError, UnauthorizedError

ORG_ID = uuid.UUID("9a61e05d-7a32-4112-9c17-1833d7b42f65")
WORKER_ID = uuid.UUID("d0000000-0000-0000-0000-000000000001")
RECIPIENT_ID = uuid.UUID("c0000000-0000-0000-0000-000000000003")


@pytest.fixture
def assistance_repo():
    return MagicMock()


@pytest.fixture
def notifications_repo():
    return MagicMock()


@pytest.fixture
def service(assistance_repo, notifications_repo):
    return AssistanceService(
        assistance_repo=assistance_repo,
        notifications_repo=notifications_repo,
    )


def _now():
    return datetime.now(timezone.utc)


def _assistance_row(row_id, org_id=ORG_ID, status="open", priority="normal"):
    now = _now()
    return {
        "id": row_id,
        "organization_id": org_id,
        "worker_profile_id": WORKER_ID,
        "work_session_id": None,
        "workflow_assignment_id": None,
        "worker_task_assignment_id": None,
        "status": status,
        "priority": priority,
        "reason": "needs help",
        "request_data": {"source": "test"},
        "requested_at": now,
        "acknowledged_at": None,
        "resolved_at": None,
        "created_at": now,
        "updated_at": now,
    }


def _notification_row(row_id, org_id=ORG_ID, status="unread"):
    now = _now()
    return {
        "id": row_id,
        "organization_id": org_id,
        "recipient_user_id": RECIPIENT_ID,
        "notification_type": "assistance_request",
        "title": "Help requested",
        "message": "Worker requested assistance",
        "notification_data": {"priority": "high"},
        "status": status,
        "created_at": now,
        "read_at": None,
    }


# ======================================================================
# create_assistance_request
# ======================================================================

def test_create_assistance_request_passes_all_fields_and_validates(service, assistance_repo):
    request_id = uuid.uuid4()
    assistance_repo.create.return_value = _assistance_row(request_id, priority="high")

    payload = AssistanceRequestCreate(
        organization_id=ORG_ID,
        worker_profile_id=WORKER_ID,
        priority=AssistancePriority.HIGH,
        reason="part misaligned",
        request_data={"step": 4},
    )
    result = service.create_assistance_request(payload)

    assistance_repo.create.assert_called_once_with(
        organization_id=ORG_ID,
        worker_profile_id=WORKER_ID,
        work_session_id=None,
        workflow_assignment_id=None,
        worker_task_assignment_id=None,
        priority=AssistancePriority.HIGH,
        reason="part misaligned",
        request_data={"step": 4},
    )
    assert isinstance(result, AssistanceRequestRead)
    assert result.id == request_id
    assert result.priority == "high"


# ======================================================================
# acknowledge_request / resolve_request
# ======================================================================

@pytest.mark.parametrize("method,repo_method,expected_status", [
    ("acknowledge_request", "acknowledge", "acknowledged"),
    ("resolve_request", "resolve", "resolved"),
])
def test_acknowledge_and_resolve_success(
    service, assistance_repo, method, repo_method, expected_status
):
    request_id = uuid.uuid4()
    assistance_repo.get_by_id.return_value = _assistance_row(request_id)
    assistance_repo.__getattr__(repo_method).return_value = _assistance_row(
        request_id, status=expected_status
    )

    result = getattr(service, method)(request_id, ORG_ID)

    assert isinstance(result, AssistanceRequestRead)
    assert result.status == expected_status
    assistance_repo.__getattr__(repo_method).assert_called_once_with(request_id)


@pytest.mark.parametrize("method", ["acknowledge_request", "resolve_request"])
def test_acknowledge_and_resolve_unknown_request_raises_not_found(service, assistance_repo, method):
    assistance_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError, match="not found"):
        getattr(service, method)(uuid.uuid4(), ORG_ID)


@pytest.mark.parametrize("method", ["acknowledge_request", "resolve_request"])
def test_acknowledge_and_resolve_cross_tenant_raises_unauthorized(service, assistance_repo, method):
    other_org = uuid.uuid4()
    assistance_repo.get_by_id.return_value = _assistance_row(uuid.uuid4(), org_id=other_org)

    with pytest.raises(UnauthorizedError, match="organization"):
        getattr(service, method)(uuid.uuid4(), ORG_ID)


# ======================================================================
# send_notification
# ======================================================================

def test_send_notification_passes_fields_and_validates(service, notifications_repo):
    notification_id = uuid.uuid4()
    notifications_repo.create.return_value = _notification_row(notification_id)

    payload = NotificationCreate(
        organization_id=ORG_ID,
        recipient_user_id=RECIPIENT_ID,
        notification_type="assistance_request",
        title="Help requested",
        message="Worker requested assistance",
    )
    result = service.send_notification(payload)

    notifications_repo.create.assert_called_once_with(
        organization_id=ORG_ID,
        recipient_user_id=RECIPIENT_ID,
        notification_type="assistance_request",
        title="Help requested",
        message="Worker requested assistance",
        notification_data={},
        status="unread",
    )
    assert isinstance(result, NotificationRead)
    assert result.id == notification_id
    assert result.status == "unread"


# ======================================================================
# mark_notification_as_read
# ======================================================================

def test_mark_notification_as_read_success(service, notifications_repo):
    notification_id = uuid.uuid4()
    notifications_repo.get_by_id.return_value = _notification_row(notification_id)
    notifications_repo.mark_as_read.return_value = _notification_row(
        notification_id, status="read"
    )

    result = service.mark_notification_as_read(notification_id, RECIPIENT_ID)

    assert isinstance(result, NotificationRead)
    assert result.status == "read"
    notifications_repo.mark_as_read.assert_called_once_with(notification_id)


def test_mark_notification_as_read_unknown_raises_not_found(service, notifications_repo):
    notifications_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError, match="not found"):
        service.mark_notification_as_read(uuid.uuid4(), RECIPIENT_ID)


def test_mark_notification_as_read_wrong_recipient_raises_unauthorized(service, notifications_repo):
    notifications_repo.get_by_id.return_value = _notification_row(uuid.uuid4())

    with pytest.raises(UnauthorizedError, match="does not belong"):
        service.mark_notification_as_read(uuid.uuid4(), uuid.uuid4())
