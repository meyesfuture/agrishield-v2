"""
Central Pool foodgrain stock observations route handler.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...schemas.stocks import StockResponse
from ...services.data_service import data_service

router = APIRouter(prefix="/api/v1/stocks", tags=["Procurement & Stocks"])


@router.get("", response_model=StockResponse, summary="Query Central Pool foodgrain stock observations")
def get_stocks(
    commodity: Optional[str] = Query(default=None, description="Filter by commodity (wheat, rice)"),
    measure_name: Optional[str] = Query(default=None, description="Filter by measure (actual_central_pool_stock, foodgrain_stocking_norm)"),
    observation_type: Optional[str] = Query(default=None, description="Filter by type (stock_level, norm_not_observed_stock)"),
    limit: int = Query(default=50, ge=1, le=500, description="Page limit (1-500)"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
):
    """
    Returns verified Central Pool foodgrain stock observations and stocking norms from DFPD/FCI.
    
    CRITICAL DOMAIN INVARIANT:
    Geographic coverage is strictly National Central Pool (all 100 records).
    State is null (100%). These figures must NEVER be labeled or inferred as Punjab state or district stocks.
    """
    try:
        return data_service.query_stocks(
            commodity=commodity,
            measure_name=measure_name,
            observation_type=observation_type,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query stock observations: {str(e)}")
