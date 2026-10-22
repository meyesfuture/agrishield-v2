"""
Integration Tests for the Decision Engine REST API Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas.decision import DecisionStatus, EvidenceMode


@pytest.fixture
def client():
    return TestClient(app)


def test_list_scenarios_endpoint(client):
    response = client.get("/api/v1/decision/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5

    scenario_ids = [s["scenario_id"] for s in data]
    assert "scenario_a_normal_baseline" in scenario_ids
    assert "scenario_b_convergent_anomaly" in scenario_ids
    assert "scenario_c_price_spike_only" in scenario_ids
    assert "scenario_d_arrival_drop_only" in scenario_ids
    assert "scenario_e_insufficient_evidence" in scenario_ids

    for s in data:
        assert s["is_synthetic"] is True
        assert s["data_mode"] == "SYNTHETIC_DEMO"


def test_get_scenario_detail_endpoint(client):
    response = client.get("/api/v1/decision/scenarios/scenario_b_convergent_anomaly")
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == "scenario_b_convergent_anomaly"
    assert data["is_synthetic"] is True
    assert len(data["observations"]) == 45
    assert data["synthetic_watermark"] == "SYNTHETIC DEMO — NOT LIVE MARKET EVIDENCE"


def test_run_scenario_b_endpoint(client):
    response = client.post("/api/v1/decision/scenarios/scenario_b_convergent_anomaly/run")
    assert response.status_code == 200
    data = response.json()
    assert data["decision_status"] == DecisionStatus.CONVERGENT_SUPPLY_ANOMALY
    assert data["evidence_mode"] == EvidenceMode.SYNTHETIC_DEMO
    assert data["anomaly_intensity_score"] > 50.0
    assert data["signals"]["price"]["status"] == "ANOMALOUS"
    assert data["signals"]["arrival"]["status"] == "ANOMALOUS"
    assert "Rule 6" in data["legal_caveat"]


def test_run_scenario_a_endpoint(client):
    response = client.post("/api/v1/decision/scenarios/scenario_a_normal_baseline/run")
    assert response.status_code == 200
    data = response.json()
    assert data["decision_status"] == DecisionStatus.NO_MATERIAL_ANOMALY
    assert data["anomaly_intensity_score"] == 0.0


def test_run_scenario_e_endpoint(client):
    response = client.post("/api/v1/decision/scenarios/scenario_e_insufficient_evidence/run")
    assert response.status_code == 200
    data = response.json()
    assert data["decision_status"] == DecisionStatus.INSUFFICIENT_DATA
    assert data["anomaly_intensity_score"] is None


def test_assess_real_location_endpoint(client):
    response = client.post(
        "/api/v1/decision/assess",
        json={"evidence_mode": "REAL", "location_name": "Ludhiana", "commodity_name": "Wheat"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["decision_status"] == DecisionStatus.INSUFFICIENT_DATA
    assert data["evidence_mode"] == EvidenceMode.REAL
    assert data["anomaly_intensity_score"] is None
    assert "insufficient empirical market data" in data["human_explanation"]


def test_methodology_endpoint(client):
    response = client.get("/api/v1/decision/methodology")
    assert response.status_code == 200
    data = response.json()
    assert data["methodology_version"] == "v2.1.0-robust-mad"
    assert data["minimum_baseline_observations"] == 14
    assert len(data["decision_rules"]) >= 5
