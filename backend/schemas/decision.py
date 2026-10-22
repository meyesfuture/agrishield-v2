"""
Typed Domain Schemas for the Punjab GrainWatch Decision Engine & Anomaly Detection Pipeline.
Strictly enforces Rule 6 of AGENTS.md: Anomaly != Proof of Hoarding.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class EvidenceMode(str, Enum):
    REAL = "REAL"
    SYNTHETIC_DEMO = "SYNTHETIC_DEMO"


class DecisionStatus(str, Enum):
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    NO_MATERIAL_ANOMALY = "NO_MATERIAL_ANOMALY"
    PRICE_SIGNAL = "PRICE_SIGNAL"
    ARRIVAL_SIGNAL = "ARRIVAL_SIGNAL"
    CONVERGENT_SUPPLY_ANOMALY = "CONVERGENT_SUPPLY_ANOMALY"


class SignalAssessment(BaseModel):
    """Evaluation of an individual analytical supply signal."""
    signal_type: str = Field(..., description="Signal identifier: price, arrival, weather, production")
    status: str = Field(..., description="Status: ANOMALOUS, NORMAL, INSUFFICIENT, UNAVAILABLE")
    observed_value: Optional[float] = Field(None, description="Current or latest observed metric value")
    baseline_median: Optional[float] = Field(None, description="Historical baseline median value")
    deviation_pct: Optional[float] = Field(None, description="Percentage deviation from baseline median")
    robust_z_score: Optional[float] = Field(None, description="Normalized deviation using Median Absolute Deviation (MAD)")
    unit: str = Field(..., description="Measurement unit (e.g. Rs./Quintal, Quintals, kg/ha)")
    contribution_pct: float = Field(0.0, description="Percentage contribution to the anomaly intensity score")
    explanation: str = Field(..., description="Human-readable explanation of the signal calculation and outcome")


class MetricBaseline(BaseModel):
    """Historical baseline statistical parameters for a metric."""
    metric_name: str
    baseline_median: Optional[float] = None
    baseline_mad: Optional[float] = None
    baseline_observation_count: int
    baseline_window: str
    unit: str


class DecisionAssessmentResponse(BaseModel):
    """Structured, typed output of the Punjab GrainWatch Decision Engine."""
    assessment_id: str
    assessment_timestamp_utc: str
    evidence_mode: EvidenceMode
    scenario_id: Optional[str] = None
    location_id: str
    location_name: str
    geographic_granularity: str = "district"
    canonical_commodity: str
    observation_date: str
    baseline_interval: str
    decision_status: DecisionStatus
    status_label: str
    human_explanation: str
    anomaly_intensity_score: Optional[float] = None
    signals: Dict[str, SignalAssessment]
    metric_baselines: Dict[str, MetricBaseline]
    evidence_coverage: Dict[str, Any]
    unavailable_signals: List[str]
    data_quality_warnings: List[str]
    eligibility_gate_passed: bool
    methodology_version: str = "v2.1.0-robust-mad"
    threshold_config_version: str = "v2.1.0-config"
    recommended_action: str
    legal_caveat: str = (
        "Under AGENTS.md Rule 6, a statistical anomaly is an investigative screening prompt only. "
        "It does NOT establish criminal intent, concealment, or the fact of hoarding."
    )


class ObservationPoint(BaseModel):
    """Single daily market observation for analysis or scenario simulation."""
    date: str
    modal_price: Optional[float] = None
    arrival_quantity: Optional[float] = None
    unit_price: str = "Rs./Quintal"
    unit_arrival: str = "Quintals"
    is_anomaly_candidate: bool = False
    notes: Optional[str] = None


class ScenarioSummary(BaseModel):
    """Summary metadata for an isolated synthetic demonstration scenario."""
    scenario_id: str
    title: str
    description: str
    expected_decision_status: DecisionStatus
    location_name: str
    commodity_name: str
    total_observation_days: int
    is_synthetic: bool = True
    data_mode: str = "SYNTHETIC_DEMO"


class ScenarioDetail(BaseModel):
    """Full detail of a synthetic demonstration scenario including time-series points."""
    scenario_id: str
    title: str
    description: str
    expected_decision_status: DecisionStatus
    location_name: str
    commodity_name: str
    unit_price: str = "Rs./Quintal"
    unit_arrival: str = "Quintals"
    baseline_window: str
    anomaly_window: Optional[str] = None
    is_synthetic: bool = True
    data_mode: str = "SYNTHETIC_DEMO"
    synthetic_watermark: str = "SYNTHETIC DEMO — NOT LIVE MARKET EVIDENCE"
    observations: List[ObservationPoint]


class ScenarioRunRequest(BaseModel):
    """Parameters for executing a synthetic scenario through the decision engine."""
    scenario_id: str
    target_date: Optional[str] = None


class AssessRequest(BaseModel):
    """Request payload for running assessment on custom observations or real location."""
    evidence_mode: EvidenceMode = EvidenceMode.REAL
    location_name: str
    commodity_name: str = "Wheat"
    observations: Optional[List[ObservationPoint]] = None


class MethodologyConfig(BaseModel):
    """Current versioned parameters and thresholds for the Decision Engine."""
    methodology_name: str
    methodology_version: str
    minimum_baseline_observations: int
    price_deviation_threshold_pct: float
    arrival_deviation_threshold_pct: float
    robust_mad_multiplier: float
    decision_rules: List[str]
    governance_invariants: List[str]
