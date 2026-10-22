"""
Grain Supply Flow Coverage Matrix route handler.
"""

from fastapi import APIRouter, HTTPException
from ...schemas.coverage import CoverageMatrixResponse
from ...services.data_service import data_service

router = APIRouter(prefix="/api/v1/coverage", tags=["Supply Chain Coverage"])


@router.get("", response_model=CoverageMatrixResponse, summary="Get 8-element Grain Supply Flow Coverage Matrix")
def get_coverage_matrix():
    """
    Returns the comprehensive 8-element Grain Supply Flow Coverage Matrix,
    documenting empirical coverage, critical data gaps, and the overall reconciliation verdict.
    
    VERDICT: NO-GO for grain supply reconciliation or hoarding detection.
    """
    try:
        return data_service.get_coverage_matrix()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load coverage matrix: {str(e)}")
