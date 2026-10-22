"""
Dataset catalog API routes for Punjab GrainWatch Backend.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...schemas.dataset import DatasetListResponse, DatasetDetailResponse
from ...services.catalog_service import catalog_service

router = APIRouter(prefix="/api/v1/datasets", tags=["Dataset Catalog"])


@router.get("", response_model=DatasetListResponse, summary="List verified datasets in catalog")
def list_datasets(
    status: Optional[str] = Query(None, description="Filter by evidence status (observed, derived, metadata only, blocked, stale, missing)"),
    commodity: Optional[str] = Query(None, description="Filter by commodity name substring"),
    search: Optional[str] = Query(None, description="Free text search across ID, source, caveats, coverage"),
    reload: bool = Query(False, description="Force re-reading catalog from disk")
):
    """Retrieve all cataloged datasets with optional filtering."""
    items = catalog_service.get_all(status=status, commodity=commodity, search=search, force_reload=reload)
    filters = {}
    if status:
        filters["status"] = status
    if commodity:
        filters["commodity"] = commodity
    if search:
        filters["search"] = search

    return DatasetListResponse(
        total=len(items),
        items=items,
        filters_applied=filters
    )


@router.get("/{dataset_id}", response_model=DatasetDetailResponse, summary="Get single dataset details")
def get_dataset(dataset_id: str):
    """Retrieve complete metadata and path resolution for a specific dataset ID."""
    detail = catalog_service.get_by_id(dataset_id)
    if not detail:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset with ID '{dataset_id}' not found in catalog."
        )
    return detail
