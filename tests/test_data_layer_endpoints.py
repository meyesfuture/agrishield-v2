"""
Comprehensive integration tests for Punjab GrainWatch Data Layer API endpoints.
Tests query filters, pagination, domain guardrails, null preservation,
and blocked provider handling. Zero external internet dependencies.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# -----------------------------------------------------------------------------
# 1. Supply Flow Coverage Matrix (/api/v1/coverage)
# -----------------------------------------------------------------------------
def test_get_coverage_matrix(client):
    """GET /api/v1/coverage returns 8-element matrix and NO-GO verdict."""
    response = client.get("/api/v1/coverage")
    assert response.status_code == 200
    data = response.json()
    assert data["total_elements"] == 8
    assert len(data["items"]) == 8
    assert "NO-GO" in data["reconciliation_overall_verdict"]
    assert data["critical_gaps_count"] >= 5


# -----------------------------------------------------------------------------
# 2. District Crop Production (/api/v1/production)
# -----------------------------------------------------------------------------
def test_get_production_all_and_pagination(client):
    """GET /api/v1/production returns 230 rows and supports pagination."""
    response = client.get("/api/v1/production?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 230
    assert len(data["items"]) == 10
    assert data["limit"] == 10
    assert data["offset"] == 0


def test_get_production_filters(client):
    """GET /api/v1/production filter by crop, district, and year."""
    # Filter by crop=wheat
    resp_wheat = client.get("/api/v1/production?crop=wheat")
    assert resp_wheat.status_code == 200
    wheat_data = resp_wheat.json()
    assert wheat_data["total"] == 115
    assert all(i["crop_standard"] == "wheat" for i in wheat_data["items"])

    # Filter by crop=rice
    resp_rice = client.get("/api/v1/production?crop=rice")
    assert resp_rice.status_code == 200
    rice_data = resp_rice.json()
    assert rice_data["total"] == 115
    assert all("paddy" in i["crop_standard"] or "rice" in i["crop_standard"] for i in rice_data["items"])

    # Filter by district=Amritsar
    resp_dist = client.get("/api/v1/production?district=Amritsar")
    assert resp_dist.status_code == 200
    dist_data = resp_dist.json()
    assert dist_data["total"] == 10  # 5 years x 2 crops
    assert all(i["district_original"].lower() == "amritsar" for i in dist_data["items"])


def test_production_null_preservation_and_calendar_year():
    """Missing cells in production must serialize as null, and calendar_year must be null."""
    with TestClient(app) as client:
        # Malerkotla in 2020-21 has null production in source
        response = client.get("/api/v1/production?district=Malerkotla&agricultural_year=2020-21")
        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) > 0
        # Verify null values are preserved (None)
        malerkotla = items[0]
        assert malerkotla["production_value"] is None
        assert malerkotla["area_value"] is None
        assert malerkotla["yield_value"] is None
        assert malerkotla["calendar_year"] is None


# -----------------------------------------------------------------------------
# 3. Crop Yield History (/api/v1/yields)
# -----------------------------------------------------------------------------
def test_get_yields_filters_and_pagination(client):
    """GET /api/v1/yields returns yield history and supports filters."""
    response = client.get("/api/v1/yields?district=Gurdaspur&crop=wheat&year_from=2015&year_to=2020")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert item["district_original"].lower() == "gurdaspur"
        assert item["crop_standard"] == "wheat"
        assert "2015" <= item["effective_year"] <= "2020"
        assert item["yield_value"] > 0


# -----------------------------------------------------------------------------
# 4. Mandi Wholesale Prices (/api/v1/markets/prices)
# -----------------------------------------------------------------------------
def test_get_prices_and_null_arrival_quantity_invariant(client):
    """
    CRITICAL DOMAIN TEST:
    GET /api/v1/markets/prices must preserve arrival_quantity as strictly null (None).
    Under NO circumstance may arrival_quantity be converted to 0.0 or 0.
    """
    response = client.get("/api/v1/markets/prices?limit=100")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 53
    assert len(data["items"]) == 53

    # Verify 100% of rows have arrival_quantity IS None
    for item in data["items"]:
        assert item["arrival_quantity"] is None, "Violation: arrival_quantity was converted to non-null!"
        assert item["arrival_unit"] is None
        assert item["modal_price"] > 0.0
        assert item["commodity_name"] in ("Paddy(Common)", "Paddy(Basmati)")



def test_get_prices_filtered(client):
    """Filter market prices by market_name."""
    response = client.get("/api/v1/markets/prices?market_name=Abohar")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 7
    assert all("Abohar" in i["market_name"] for i in data["items"])


# -----------------------------------------------------------------------------
# 5. Multi-zone Daily Weather (/api/v1/weather)
# -----------------------------------------------------------------------------
def test_get_weather_station_and_date_filter(client):
    """GET /api/v1/weather returns 3,655 rows and filters by station and date."""
    response = client.get("/api/v1/weather?station_name=Ludhiana&date_from=2024-01-01&date_to=2024-01-07")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 7
    assert len(data["items"]) == 7
    for item in data["items"]:
        assert item["station_name"] == "Ludhiana"
        assert item["temperature_mean_c"] is not None
        assert item["precipitation_mm_day"] is not None


# -----------------------------------------------------------------------------
# 6. Government Procurement Snapshot (/api/v1/procurement)
# -----------------------------------------------------------------------------
def test_get_procurement_non_summing_semantics(client):
    """
    CRITICAL DOMAIN TEST:
    GET /api/v1/procurement must declare cannot_be_summed=True and is_time_series=False.
    """
    response = client.get("/api/v1/procurement")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["as_of_date"] == "2025-05-15"
    assert data["state"] == "Punjab"
    assert data["cannot_be_summed"] is True
    assert data["is_time_series"] is False
    assert "temporal_basis_warning" in data

    measure_names = [i["measure_name"] for i in data["items"]]
    assert "season_estimate" in measure_names
    assert "daily_procurement" in measure_names
    assert "progressive_procurement" in measure_names


def test_get_procurement_filter(client):
    """Filter procurement by measure_name."""
    response = client.get("/api/v1/procurement?measure_name=season_estimate")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["measure_value"] == 124.0
    assert data["items"][0]["measure_unit"] == "Lakh Metric Tonnes (LMT)"


# -----------------------------------------------------------------------------
# 7. National Central Pool Stocks (/api/v1/stocks)
# -----------------------------------------------------------------------------
def test_get_stocks_national_scope_and_null_state_invariant(client):
    """
    CRITICAL DOMAIN TEST:
    GET /api/v1/stocks must declare geographic_scope='National Central Pool only'.
    State column must be strictly null (100% of records).
    Must NEVER be labeled as Punjab regional stocks.
    """
    response = client.get("/api/v1/stocks?limit=100")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 100
    assert data["geographic_scope"] == "National Central Pool only"
    assert "punjab_specific_warning" in data

    # Verify 100% of records have state is None
    for item in data["items"]:
        assert item["state"] is None, "Violation: stock state was assigned a non-null value!"
        assert item["geographic_coverage"] == "India Central Pool"
        assert item["agency"] == "DFPD/FCI"


def test_get_stocks_filters(client):
    """Filter stocks by commodity and measure_name."""
    response = client.get("/api/v1/stocks?commodity=wheat&measure_name=actual_central_pool_stock")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 25
    assert all(i["commodity_standard"] == "wheat" for i in data["items"])
    assert all(i["measure_name"] == "actual_central_pool_stock" for i in data["items"])


# -----------------------------------------------------------------------------
# 8. District Boundaries & Crosswalk (/api/v1/geo/districts & /geo/crosswalk)
# -----------------------------------------------------------------------------
def test_get_district_boundaries_geojson(client):
    """GET /api/v1/geo/districts returns FeatureCollection with 23 features."""
    response = client.get("/api/v1/geo/districts")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert data["total_features"] == 23
    assert len(data["features"]) == 23


def test_get_district_boundaries_filter_and_detail(client):
    """Filter district boundaries by name and get single district by ID."""
    # Filter by name
    resp_filter = client.get("/api/v1/geo/districts?name=Amritsar")
    assert resp_filter.status_code == 200
    assert resp_filter.json()["total_features"] == 1

    # Detail by ID (Amritsar has district_id=27)
    resp_detail = client.get("/api/v1/geo/districts/27")
    assert resp_detail.status_code == 200
    feat = resp_detail.json()
    assert feat["type"] == "Feature"
    assert feat["properties"]["dtname"] == "Amritsar"

    # Detail with invalid ID returns 404
    resp_404 = client.get("/api/v1/geo/districts/999999")
    assert resp_404.status_code == 404


def test_get_district_crosswalk(client):
    """GET /api/v1/geo/crosswalk returns 23 crosswalk mappings with caveats."""
    response = client.get("/api/v1/geo/crosswalk")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 23
    assert len(data["items"]) == 23

    # Verify Sangrur / Malerkotla temporal notes
    malerkotla = next(i for i in data["items"] if i["district_name_boundary"] == "Malerkotla")
    assert "2022" in malerkotla["temporal_note"]


# -----------------------------------------------------------------------------
# 9. API Source Registry (/api/v1/sources)
# -----------------------------------------------------------------------------
def test_get_sources_and_evidence_statuses(client):
    """GET /api/v1/sources returns all 10 sources with evidence-based statuses."""
    response = client.get("/api/v1/sources")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert data["working_tested_count"] >= 3
    assert data["blocked_count"] >= 3
    assert data["offline_guarantee"] is not None


def test_get_source_detail_working_and_blocked(client):
    """GET /api/v1/sources/{source_id} for working and blocked sources."""
    # Working source
    resp_work = client.get("/api/v1/sources/emandikaran_pb")
    assert resp_work.status_code == 200
    work = resp_work.json()
    assert work["evidence_status"] == "working-tested"

    # Blocked auth source
    resp_auth = client.get("/api/v1/sources/data_gov_in_ogd")
    assert resp_auth.status_code == 200
    auth = resp_auth.json()
    assert auth["evidence_status"] == "blocked-auth"
    assert "data.gov.in" in auth["next_legitimate_step"]

    # TLS verification blocked source
    resp_tls = client.get("/api/v1/sources/des_agri_gov_in")
    assert resp_tls.status_code == 200
    tls = resp_tls.json()
    assert tls["evidence_status"] == "unavailable"
    assert "root CA" in tls["next_legitimate_step"]

    # Invalid source returns 404
    resp_404 = client.get("/api/v1/sources/fake_nonexistent_source")
    assert resp_404.status_code == 404


# -----------------------------------------------------------------------------
# 10. Data Quality Issues (/api/v1/quality/issues)
# -----------------------------------------------------------------------------
def test_get_quality_issues_and_severities(client):
    """GET /api/v1/quality/issues returns empirical audit issues."""
    response = client.get("/api/v1/quality/issues")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 6
    assert data["severity_breakdown"]["CRITICAL"] >= 3

    # Filter by severity=CRITICAL
    resp_crit = client.get("/api/v1/quality/issues?severity=CRITICAL")
    assert resp_crit.status_code == 200
    crit = resp_crit.json()
    assert all(i["severity"] == "CRITICAL" for i in crit["items"])


# -----------------------------------------------------------------------------
# 11. Methodology & Anti-Hoarding Charter (/api/v1/methodology)
# -----------------------------------------------------------------------------
def test_get_methodology_anti_hoarding(client):
    """GET /api/v1/methodology returns anti-hoarding charter and data contracts."""
    response = client.get("/api/v1/methodology")
    assert response.status_code == 200
    data = response.json()
    assert "statistical anomaly is strictly an audit prompt" in data["anti_hoarding_charter"].lower()
    assert len(data["core_principles"]) >= 5
    assert "mandi_arrivals" in data["data_contracts"]


# -----------------------------------------------------------------------------
# 12. Edge Cases and Filter Validation
# -----------------------------------------------------------------------------
def test_pagination_validation_errors(client):
    """Invalid limit or offset values must return 422 Unprocessable Entity."""
    # limit = 0 is invalid (ge=1)
    resp_0 = client.get("/api/v1/production?limit=0")
    assert resp_0.status_code == 422

    # limit > 500 is invalid (le=500)
    resp_huge = client.get("/api/v1/production?limit=501")
    assert resp_huge.status_code == 422

    # negative offset is invalid (ge=0)
    resp_neg = client.get("/api/v1/production?offset=-1")
    assert resp_neg.status_code == 422


def test_unknown_filter_yields_empty_items_gracefully(client):
    """Filtering by an unknown string should return total=0 and items=[], not 500."""
    response = client.get("/api/v1/production?district=NonExistentDistrictXYZ")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
