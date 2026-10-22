"""
Catalog service for Punjab GrainWatch Backend.
Reads and queries the validated dataset catalog produced in Phase 1.
"""

import json
from typing import List, Optional, Dict, Any
from ..config import settings
from ..logger import logger
from ..schemas.dataset import DatasetCatalogItem, DatasetDetailResponse


class CatalogService:
    """Service to load, filter, and inspect datasets from the validated catalog."""

    def __init__(self):
        self._cached_catalog: Optional[List[Dict[str, Any]]] = None

    def _load_raw_catalog(self, force_reload: bool = False) -> List[Dict[str, Any]]:
        """Load JSON catalog from data/manifests/dataset_catalog.json."""
        if self._cached_catalog is not None and not force_reload:
            return self._cached_catalog

        catalog_path = settings.catalog_json
        if not catalog_path.exists():
            logger.warning(f"Catalog file not found at {catalog_path}")
            return []

        try:
            with open(catalog_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._cached_catalog = data
                return data
        except Exception as e:
            logger.error(f"Failed to read catalog file: {e}")
            return []

    def get_all(
        self,
        status: Optional[str] = None,
        commodity: Optional[str] = None,
        search: Optional[str] = None,
        force_reload: bool = False
    ) -> List[DatasetCatalogItem]:
        """Retrieve all catalog items with optional filtering."""
        raw_items = self._load_raw_catalog(force_reload=force_reload)
        filtered = []

        for item in raw_items:
            # Filter by evidence status
            if status and item.get("evidence_status", "").lower() != status.lower():
                continue

            # Filter by commodity substring
            if commodity and commodity.lower() not in item.get("commodity_coverage", "").lower():
                continue

            # Text search across dataset_id, source_name, caveats
            if search:
                s_lower = search.lower()
                id_match = s_lower in item.get("dataset_id", "").lower()
                source_match = s_lower in item.get("source_name", "").lower()
                caveat_match = s_lower in item.get("caveats", "").lower()
                coverage_match = s_lower in item.get("geographic_coverage", "").lower()
                if not (id_match or source_match or caveat_match or coverage_match):
                    continue

            try:
                filtered.append(DatasetCatalogItem(**item))
            except Exception as e:
                logger.warning(f"Failed to parse catalog entry {item.get('dataset_id')}: {e}")

        return filtered

    def get_by_id(self, dataset_id: str) -> Optional[DatasetDetailResponse]:
        """Retrieve detailed information for a single dataset by ID."""
        raw_items = self._load_raw_catalog()
        item = next((i for i in raw_items if i.get("dataset_id") == dataset_id), None)
        if not item:
            return None

        # Resolve safe path
        rel_path = item.get("file_path", "")
        safe_path = settings.resolve_safe_path(rel_path)
        exists = safe_path.exists() if safe_path else False

        # Parse column list from semicolon-separated schema_columns
        cols_str = item.get("schema_columns", "")
        cols_list = [c.strip() for c in cols_str.split(";") if c.strip()] if cols_str and cols_str != "N/A" else []

        catalog_item = DatasetCatalogItem(**item)
        return DatasetDetailResponse(
            dataset=catalog_item,
            exists_on_disk=exists,
            safe_path_resolved=str(safe_path) if safe_path else None,
            column_list=cols_list
        )


catalog_service = CatalogService()
