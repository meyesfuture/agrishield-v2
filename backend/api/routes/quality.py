"""
Data quality and validation summary API routes for Punjab GrainWatch Backend.
"""

from fastapi import APIRouter, HTTPException, Query
from ...schemas.quality import QualitySummaryResponse
from ...services.quality_service import quality_service

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
