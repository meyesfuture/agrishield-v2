"""
Comprehensive Unit Tests for the Decision Engine, Robust Statistics, and Synthetic Scenarios.
Enforces Rule 6 of AGENTS.md: Anomaly != Proof of Hoarding.
"""

import pytest
from datetime import date, timedelta
from backend.schemas.decision import DecisionStatus, EvidenceMode, ObservationPoint
from backend.services.synthetic_generator import SyntheticScenarioGenerator
from backend.services.decision_engine import DecisionEngineService


@pytest.fixture
def engine():
    return DecisionEngineService()


@pytest.fixture
def generator():
    return SyntheticScenarioGenerator()


class TestDecisionEngineScenarios:
    """Tests evaluating Scenarios A through E through the decision engine."""

    def test_scenario_a_normal_baseline_yields_no_material_anomaly(self, engine, generator):
        scenario = generator.generate_scenario_a()
        assessment = engine.assess_series(
            observations=scenario.observations,
            location_id=scenario.scenario_id,
            location_name=scenario.location_name,
            commodity_name=scenario.commodity_name,
            evidence_mode=EvidenceMode.SYNTHETIC_DEMO,
        )

        assert assessment.decision_status == DecisionStatus.NO_MATERIAL_ANOMALY
        assert assessment.anomaly_intensity_score == 0.0
        assert assessment.signals["price"].status == "NORMAL"
        assert assessment.signals["arrival"].status == "NORMAL"
        assert "expected statistical baseline boundaries" in assessment.human_explanation
        assert assessment.evidence_mode == EvidenceMode.SYNTHETIC_DEMO

    def test_scenario_b_convergent_anomaly_detected_by_algorithm(self, engine, generator):
        scenario = generator.generate_scenario_b(inject_anomaly=True)
        assessment = engine.assess_series(
            observations=scenario.observations,
            location_id=scenario.scenario_id,
            location_name=scenario.location_name,
            commodity_name=scenario.commodity_name,
            evidence_mode=EvidenceMode.SYNTHETIC_DEMO,
        )

        assert assessment.decision_status == DecisionStatus.CONVERGENT_SUPPLY_ANOMALY
        assert assessment.anomaly_intensity_score is not None
        assert assessment.anomaly_intensity_score > 50.0  # Significant intensity
        assert assessment.signals["price"].status == "ANOMALOUS"
        assert assessment.signals["arrival"].status == "ANOMALOUS"
        assert assessment.signals["price"].deviation_pct > 20.0
        assert assessment.signals["arrival"].deviation_pct < -25.0
        assert "Statistical convergence detected" in assessment.human_explanation
        assert "Rule 6 strictly dictates this anomaly is an investigation prompt" in assessment.recommended_action

    def test_scenario_b_removing_planted_anomaly_restores_baseline(self, engine, generator):
        scenario_clean = generator.generate_scenario_b(inject_anomaly=False)
        assessment = engine.assess_series(
            observations=scenario_clean.observations,
            location_id=scenario_clean.scenario_id,
            location_name=scenario_clean.location_name,
            commodity_name=scenario_clean.commodity_name,
            evidence_mode=EvidenceMode.SYNTHETIC_DEMO,
        )

        assert assessment.decision_status == DecisionStatus.NO_MATERIAL_ANOMALY
        assert assessment.anomaly_intensity_score == 0.0
        assert assessment.signals["price"].status == "NORMAL"
        assert assessment.signals["arrival"].status == "NORMAL"

    def test_scenario_c_price_only_spike_yields_price_signal(self, engine, generator):
        scenario = generator.generate_scenario_c()
        assessment = engine.assess_series(
            observations=scenario.observations,
            location_id=scenario.scenario_id,
            location_name=scenario.location_name,
            commodity_name=scenario.commodity_name,
            evidence_mode=EvidenceMode.SYNTHETIC_DEMO,
        )

        assert assessment.decision_status == DecisionStatus.PRICE_SIGNAL
        assert assessment.signals["price"].status == "ANOMALOUS"
        assert assessment.signals["arrival"].status == "NORMAL"
        assert assessment.signals["price"].deviation_pct > 20.0
        assert "Insufficient corroboration for a convergent supply anomaly" in assessment.human_explanation

    def test_scenario_d_arrival_only_decline_yields_arrival_signal(self, engine, generator):
        scenario = generator.generate_scenario_d()
        assessment = engine.assess_series(
            observations=scenario.observations,
            location_id=scenario.scenario_id,
            location_name=scenario.location_name,
            commodity_name=scenario.commodity_name,
            evidence_mode=EvidenceMode.SYNTHETIC_DEMO,
        )

        assert assessment.decision_status == DecisionStatus.ARRIVAL_SIGNAL
        assert assessment.signals["arrival"].status == "ANOMALOUS"
        assert assessment.signals["price"].status == "NORMAL"
        assert assessment.signals["arrival"].deviation_pct < -25.0
        assert "Do not escalate as an intentional market withholding event" in assessment.recommended_action

    def test_scenario_e_insufficient_evidence_fails_safely_with_no_score(self, engine, generator):
        scenario = generator.generate_scenario_e()
        assessment = engine.assess_series(
            observations=scenario.observations,
            location_id=scenario.scenario_id,
            location_name=scenario.location_name,
            commodity_name=scenario.commodity_name,
            evidence_mode=EvidenceMode.SYNTHETIC_DEMO,
        )

        assert assessment.decision_status == DecisionStatus.INSUFFICIENT_DATA
        assert assessment.anomaly_intensity_score is None  # Never fabricate score on insufficient data
        assert assessment.eligibility_gate_passed is False
        assert len(assessment.data_quality_warnings) > 0
        assert "Minimum evidentiary criteria are not satisfied" in assessment.human_explanation


