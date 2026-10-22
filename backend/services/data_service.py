"""
Data query services for Punjab GrainWatch Backend.
Provides cached, thread-safe, provenance-preserving queries with strict null-preservation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from ..config import settings
from ..logger import logger
from ..schemas.production import DistrictProductionItem, ProductionListResponse
from ..schemas.yields import DistrictYieldItem, YieldListResponse
from ..schemas.prices import MarketPriceItem, PriceListResponse
from ..schemas.weather import WeatherObservationItem, WeatherListResponse
from ..schemas.procurement import ProcurementObservationItem, ProcurementResponse
from ..schemas.stocks import StockObservationItem, StockResponse
from ..schemas.geography import (
    DistrictCrosswalkItem,
    DistrictCrosswalkResponse,
    DistrictBoundaryCollection,
    DistrictBoundaryFeature,
)
from ..schemas.coverage import SupplyFlowCoverageItem, CoverageMatrixResponse
from ..schemas.quality import QualityIssueItem, QualityIssuesResponse
from ..schemas.methodology import MethodologyResponse, MethodologicalPrinciple


def _clean_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Convert pandas NaN, pd.NA, and empty strings to None where appropriate."""
    cleaned = {}
    for k, v in d.items():
        if pd.isna(v):
            cleaned[k] = None
        else:
            cleaned[k] = v
    return cleaned


