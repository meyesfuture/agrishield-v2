"""
Pydantic schemas for data quality and validation summary representations.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class CriticalAssertionStatus(BaseModel):
    assertion_key: str
    description: str
    verified: bool
    details: str


class QualitySummaryResponse(BaseModel):
    overall_validation_gate: str
    report_generated_utc: str
    manifest_integrity: Dict[str, Any]
    critical_assertions: List[CriticalAssertionStatus]
    dataset_status_counts: Dict[str, int]
    quarantined_files: List[Dict[str, Any]]
