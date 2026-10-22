"""
Test suite for Phase 6: Transparent Analytics, Eligibility Gates, and Segregated Synthetic Lab.
Enforces non-negotiable rules:
- Rule 6 of AGENTS.md: No hoarding conclusions, no actor-level rankings, statistical anomaly != hoarding
- 7-point eligibility gate: zero wheat/paddy arrivals, national stocks != Punjab stocks, etc.
- Synthetic isolation: data/synthetic/, is_synthetic=True, excluded from production metrics
"""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.analytics_service import AnalyticsEligibilityService
from backend.schemas.analytics import (
    EligibilityCheckItem,
    DatasetEligibilityResult,
    ReadinessMetrics,
    EligibilityGateResponse,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def analytics_service():
    return AnalyticsEligibilityService()


class TestPhase6EligibilityGates:
    """Tests for the 7-point statistical anomaly eligibility gate."""

    def test_overall_hoarding_detection_is_strictly_forbidden(self, analytics_service):
        response = analytics_service.evaluate_eligibility_gates()
        assert "STRICTLY FORBIDDEN" in response.overall_hoarding_detection_eligibility
        assert "Rule 6" in response.overall_hoarding_detection_eligibility
        assert response.total_streams_evaluated == 4
        assert response.eligible_streams_count == 0
        assert len(response.stream_evaluations) == 4

    def test_all_streams_fail_with_insufficient_evidence(self, analytics_service):
        response = analytics_service.evaluate_eligibility_gates()
        for stream in response.stream_evaluations:
            assert stream.eligibility_verdict == "INELIGIBLE (BLOCKED)"
            assert stream.eligible_for_grain_anomaly is False
            assert len(stream.missing_prerequisites) > 0
            assert stream.failed_criteria_count > 0

    def test_mandi_arrivals_blocked_due_to_zero_wheat_paddy(self, analytics_service):
        response = analytics_service.evaluate_eligibility_gates()
        arrivals = next(s for s in response.stream_evaluations if s.dataset_id == "punjab_mandi_arrivals_oct2026")
        
        # Check specific gate criteria
        gate_map = {c.criteria_id: c for c in arrivals.criteria_checks}
        assert gate_map["CRIT-01"].passed is False
        assert "0 wheat/paddy" in gate_map["CRIT-01"].current_evidence
        assert "Produce volume variations cannot proxy staple grain" in gate_map["CRIT-01"].blocking_reason
        assert gate_map["CRIT-02"].passed is True   # daily observations present
        assert gate_map["CRIT-03"].passed is False  # historical depth missing (only 14 days)
        assert gate_map["CRIT-07"].passed is False  # cross-commodity comparison basis fails
        
        # Verify missing prerequisites
        assert any("Anaaj Kharid" in prereq for prereq in arrivals.missing_prerequisites)
        assert "DISPLAY_AS_DESCRIPTIVE_PRODUCE_ONLY" in arrivals.handling_policy

    def test_paddy_prices_cannot_be_used_as_arrivals(self, analytics_service):
        response = analytics_service.evaluate_eligibility_gates()
        prices = next(s for s in response.stream_evaluations if s.dataset_id == "agmarknet_punjab_daily_prices")
        
        gate_map = {c.criteria_id: c for c in prices.criteria_checks}
        assert gate_map["CRIT-01"].passed is True   # paddy is foodgrain
        assert gate_map["CRIT-02"].passed is False  # arrival volumes are 100% null
        assert "arrival quantities cannot be inferred from prices" in gate_map["CRIT-02"].blocking_reason.lower()
        assert gate_map["CRIT-07"].passed is False  # volume-price comparison basis fails
        assert "DISPLAY_MODAL_PRICES_ONLY" in prices.handling_policy

    def test_national_stocks_cannot_be_used_as_punjab_stocks(self, analytics_service):
        response = analytics_service.evaluate_eligibility_gates()
        stocks = next(s for s in response.stream_evaluations if s.dataset_id == "stock_observations_national_dfpd")
        
        gate_map = {c.criteria_id: c for c in stocks.criteria_checks}
        assert gate_map["CRIT-06"].passed is False
        assert "state column is 100% null" in gate_map["CRIT-06"].current_evidence.lower()
        assert "national totals cannot be downscaled" in gate_map["CRIT-06"].blocking_reason.lower()
        assert "DISPLAY_AS_NATIONAL_MACRO_CONTEXT_ONLY" in stocks.handling_policy

    def test_procurement_snapshot_cannot_be_daily_supply(self, analytics_service):
        response = analytics_service.evaluate_eligibility_gates()
        procurement = next(s for s in response.stream_evaluations if s.dataset_id == "cfpp_punjab_wheat_procurement_2025_26")
        
        gate_map = {c.criteria_id: c for c in procurement.criteria_checks}
        assert gate_map["CRIT-02"].passed is False
        assert "Single date snapshot" in gate_map["CRIT-02"].current_evidence
        assert "single point in time cannot be interpolated" in gate_map["CRIT-02"].blocking_reason.lower()
        assert gate_map["CRIT-06"].passed is False  # State aggregate only, not district/mandi
        assert "DISPLAY_AS_ISOLATED_SNAPSHOT_ONLY" in procurement.handling_policy


class TestPhase6ReadinessMetrics:
    """Tests for explainable data completeness, freshness, and readiness."""

    def test_readiness_metrics_are_grounded_in_catalog(self, analytics_service):
        metrics = analytics_service.get_readiness_metrics()
        assert metrics.schema_validity_pct == 100.0
        assert metrics.geographic_coverage_pct == 100.0
        assert metrics.completeness_score_pct > 90.0
        assert "PRODUCE_ONLY_FOR_ARRIVALS" in metrics.commodity_coverage_state
        assert metrics.api_readiness_tested_count == 4
        assert metrics.api_blocked_count == 5


class TestPhase6SyntheticIsolation:
    """Tests ensuring synthetic demo data is strictly isolated and identified."""

    def test_synthetic_scenario_file_exists_in_synthetic_dir(self):
        root = Path(__file__).resolve().parent.parent
        synthetic_path = root / "data" / "synthetic" / "scenario_hypothetical_wheat_dip.json"
        assert synthetic_path.exists()
        
        with open(synthetic_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert data["is_synthetic"] is True
        assert data["evidence_level"] == "synthetic demo"
        assert "synthetic example" in data["synthetic_warning"].lower()
        assert len(data["time_series"]) == 14
        assert data["methodology"]["target_commodity"] == "Wheat (Common Foodgrain)"
        assert data["methodology"]["baseline_window_years"] == 3
        assert "strictly_forbidden_actions" in data["investigation_protocol"]
        assert any("hoarder" in act.lower() for act in data["investigation_protocol"]["strictly_forbidden_actions"])

    def test_synthetic_scenario_frontend_mirror_exists(self):
        root = Path(__file__).resolve().parent.parent
        frontend_mirror = root / "frontend" / "public" / "data" / "synthetic_scenario.json"
        assert frontend_mirror.exists()
        
        with open(frontend_mirror, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        assert data["is_synthetic"] is True
        assert data["evidence_level"] == "synthetic demo"
        assert len(data["time_series"]) == 14

    def test_synthetic_scenario_not_in_dataset_catalog(self):
        root = Path(__file__).resolve().parent.parent
        catalog_path = root / "data" / "manifests" / "dataset_catalog.json"
        assert catalog_path.exists()
        
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        
        # Ensure no synthetic dataset appears as production observed data
        for entry in catalog:
            assert entry.get("evidence_status") != "synthetic demo"
            assert "synthetic" not in entry.get("id", "").lower()


class TestPhase6ApiEndpoints:
    """Tests for FastAPI analytics endpoints."""

    def test_eligibility_gate_endpoint(self, client):
        res = client.get("/api/v1/analytics/eligibility-gate")
        assert res.status_code == 200
        data = res.json()
        assert "STRICTLY FORBIDDEN" in data["overall_hoarding_detection_eligibility"]
        assert len(data["stream_evaluations"]) == 4
        for stream in data["stream_evaluations"]:
            assert stream["eligibility_verdict"] == "INELIGIBLE (BLOCKED)"
            assert stream["eligible_for_grain_anomaly"] is False

    def test_readiness_metrics_endpoint(self, client):
        res = client.get("/api/v1/analytics/readiness-metrics")
        assert res.status_code == 200
        data = res.json()
        assert data["schema_validity_pct"] == 100.0
        assert data["geographic_coverage_pct"] == 100.0

    def test_synthetic_scenario_endpoint(self, client):
        res = client.get("/api/v1/analytics/synthetic-scenario")
        assert res.status_code == 200
        data = res.json()
        assert data["is_synthetic"] is True
        assert data["evidence_level"] == "synthetic demo"
        assert len(data["time_series"]) == 14


class TestPhase6AntiHoardingProhibition:
    """Verifies that no actor-level rankings, hoarding scores, or trader names exist."""

    def test_no_hoarding_score_or_trader_rankings_in_analytics(self, analytics_service):
        response = analytics_service.evaluate_eligibility_gates()
        serialized = response.model_dump_json()
        
        # Forbidden concepts:
        forbidden_phrases = [
            "hoarding detected",
            "hoarder ranking",
            "trader score",
            "trader ranking",
            "market hoarder",
            "hoarding probability",
        ]
        for phrase in forbidden_phrases:
            assert phrase not in serialized.lower()

    def test_frontend_templates_do_not_contain_hoarding_claims(self):
        root = Path(__file__).resolve().parent.parent
        dashboard_view_file = root / "frontend" / "src" / "components" / "DashboardView.tsx"
        assert dashboard_view_file.exists()
        
        content = dashboard_view_file.read_text(encoding="utf-8")
        
        # Verify prohibition statements and insufficient evidence disclaimers exist
        assert "INSUFFICIENT DATA TO ASSESS RISK" in content
        assert "Zero Wheat/Paddy" in content
        assert "100% Null Arrival Volumes" in content
        assert "AGENTS.md Rule 6" in content
        
        # Ensure no trader ranking table exists in frontend view
        assert "Trader Rank" not in content
        assert "Top Hoarders" not in content
        assert "Hoarding Detected" not in content

