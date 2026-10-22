"""
Pydantic schemas for health and system status endpoints.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ComponentCheck(BaseModel):
    name: str
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str = Field(..., description="'healthy', 'degraded', or 'unhealthy'")
    version: str
    timestamp_utc: str
    checks: Dict[str, bool]
    notes: List[str] = Field(default_factory=list)


class EvidenceGuardrail(BaseModel):
    guardrail: str
    finding: str
    status: str


class StatusResponse(BaseModel):
    project_name: str
    version: str
    timestamp_utc: str
    overall_data_gate: str
    total_datasets_cataloged: int
    evidence_guardrails: List[EvidenceGuardrail]
    manifest_verification: Dict[str, Any]