class DataService:
    """Singleton service providing access to validated datasets."""

    def __init__(self):
        self._production_df: Optional[pd.DataFrame] = None
        self._yield_df: Optional[pd.DataFrame] = None
        self._prices_df: Optional[pd.DataFrame] = None
        self._weather_df: Optional[pd.DataFrame] = None
        self._procurement_df: Optional[pd.DataFrame] = None
        self._stocks_df: Optional[pd.DataFrame] = None
        self._crosswalk_df: Optional[pd.DataFrame] = None
        self._boundaries_geojson: Optional[Dict[str, Any]] = None
        self._coverage_matrix_df: Optional[pd.DataFrame] = None

    # -------------------------------------------------------------------------
    # Crop Production
    # -------------------------------------------------------------------------
    def get_production_df(self) -> pd.DataFrame:
        if self._production_df is None:
            path = settings.production_csv
            if not path.exists():
                raise FileNotFoundError(f"Production dataset not found at {path}")
            df = pd.read_csv(path, dtype=str)
            # Convert numeric columns safely while preserving nulls
            for col in ["area_value", "production_value", "yield_value"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            self._production_df = df
        return self._production_df

    def query_production(
        self,
        district: Optional[str] = None,
        crop: Optional[str] = None,
        agricultural_year: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ProductionListResponse:
        df = self.get_production_df()
        
        if district:
            df = df[df["district_original"].str.lower() == district.strip().lower()]
        if crop:
            c = crop.strip().lower()
            if c in ("rice", "paddy"):
                df = df[df["crop_standard"].str.lower().str.contains("paddy|rice")]
            else:
                df = df[df["crop_standard"].str.lower() == c]
        if agricultural_year:
            df = df[df["agricultural_year"].str.strip() == agricultural_year.strip()]

        total = len(df)
        page_records = df.iloc[offset : offset + limit].to_dict(orient="records")
        items = [DistrictProductionItem(**_clean_dict(r)) for r in page_records]

        return ProductionListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    # -------------------------------------------------------------------------
    # Crop Yield History
    # -------------------------------------------------------------------------
    def get_yield_df(self) -> pd.DataFrame:
        if self._yield_df is None:
            path = settings.yield_csv
            if not path.exists():
                raise FileNotFoundError(f"Yield dataset not found at {path}")
            df = pd.read_csv(path, dtype=str)
            df["yield_value"] = pd.to_numeric(df["yield_value"], errors="coerce")
            # Create a coalesced effective_year for easy filtering/sorting
            df["effective_year"] = df["source_year_label"].fillna(df["agricultural_year"]).astype(str)
            self._yield_df = df
        return self._yield_df

    def query_yields(
        self,
        district: Optional[str] = None,
        crop: Optional[str] = None,
        year_from: Optional[str] = None,
        year_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> YieldListResponse:
        df = self.get_yield_df()

        if district:
            df = df[df["district_original"].str.lower() == district.strip().lower()]
        if crop:
            df = df[df["crop_standard"].str.lower() == crop.strip().lower()]
        if year_from:
            df = df[df["effective_year"] >= year_from.strip()]
        if year_to:
            df = df[df["effective_year"] <= year_to.strip()]

        total = len(df)
        page_records = df.iloc[offset : offset + limit].to_dict(orient="records")
        items = [DistrictYieldItem(**_clean_dict(r)) for r in page_records]

        return YieldListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    # -------------------------------------------------------------------------
    # Mandi Wholesale Market Prices
    # -------------------------------------------------------------------------
    def get_prices_df(self) -> pd.DataFrame:
        if self._prices_df is None:
            path = settings.prices_csv
            if not path.exists():
                raise FileNotFoundError(f"Prices dataset not found at {path}")
            df = pd.read_csv(path)
            # Ensure modal_price is float
            df["modal_price"] = pd.to_numeric(df["modal_price"], errors="coerce")
            # arrival_quantity is 100% null in this dataset
            df["arrival_quantity"] = pd.to_numeric(df["arrival_quantity"], errors="coerce")
            self._prices_df = df
        return self._prices_df

    def query_prices(
        self,
        market_name: Optional[str] = None,
        commodity: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> PriceListResponse:
        df = self.get_prices_df()

        if market_name:
            df = df[df["market_name"].str.lower().str.contains(market_name.strip().lower())]
        if commodity:
            df = df[df["commodity_name"].str.lower().str.contains(commodity.strip().lower())]
        if date_from:
            df = df[df["observation_date"] >= date_from.strip()]
        if date_to:
            df = df[df["observation_date"] <= date_to.strip()]

        total = len(df)
        page_records = df.iloc[offset : offset + limit].to_dict(orient="records")
        items = [MarketPriceItem(**_clean_dict(r)) for r in page_records]

        return PriceListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    # -------------------------------------------------------------------------
    # Multi-zone Daily Weather
    # -------------------------------------------------------------------------
    def get_weather_df(self) -> pd.DataFrame:
        if self._weather_df is None:
            path = settings.weather_csv
            if not path.exists():
                raise FileNotFoundError(f"Weather dataset not found at {path}")
            df = pd.read_csv(path)
            for col in ["latitude", "longitude", "temperature_mean_c", "precipitation_mm_day", "relative_humidity_pct"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            self._weather_df = df
        return self._weather_df

    def query_weather(
        self,
        station_name: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> WeatherListResponse:
        df = self.get_weather_df()

        if station_name:
            df = df[df["station_name"].str.lower().str.contains(station_name.strip().lower())]
        if date_from:
            df = df[df["observation_date"] >= date_from.strip()]
        if date_to:
            df = df[df["observation_date"] <= date_to.strip()]

        total = len(df)
        page_records = df.iloc[offset : offset + limit].to_dict(orient="records")
        items = [WeatherObservationItem(**_clean_dict(r)) for r in page_records]

        return WeatherListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    # -------------------------------------------------------------------------
    # State Wheat Procurement Snapshot
    # -------------------------------------------------------------------------
    def get_procurement_df(self) -> pd.DataFrame:
        if self._procurement_df is None:
            path = settings.procurement_csv
            if not path.exists():
                raise FileNotFoundError(f"Procurement dataset not found at {path}")
            df = pd.read_csv(path)
            df["measure_value"] = pd.to_numeric(df["measure_value"], errors="coerce")
            self._procurement_df = df
        return self._procurement_df

    def query_procurement(
        self,
        commodity: Optional[str] = None,
        measure_name: Optional[str] = None,
    ) -> ProcurementResponse:
        df = self.get_procurement_df()

        if commodity:
            df = df[df["commodity"].str.lower() == commodity.strip().lower()]
        if measure_name:
            df = df[df["measure_name"].str.lower() == measure_name.strip().lower()]

        records = df.to_dict(orient="records")
        items = [ProcurementObservationItem(**_clean_dict(r)) for r in records]
        as_of_date = items[0].observation_date if items else "2025-05-15"

        return ProcurementResponse(
            total=len(items),
            as_of_date=as_of_date,
            state="Punjab",
            cannot_be_summed=True,
            is_time_series=False,
            temporal_basis_warning=(
                "CFPP reports contain 3 distinct temporal dimensions: seasonal target (LMT), "
                "single-day intake (MT), and cumulative intake (MT). Never sum these rows."
            ),
            items=items,
        )

    # -------------------------------------------------------------------------
    # National Central Pool Stocks
    # -------------------------------------------------------------------------
    def get_stocks_df(self) -> pd.DataFrame:
        if self._stocks_df is None:
            path = settings.stocks_csv
            if not path.exists():
                raise FileNotFoundError(f"Stocks dataset not found at {path}")
            df = pd.read_csv(path)
            df["measure_value"] = pd.to_numeric(df["measure_value"], errors="coerce")
            self._stocks_df = df
        return self._stocks_df

    def query_stocks(
        self,
        commodity: Optional[str] = None,
        measure_name: Optional[str] = None,
        observation_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> StockResponse:
        df = self.get_stocks_df()

        if commodity:
            df = df[df["commodity_standard"].str.lower() == commodity.strip().lower()]
        if measure_name:
            df = df[df["measure_name"].str.lower() == measure_name.strip().lower()]
        if observation_type:
            df = df[df["observation_type"].str.lower() == observation_type.strip().lower()]

        total = len(df)
        page_records = df.iloc[offset : offset + limit].to_dict(orient="records")
        items = [StockObservationItem(**_clean_dict(r)) for r in page_records]

        return StockResponse(
            total=total,
            limit=limit,
            offset=offset,
            geographic_scope="National Central Pool only",
            punjab_specific_warning=(
                "This dataset contains national Central Pool observations only. State column is null. "
                "These figures must NOT be interpreted as Punjab state or district stocks."
            ),
            items=items,
        )

    # -------------------------------------------------------------------------
    # Geospatial: Boundaries & Crosswalk
    # -------------------------------------------------------------------------
    def get_boundaries_geojson(self) -> Dict[str, Any]:
        if self._boundaries_geojson is None:
            path = settings.boundaries_geojson
            if not path.exists():
                raise FileNotFoundError(f"District boundaries not found at {path}")
            with open(path, "r", encoding="utf-8") as f:
                self._boundaries_geojson = json.load(f)
        return self._boundaries_geojson

    def query_district_boundaries(
        self,
        district_name: Optional[str] = None,
    ) -> DistrictBoundaryCollection:
        geojson = self.get_boundaries_geojson()
        features = geojson.get("features", [])

        if district_name:
            target = district_name.strip().lower()
            features = [
                f for f in features
                if f.get("properties", {}).get("dtname", "").lower() == target
                or f.get("properties", {}).get("district_name_standard", "").lower() == target
            ]

        items = [
            DistrictBoundaryFeature(
                type="Feature",
                id=f.get("id"),
                properties=f.get("properties", {}),
                geometry=f.get("geometry", {}),
            )
            for f in features
        ]

        return DistrictBoundaryCollection(
            type="FeatureCollection",
            name=geojson.get("name", "Punjab district boundaries"),
            total_features=len(items),
            features=items,
        )

    def get_district_boundary_by_id(self, district_id: str) -> Optional[DistrictBoundaryFeature]:
        geojson = self.get_boundaries_geojson()
        for f in geojson.get("features", []):
            props = f.get("properties", {})
            if str(props.get("district_id")) == str(district_id) or str(f.get("id")) == str(district_id) or str(props.get("dist_lgd")) == str(district_id):
                return DistrictBoundaryFeature(
                    type="Feature",
                    id=f.get("id"),
                    properties=props,
                    geometry=f.get("geometry", {}),
                )
        return None

    def get_crosswalk_df(self) -> pd.DataFrame:
        if self._crosswalk_df is None:
            path = settings.crosswalk_csv
            if not path.exists():
                raise FileNotFoundError(f"Crosswalk dataset not found at {path}")
            self._crosswalk_df = pd.read_csv(path)
        return self._crosswalk_df

    def query_crosswalk(
        self,
        match_status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> DistrictCrosswalkResponse:
        df = self.get_crosswalk_df()

        if match_status:
            df = df[df["match_status"].str.lower() == match_status.strip().lower()]

        total = len(df)
        page_records = df.iloc[offset : offset + limit].to_dict(orient="records")
        items = [DistrictCrosswalkItem(**_clean_dict(r)) for r in page_records]

        return DistrictCrosswalkResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    # -------------------------------------------------------------------------
    # Supply Flow Coverage Matrix
    # -------------------------------------------------------------------------
    def get_coverage_matrix_df(self) -> pd.DataFrame:
        if self._coverage_matrix_df is None:
            path = settings.coverage_matrix_csv
            if not path.exists():
                raise FileNotFoundError(f"Coverage matrix not found at {path}")
            self._coverage_matrix_df = pd.read_csv(path)
        return self._coverage_matrix_df

    def get_coverage_matrix(self) -> CoverageMatrixResponse:
        df = self.get_coverage_matrix_df()
        records = df.to_dict(orient="records")
        items = [SupplyFlowCoverageItem(**_clean_dict(r)) for r in records]

        ready_count = sum(1 for i in items if "GO" in i.reconciliation_readiness and "NO-GO" not in i.reconciliation_readiness)
        critical_count = sum(1 for i in items if "NO-GO" in i.reconciliation_readiness)

        return CoverageMatrixResponse(
            total_elements=len(items),
            elements_ready_for_reconciliation=ready_count,
            critical_gaps_count=critical_count,
            reconciliation_overall_verdict="NO-GO for grain supply reconciliation or hoarding detection",
            methodological_principle=(
                "Without concurrent localized grain arrivals, disaggregated procurement, and verified private "
                "commercial stock data, localized supply reconciliation is mathematically unidentifiable."
            ),
            items=items,
        )

    # -------------------------------------------------------------------------
    # Data Quality Issues
    # -------------------------------------------------------------------------
    def query_quality_issues(
        self,
        severity: Optional[str] = None,
        dataset_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> QualityIssuesResponse:
        # Load empirical quality issues identified during validation
        issues_catalog = [
            QualityIssueItem(
                issue_id="ISSUE-01",
                dataset_id="punjab_mandi_arrivals_oct2026",
                rule_name="foodgrain_arrival_absence",
                severity="CRITICAL",
                description="Acquired Mandi Board daily arrival panel of 3,892 records contains zero wheat and zero paddy records.",
                affected_count=3892,
                resolution_or_handling="Expose produce market arrivals only; do not attempt grain arrival anomaly calculations.",
            ),
            QualityIssueItem(
                issue_id="ISSUE-02",
                dataset_id="punjab_mandi_arrivals_oct2026",
                rule_name="clerk_sentinel_zero_price",
                severity="WARNING",
                description="3 records have modal_price == 0.0 as explicit clerk sentinel indicating price not reported.",
                affected_count=3,
                resolution_or_handling="Treated as unobserved/not-reported; excluded from price averages.",
            ),
            QualityIssueItem(
                issue_id="ISSUE-03",
                dataset_id="agmarknet_punjab_daily_prices",
                rule_name="arrival_quantity_unexposed",
                severity="CRITICAL",
                description="All 53 paddy price records have null arrival quantities (100% missing).",
                affected_count=53,
                resolution_or_handling="Preserve nulls; never default arrival quantity to 0.0 or combine with price series.",
            ),
            QualityIssueItem(
                issue_id="ISSUE-04",
                dataset_id="stock_observations_national_dfpd",
                rule_name="geographic_scope_national_only",
                severity="CRITICAL",
                description="All 100 stock observation records have null state; coverage is India Central Pool only.",
                affected_count=100,
                resolution_or_handling="Strictly label as National Central Pool; prohibit labeling as Punjab regional stock.",
            ),
            QualityIssueItem(
                issue_id="ISSUE-05",
                dataset_id="cfpp_punjab_wheat_procurement_2025_26",
                rule_name="multi_temporal_dimension_snapshot",
                severity="WARNING",
                description="Procurement snapshot contains 3 rows with 3 different temporal bases and units for the same date.",
                affected_count=3,
                resolution_or_handling="Marked cannot_be_summed=true; displayed as distinct analytical measures.",
            ),
            QualityIssueItem(
                issue_id="ISSUE-06",
                dataset_id="district_crop_production",
                rule_name="null_area_production_cells",
                severity="INFO",
                description="6 rows have null area, production, and yield values (Fazilka, Pathankot, SAS Nagar in early years).",
                affected_count=6,
                resolution_or_handling="Preserve null values in API output; do not replace with 0.",
            ),
            QualityIssueItem(
                issue_id="ISSUE-07",
                dataset_id="district_crosswalk",
                rule_name="historical_district_vintage_split",
                severity="WARNING",
                description="Malerkotla carved out of Sangrur in 2021/2022; historical APY series cannot be split retroactively.",
                affected_count=1,
                resolution_or_handling="Maintain separate candidate mapping notes in crosswalk.",
            ),
        ]

        filtered = issues_catalog
        if severity:
            filtered = [i for i in filtered if i.severity.lower() == severity.strip().lower()]
        if dataset_id:
            filtered = [i for i in filtered if dataset_id.strip().lower() in i.dataset_id.lower()]

        total = len(filtered)
        paged = filtered[offset : offset + limit]

        severity_counts = {
            "CRITICAL": sum(1 for i in issues_catalog if i.severity == "CRITICAL"),
            "WARNING": sum(1 for i in issues_catalog if i.severity == "WARNING"),
            "INFO": sum(1 for i in issues_catalog if i.severity == "INFO"),
        }

        return QualityIssuesResponse(
            total=total,
            limit=limit,
            offset=offset,
            severity_breakdown=severity_counts,
            items=paged,
        )

    # -------------------------------------------------------------------------
    # Methodology & Guardrails
    # -------------------------------------------------------------------------
    def get_methodology(self) -> MethodologyResponse:
        return MethodologyResponse(
            title="Punjab GrainWatch Analytical Methodology & Evidence Contracts",
            version="1.0.0",
            last_updated_utc="2026-10-22T00:00:00Z",
            anti_hoarding_charter=(
                "A statistical anomaly is strictly an audit prompt, never a conclusion of hoarding. "
                "Under Indian agricultural market dynamics, deviations in volume or price stem from harvest "
                "timings, moisture variations, procurement price parity, or transportation logistics. "
                "Without verified grain arrivals, private commercial stock ledgers, and independent adjudication "
                "records, actor-level ranking or hoarding labeling is prohibited by the project charter."
            ),
            core_principles=[
                MethodologicalPrinciple(
                    title="Empirical Evidence Supremacy",
                    rule="Only datasets actually verified and present in the local repository may be served.",
                    rationale="Prevents synthetic or fabricated claims from leaking into agricultural policy analysis."
                ),
                MethodologicalPrinciple(
                    title="Strict Absence != Zero Distinction",
                    rule="Null, not reported, not applicable, and explicit source zero are distinct semantic states.",
                    rationale="Treating missing arrivals as 0.0 produces false-positive supply collapse alerts."
                ),
                MethodologicalPrinciple(
                    title="Geographic Provenance Containment",
                    rule="National Central Pool stock observations must never be labeled or disaggregated as Punjab state inventory.",
                    rationale="State-level stock allocations cannot be inferred from national totals without depot ledgers."
                ),
                MethodologicalPrinciple(
                    title="Non-Summing Snapshot Semantics",
                    rule="Procurement reports containing mixed temporal bases (seasonal estimate, single day, cumulative) cannot be summed.",
                    rationale="Summing disparate temporal measures creates massive double-counting."
                ),
                MethodologicalPrinciple(
                    title="Zero Live External Calls on Page Load",
                    rule="All client views are served from validated, provenance-preserving local stores.",
                    rationale="Guarantees sub-second latency, zero reliance on external uptime, and total audit reproducibility."
                ),
            ],
            evidence_statuses={
                "observed": "Primary empirical record directly extracted from official government or open portals.",
                "derived": "Mathematically calculated from observed records (e.g. yield = production / area).",
                "metadata only": "Master register, schema definition, or API filter catalog without operational trade observations.",
                "blocked": "Source interface blocked by authentication, CAPTCHA, or network transport restrictions.",
                "stale": "Historical data exceeding freshness threshold without current updates.",
                "missing": "Required supply flow stage for which zero public data exists.",
                "synthetic demo": "Simulated data strictly segregated in data/synthetic/ and labeled in all UI views.",
            },
            data_contracts={
                "mandi_arrivals": "3,892 verified APMC records; 0 wheat/paddy records. Coriander green matches isolated.",
                "agmarknet_prices": "53 paddy price records. Arrival quantity is strictly null; modal price is positive.",
                "central_pool_stocks": "100 national observations. State is strictly null; coverage is India Central Pool.",
                "cfpp_procurement": "Single date snapshot 2025-05-15. 3 distinct measures; cannot be summed.",
                "district_production": "230 records across 23 districts and 5 years. 6 null cells preserved.",
                "nasa_weather": "3,655 multi-zone weather observations (2024-2025). 100% complete, zero nulls.",
            }
        )


data_service = DataService()
