"""
Integration Tests for Cross-Modal API and Multi-Tenant Repositories.
"""

import sys
import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent / "backend"
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.dependencies import get_current_active_worker, get_current_user
from app.main import app
from models.auth import AuthenticatedUserContext


@pytest.fixture
def mock_worker_context():
    org_id = uuid.UUID("9a61e05d-7a32-4112-9c17-1833d7b42f65")
    user_id = uuid.UUID("c0000000-0000-0000-0000-000000000003")
    worker_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    return AuthenticatedUserContext(
        user_id=user_id,
        organization_id=org_id,
        email="alex.worker@amap.com",
        full_name="Alex Morgan",
        status="active",
        roles=["worker", "admin"],
        permissions=["session:read", "session:write", "multimodal:input"],
        worker_profile_id=worker_id,
    )


@pytest.fixture
def client(mock_worker_context):
    app.dependency_overrides[get_current_user] = lambda: mock_worker_context
    app.dependency_overrides[get_current_active_worker] = lambda: mock_worker_context
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def test_multimodal_spatial_voice_integration(client):
    """
    Test combining spatial gesture pointer target with voice confirmation command.

    The pointing gesture must carry spatial context (pointer target) so the
    fusion engine treats it as a spatial carrier; the voice command supplies
    the operational action. Expected result: complementary fusion binding
    "confirm_action" onto the pointed target (see multimodal_service step 7).
    """
    resp = client.post(
        "/api/v1/multimodal/fuse",
        json={
            "inputs": [
                {
                    "mode": "gesture",
                    "raw_intent": "pointing",
                    "confidence": 0.88,
                    "timestamp_ms": 1000,
                    "context_data": {
                        "target_part_id": "7f1c9e2a-2b7d-4c3e-9a10-5e8d6f4b3c21",
                        "spatial_x": 0.42,
                        "spatial_y": 0.61,
                    },
                },
                {
                    "mode": "voice",
                    "raw_intent": "confirm_action",
                    "confidence": 0.94,
                    "timestamp_ms": 1050,
                },
            ],
            "temporal_window_ms": 1500,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["fused_action"] == "confirm_action"
    assert data["validation_status"] == "valid"
    assert data["fusion_strategy"] == "complementary"
    assert data["target_context"]["target_part_id"] == "7f1c9e2a-2b7d-4c3e-9a10-5e8d6f4b3c21"
    # contributing_modes is built from a set in the service -> order is not
    # guaranteed across interpreter runs; compare order-insensitively.
    assert sorted(data["contributing_modes"]) == ["gesture", "voice"]


def test_multimodal_single_gesture_frame_processing(client):
    """
    Test processing standalone optical hand gesture frame via /gestures/process-frame.
    """
    resp = client.post(
        "/api/v1/gestures/process-frame",
        json={
            "landmarks": [{"x": 0.5, "y": 0.5, "z": 0.0} for _ in range(21)],
            "handedness": "Right",
            "timestamp_ms": 1000,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "detected_gesture" in data
    assert "confidence" in data
