"""
Quality service for Punjab GrainWatch Backend.
Reads and provides access to the Phase 1 quality audit and validation reports.
"""

import json
from typing import Optional, Dict, Any, List
from ..config import settings
from ..logger import logger
from ..schemas.quality import QualitySummaryResponse, CriticalAssertionStatus


class QualityService:
    """Service to load and inspect data quality and validation results."""

    def __init__(self):
        self._cached_report: Optional[Dict[str, Any]] = None

    def _load_report(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        if self._cached_report is not None and not force_reload:
            return self._cached_report

        report_path = settings.quality_report_json
        if not report_path.exists():
            logger.warning(f"Quality report not found at {report_path}")
            return None

        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._cached_report = data
                return data
        except Exception as e:
            logger.error(f"Failed to read quality report: {e}")
            return None

    def get_summary(self, force_reload: bool = False) -> Optional[QualitySummaryResponse]:
        """Compile a summary of data quality and boundary guardrails."""
        report = self._load_report(force_reload=force_reload)
        if not report:
            return None

        # Build critical assertion items
        assertions_dict = report.get("critical_assertions", {})
        assertions_list = [
            CriticalAssertionStatus(
                assertion_key="zero_grain_arrivals_verified",
                description="Mandi arrival panel contains zero wheat or paddy grain rows",
                verified=assertions_dict.get("zero_grain_arrivals_verified", False),
                details="3,892 rows contain 62 APMC produce commodities; foodgrains routed separately."
            ),
            CriticalAssertionStatus(
                assertion_key="dhan_matches_are_coriander_green",
                description="All 71 'dhan' substring matches are Coriander Green (Hara Dhaniya)",
                verified=assertions_dict.get("dhan_matches_are_coriander_green", False),
                details=f"Exactly {assertions_dict.get('dhan_matches_count', 71)} matches confirmed as vegetable produce."
            ),
            CriticalAssertionStatus(
                assertion_key="paddy_prices_arrival_quantity_100pct_null",
                description="AGMARKNET daily prices feed contains 100% null arrival quantities",
                verified=assertions_dict.get("paddy_prices_arrival_quantity_100pct_null", False),
                details="Feed is modal price only (Rs. 2,320 MSP benchmark); volume is unobserved."
            ),
            CriticalAssertionStatus(
                assertion_key="national_stocks_state_100pct_null",
                description="DFPD buffer stock state is null (National Central Pool only)",
                verified=assertions_dict.get("national_stocks_state_100pct_null", False),
                details="All 100 rows represent national buffer stock; cannot be partitioned to Punjab silos."
            ),
            CriticalAssertionStatus(
                assertion_key="procurement_is_single_date_snapshot",
                description="Procurement data is a single date position (2025-05-15)",
                verified=assertions_dict.get("procurement_is_single_date_snapshot", False),
                details="3 rows represent target, single-day, and progressive totals; cannot be summed as a time series."
            ),
            CriticalAssertionStatus(
                assertion_key="satellite_is_single_window_tile",
                description="Satellite raster is a single scene tile (2024-10-05)",
                verified=assertions_dict.get("satellite_is_single_window_tile", False),
                details="512x512 tile window; does not constitute a temporal monitoring time-series."
            )
        ]

        # Calculate dataset counts by status
        dataset_validations = report.get("dataset_validations", {})
        status_counts: Dict[str, int] = {}
        for k, v in dataset_validations.items():
            status = v.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1

        quarantined = dataset_validations.get("legacy_audit", {}).get("syntax_errors", [])

        return QualitySummaryResponse(
            overall_validation_gate=report.get("overall_validation_gate", "UNKNOWN"),
            report_generated_utc=report.get("report_generated_utc", ""),
            manifest_integrity=report.get("manifest_integrity", {}),
            critical_assertions=assertions_list,
            dataset_status_counts=status_counts,
            quarantined_files=quarantined
        )


quality_service = QualityService()
