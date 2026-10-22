"""
API Source Registry and Provider Status route handlers.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...schemas.sources import SourceRegistryItem, SourceRegistryResponse
from ...services.sources_service import sources_service

router = APIRouter(prefix="/api/v1/sources", tags=["API Registry & Connectors"])


@router.get("", response_model=SourceRegistryResponse, summary="List registered external sources and operational statuses")
def get_sources(
    category: Optional[str] = Query(default=None, description="Filter by category (e.g. APMC, Central, Open Data)"),
    status: Optional[str] = Query(default=None, description="Filter by status (working-tested, blocked-auth, blocked-captcha, metadata-only, unavailable)"),
):
    """
    Returns empirical operational statuses for all 10 evaluated external providers.
    
    CRITICAL POLICY GUARANTEE:
    All client requests are served strictly from validated local stores; zero live external HTTP requests occur during page load.
    """
    try:
        return sources_service.get_sources(category=category, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query source registry: {str(e)}")


@router.get("/{source_id}", response_model=SourceRegistryItem, summary="Get details and blockers for a specific provider")
def get_source_by_id(source_id: str):
    """
    Returns operational details, verified technical blockers, and legitimate next steps for an external source.
    """
    try:
        source = sources_service.get_source_by_id(source_id)
        if not source:
            raise HTTPException(status_code=404, detail=f"Source with ID '{source_id}' not found in registry.")
        return source
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query source '{source_id}': {str(e)}")
