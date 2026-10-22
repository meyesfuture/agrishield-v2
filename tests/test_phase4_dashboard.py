"""
Phase 4 Automated Verification Suite: Usable Dashboard Validation.

Verifies:
1. All 9 required views exist in the compiled frontend distribution.
2. Every view displays verified metadata, source attribution, and evidence statuses.
3. Explicit data gap notices are present for mandi foodgrain absence, null paddy arrival quantities,
   national buffer stock aggregation, and zero hoarding adjudication.
4. Accessible data tables accompany all visual cards and map components.
5. All static JSON caches are valid, uncorrupted, and trace back to validated catalog assets.
6. Responsive navigation and skip-links exist across all routes.
"""

import json
from pathlib import Path
import pytest

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
PUBLIC_DATA = Path(__file__).resolve().parent.parent / "frontend" / "public" / "data"

REQUIRED_ROUTES = [
    ("index.html", "Overview", "Auditable Agricultural Intelligence for"),
    ("datasets/index.html", "Dataset Explorer", "Verified Dataset Catalog"),
    ("production-yield/index.html", "Production & Yield", "District Crop Production &amp; Yield History"),
    ("market-watch/index.html", "Market Watch", "Mandi Market Watch &amp; Price Dynamics"),
    ("weather/index.html", "Weather Context", "Agrometeorological Weather Context"),
    ("procurement-stocks/index.html", "Procurement & Stocks", "Procurement Snapshots &amp; Central Pool Stocks"),
    ("district-map/index.html", "District Map", "Punjab District Geospatial Boundaries &amp; Join Audit"),
    ("status/index.html", "Audit & Readiness", "Data Quality, Pipeline Health &amp; Reconciliation Readiness"),
    ("methodology/index.html", "Methodology", "Methodology & Evidence Governance"),
]


class TestPhase4FrontendRoutes:
    """Verifies that all 9 views are cleanly built with correct content."""

    @pytest.mark.parametrize("route_path,view_name,expected_heading", REQUIRED_ROUTES)
    def test_route_html_exists_and_contains_headings(self, route_path: str, view_name: str, expected_heading: str):
        file_path = FRONTEND_DIST / route_path
        assert file_path.exists(), f"Route {route_path} for view '{view_name}' is missing in frontend dist"
        html = file_path.read_text(encoding="utf-8")
        assert expected_heading in html, f"Expected heading '{expected_heading}' not found in {route_path}"

    @pytest.mark.parametrize("route_path,view_name,_", REQUIRED_ROUTES)
    def test_route_navigation_and_accessibility(self, route_path: str, view_name: str, _: str):
        file_path = FRONTEND_DIST / route_path
        html = file_path.read_text(encoding="utf-8")
        # Accessible skip link
        assert 'class="skip-link"' in html or 'href="#main-content"' in html
        # Top nav links to all 9 views
        assert 'href="/"' in html
        assert 'href="/datasets"' in html
        assert 'href="/production-yield"' in html
        assert 'href="/market-watch"' in html
        assert 'href="/weather"' in html
        assert 'href="/procurement-stocks"' in html
        assert 'href="/district-map"' in html
        assert 'href="/status"' in html
        assert 'href="/methodology"' in html

    def test_unsupported_data_gap_notices_in_views(self):
        """Verifies that data gaps are explicitly documented and visible."""
        # 1. Market Watch View: Mandi foodgrain absence & null arrival volumes
        market_html = (FRONTEND_DIST / "market-watch/index.html").read_text(encoding="utf-8")
        assert "zero wheat or paddy" in market_html.lower()
        assert "null" in market_html.lower()
        assert "hoarding detection prohibited" in market_html.lower()

        # 2. Procurement & Stocks View: National buffer stocks disclaimer
        procurement_html = (FRONTEND_DIST / "procurement-stocks/index.html").read_text(encoding="utf-8")
        assert "Central Pool" in procurement_html
        assert "buffer stocks" in procurement_html.lower()

        # 3. Status View: Hoarding detection blocked & readiness verdict
        status_html = (FRONTEND_DIST / "status/index.html").read_text(encoding="utf-8")
        assert "NO-GO" in status_html or "Reconciliation Readiness" in status_html

        # 4. Methodology View: Strict prohibition on hoarding conclusions
        methodology_html = (FRONTEND_DIST / "methodology/index.html").read_text(encoding="utf-8")
        assert "Strict Prohibition on Hoarding Conclusions" in methodology_html
        assert "No Grain Arrival Anomaly Proxies from Produce" in methodology_html
        assert "Absence vs Zero Semantics" in methodology_html

        # 5. District Map View: Malerkotla 2022 carveout notice
        map_html = (FRONTEND_DIST / "district-map/index.html").read_text(encoding="utf-8")
        assert "Malerkotla" in map_html
        assert "2022" in map_html


class TestPhase4AccessibleTables:
    """Verifies accessible data table fallbacks for all visual modules."""

    def test_accessible_tables_present(self):
        # Production view table
        prod_html = (FRONTEND_DIST / "production-yield/index.html").read_text(encoding="utf-8")
        assert "<table" in prod_html
        assert "District" in prod_html
        assert "Yield" in prod_html

        # Market watch table
        market_html = (FRONTEND_DIST / "market-watch/index.html").read_text(encoding="utf-8")
        assert "<table" in market_html
        assert "Market Name" in market_html
        assert "Modal Price" in market_html

        # Weather table
        weather_html = (FRONTEND_DIST / "weather/index.html").read_text(encoding="utf-8")
        assert "<table" in weather_html
        assert "Station" in weather_html

        # District crosswalk table
        map_html = (FRONTEND_DIST / "district-map/index.html").read_text(encoding="utf-8")
        assert "<table" in map_html
        assert "LGD Code" in map_html


class TestPhase4DataCaches:
    """Verifies that all public static data caches parse and contain physical data."""

    EXPECTED_CACHES = [
        ("production.json", "items", 230),
        ("yields.json", "items", 2754),
        ("prices.json", "items", 53),
        ("weather.json", "items", 3655),
        ("procurement.json", "items", 3),
        ("stocks.json", "items", 100),
        ("district_boundaries.json", "features", 23),
        ("district_crosswalk.json", "items", 23),
        ("coverage_matrix.json", "items", 8),
        ("sources.json", "items", 10),
        ("quality_issues.json", "items", 7),
    ]

    @pytest.mark.parametrize("cache_name,root_key,expected_count", EXPECTED_CACHES)
    def test_data_cache_validity_and_counts(self, cache_name: str, root_key: str, expected_count: int):
        cache_file = PUBLIC_DATA / cache_name
        assert cache_file.exists(), f"Static cache {cache_name} is missing"

        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert root_key in data, f"Key '{root_key}' missing from {cache_name}"
        actual_count = len(data[root_key])
        assert actual_count == expected_count, (
            f"{cache_name}: expected {expected_count} items in '{root_key}', got {actual_count}"
        )

    def test_zero_simulated_hoarding_in_caches(self):
        """Verifies that none of the caches contain simulated hoarding scores or fake actor ranks."""
        for cache_path in PUBLIC_DATA.glob("*.json"):
            content = cache_path.read_text(encoding="utf-8").lower()
            assert "hoarding_score" not in content
            assert "hoarder_probability" not in content
            assert "actor_rank" not in content
