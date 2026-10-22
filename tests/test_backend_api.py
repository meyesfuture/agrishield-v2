"""
Tests for Punjab GrainWatch Backend API endpoints and safe configuration.
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import settings


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    """GET / should return project identity and evidence standard."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "Punjab GrainWatch API"
    assert "evidence_standard" in data
    assert "no simulated hoarding scores" in data["evidence_standard"]


def test_healthz_liveness(client):
    """GET /healthz should return 200 with status ok."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp_utc" in data


def test_api_v1_health_detailed(client):
    """GET /api/v1/health should verify all components are healthy."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["checks"]["dataset_catalog_present"] is True
    assert data["checks"]["quality_report_present"] is True
    assert data["checks"]["data_directory_present"] is True


def test_api_v1_status_guardrails(client):
    """GET /api/v1/status should report verified critical guardrails."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_data_gate"] == "PASSED"
    assert data["total_datasets_cataloged"] == 20
    assert len(data["evidence_guardrails"]) == 6
    for g in data["evidence_guardrails"]:
        assert g["status"] == "VERIFIED"


def test_api_v1_datasets_list_and_filters(client):
    """GET /api/v1/datasets should return catalog items and support query filters."""
    # List all
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 20
    assert len(data["items"]) == 20

    # Filter by status: observed
    resp_obs = client.get("/api/v1/datasets?status=observed")
    assert resp_obs.status_code == 200
    obs_data = resp_obs.json()
    assert obs_data["total"] > 0
    assert all(i["evidence_status"] == "observed" for i in obs_data["items"])

    # Filter by search
    resp_search = client.get("/api/v1/datasets?search=coriander")
    assert resp_search.status_code == 200
    search_data = resp_search.json()
    assert search_data["total"] > 0


def test_api_v1_dataset_detail_existing(client):
    """GET /api/v1/datasets/{id} for valid ID returns complete metadata."""
    response = client.get("/api/v1/datasets/punjab_mandi_arrivals_oct2026")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset"]["dataset_id"] == "punjab_mandi_arrivals_oct2026"
    assert data["exists_on_disk"] is True
    assert len(data["column_list"]) == 16


def test_api_v1_dataset_detail_not_found(client):
    """GET /api/v1/datasets/{id} for invalid ID returns 404."""
    response = client.get("/api/v1/datasets/non_existent_fake_id")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_api_v1_quality_summary(client):
    """GET /api/v1/quality/summary returns audit findings and verified assertions."""
    response = client.get("/api/v1/quality/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_validation_gate"] == "PASSED"
    assert len(data["critical_assertions"]) == 6
    assert all(a["verified"] is True for a in data["critical_assertions"])
    assert len(data["quarantined_files"]) == 2


def test_safe_path_resolution():
    """Path resolution must reject directory traversal attempts."""
    # Valid relative path inside workspace
    valid_path = settings.resolve_safe_path("data/manifests/dataset_catalog.json")
    assert valid_path is not None
    assert valid_path.exists()

    # Traversal attack attempts
    traversal_path = settings.resolve_safe_path("../../../Windows/System32")
    assert traversal_path is None

    traversal_root = settings.resolve_safe_path("..")
    assert traversal_root is None
