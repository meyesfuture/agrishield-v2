"""
District crop production API route handler.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...schemas.production import ProductionListResponse
from ...services.data_service import data_service

router = APIRouter(prefix="/api/v1/production", tags=["Production & Yield"])


@router.get("", response_model=ProductionListResponse, summary="Query district annual crop production and area")
def get_production(
    district: Optional[str] = Query(default=None, description="Filter by district name (case-insensitive)"),
    crop: Optional[str] = Query(default=None, description="Filter by standardized crop name (wheat, rice)"),
    agricultural_year: Optional[str] = Query(default=None, description="Filter by agricultural year YYYY-YY (e.g. 2018-19)"),
    limit: int = Query(default=50, ge=1, le=500, description="Page limit (1-500)"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
):
    """
    Returns verified annual district-level cultivated area (hectares), production (tonnes),
    and derived yield (kg/ha) from DES APY extracts.
    
    6 historical cells with missing values for Fazilka, Pathankot, and SAS Nagar are
    preserved as null, never converted to 0.
    """
    try:
        return data_service.query_production(
            district=district,
            crop=crop,
            agricultural_year=agricultural_year,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query production dataset: {str(e)}")
