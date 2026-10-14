"""Route-level RBAC matrix (defense-in-depth for the role-aware navigation).

The frontend navbar + edge middleware hide and block unauthorized routes, but
the backend remains the authoritative boundary. These tests pin the API layer
to the exact same matrix the UI enforces:

  worker      -> /supervisor/* DENIED,  /admin/* DENIED,  /tasks/assigned OK
  supervisor  -> /supervisor/* OK,      /admin/* DENIED
  admin       -> /supervisor/* OK,      /admin/* OK
  anonymous   -> everything DENIED (401)
"""

import pytest
from starlette.testclient import TestClient

from app.main import app

ORG = "9a61e05d-7a32-4112-9c17-1833d7b42f65"
PASSWORD = "SecurePassword123!"


@pytest.fixture()
def client():
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


def _login(client: TestClient, email: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"organization_id": ORG, "email": email, "password": PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_worker_blocked_from_supervisor_and_admin_routes(client):
    tok = _login(client, "alex.worker@amap.com")
    assert client.get("/api/v1/supervisor/dashboard", headers=_auth(tok)).status_code == 403
    assert client.get("/api/v1/supervisor/workers", headers=_auth(tok)).status_code == 403
    assert client.get("/api/v1/admin/users", headers=_auth(tok)).status_code == 403
    # Worker's own surface stays available.
    assert client.get("/api/v1/tasks/assigned", headers=_auth(tok)).status_code == 200


def test_supervisor_allowed_fleet_but_blocked_from_admin(client):
    tok = _login(client, "supervisor@amap.com")
    assert client.get("/api/v1/supervisor/dashboard", headers=_auth(tok)).status_code == 200
    assert client.get("/api/v1/supervisor/workers", headers=_auth(tok)).status_code == 200
    assert client.get("/api/v1/admin/users", headers=_auth(tok)).status_code == 403


def test_admin_allowed_fleet_and_admin_routes(client):
    tok = _login(client, "admin@amap.com")
    assert client.get("/api/v1/supervisor/dashboard", headers=_auth(tok)).status_code == 200
    assert client.get("/api/v1/admin/users", headers=_auth(tok)).status_code == 200


def test_anonymous_blocked_from_all_role_routes(client):
    for path in (
        "/api/v1/supervisor/dashboard",
        "/api/v1/admin/users",
        "/api/v1/tasks/assigned",
    ):
        assert client.get(path).status_code == 401, path


def test_cross_organization_isolation_still_enforced(client):
    """Org isolation is orthogonal to roles and must remain intact."""
    other_org = "aa100000-0000-0000-0000-000000000002"
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": other_org,
            "email": "supervisor1@medicare-health.com",
            "password": PASSWORD,
        },
    )
    assert resp.status_code == 200, resp.text
    tok = resp.json()["access_token"]
    # Acme's task must be invisible to the MediCare supervisor.
    acme_task = "51000000-0000-0000-0000-000000000001"
    resp = client.get(f"/api/v1/tasks/{acme_task}", headers=_auth(tok))
    assert resp.status_code == 403, resp.status_code
