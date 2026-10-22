"""
Schemas package for Punjab GrainWatch Backend.
Provides typed Pydantic models for all data domain entities and API endpoints.
"""

from .common import PaginatedResponse, ErrorResponse, EvidenceStatus, SourceRegistryStatus
from .health import HealthResponse, StatusResponse, EvidenceGuardrail
from .dataset import DatasetCatalogItem, DatasetListResponse, DatasetDetailResponse
from .quality import QualitySummaryResponse, CriticalAssertionStatus, QualityIssueItem, QualityIssuesResponse
from .production import DistrictProductionItem, ProductionListResponse
from .yields import DistrictYieldItem, YieldListResponse
from .prices import MarketPriceItem, PriceListResponse
from .weather import WeatherObservationItem, WeatherListResponse
from .procurement import ProcurementObservationItem, ProcurementResponse
from .stocks import StockObservationItem, StockResponse
from .geography import (
    DistrictCrosswalkItem,
    DistrictCrosswalkResponse,
    DistrictBoundaryFeature,
    DistrictBoundaryCollection,
)
from .coverage import SupplyFlowCoverageItem, CoverageMatrixResponse
from .sources import SourceRegistryItem, SourceRegistryResponse
from .methodology import MethodologyResponse, MethodologicalPrinciple

__all__ = [
    "PaginatedResponse",
    "ErrorResponse",
    "EvidenceStatus",
    "SourceRegistryStatus",
    "HealthResponse",
    "StatusResponse",
    "EvidenceGuardrail",
    "DatasetCatalogItem",
    "DatasetListResponse",
    "DatasetDetailResponse",
    "QualitySummaryResponse",
    "CriticalAssertionStatus",
    "QualityIssueItem",
    "QualityIssuesResponse",
    "DistrictProductionItem",
    "ProductionListResponse",
    "DistrictYieldItem",
    "YieldListResponse",
    "MarketPriceItem",
    "PriceListResponse",
    "WeatherObservationItem",
    "WeatherListResponse",
    "ProcurementObservationItem",
    "ProcurementResponse",
    "StockObservationItem",
    "StockResponse",
    "DistrictCrosswalkItem",
    "DistrictCrosswalkResponse",
    "DistrictBoundaryFeature",
    "DistrictBoundaryCollection",
    "SupplyFlowCoverageItem",
    "CoverageMatrixResponse",
    "SourceRegistryItem",
    "SourceRegistryResponse",
    "MethodologyResponse",
    "MethodologicalPrinciple",
]
