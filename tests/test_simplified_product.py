"""
Dedicated Verification Suite for Simplified Punjab GrainWatch.
Tests the core interaction flow:
Landing Page (/) -> Dashboard (/dashboard) -> Select Location -> Understand Evidence & Potential Risk.
"""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.main import app

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
FRONTEND_SRC = Path(__file__).resolve().parent.parent / "frontend" / "src"
PUBLIC_DATA = Path(__file__).resolve().parent.parent / "frontend" / "public" / "data"


@pytest.fixture
def client():
    return TestClient(app)


class TestCoreProductScope:
    """Verifies that the product surface area is strictly limited to the two core experiences."""

    def test_only_two_pages_exist_in_source(self):
        pages_dir = FRONTEND_SRC / "pages"
        pages = list(pages_dir.glob("*.astro"))
        page_names = sorted([p.name for p in pages])
        assert page_names == ["dashboard.astro", "index.astro"], (
            f"Expected exactly ['dashboard.astro', 'index.astro'], got {page_names}"
        )

    def test_only_two_pages_exist_in_distribution(self):
        dist_html_files = [
            p.relative_to(FRONTEND_DIST).as_posix()
            for p in FRONTEND_DIST.glob("**/*.html")
        ]
        assert "index.html" in dist_html_files
        assert "dashboard/index.html" in dist_html_files
        # Verify no secondary modules exist
        forbidden_routes = [
            "analytics/index.html",
            "datasets/index.html",
            "market-watch/index.html",
            "weather/index.html",
            "procurement-stocks/index.html",
            "district-map/index.html",
            "status/index.html",
            "methodology/index.html",
            "production-yield/index.html",
        ]
        for route in forbidden_routes:
            assert route not in dist_html_files, f"Found forbidden route in dist: {route}"


class TestLandingPageExperience:
    """Tests Landing page requirements: Name, Purpose, CTA, Visual, Explanations, Footer."""

    def test_landing_page_elements(self):
        html = (FRONTEND_DIST / "index.html").read_text(encoding="utf-8")
        
        # 1. Product name and purpose
        assert "PUNJAB GRAINWATCH" in html
        assert "Grain-Hoarding Risk" in html
        
        # 2. Primary CTA: Open Dashboard
        assert 'href="/dashboard"' in html
        assert "Open Dashboard" in html
        
        # 3. Agricultural visual
        assert "hero-visual" in html
        
        # 4. Explanations of how system works
        assert "How Potential Risk Screening Works" in html
        assert "Geospatial Mapping" in html
        assert "7-Point Qualification Gate" in html
        assert "Explainable Assessment" in html
        
        # 5. Clean footer
        assert "app-footer" in html
        assert "AGENTS.md Rule 6" in html


class TestDashboardExperience:
    """Tests Dashboard requirements: Map, Location Markers, Assessment Panel, Insufficient Data."""

    def test_dashboard_elements(self):
        html = (FRONTEND_DIST / "dashboard/index.html").read_text(encoding="utf-8")
        
        # 1. Interactive map container
        assert "Interactive Punjab Map" in html
        assert "map-panel" in html
        
        # 2. Selected location panel
        assert "assessment-panel" in html
        assert "Location Assessment" in html
        
        # 3. Insufficient data to assess risk
        assert "INSUFFICIENT DATA TO ASSESS RISK" in html
        assert "insufficient empirical data" in html.lower()
        
        # 4. Governance limitations & missing prerequisites
        assert "Zero Wheat/Paddy Market Arrivals" in html
        assert "100% Null Arrival Volumes" in html
        assert "Unmeasured Private Warehousing" in html
        
        # 5. Verified observations present in panel
        assert "Agricultural Production &amp; Yield" in html or "Agricultural Production & Yield" in html
        assert "Wholesale APMC Mandi Market Prices" in html
        assert "Agrometeorological Monitoring" in html

    def test_district_geojson_contains_23_districts(self):
        boundaries_file = PUBLIC_DATA / "district_boundaries.json"
        assert boundaries_file.exists()
        with open(boundaries_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["features"]) == 23

    def test_location_assessment_never_claims_hoarding_detected(self):
        dashboard_component = (FRONTEND_SRC / "components" / "DashboardView.tsx").read_text(encoding="utf-8")
        assert "INSUFFICIENT DATA TO ASSESS RISK" in dashboard_component
        assert "hoarding detected" not in dashboard_component.lower()
        assert "trader rank" not in dashboard_component.lower()
        assert "hoarder ranking" not in dashboard_component.lower()


class TestBackendEndpointsPreserved:
    """Confirms that backend endpoints and data services were preserved."""

    def test_health_endpoint(self, client):
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

    def test_geo_districts_endpoint(self, client):
        res = client.get("/api/v1/geo/districts")
        assert res.status_code == 200
        assert len(res.json()["features"]) == 23

    def test_prices_endpoint(self, client):
        res = client.get("/api/v1/markets/prices?limit=10")
        assert res.status_code == 200
        assert len(res.json()["items"]) > 0

    def test_production_endpoint(self, client):
        res = client.get("/api/v1/production?limit=10")
        assert res.status_code == 200
        assert len(res.json()["items"]) > 0
