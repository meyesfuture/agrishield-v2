"""
Data quality, audit assertions, and validation issues API routes.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...schemas.quality import QualitySummaryResponse, QualityIssuesResponse
from ...services.quality_service import quality_service
from ...services.data_service import data_service

router = APIRouter(prefix="/api/v1/quality", tags=["Data Quality & Integrity"])


@router.get("/summary", response_model=QualitySummaryResponse, summary="Get data quality and audit summary")
def get_quality_summary(reload: bool = Query(False, description="Force re-reading quality report from disk")):
    """Retrieve full audit report summary including critical assertions and manifest integrity."""
    summary = quality_service.get_summary(force_reload=reload)
    if not summary:
        raise HTTPException(
            status_code=503,
            detail="Quality report not found or unreadable. Run 'python scripts/run_validation_pipeline.py' to generate it."
        )
    return summary


@router.get("/issues", response_model=QualityIssuesResponse, summary="List verified data quality issues and audit caveats")
def get_quality_issues(
    severity: Optional[str] = Query(default=None, description="Filter by severity (CRITICAL, WARNING, INFO)"),
    dataset_id: Optional[str] = Query(default=None, description="Filter by affected dataset identifier"),
    limit: int = Query(default=50, ge=1, le=500, description="Page limit (1-500)"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
):
    """
    Returns specific empirical data quality issues (e.g. foodgrain absence in Mandi Board,
    null arrival quantities in Agmarknet, national scope of Central Pool stocks) and their resolutions.
    """
    try:
        return data_service.query_quality_issues(
            severity=severity,
            dataset_id=dataset_id,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query quality issues: {str(e)}")
