"""
Pydantic schemas for data quality, critical assertions, and audit issues.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .common import PaginatedResponse


class CriticalAssertionStatus(BaseModel):
    assertion_key: str = Field(..., description="Unique assertion identifier")
    description: str = Field(..., description="Description of rule being verified")
    verified: bool = Field(..., description="Whether assertion holds strictly true")
    details: str = Field(..., description="Audit evidence or verification details")


class QualitySummaryResponse(BaseModel):
    """Aggregate summary of data validation pipeline gate."""
    overall_validation_gate: str = Field(..., description="Overall gate status (PASSED/FAILED)")
    report_generated_utc: str = Field(..., description="Timestamp of quality report generation")
    manifest_integrity: Dict[str, Any] = Field(..., description="Manifest checksum verification counts")
    critical_assertions: List[CriticalAssertionStatus] = Field(..., description="Core empirical assertions")
    dataset_status_counts: Dict[str, int] = Field(..., description="Counts of datasets by evidence status")
    quarantined_files: List[Dict[str, Any]] = Field(..., description="Files excluded from ingestion due to errors")


class QualityIssueItem(BaseModel):
    """Granular data quality issue or audit limitation."""
    issue_id: str = Field(..., description="Unique issue code")
    dataset_id: str = Field(..., description="Dataset or source affected")
    rule_name: str = Field(..., description="Name of validation rule")
    severity: str = Field(..., description="Severity level: CRITICAL, WARNING, INFO")
    description: str = Field(..., description="Specific finding details")
    affected_count: int = Field(..., description="Number of affected records/cells")
    resolution_or_handling: str = Field(..., description="How the application handles this condition")


class QualityIssuesResponse(PaginatedResponse[QualityIssueItem]):
    """Paginated list of data quality issues with severity breakdown."""
    severity_breakdown: Dict[str, int] = Field(..., description="Counts of issues by severity")
