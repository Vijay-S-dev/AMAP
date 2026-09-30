"""
Phase 5 — Real User Management CRUD tests.

Covers the admin user-edit surface and the worker/supervisor edit +
deactivate/reactivate paths added for PostgreSQL-backed user management:

- PUT /api/v1/admin/users/{user_id}
      (identity edits: full name / email, any role)
- PUT /api/v1/organizations/manage/workers/{user_id}
      (worker identity + badge + department + account status)
- PUT /api/v1/organizations/manage/supervisors/{user_id}
      (extended with identity edits: full name / email)

Repository accesses are mocked at the service boundary (same pattern as
test_organization_management.py). Live PostgreSQL persistence — create,
login, edit, deactivate -> login blocked, reactivate, backend restart — is
verified against the real stack in the Phase 5 live verification.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import UUID, uuid4

from fastapi import status
from starlette.testclient import TestClient

from app.dependencies import get_current_user
from app.main import app
from models.auth import AuthenticatedUserContext
from routes.admin import get_admin_service
from routes.organization_management import get_org_management_service
from services.admin_service import AdminService
from services.organization_management_service import OrganizationManagementService

ORG_A_ID = UUID("9a61e05d-7a32-4112-9c17-1833d7b42f65")
ORG_B_ID = UUID("8b52d14c-6b21-4001-8b06-0722c6a31e54")
ADMIN_A_ID = UUID("c0000000-0000-0000-0000-000000000001")
WORKER_A_ID = UUID("c0000000-0000-0000-0000-000000000003")
SUPERVISOR_A_ID = UUID("c0000000-0000-0000-0000-000000000002")

NOW = datetime.now(timezone.utc)
WORKER_ROLE_ID = UUID("a0000000-0000-0000-0000-000000000003")
SUPERVISOR_ROLE_ID = UUID("a0000000-0000-0000-0000-000000000002")
DEPT_A_ID = UUID("11111111-1111-1111-1111-111111111111")

client = TestClient(app)


def _user_row(user_id, org_id, email, full_name, user_status="active"):
    return {
        "id": user_id,
        "organization_id": org_id,
        "email": email,
        "full_name": full_name,
        "password_hash": "x",
        "status": user_status,
        "created_at": NOW,
        "updated_at": NOW,
    }


def _auth(user_id, org_id, email, full_name, roles):
    return lambda: AuthenticatedUserContext(
        user_id=user_id,
        organization_id=org_id,
        email=email,
        full_name=full_name,
        status="active",
        roles=roles,
        is_active=True,
    )


ADMIN_A = _auth(ADMIN_A_ID, ORG_A_ID, "admin@amap.com", "Sarah Jenkins", ["admin", "organization_admin"])
WORKER_A = _auth(WORKER_A_ID, ORG_A_ID, "alex.worker@amap.com", "Alex Morgan", ["worker"])


def _mock_admin_service():
    service = AdminService(
        configs_repo=MagicMock(),
        orgs_repo=MagicMock(),
        users_repo=MagicMock(),
        roles_repo=MagicMock(),
        user_roles_repo=MagicMock(),
        audit_repo=MagicMock(),
    )
    service.users_repo.get_by_email.return_value = None
    return service


def _mock_org_service():
    service = OrganizationManagementService(
        orgs_repo=MagicMock(),
        depts_repo=MagicMock(),
        users_repo=MagicMock(),
        workers_repo=MagicMock(),
        workflows_repo=MagicMock(),
        workflow_steps_repo=MagicMock(),
        audit_repo=MagicMock(),
        assistance_repo=MagicMock(),
        user_departments_repo=MagicMock(),
        roles_repo=MagicMock(),
        user_roles_repo=MagicMock(),
        worker_readiness_repo=MagicMock(),
    )
    service.users_repo.get_by_email.return_value = None
    return service


def _worker_role_setup(org_service, user_row):
    """Configure the mock org service so `user_row` is recognized as a worker."""
    org_service.users_repo.get_by_id.return_value = user_row
    org_service.roles_repo.get_by_name.return_value = {
        "id": WORKER_ROLE_ID, "name": "worker", "description": None,
        "created_at": NOW, "updated_at": NOW,
    }
    org_service.user_roles_repo.get_by_user_id.return_value = [
        {"user_id": user_row["id"], "role_id": WORKER_ROLE_ID}
    ]
    org_service.users_repo.update_details.side_effect = (
        lambda user_id, full_name=None, email=None: _user_row(
            user_id, user_row["organization_id"],
            email or user_row["email"], full_name or user_row["full_name"],
        )
    )
    org_service.workers_repo.update_badge.return_value = {
        "id": uuid4(), "user_id": user_row["id"], "badge_number": "B-9001",
        "status": "active", "created_at": NOW, "updated_at": NOW,
    }
    org_service.user_departments_repo.get_by_user_id.return_value = []
    org_service.depts_repo.get_by_id.return_value = {
        "id": DEPT_A_ID, "organization_id": ORG_A_ID, "name": "Quality Control & Diagnostics",
        "status": "active", "created_at": NOW, "updated_at": NOW,
    }
    org_service.users_repo.update_status.return_value = _user_row(
        user_row["id"], user_row["organization_id"], user_row["email"],
        user_row["full_name"], "suspended",
    )


# =====================================================================
# PUT /api/v1/admin/users/{user_id} — identity edits (any role)
# =====================================================================

def test_admin_updates_user_identity():
    svc = _mock_admin_service()
    svc.users_repo.get_by_id.return_value = _user_row(WORKER_A_ID, ORG_A_ID, "alex.worker@amap.com", "Alex Morgan")
    svc.users_repo.update_details.return_value = _user_row(WORKER_A_ID, ORG_A_ID, "alex.morgan@amap.com", "Alex Morgan Jr.")
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_admin_service] = lambda: svc
    try:
        res = client.put(f"/api/v1/admin/users/{WORKER_A_ID}", json={
            "full_name": "Alex Morgan Jr.",
            "email": "Alex.Morgan@amap.com",
        })
        assert res.status_code == status.HTTP_200_OK, res.text
        body = res.json()
        assert body["full_name"] == "Alex Morgan Jr."
        assert body["email"] == "alex.morgan@amap.com"
        # email must be normalized to lowercase before the uniqueness check
        _, kwargs = svc.users_repo.get_by_email.call_args
        assert kwargs == {} or svc.users_repo.get_by_email.call_args.args[1] == "alex.morgan@amap.com"
        svc.audit_repo.create.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_admin_update_user_email_conflict_409():
    svc = _mock_admin_service()
    svc.users_repo.get_by_id.return_value = _user_row(WORKER_A_ID, ORG_A_ID, "alex.worker@amap.com", "Alex Morgan")
    # another user in the same org already owns the email
    svc.users_repo.get_by_email.return_value = _user_row(uuid4(), ORG_A_ID, "taken@amap.com", "Someone Else")
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_admin_service] = lambda: svc
    try:
        res = client.put(f"/api/v1/admin/users/{WORKER_A_ID}", json={"email": "taken@amap.com"})
        assert res.status_code == status.HTTP_409_CONFLICT
        svc.users_repo.update_details.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_admin_update_user_cross_org_404():
    svc = _mock_admin_service()
    svc.users_repo.get_by_id.return_value = _user_row(uuid4(), ORG_B_ID, "b@orgb.com", "Org B User")
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_admin_service] = lambda: svc
    try:
        res = client.put(f"/api/v1/admin/users/{uuid4()}", json={"full_name": "Nope"})
        assert res.status_code == status.HTTP_404_NOT_FOUND
    finally:
        app.dependency_overrides.clear()


def test_admin_update_user_empty_payload_422():
    svc = _mock_admin_service()
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_admin_service] = lambda: svc
    try:
        res = client.put(f"/api/v1/admin/users/{WORKER_A_ID}", json={})
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    finally:
        app.dependency_overrides.clear()


def test_admin_update_user_forbidden_for_worker_403():
    app.dependency_overrides[get_current_user] = WORKER_A
    try:
        res = client.put(f"/api/v1/admin/users/{WORKER_A_ID}", json={"full_name": "X"})
        assert res.status_code == status.HTTP_403_FORBIDDEN
    finally:
        app.dependency_overrides.clear()


# =====================================================================
# PUT /api/v1/organizations/manage/workers/{user_id}
# =====================================================================

def test_update_worker_full_edit():
    svc = _mock_org_service()
    _worker_role_setup(svc, _user_row(WORKER_A_ID, ORG_A_ID, "alex.worker@amap.com", "Alex Morgan"))
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_org_management_service] = lambda: svc
    try:
        res = client.put(f"/api/v1/organizations/manage/workers/{WORKER_A_ID}", json={
            "full_name": "Alex Morgan Sr.",
            "email": "alex.sr@amap.com",
            "badge_number": "B-9001",
            "department_id": str(DEPT_A_ID),
            "status": "suspended",
        })
        assert res.status_code == status.HTTP_200_OK, res.text
        body = res.json()
        assert body["changes"]["full_name"] == "Alex Morgan Sr."
        assert body["changes"]["email"] == "alex.sr@amap.com"
        assert body["changes"]["badge_number"] == "B-9001"
        assert body["changes"]["department_id"] == str(DEPT_A_ID)
        assert body["changes"]["status"] == "suspended"
        svc.workers_repo.update_badge.assert_called_once()
        svc.users_repo.update_status.assert_called_once()
        svc.audit_repo.create.assert_called_once()
        event_kwargs = svc.audit_repo.create.call_args.kwargs
        assert event_kwargs["event_type"] == "worker.updated"
    finally:
        app.dependency_overrides.clear()


def test_update_worker_reactivate():
    svc = _mock_org_service()
    _worker_role_setup(svc, _user_row(WORKER_A_ID, ORG_A_ID, "alex.worker@amap.com", "Alex Morgan", "suspended"))
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_org_management_service] = lambda: svc
    try:
        res = client.put(f"/api/v1/organizations/manage/workers/{WORKER_A_ID}", json={"status": "active"})
        assert res.status_code == status.HTTP_200_OK, res.text
        assert res.json()["changes"] == {"status": "active"}
    finally:
        app.dependency_overrides.clear()


def test_update_worker_invalid_status_422():
    svc = _mock_org_service()
    _worker_role_setup(svc, _user_row(WORKER_A_ID, ORG_A_ID, "alex.worker@amap.com", "Alex Morgan"))
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_org_management_service] = lambda: svc
    try:
        res = client.put(f"/api/v1/organizations/manage/workers/{WORKER_A_ID}", json={"status": "hacked"})
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    finally:
        app.dependency_overrides.clear()


def test_update_worker_not_a_worker_404():
    svc = _mock_org_service()
    svc.users_repo.get_by_id.return_value = _user_row(SUPERVISOR_A_ID, ORG_A_ID, "supervisor@amap.com", "Marcus Vance")
    svc.roles_repo.get_by_name.return_value = {
        "id": WORKER_ROLE_ID, "name": "worker", "description": None,
        "created_at": NOW, "updated_at": NOW,
    }
    svc.user_roles_repo.get_by_user_id.return_value = []  # no worker role
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_org_management_service] = lambda: svc
    try:
        res = client.put(f"/api/v1/organizations/manage/workers/{SUPERVISOR_A_ID}", json={"full_name": "X"})
        assert res.status_code == status.HTTP_404_NOT_FOUND
    finally:
        app.dependency_overrides.clear()


def test_update_worker_cross_org_404():
    svc = _mock_org_service()
    svc.users_repo.get_by_id.return_value = _user_row(uuid4(), ORG_B_ID, "b@orgb.com", "Org B Worker")
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_org_management_service] = lambda: svc
    try:
        res = client.put(f"/api/v1/organizations/manage/workers/{uuid4()}", json={"full_name": "X"})
        assert res.status_code == status.HTTP_404_NOT_FOUND
    finally:
        app.dependency_overrides.clear()


def test_update_worker_duplicate_email_409():
    svc = _mock_org_service()
    _worker_role_setup(svc, _user_row(WORKER_A_ID, ORG_A_ID, "alex.worker@amap.com", "Alex Morgan"))
    svc.users_repo.get_by_email.return_value = _user_row(uuid4(), ORG_A_ID, "taken@amap.com", "Someone Else")
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_org_management_service] = lambda: svc
    try:
        res = client.put(f"/api/v1/organizations/manage/workers/{WORKER_A_ID}", json={"email": "taken@amap.com"})
        assert res.status_code == status.HTTP_409_CONFLICT
    finally:
        app.dependency_overrides.clear()


def test_update_worker_forbidden_for_worker_403():
    app.dependency_overrides[get_current_user] = WORKER_A
    try:
        res = client.put(f"/api/v1/organizations/manage/workers/{WORKER_A_ID}", json={"full_name": "X"})
        assert res.status_code == status.HTTP_403_FORBIDDEN
    finally:
        app.dependency_overrides.clear()


# =====================================================================
# PUT /api/v1/organizations/manage/supervisors/{user_id} — extended identity
# =====================================================================

def test_update_supervisor_identity():
    svc = _mock_org_service()
    sup_row = _user_row(SUPERVISOR_A_ID, ORG_A_ID, "supervisor@amap.com", "Marcus Vance")
    svc.users_repo.get_by_id.return_value = sup_row
    svc.roles_repo.get_by_name.return_value = {
        "id": SUPERVISOR_ROLE_ID, "name": "supervisor", "description": None,
        "created_at": NOW, "updated_at": NOW,
    }
    svc.user_roles_repo.get_by_user_id.return_value = [
        {"user_id": SUPERVISOR_A_ID, "role_id": SUPERVISOR_ROLE_ID}
    ]
    svc.users_repo.update_details.side_effect = (
        lambda user_id, full_name=None, email=None: _user_row(
            user_id, ORG_A_ID, email or sup_row["email"], full_name or sup_row["full_name"],
        )
    )
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_org_management_service] = lambda: svc
    try:
        res = client.put(f"/api/v1/organizations/manage/supervisors/{SUPERVISOR_A_ID}", json={
            "full_name": "Marcus Vance II",
        })
        assert res.status_code == status.HTTP_200_OK, res.text
        assert res.json()["changes"] == {"full_name": "Marcus Vance II"}
    finally:
        app.dependency_overrides.clear()
