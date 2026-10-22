"""
FastAPI Routes for Transparent Analytics, Eligibility Gates, and Synthetic Scenarios.
Enforces Rule 6 of AGENTS.md and docs/ANALYTICS_AND_ALERTS.md.
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.schemas.analytics import EligibilityGateResponse, ReadinessMetrics
from backend.services.analytics_service import AnalyticsEligibilityService
from backend.config import get_settings

router = APIRouter(prefix="/api/v1/analytics", tags=["Transparent Analytics & Eligibility Gates"])
analytics_service = AnalyticsEligibilityService()
settings = get_settings()


@router.get(
    "/eligibility-gate",
    response_model=EligibilityGateResponse,
    summary="7-Point Statistical Anomaly Calculation Eligibility Gate",
    description="Evaluates all candidate supply streams against prerequisite criteria before any anomaly calculation."
)
def get_eligibility_gate_status():
    return analytics_service.evaluate_eligibility_gates()


@router.get(
    "/readiness-metrics",
    response_model=ReadinessMetrics,
    summary="Explainable Data Quality, Completeness & Freshness Metrics",
    description="Returns audited completeness, schema validity, geographic matching, and API readiness indicators."
)
def get_readiness_metrics():
    return analytics_service.get_readiness_metrics()


@router.get(
    "/synthetic-scenario",
    summary="Hypothetical Synthetic Demonstration Scenario",
    description="Returns isolated synthetic counterfactual wheat deficit scenario from data/synthetic/ with mandatory disclaimers."
)
def get_synthetic_scenario():
    scenario_path = settings.data_dir / "synthetic" / "scenario_hypothetical_wheat_dip.json"
    if not scenario_path.exists():
        raise HTTPException(status_code=404, detail="Synthetic scenario file not found in data/synthetic/")
    
    with open(scenario_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Invariant assertion: must have is_synthetic = True
    if not data.get("is_synthetic"):
        raise HTTPException(status_code=500, detail="Data safety error: Scenario is not flagged as synthetic.")
        
    return data
