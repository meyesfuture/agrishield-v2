"""
Geospatial district boundaries and crosswalk route handlers.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...schemas.geography import (
    DistrictBoundaryCollection,
    DistrictBoundaryFeature,
    DistrictCrosswalkResponse,
)
from ...services.data_service import data_service

router = APIRouter(prefix="/api/v1/geo", tags=["Geospatial & Administrative"])


@router.get("/districts", response_model=DistrictBoundaryCollection, summary="Get Punjab district boundaries GeoJSON")
def get_district_boundaries(
    name: Optional[str] = Query(default=None, description="Filter by district name (case-insensitive)"),
):
    """
    Returns verified GeoJSON FeatureCollection of Punjab's 23 district boundaries in EPSG:4326.
    """
    try:
        return data_service.query_district_boundaries(district_name=name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load district boundaries: {str(e)}")


@router.get("/districts/{district_id}", response_model=DistrictBoundaryFeature, summary="Get single district boundary by ID")
def get_district_boundary_by_id(district_id: str):
    """
    Returns boundary feature for a specific district identifier or LGD code.
    """
    try:
        feat = data_service.get_district_boundary_by_id(district_id)
        if not feat:
            raise HTTPException(status_code=404, detail=f"District boundary with ID '{district_id}' not found.")
        return feat
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query district boundary: {str(e)}")


@router.get("/crosswalk", response_model=DistrictCrosswalkResponse, summary="Get statistical to geospatial district crosswalk")
def get_district_crosswalk(
    match_status: Optional[str] = Query(default=None, description="Filter by crosswalk match status"),
    limit: int = Query(default=50, ge=1, le=500, description="Page limit (1-500)"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
):
    """
    Returns administrative name and code crosswalk between DES APY reporting names,
    candidate LGD identifiers, and geospatial boundary feature names.
    """
    try:
        return data_service.query_crosswalk(
            match_status=match_status,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query crosswalk: {str(e)}")
