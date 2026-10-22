"""
Domain schema for district crop yield history in Punjab.
Sources: Open Government Data (OGD Punjab) and DES APY.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .common import PaginatedResponse


class DistrictYieldItem(BaseModel):
    """Historical district crop yield observation."""
    source_id: str = Field(..., description="Source dataset identifier")
    state: str = Field(..., description="State name (Punjab)")
    district_original: str = Field(..., description="District name as registered in source")
    district_id: Optional[str] = Field(default=None, description="Standard district ID if established")
    district_id_candidate: Optional[str] = Field(default=None, description="Candidate LGD district ID")
    crop_original: str = Field(..., description="Original crop name from source")
    crop_standard: str = Field(..., description="Canonical standardized crop name (wheat, rice)")
    season: Optional[str] = Field(default=None, description="Agricultural season (Rabi, Kharif)")
    agricultural_year: Optional[str] = Field(default=None, description="Agricultural year format YYYY-YY")
    source_year_label: Optional[str] = Field(default=None, description="Source year label (e.g. 2022)")
    effective_year: str = Field(..., description="Normalized effective year for query and sorting")
    yield_value: float = Field(..., description="Crop yield value in kg/ha")
    yield_unit: str = Field(..., description="Unit of yield measurement (kg/ha)")
    observation_status: str = Field(..., description="Empirical observation status")
    source_url: Optional[str] = Field(default=None, description="Source provenance URL")
    source_file: Optional[str] = Field(default=None, description="Relative path of source file")
    quality_note: Optional[str] = Field(default=None, description="Data quality or caveats note")


class YieldListResponse(PaginatedResponse[DistrictYieldItem]):
    """Paginated list of district crop yield records."""
    pass
