"""
Domain schema for the 8-element Grain Supply Flow Coverage Matrix.
Documents empirical coverage, critical data gaps, and reconciliation readiness.
"""

from typing import List
from pydantic import BaseModel, Field


class SupplyFlowCoverageItem(BaseModel):
    """Assessment of a single grain supply flow component."""
    supply_flow_element: str = Field(..., description="Stage in the foodgrain supply chain")
    required_granularity: str = Field(..., description="Required data dimensions for localized balance")
    available_sources: str = Field(..., description="Acquired or attempted official sources")
    current_status: str = Field(..., description="Empirical status (e.g. CRITICAL GAP FOR GRAINS, NATIONAL TOTALS ONLY)")
    exact_coverage: str = Field(..., description="Exact empirical scope of acquired data")
    unit_standard: str = Field(..., description="Unit of measurement used by acquired data")
    audit_limitation: str = Field(..., description="Auditable blocker or methodological constraint")
    reconciliation_readiness: str = Field(..., description="Readiness for supply-demand reconciliation (e.g. NO-GO)")


class CoverageMatrixResponse(BaseModel):
    """Complete supply flow coverage matrix and reconciliation verdict."""
    total_elements: int = Field(..., description="Total supply chain elements evaluated (8)")
    elements_ready_for_reconciliation: int = Field(..., description="Number of elements ready for localized reconciliation")
    critical_gaps_count: int = Field(..., description="Number of supply chain elements with critical gaps or complete absence")
    reconciliation_overall_verdict: str = Field(
        default="NO-GO for grain supply reconciliation or hoarding detection",
        description="Empirical gate verdict"
    )
    methodological_principle: str = Field(
        default="Without concurrent localized grain arrivals, disaggregated procurement, and verified private commercial stock data, localized supply reconciliation is mathematically unidentifiable.",
        description="Reasoning explaining why actor ranking or hoarding detection is banned"
    )
    items: List[SupplyFlowCoverageItem] = Field(..., description="List of supply flow elements")
