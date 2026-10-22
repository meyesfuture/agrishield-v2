"""
Service for managing the external API Source Registry and operational statuses.
Reads SOURCE_STATUS.csv and maps each source to evidence-based health statuses.
"""

from typing import List, Optional
import pandas as pd

from ..config import settings
from ..logger import logger
from ..schemas.sources import SourceRegistryItem, SourceRegistryResponse
from ..schemas.common import SourceRegistryStatus


def _map_evidence_status(source_id: str, final_verdict: str) -> SourceRegistryStatus:
    """Map audited verdict to standardized evidence status enum."""
    verdict_upper = final_verdict.upper()
    if "VERIFIED_WORKING_METADATA" in verdict_upper:
        return "metadata-only"
    if "VERIFIED_WORKING" in verdict_upper:
        return "working-tested"
    if "AUTHENTICATION_BLOCKED" in verdict_upper:
        return "blocked-auth"
    if "TLS_VERIFICATION" in verdict_upper or "SSL" in verdict_upper:
        return "unavailable"
    if "ACCESS_RESTRICTED" in verdict_upper or "NO_PUBLIC" in verdict_upper:
        return "unavailable"
    return "not-tested"


def _get_next_legitimate_step(source_id: str) -> str:
    """Provide verified, policy-compliant instructions for accessing blocked sources."""
    steps = {
        "emandikaran_pb": "Public APMC API verified working. Use for fruits and vegetables; do not expect wheat/paddy arrivals.",
        "agmarknet_v2_prices": "Public last-week price endpoint verified working. To acquire arrival volumes, use official DMI data request.",
        "agmarknet_v2_filters": "Master filters catalog verified working. Extracted 245 Punjab markets, 22 districts, and 605 commodities.",
        "cfpp_procurement": "Public reports verified working with strict TLS verification. Exposes state wheat RMS targets and progress.",
        "nasa_power_weather": "Open access agrometeorological API verified working. Multi-zone panel acquired cleanly.",
        "data_gov_in_ogd": "Register for an official developer account at data.gov.in, create an application, and configure the DATA_GOV_IN_API_KEY environment variable.",
        "des_agri_gov_in": "Install the National Informatics Centre (NIC) root CA certificate into the operating system cert store to resolve TLS trust without disabling verification.",
        "ceda_ashoka_api": "Submit an academic data access request to Ashoka University CEDA and configure the CEDA_BEARER_TOKEN environment variable.",
        "enam_portal": "Apply for institutional market participant credentials or execute a state-level agricultural data exchange agreement.",
        "anaajkharid_pb": "Operational gatepass tracking is restricted to licensed state procurement agencies and millers; request formal data-sharing MoU with Punjab Food & Civil Supplies.",
    }
    return steps.get(source_id, "Inspect provider documentation and request authorized credentials.")


class SourcesService:
    """Service providing access to audited provider statuses."""

    def __init__(self):
        self._sources_df: Optional[pd.DataFrame] = None

    def get_sources_df(self) -> pd.DataFrame:
        if self._sources_df is None:
            path = settings.source_status_csv
            if not path.exists():
                raise FileNotFoundError(f"Source status file not found at {path}")
            df = pd.read_csv(path)
            self._sources_df = df
        return self._sources_df

    def get_sources(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> SourceRegistryResponse:
        df = self.get_sources_df()

        items: List[SourceRegistryItem] = []
        for _, row in df.iterrows():
            source_id = str(row["source_id"])
            verdict = str(row.get("final_verdict", ""))
            ev_status = _map_evidence_status(source_id, verdict)

            item = SourceRegistryItem(
                source_id=source_id,
                source_name=str(row["source_name"]),
                url=str(row["url"]),
                category=str(row["category"]),
                protocol_or_method=str(row["protocol_or_method"]),
                auth_type=str(row["auth_type"]),
                live_status_code=str(row["live_status_code"]),
                observations_acquired=int(row["observations_acquired"]),
                arrival_quantity_exposed=str(row["arrival_quantity_exposed"]),
                prices_exposed=str(row["prices_exposed"]),
                operational_blockers=str(row["operational_blockers"]),
                final_verdict=verdict,
                evidence_status=ev_status,
                next_legitimate_step=_get_next_legitimate_step(source_id),
            )
            items.append(item)

        if category:
            items = [i for i in items if category.strip().lower() in i.category.lower()]
        if status:
            items = [i for i in items if i.evidence_status == status.strip().lower()]

        working_count = sum(1 for i in items if i.evidence_status == "working-tested")
        blocked_count = sum(1 for i in items if i.evidence_status in ("blocked-auth", "blocked-captcha", "unavailable"))
        metadata_count = sum(1 for i in items if i.evidence_status == "metadata-only")

        return SourceRegistryResponse(
            total=len(items),
            working_tested_count=working_count,
            blocked_count=blocked_count,
            metadata_only_count=metadata_count,
            offline_guarantee=(
                "All client requests are served strictly from validated local stores; "
                "zero live external HTTP requests occur during page load."
            ),
            items=items,
        )

    def get_source_by_id(self, source_id: str) -> Optional[SourceRegistryItem]:
        resp = self.get_sources()
        for item in resp.items:
            if item.source_id.lower() == source_id.strip().lower():
                return item
        return None


sources_service = SourcesService()
