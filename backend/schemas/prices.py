"""
Domain schema for mandi daily wholesale market prices in Punjab.
Source: AGMARKNET 2.0 (DMI, MoA&FW).
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .common import PaginatedResponse


class MarketPriceItem(BaseModel):
    """Mandi daily price record.
    
    CRITICAL DOMAIN INVARIANT:
    Arrival quantity is not exposed by this endpoint (100% null across all 53 rows).
    arrival_quantity MUST be serialized as null (None), never as 0.0.
    """
    observation_date: str = Field(..., description="Observation trade date (YYYY-MM-DD)")
    state: str = Field(..., description="State name (Punjab)")
    state_id: Optional[int] = Field(default=None, description="State ID in Agmarknet")
    market_id: int = Field(..., description="Market ID in Agmarknet")
    market_name: str = Field(..., description="Market name (e.g. Abohar APMC)")
    commodity_id: int = Field(..., description="Commodity ID in Agmarknet")
    commodity_name: str = Field(..., description="Commodity name (Paddy(Common))")
    variety: Optional[str] = Field(default=None, description="Reported variety name")
    modal_price: float = Field(..., description="Modal wholesale price in Rs./Quintal")
    price_unit: str = Field(..., description="Price unit (Rs./Quintal)")
    arrival_quantity: Optional[float] = Field(
        default=None,
        description="Arrival quantity. Strictly null for this endpoint; cannot be treated as 0."
    )
    arrival_unit: Optional[str] = Field(
        default=None,
        description="Arrival quantity unit. Strictly null when quantity is null."
    )
    source_endpoint: str = Field(..., description="Source API endpoint URL")
    retrieval_date_utc: str = Field(..., description="Timestamp of data acquisition")
    data_gap_note: str = Field(
        default="Arrival quantities are not exposed by this endpoint (100% null). Price observations cannot be combined with arrival volumes.",
        description="Auditable caveat documenting why arrival quantity is null"
    )


class PriceListResponse(PaginatedResponse[MarketPriceItem]):
    """Paginated list of mandi daily market price records."""
    pass
