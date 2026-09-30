"""
Phase 7 — Organization-owned datasets / records tests.

Focused coverage for the dataset management surface:
- listing an organization's datasets with real record statistics
- listing records inside an organization-owned dataset (pagination, type filter)
- server-side organization scoping (cross-org dataset access is a 404)
- role gating (workers cannot reach the admin dataset endpoints)
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import UUID, uuid4

from fastapi import status
from starlette.testclient import TestClient

from app.dependencies import get_current_user
from app.main import app
from models.auth import AuthenticatedUserContext
from models.enterprise_organization import DatasetItem
from routes.organization_management import get_org_management_service
from services.base import NotFoundError
from services.organization_management_service import OrganizationManagementService

ORG_A_ID = UUID("9a61e05d-7a32-4112-9c17-1833d7b42f65")
ORG_B_ID = UUID("8b52d14c-6b21-4001-8b06-0722c6a31e54")
ADMIN_A_ID = UUID("c0000000-0000-0000-0000-000000000001")
WORKER_A_ID = UUID("c0000000-0000-0000-0000-000000000003")

NOW = datetime.now(timezone.utc)
DATASET_A_ID = UUID("ba100000-0000-0000-0000-000000000001")

client = TestClient(app)


def _auth(user_id, org_id, email, roles):
    return lambda: AuthenticatedUserContext(
        user_id=user_id,
        organization_id=org_id,
        email=email,
        full_name="Test User",
        status="active",
        roles=roles,
        is_active=True,
    )


ADMIN_A = _auth(ADMIN_A_ID, ORG_A_ID, "admin@amap.com", ["admin", "organization_admin"])
WORKER_A = _auth(WORKER_A_ID, ORG_A_ID, "alex.worker@amap.com", ["worker"])


def _service() -> OrganizationManagementService:
    service = OrganizationManagementService(
        orgs_repo=MagicMock(),
        depts_repo=MagicMock(),
        users_repo=MagicMock(),
        workers_repo=MagicMock(),
        workflows_repo=MagicMock(),
        workflow_steps_repo=MagicMock(),
        tasks_repo=MagicMock(),
        worker_task_assignments_repo=MagicMock(),
        audit_repo=MagicMock(),
        assistance_repo=MagicMock(),
        user_departments_repo=MagicMock(),
        roles_repo=MagicMock(),
        user_roles_repo=MagicMock(),
        worker_readiness_repo=MagicMock(),
        datasets_repo=MagicMock(),
    )
    return service


def _dataset_row(dataset_id, org_id, record_count=3, record_types=None):
    return {
        "id": dataset_id,
        "organization_id": org_id,
        "name": "Powertrain Quality Tracer — Line 3",
        "description": "Synthetic sample dataset.",
        "domain": "manufacturing_quality",
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
        "record_count": record_count,
        "record_types": record_types or ["production", "inspection"],
    }


def _record_row(record_id, dataset_id, org_id, record_type="production"):
    return {
        "id": record_id,
        "dataset_id": dataset_id,
        "organization_id": org_id,
        "record_type": record_type,
        "title": f"Sample {record_type} record",
        "source_ref": "BR-2026-0917",
        "payload": {"result": "fail"},
        "occurred_at": NOW,
        "related_record_id": None,
        "created_at": NOW,
        "updated_at": NOW,
    }


# =====================================================================
# Service level
# =====================================================================

def test_list_datasets_returns_org_datasets_with_stats():
    service = _service()
    service.datasets_repo.list_by_organization.return_value = [
        _dataset_row(DATASET_A_ID, ORG_A_ID, record_count=13,
                     record_types=["production", "inspection", "maintenance", "incident"])
    ]

    datasets = service.list_datasets(ORG_A_ID)

    assert len(datasets) == 1
    ds = datasets[0]
    assert isinstance(ds, DatasetItem)
    assert ds.record_count == 13
    assert ds.record_types == ["incident", "inspection", "maintenance", "production"]
    assert ds.domain == "manufacturing_quality"
    service.datasets_repo.list_by_organization.assert_called_once_with(ORG_A_ID)


def test_list_datasets_empty_org_returns_empty_list():
    """Honest empty state — no fabricated datasets."""
    service = _service()
    service.datasets_repo.list_by_organization.return_value = []

    assert service.list_datasets(ORG_A_ID) == []


def test_list_dataset_records_cross_org_is_not_found():
    """A dataset owned by another organization must be indistinguishable from missing."""
    service = _service()
    service.datasets_repo.get_by_id.return_value = _dataset_row(
        uuid4(), ORG_B_ID
    )["id"] and {
        "id": uuid4(), "organization_id": ORG_B_ID, "name": "Other Org Dataset",
        "domain": "general", "status": "active", "created_at": NOW, "updated_at": NOW,
    }

    try:
        service.list_dataset_records(dataset_id=uuid4(), organization_id=ORG_A_ID)
        raise AssertionError("expected NotFoundError")
    except NotFoundError:
        pass
    service.datasets_repo.list_records.assert_not_called()


def test_list_dataset_records_passes_type_filter_and_pagination():
    service = _service()
    service.datasets_repo.get_by_id.return_value = {
        "id": DATASET_A_ID, "organization_id": ORG_A_ID,
        "name": "Powertrain Quality Tracer — Line 3",
        "domain": "manufacturing_quality", "status": "active",
        "created_at": NOW, "updated_at": NOW,
    }
    rec_id = uuid4()
    service.datasets_repo.list_records.return_value = ([_record_row(rec_id, DATASET_A_ID, ORG_A_ID)], 1)

    result = service.list_dataset_records(
        dataset_id=DATASET_A_ID, organization_id=ORG_A_ID,
        page=2, page_size=10, record_type="inspection",
    )

    assert result["dataset"]["name"] == "Powertrain Quality Tracer — Line 3"
    assert result["total_count"] == 1
    assert result["page"] == 2
    assert result["page_size"] == 10
    assert result["items"][0].record_type == "production"  # mirrors mocked row
    service.datasets_repo.list_records.assert_called_once_with(
        dataset_id=DATASET_A_ID, limit=10, offset=10, record_type="inspection"
    )


# =====================================================================
# Route level
# =====================================================================

def test_datasets_route_returns_items():
    mock_service = MagicMock()
    mock_service.list_datasets.return_value = [
        DatasetItem(
            id=DATASET_A_ID, organization_id=ORG_A_ID,
            name="Powertrain Quality Tracer — Line 3",
            description="Synthetic sample dataset.", domain="manufacturing_quality",
            status="active", record_count=13,
            record_types=["incident", "inspection", "maintenance", "production"],
            created_at=NOW, updated_at=NOW,
        )
    ]
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_org_management_service] = lambda: mock_service
    try:
        res = client.get("/api/v1/organizations/manage/datasets")
        assert res.status_code == status.HTTP_200_OK, res.text
        body = res.json()
        assert len(body) == 1
        assert body[0]["record_count"] == 13
        assert "production" in body[0]["record_types"]
        mock_service.list_datasets.assert_called_once_with(organization_id=ORG_A_ID)
    finally:
        app.dependency_overrides.clear()


def test_dataset_records_route_cross_org_404():
    mock_service = MagicMock()
    mock_service.list_dataset_records.side_effect = NotFoundError(
        "Dataset not found in your organization."
    )
    app.dependency_overrides[get_current_user] = ADMIN_A
    app.dependency_overrides[get_org_management_service] = lambda: mock_service
    try:
        res = client.get(f"/api/v1/organizations/manage/datasets/{uuid4()}/records")
        assert res.status_code == status.HTTP_404_NOT_FOUND
    finally:
        app.dependency_overrides.clear()


def test_datasets_route_forbidden_for_worker():
    app.dependency_overrides[get_current_user] = WORKER_A
    try:
        res = client.get("/api/v1/organizations/manage/datasets")
        assert res.status_code == status.HTTP_403_FORBIDDEN
        res = client.get(f"/api/v1/organizations/manage/datasets/{uuid4()}/records")
        assert res.status_code == status.HTTP_403_FORBIDDEN
    finally:
        app.dependency_overrides.clear()
