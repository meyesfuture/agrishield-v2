"""
Unit tests for domain schemas and transformation invariants.
Validates typed Pydantic models, null preservation, and domain guardrails.
"""

import pytest
from pydantic import ValidationError

from backend.schemas.prices import MarketPriceItem
from backend.schemas.stocks import StockObservationItem, StockResponse
from backend.schemas.procurement import ProcurementObservationItem, ProcurementResponse
from backend.schemas.production import DistrictProductionItem
from backend.schemas.yields import DistrictYieldItem
from backend.schemas.weather import WeatherObservationItem
from backend.schemas.coverage import SupplyFlowCoverageItem, CoverageMatrixResponse
from backend.schemas.sources import SourceRegistryItem


def test_market_price_item_preserves_null_arrival_quantity():
    """MarketPriceItem must preserve arrival_quantity as None and not convert to 0.0."""
    item = MarketPriceItem(
        observation_date="2026-10-19",
        state="Punjab",
        state_id=28,
        market_id=221,
        market_name="Abohar APMC",
        commodity_id=2,
        commodity_name="Paddy(Common)",
        variety="Abohar APMC - Paddy",
        modal_price=2461.0,
        price_unit="Rs./Quintal",
        arrival_quantity=None,
        arrival_unit=None,
        source_endpoint="https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-price/lastweek",
        retrieval_date_utc="20261021T191254Z",
    )
    assert item.arrival_quantity is None
    assert item.arrival_unit is None
    serialized = item.model_dump()
    assert serialized["arrival_quantity"] is None
    assert serialized["arrival_quantity"] != 0.0


def test_stock_observation_item_preserves_null_state():
    """Central pool stock observation state must be null; never labeled Punjab."""
    item = StockObservationItem(
        source_id="dfpd_fci_central_pool_stock_position",
        observation_date="2020-01-01",
        geographic_coverage="India Central Pool",
        state=None,
        agency="DFPD/FCI",
        commodity_original="Wheat",
        commodity_standard="wheat",
        grain_form="wheat",
        measure_name="actual_central_pool_stock",
        measure_value=327.96,
        measure_unit="LMT",
        observation_type="stock_level",
        source_url="https://dfpd.gov.in/",
        raw_file="raw/stocks/dfpd_fci_stock_position.pdf",
        quality_note="National Central Pool value, not Punjab.",
    )
    assert item.state is None
    assert item.geographic_coverage == "India Central Pool"
    serialized = item.model_dump()
    assert serialized["state"] is None


def test_procurement_response_invariants():
    """ProcurementResponse must declare cannot_be_summed=True and is_time_series=False."""
    resp = ProcurementResponse(
        total=3,
        as_of_date="2025-05-15",
        state="Punjab",
        cannot_be_summed=True,
        is_time_series=False,
        temporal_basis_warning="Cannot be summed",
        items=[
            ProcurementObservationItem(
                observation_date="2025-05-15",
                state="Punjab",
                commodity="Wheat",
                season="RMS 2025-26",
                measure_name="season_estimate",
                measure_value=124.0,
                measure_unit="Lakh Metric Tonnes (LMT)",
                temporal_basis="seasonal_target_estimate",
                reporting_agency="CFPP",
                source_url="https://cfpp.nic.in/",
                retrieval_date_utc="20261021T191516Z",
                quality_note="Seasonal target estimate",
            )
        ]
    )
    assert resp.cannot_be_summed is True
    assert resp.is_time_series is False
    assert len(resp.items) == 1


def test_production_item_preserves_null_cells():
    """Fazilka / Pathankot historical null cells must be accepted as None."""
    item = DistrictProductionItem(
        source_id="des_apy_query_phase3",
        state="Punjab",
        district_original="Fazilka",
        district_id=None,
        district_id_candidate="651",
        district_mapping_status="candidate",
        crop_original="Wheat",
        crop_standard="wheat",
        season="Rabi",
        agricultural_year="2018-19",
        calendar_year=None,
        area_value=None,
        area_unit="hectares",
        production_value=None,
        production_unit="tonnes",
        yield_value=None,
        yield_unit="kg/ha",
        observation_status="MISSING_IN_SOURCE",
        source_url="https://data.desagri.gov.in/",
        source_file="raw/des_apy.json",
        quality_note="Missing cell in official table",
    )
    assert item.area_value is None
    assert item.production_value is None
    assert item.yield_value is None
    assert item.calendar_year is None


def test_weather_observation_item_numeric_validation():
    """WeatherObservationItem must validate numeric bounds."""
    item = WeatherObservationItem(
        observation_date="2024-06-15",
        state="Punjab",
        station_name="Ludhiana",
        agro_climatic_zone="Central Plain Zone",
        latitude=30.9,
        longitude=75.85,
        temperature_mean_c=34.5,
        precipitation_mm_day=12.2,
        relative_humidity_pct=55.0,
        source_dataset="NASA POWER MERRA-2",
        source_url="https://power.larc.nasa.gov/",
        retrieval_date_utc="20261021T191429Z",
    )
    assert item.temperature_mean_c == 34.5
    assert item.precipitation_mm_day == 12.2


def test_source_registry_item_status_validation():
    """SourceRegistryItem must enforce valid evidence status."""
    item = SourceRegistryItem(
        source_id="emandikaran_pb",
        source_name="Punjab Mandi Board",
        url="https://api.emandikaran-pb.in/",
        category="State APMC Marketing Authority",
        protocol_or_method="REST GET",
        auth_type="None (Public)",
        live_status_code="200",
        observations_acquired=3892,
        arrival_quantity_exposed="YES",
        prices_exposed="YES",
        operational_blockers="None for produce. Foodgrains routed to separate Anaaj Kharid infrastructure.",
        final_verdict="VERIFIED_WORKING_DATA_ACQUIRED",
        evidence_status="working-tested",
        next_legitimate_step="Use for produce; do not expect wheat/paddy arrivals.",
    )
    assert item.evidence_status == "working-tested"

    # Invalid status enum must fail validation
    with pytest.raises(ValidationError):
        SourceRegistryItem(
            source_id="test_invalid",
            source_name="Invalid Source",
            url="https://invalid.com",
            category="Test",
            protocol_or_method="GET",
            auth_type="None",
            live_status_code="200",
            observations_acquired=0,
            arrival_quantity_exposed="NO",
            prices_exposed="NO",
            operational_blockers="None",
            final_verdict="TEST",
            evidence_status="invalid_fake_status_not_allowed",  # type: ignore
            next_legitimate_step="None",
        )
