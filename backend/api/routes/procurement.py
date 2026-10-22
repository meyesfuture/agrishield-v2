"""
Government grain procurement snapshot route handler.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...schemas.procurement import ProcurementResponse
from ...services.data_service import data_service

router = APIRouter(prefix="/api/v1/procurement", tags=["Procurement & Stocks"])


@router.get("", response_model=ProcurementResponse, summary="Get state foodgrain procurement snapshot")
def get_procurement(
    commodity: Optional[str] = Query(default=None, description="Filter by commodity (e.g. Wheat)"),
    measure_name: Optional[str] = Query(default=None, description="Filter by measure (season_estimate, daily_procurement, progressive_procurement)"),
):
    """
    Returns state-level wheat procurement position report from CFPP (position date 2025-05-15).
    
    CRITICAL DOMAIN INVARIANTS:
    - cannot_be_summed: true. The measures represent an annual target (LMT), a single-day intake (MT),
      and a cumulative season intake (MT). Summing them creates massive double-counting.
    - is_time_series: false. This is a single position report, not a continuous daily time series.
    """
    try:
        return data_service.query_procurement(
            commodity=commodity,
            measure_name=measure_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query procurement dataset: {str(e)}")
