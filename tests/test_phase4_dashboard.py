"""
Simplified Dashboard & Landing Page Verification Suite.
Validates the streamlined two-experience architecture:
1. Landing Page (/) -> Open Dashboard CTA, 3D/SVG agricultural visual, how it works, evidentiary boundaries.
2. Main Dashboard (/dashboard) -> Interactive Punjab Map, APMC mandi markers, selected location assessment panel.
3. Insufficient data to assess risk displayed when prerequisites are missing.
4. No removed routes exist in frontend distribution.
5. All public static data caches remain intact and uncorrupted.
"""

import json
from pathlib import Path
import pytest

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
PUBLIC_DATA = Path(__file__).resolve().parent.parent / "frontend" / "public" / "data"

PRIMARY_ROUTES = [
    ("index.html", "Landing Page", "Grain-Hoarding Risk"),
    ("dashboard/index.html", "Main Dashboard", "Interactive Punjab Map"),
]

REMOVED_ROUTES = [
    "datasets/index.html",
    "production-yield/index.html",
    "market-watch/index.html",
    "weather/index.html",
    "procurement-stocks/index.html",
    "district-map/index.html",
    "status/index.html",
    "analytics/index.html",
    "methodology/index.html",
]


class TestSimplifiedFrontendRoutes:
    """Verifies that only the two core experiences are built with correct content."""

    @pytest.mark.parametrize("route_path,view_name,expected_content", PRIMARY_ROUTES)
    def test_primary_route_html_exists_and_contains_content(self, route_path: str, view_name: str, expected_content: str):
        file_path = FRONTEND_DIST / route_path
        assert file_path.exists(), f"Primary route {route_path} for '{view_name}' is missing in frontend dist"
        html = file_path.read_text(encoding="utf-8")
        assert expected_content in html, f"Expected content '{expected_content}' not found in {route_path}"

    def test_landing_page_has_dashboard_cta_and_visual(self):
        index_html = (FRONTEND_DIST / "index.html").read_text(encoding="utf-8")
        # Primary CTA
        assert 'href="/dashboard"' in index_html
        assert "Open Dashboard" in index_html
        # Hero visual container
        assert "hero-visual" in index_html
        # Explainer & boundaries
        assert "How Potential Risk Screening Works" in index_html
        assert "System Boundaries &amp; Governance Limitations" in index_html or "System Boundaries & Governance Limitations" in index_html
        assert "Statistical Anomaly != Hoarding" in index_html or "Statistical Anomaly" in index_html

    def test_dashboard_page_has_map_and_assessment_panel(self):
        dash_html = (FRONTEND_DIST / "dashboard/index.html").read_text(encoding="utf-8")
        # Navigation
        assert 'href="/"' in dash_html
        assert 'href="/dashboard"' in dash_html
        # Map landmarks
        assert "Interactive Punjab Map" in dash_html
        assert "punjab-svg-map" in dash_html or "svg" in dash_html
        # Location assessment panel landmarks
        assert "Location Assessment" in dash_html
        assert "Hoarding Risk Evaluation" in dash_html
        assert "INSUFFICIENT DATA TO ASSESS RISK" in dash_html

    @pytest.mark.parametrize("removed_route", REMOVED_ROUTES)
    def test_removed_routes_do_not_exist_in_dist(self, removed_route: str):
        file_path = FRONTEND_DIST / removed_route
        assert not file_path.exists(), f"Removed route {removed_route} should not exist in frontend dist"

    def test_minimal_top_navigation(self):
        """Verifies that navigation only links to Home and Dashboard."""
        index_html = (FRONTEND_DIST / "index.html").read_text(encoding="utf-8")
        dash_html = (FRONTEND_DIST / "dashboard/index.html").read_text(encoding="utf-8")

        for html in [index_html, dash_html]:
            # Permitted links
            assert 'href="/"' in html
            assert 'href="/dashboard"' in html
            # Removed links should not be present in navigation
            assert 'href="/datasets"' not in html
            assert 'href="/production-yield"' not in html
            assert 'href="/market-watch"' not in html
            assert 'href="/weather"' not in html
            assert 'href="/procurement-stocks"' not in html
            assert 'href="/district-map"' not in html
            assert 'href="/status"' not in html
            assert 'href="/analytics"' not in html
            assert 'href="/methodology"' not in html


class TestSimplifiedDataCaches:
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
