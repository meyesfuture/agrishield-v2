"""
Domain schema for district crop production and area in Punjab.
Source: Directorate of Economics & Statistics (DES APY).
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .common import PaginatedResponse


class DistrictProductionItem(BaseModel):
    """District-level annual crop production, cultivated area, and derived yield."""
    source_id: str = Field(..., description="Source dataset identifier")
    state: str = Field(..., description="State name (Punjab)")
    district_original: str = Field(..., description="Original district name as registered in source")
    district_id: Optional[str] = Field(default=None, description="Standard district ID if established")
    district_id_candidate: Optional[str] = Field(default=None, description="Candidate LGD district ID")
    district_mapping_status: Optional[str] = Field(default=None, description="Mapping verification status")
    crop_original: str = Field(..., description="Original crop name from source")
    crop_standard: str = Field(..., description="Canonical standardized crop name (wheat, rice)")
    season: str = Field(..., description="Agricultural season (Rabi, Kharif)")
    agricultural_year: str = Field(..., description="Agricultural year format YYYY-YY (e.g. 2018-19)")
    calendar_year: Optional[str] = Field(default=None, description="Calendar year (strictly null in DES source)")
    area_value: Optional[float] = Field(default=None, description="Cultivated area in hectares")
    area_unit: Optional[str] = Field(default=None, description="Unit of area measurement (hectares)")
    production_value: Optional[float] = Field(default=None, description="Crop production in tonnes")
    production_unit: Optional[str] = Field(default=None, description="Unit of production measurement (tonnes)")
    yield_value: Optional[float] = Field(default=None, description="Derived crop yield in kg/ha")
    yield_unit: Optional[str] = Field(default=None, description="Unit of yield measurement (kg/ha)")
    observation_status: str = Field(..., description="Empirical observation status")
    source_url: Optional[str] = Field(default=None, description="Source provenance URL")
    source_file: Optional[str] = Field(default=None, description="Relative path of source file")
    quality_note: Optional[str] = Field(default=None, description="Data quality or caveats note")


class ProductionListResponse(PaginatedResponse[DistrictProductionItem]):
    """Paginated list of district crop production records."""
    pass
