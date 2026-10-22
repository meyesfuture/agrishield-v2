"""
Domain schemas for Transparent Analytics and Anomaly Screening Eligibility Gates.
Enforces AGENTS.md Rule 6, PRD §7, and docs/ANALYTICS_AND_ALERTS.md.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class EligibilityCheckItem(BaseModel):
    criteria_id: str = Field(..., description="Unique criterion code (e.g. CRIT-01)")
    criteria_name: str = Field(..., description="Name of the eligibility requirement")
    required_standard: str = Field(..., description="Minimum evidentiary bar required for calculation")
    current_evidence: str = Field(..., description="Observed status in currently acquired datasets")
    passed: bool = Field(..., description="Whether this criterion passed")
    blocking_reason: Optional[str] = Field(None, description="Detailed explanation if blocked")


class DatasetEligibilityResult(BaseModel):
    dataset_id: str
    stream_name: str
    commodity: str
    temporal_granularity: str
    eligible_for_grain_anomaly: bool = Field(False, description="Strictly false if any criterion fails")
    eligibility_verdict: str = Field(..., description="INELIGIBLE (BLOCKED) or ELIGIBLE")
    passed_criteria_count: int
    failed_criteria_count: int
    criteria_checks: List[EligibilityCheckItem]
    missing_prerequisites: List[str]
    handling_policy: str


class ReadinessMetrics(BaseModel):
    completeness_score_pct: float = Field(..., description="Average non-null cell percentage across valid schema")
    freshness_status: str = Field(..., description="Temporal coverage status of acquired assets")
    schema_validity_pct: float = Field(..., description="Conformance to canonical data dictionary")
    geographic_coverage_pct: float = Field(..., description="Punjab 23-district spatial matching rate")
    commodity_coverage_state: str = Field(..., description="Foodgrain vs produce availability state")
    api_readiness_tested_count: int = Field(..., description="Working tested public feeds")
    api_blocked_count: int = Field(..., description="Feeds blocked by CAPTCHA, token, or CA trust")


class EligibilityGateResponse(BaseModel):
    overall_analytics_eligibility: str = Field(
        "BLOCKED - Insufficient Evidence for Grain Anomaly Screening",
        description="Global verdict on grain supply anomaly calculation"
    )
    overall_hoarding_detection_eligibility: str = Field(
        "STRICTLY FORBIDDEN (Rule 6: Anomaly != Hoarding; Missing Denominator & Controls)",
        description="Absolute prohibition on hoarding conclusions"
    )
    audit_timestamp_utc: str
    total_streams_evaluated: int
    eligible_streams_count: int
    readiness_metrics: ReadinessMetrics
    stream_evaluations: List[DatasetEligibilityResult]
    mandatory_governance_rules: List[str]
