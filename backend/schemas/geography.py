"""
Domain schema for Punjab district boundaries and administrative crosswalks.
Sources: Survey of India / NWIC / GSI (boundaries) and Local Government Directory (LGD).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .common import PaginatedResponse


class DistrictCrosswalkItem(BaseModel):
    """Mapping between agricultural statistical reporting names and geospatial boundaries."""
    district_source_name_apy: str = Field(..., description="District name as reported in DES APY tables")
    district_name_boundary: str = Field(..., description="District name as represented in boundary GeoJSON")
    district_id_candidate_lgd: Optional[int] = Field(default=None, description="Candidate LGD district code")
    match_status: str = Field(..., description="Crosswalk match status")
    temporal_note: str = Field(..., description="Temporal boundary caveats (e.g. Malerkotla 2022 split)")


class DistrictCrosswalkResponse(PaginatedResponse[DistrictCrosswalkItem]):
    """Paginated list of district crosswalk mappings."""
    pass


class DistrictBoundaryFeature(BaseModel):
    """GeoJSON Feature representing a district boundary."""
    type: str = Field(default="Feature", description="GeoJSON type")
    id: Optional[int] = Field(default=None, description="Feature ID")
    properties: Dict[str, Any] = Field(..., description="Feature attributes (district name, codes, vintage)")
    geometry: Dict[str, Any] = Field(..., description="GeoJSON polygon geometry in EPSG:4326")


class DistrictBoundaryCollection(BaseModel):
    """GeoJSON FeatureCollection representing Punjab district boundaries."""
    type: str = Field(default="FeatureCollection", description="GeoJSON collection type")
    name: str = Field(..., description="Layer title and coordinate reference system")
    total_features: int = Field(..., description="Total number of district features (23 in Punjab)")
    features: List[DistrictBoundaryFeature] = Field(..., description="District boundary features")
