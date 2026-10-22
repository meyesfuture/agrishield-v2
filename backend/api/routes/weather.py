"""
Multi-zone daily weather route handler.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...schemas.weather import WeatherListResponse
from ...services.data_service import data_service

router = APIRouter(prefix="/api/v1/weather", tags=["Agrometeorology"])


@router.get("", response_model=WeatherListResponse, summary="Query daily agro-climatic weather observations")
def get_weather(
    station_name: Optional[str] = Query(default=None, description="Filter by station (e.g. Ludhiana, Bathinda, Amritsar)"),
    date_from: Optional[str] = Query(default=None, description="Earliest observation date YYYY-MM-DD"),
    date_to: Optional[str] = Query(default=None, description="Latest observation date YYYY-MM-DD"),
    limit: int = Query(default=50, ge=1, le=500, description="Page limit (1-500)"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
):
    """
    Returns empirical daily weather parameters (temperature, precipitation, relative humidity)
    across Punjab's 5 agro-climatic zones sourced from NASA POWER MERRA-2.
    """
    try:
        return data_service.query_weather(
            station_name=station_name,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query weather observations: {str(e)}")
