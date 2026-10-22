"""
Domain schema for multi-zone daily agrometeorological observations in Punjab.
Source: NASA POWER MERRA-2.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .common import PaginatedResponse


class WeatherObservationItem(BaseModel):
    """Daily weather observation across Punjab agro-climatic zones."""
    observation_date: str = Field(..., description="Observation date (YYYY-MM-DD)")
    state: str = Field(..., description="State name (Punjab)")
    station_name: str = Field(..., description="Weather station / location name")
    agro_climatic_zone: str = Field(..., description="Agro-climatic zone in Punjab")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    temperature_mean_c: float = Field(..., description="Mean daily 2m temperature (°C)")
    precipitation_mm_day: float = Field(..., description="Daily precipitation (mm/day)")
    relative_humidity_pct: float = Field(..., description="Mean 2m relative humidity (%)")
    source_dataset: str = Field(..., description="NASA POWER product and collection name")
    source_url: str = Field(..., description="API request endpoint with coordinates and parameters")
    retrieval_date_utc: str = Field(..., description="Timestamp of data acquisition")


class WeatherListResponse(PaginatedResponse[WeatherObservationItem]):
    """Paginated list of daily agrometeorological observations."""
    pass
