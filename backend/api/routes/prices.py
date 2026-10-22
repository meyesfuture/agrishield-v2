"""
Mandi wholesale market prices route handler.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...schemas.prices import PriceListResponse
from ...services.data_service import data_service

router = APIRouter(prefix="/api/v1/markets/prices", tags=["Markets & Prices"])


@router.get("", response_model=PriceListResponse, summary="Query daily wholesale mandi market prices")
def get_prices(
    market_name: Optional[str] = Query(default=None, description="Filter by market name (e.g. Abohar)"),
    commodity: Optional[str] = Query(default=None, description="Filter by commodity name (e.g. Paddy)"),
    date_from: Optional[str] = Query(default=None, description="Earliest observation date YYYY-MM-DD"),
    date_to: Optional[str] = Query(default=None, description="Latest observation date YYYY-MM-DD"),
    limit: int = Query(default=50, ge=1, le=500, description="Page limit (1-500)"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
):
    """
    Returns verified daily wholesale market prices from AGMARKNET 2.0.
    
    CRITICAL DOMAIN INVARIANT:
    Arrival quantity is not exposed by this endpoint (100% null across all records).
    The arrival_quantity field is preserved as null, never converted to 0.0.
    """
    try:
        return data_service.query_prices(
            market_name=market_name,
            commodity=commodity,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query market prices: {str(e)}")
