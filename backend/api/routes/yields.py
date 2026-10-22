"""
District crop yields historical time series route handler.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...schemas.yields import YieldListResponse
from ...services.data_service import data_service

router = APIRouter(prefix="/api/v1/yields", tags=["Production & Yield"])


@router.get("", response_model=YieldListResponse, summary="Query district crop yield historical series")
def get_yields(
    district: Optional[str] = Query(default=None, description="Filter by district name (case-insensitive)"),
    crop: Optional[str] = Query(default=None, description="Filter by standardized crop name (wheat, rice)"),
    year_from: Optional[str] = Query(default=None, description="Earliest effective year (e.g. 2010)"),
    year_to: Optional[str] = Query(default=None, description="Latest effective year (e.g. 2022)"),
    limit: int = Query(default=50, ge=1, le=5000, description="Page limit (1-5000)"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
):
    """
    Returns empirical crop yield observations (kg/ha) across Punjab districts,
    combining OGD Punjab long-term records (1968-2022) and DES APY derived yields.
    """
    try:
        return data_service.query_yields(
            district=district,
            crop=crop,
            year_from=year_from,
            year_to=year_to,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query yields dataset: {str(e)}")
