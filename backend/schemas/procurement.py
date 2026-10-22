"""
Domain schema for government foodgrain procurement snapshots.
Source: Central Food Grains Procurement Portal (CFPP).
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ProcurementObservationItem(BaseModel):
    """Single procurement observation measure."""
    observation_date: str = Field(..., description="As-of position date (YYYY-MM-DD)")
    state: str = Field(..., description="State name (Punjab)")
    commodity: str = Field(..., description="Commodity name (Wheat)")
    season: str = Field(..., description="Marketing season (RMS 2025-26)")
    measure_name: str = Field(..., description="Measure identifier (season_estimate, daily_procurement, progressive_procurement)")
    measure_value: float = Field(..., description="Observed numeric quantity")
    measure_unit: str = Field(..., description="Unit of measurement (Lakh Metric Tonnes or Metric Tonnes)")
    temporal_basis: str = Field(..., description="Temporal dimension (seasonal_target_estimate, single_day, cumulative_season_to_date)")
    reporting_agency: str = Field(..., description="Official reporting agency")
    source_url: str = Field(..., description="Source portal URL")
    retrieval_date_utc: str = Field(..., description="Timestamp of data acquisition")
    quality_note: str = Field(..., description="Audit clarification on measure semantics")


class ProcurementResponse(BaseModel):
    """Procurement snapshot response.
    
    CRITICAL DOMAIN INVARIANTS:
    - cannot_be_summed: The measures represent an annual target, a single-day total, and a cumulative season total.
    - is_time_series: False (single-date position report, not a continuous daily time series).
    """
    total: int = Field(..., description="Number of observation measures")
    as_of_date: str = Field(..., description="Snapshot observation date (2025-05-15)")
    state: str = Field(default="Punjab", description="State level of aggregation")
    cannot_be_summed: bool = Field(
        default=True,
        description="Invariant: Measures share the same date but differ in temporal basis and unit. They cannot be summed."
    )
    is_time_series: bool = Field(
        default=False,
        description="Invariant: This is a single position report snapshot, not a continuous daily time series."
    )
    temporal_basis_warning: str = Field(
        default="CFPP reports contain 3 distinct temporal dimensions: seasonal target (LMT), single-day intake (MT), and cumulative intake (MT). Never sum these rows.",
        description="Auditable methodological instruction"
    )
    items: List[ProcurementObservationItem] = Field(..., description="Procurement observation measures")
