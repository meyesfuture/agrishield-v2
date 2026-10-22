"""
Domain schema for the API Source Registry.
Provides evidence-based operational statuses, verified blockers, and legitimate next steps.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .common import SourceRegistryStatus


class SourceRegistryItem(BaseModel):
    """Operational status and technical interface details of an external source."""
    source_id: str = Field(..., description="Unique source system identifier")
    source_name: str = Field(..., description="Human-readable provider name")
    url: str = Field(..., description="Source portal or API endpoint URL")
    category: str = Field(..., description="Institutional category")
    protocol_or_method: str = Field(..., description="Communication protocol (REST GET, HTTPS POST, etc.)")
    auth_type: str = Field(..., description="Authentication requirement (None, API Key, Bearer Token, Portal Login)")
    live_status_code: str = Field(..., description="HTTP status code or network diagnostic code observed")
    observations_acquired: int = Field(..., description="Number of empirical rows acquired from this source")
    arrival_quantity_exposed: str = Field(..., description="Whether arrival quantities are exposed")
    prices_exposed: str = Field(..., description="Whether wholesale prices are exposed")
    operational_blockers: str = Field(..., description="Detailed description of technical or policy blockers")
    final_verdict: str = Field(..., description="Acquisition verdict from Phase 0/1 audit")
    evidence_status: SourceRegistryStatus = Field(
        ...,
        description="Standardized status: working-tested, blocked-auth, blocked-captcha, metadata-only, unavailable, stale, not-tested"
    )
    next_legitimate_step: str = Field(
        ...,
        description="Official procedure for obtaining access (e.g. register for API key, state agency MoU)"
    )


class SourceRegistryResponse(BaseModel):
    """List of all registered external sources with aggregate health status."""
    total: int = Field(..., description="Total sources tracked")
    working_tested_count: int = Field(..., description="Sources verified working with acquired data")
    blocked_count: int = Field(..., description="Sources blocked by authentication, CAPTCHA, or network restrictions")
    metadata_only_count: int = Field(..., description="Sources providing catalog/filter metadata only")
    offline_guarantee: str = Field(
        default="All client requests are served strictly from validated local stores; zero live external HTTP requests occur during page load.",
        description="Performance and reliability policy"
    )
    items: List[SourceRegistryItem] = Field(..., description="Registered source items")