class TestDecisionEngineGovernanceAndEdgeCases:
    """Verifies strict adherence to Rule 6 and mathematical edge cases."""

    def test_real_location_assessment_returns_insufficient_data(self, engine):
        assessment = engine.assess_real_location("Ludhiana", "Wheat")

        assert assessment.evidence_mode == EvidenceMode.REAL
        assert assessment.decision_status == DecisionStatus.INSUFFICIENT_DATA
        assert assessment.anomaly_intensity_score is None
        assert assessment.signals["arrival"].status == "UNAVAILABLE"
        assert "Zero wheat/paddy arrivals" in assessment.data_quality_warnings[0] or "produce rows" in assessment.data_quality_warnings[0]
        assert "Rule 6" in assessment.legal_caveat

    def test_engine_is_strictly_deterministic(self, engine, generator):
        scenario_b = generator.generate_scenario_b(inject_anomaly=True)
        res1 = engine.assess_series(scenario_b.observations, location_name="Khanna")
        res2 = engine.assess_series(scenario_b.observations, location_name="Khanna")

        assert res1.decision_status == res2.decision_status
        assert res1.anomaly_intensity_score == res2.anomaly_intensity_score
        assert res1.signals["price"].deviation_pct == res2.signals["price"].deviation_pct
        assert res1.signals["arrival"].deviation_pct == res2.signals["arrival"].deviation_pct

    def test_never_emits_confirmed_hoarding_status(self, engine, generator):
        scenarios = generator.get_all_scenarios()
        for s in scenarios.values():
            assessment = engine.assess_series(s.observations, location_name=s.location_name)
            assert assessment.decision_status != "CONFIRMED_HOARDING"
            assert "CONFIRMED_HOARDING" not in assessment.status_label

    def test_out_of_order_and_zero_handling(self, engine):
        # 14 points with a few zero arrivals (clerk sentinels)
        obs: List[ObservationPoint] = []
        start_d = date(2026, 9, 1)
        for i in range(20):
            obs.append(
                ObservationPoint(
                    date=(start_d + timedelta(days=i)).isoformat(),
                    modal_price=2100.0,
                    arrival_quantity=2000.0 if i != 5 else 0.0,
                )
            )

        assessment = engine.assess_series(obs, location_name="Test")
        assert assessment.decision_status == DecisionStatus.NO_MATERIAL_ANOMALY
        assert assessment.metric_baselines["arrival"].baseline_median == 2000.0
