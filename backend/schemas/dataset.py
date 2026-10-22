"""
Pydantic schemas for dataset catalog representations.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DatasetCatalogItem(BaseModel):
    """Factual metadata representation of a single dataset in the catalog."""
    dataset_id: str
    file_path: str
    format: str
    source_name: str
    source_url: str
    sha256: str
    size_bytes: int
    row_count: int
    schema_columns: str
    date_range: str
    geography_level: str
    geographic_coverage: str
    commodity_coverage: str
    units: str
    retrieval_timestamp_utc: str
    evidence_status: str = Field(..., description="observed, derived, metadata only, blocked, stale, missing")
    licensing_access_notes: str
    caveats: str
    last_validation_result: str


class DatasetListResponse(BaseModel):
    """Paginated or filtered list of datasets from catalog."""
    total: int
    items: List[DatasetCatalogItem]
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


class DatasetDetailResponse(BaseModel):
    """Detailed view of a single dataset with file resolution."""
    dataset: DatasetCatalogItem
    exists_on_disk: bool
    safe_path_resolved: Optional[str] = None
    column_list: List[str] = Field(default_factory=list)
