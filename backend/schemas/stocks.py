"""
Domain schema for Central Pool foodgrain stock observations.
Source: Department of Food and Public Distribution (DFPD) / FCI.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .common import PaginatedResponse


class StockObservationItem(BaseModel):
    """Central Pool foodgrain stock level or stocking norm observation.
    
    CRITICAL DOMAIN INVARIANT:
    Geographic coverage is strictly National Central Pool (all 100 rows).
    State is null (100%). These rows must NEVER be labeled as Punjab state or district stocks.
    """
    source_id: str = Field(..., description="Source dataset identifier")
    observation_date: str = Field(..., description="Position date of stock observation (YYYY-MM-DD)")
    geographic_coverage: str = Field(..., description="Geographic coverage level (India Central Pool)")
    state: Optional[str] = Field(
        default=None,
        description="State identifier. Strictly null; this dataset has NO state or district breakdown."
    )
    agency: str = Field(..., description="Reporting agency (DFPD/FCI)")
    commodity_original: str = Field(..., description="Original commodity label")
    commodity_standard: str = Field(..., description="Standardized commodity name (wheat, rice)")
    grain_form: str = Field(..., description="Grain form description / milling status note")
    measure_name: str = Field(..., description="Measure name (actual_central_pool_stock, foodgrain_stocking_norm)")
    measure_value: float = Field(..., description="Quantity in Lakh Metric Tonnes (LMT)")
    measure_unit: str = Field(..., description="Measurement unit (LMT)")
    observation_type: str = Field(..., description="Observation type (stock_level, norm_not_observed_stock)")
    source_url: str = Field(..., description="Source bulletin URL")
    raw_file: str = Field(..., description="Relative path of source PDF in repository")
    quality_note: str = Field(..., description="Audit note documenting national scope and caveats")


class StockResponse(BaseModel):
    """Paginated list of Central Pool stock observations with explicit scope guardrails."""
    total: int = Field(..., description="Total number of stock records matching filters")
    limit: int = Field(..., description="Page limit")
    offset: int = Field(..., description="Page offset")
    geographic_scope: str = Field(
        default="National Central Pool only",
        description="Scope guardrail: Invariant stating that data is national, not regional."
    )
    punjab_specific_warning: str = Field(
        default="This dataset contains national Central Pool observations only. State column is null. These figures must NOT be interpreted as Punjab state or district stocks.",
        description="Mandatory methodological caveat"
    )
    items: List[StockObservationItem] = Field(..., description="Stock records")
