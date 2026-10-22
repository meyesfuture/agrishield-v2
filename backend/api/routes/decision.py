"""
FastAPI Routes for the Punjab GrainWatch Decision Engine & Synthetic Demonstration Lab.
Provides endpoints for running real and synthetic assessments, listing scenarios, and inspecting methodology.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from backend.schemas.decision import (
    ScenarioSummary,
    ScenarioDetail,
    DecisionAssessmentResponse,
    ScenarioRunRequest,
    AssessRequest,
    MethodologyConfig,
    EvidenceMode,
)
from backend.services.synthetic_generator import SyntheticScenarioGenerator
from backend.services.decision_engine import DecisionEngineService

router = APIRouter(prefix="/api/v1/decision", tags=["Decision Engine & Anomaly Detection"])

synthetic_generator = SyntheticScenarioGenerator()
decision_engine = DecisionEngineService()


@router.get(
    "/scenarios",
    response_model=List[ScenarioSummary],
    summary="List Synthetic Demonstration Scenarios",
    description="Returns metadata summaries for all isolated synthetic scenarios (Scenarios A through E).",
)
def list_scenarios():
    return synthetic_generator.get_scenario_summaries()


@router.get(
    "/scenarios/{scenario_id}",
    response_model=ScenarioDetail,
    summary="Get Scenario Details & Time Series",
    description="Returns full observation points and metadata for a specific synthetic demonstration scenario.",
)
def get_scenario_detail(scenario_id: str):
    scenarios = synthetic_generator.get_all_scenarios()
    if scenario_id not in scenarios:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return scenarios[scenario_id]


@router.post(
    "/scenarios/{scenario_id}/run",
    response_model=DecisionAssessmentResponse,
    summary="Execute Decision Engine on a Synthetic Scenario",
    description="Calculates deviations and evaluates anomaly convergence for a synthetic scenario through the decision engine.",
)
def run_scenario(scenario_id: str):
    scenarios = synthetic_generator.get_all_scenarios()
    if scenario_id not in scenarios:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")

    scenario = scenarios[scenario_id]
    return decision_engine.assess_series(
        observations=scenario.observations,
        location_id=scenario_id,
        location_name=scenario.location_name,
        commodity_name=scenario.commodity_name,
        evidence_mode=EvidenceMode.SYNTHETIC_DEMO,
        scenario_id=scenario_id,
        geographic_granularity="mandi",
    )


@router.post(
    "/assess",
    response_model=DecisionAssessmentResponse,
    summary="Run Decision Engine Assessment",
    description="Evaluates custom observation points or real district evidence under Rule 6 governance.",
)
def assess_location(request: AssessRequest):
    if request.evidence_mode == EvidenceMode.REAL:
        return decision_engine.assess_real_location(
            district_name=request.location_name,
            commodity_name=request.commodity_name,
        )

    if not request.observations:
        raise HTTPException(
            status_code=400,
            detail="Custom observations required when evidence_mode is SYNTHETIC_DEMO.",
        )

    return decision_engine.assess_series(
        observations=request.observations,
        location_name=request.location_name,
        commodity_name=request.commodity_name,
        evidence_mode=request.evidence_mode,
    )


@router.get(
    "/methodology",
    response_model=MethodologyConfig,
    summary="Get Decision Engine Methodology & Parameters",
    description="Returns statistical thresholds, baseline observation requirements, and governance rules.",
)
def get_methodology():
    return decision_engine.get_methodology_config()
