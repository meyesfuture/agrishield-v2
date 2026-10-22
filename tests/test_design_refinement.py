"""
Design Refinement Verification Suite: Google Material-inspired Light UI,
Data-Rich Minimal Scope, 4 Meaningful Visualizations, and Verified Integrity.
"""

from pathlib import Path
import pytest

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
FRONTEND_SRC = Path(__file__).resolve().parent.parent / "frontend" / "src"
DASHBOARD_CSS = FRONTEND_SRC / "styles" / "dashboard.css"
TOKENS_CSS = FRONTEND_SRC / "styles" / "tokens.css"


class TestGoogleMaterialLightDesign:
    """Verifies light theme tokens, restrained agricultural green, and wheat gold accents."""

    def test_light_theme_tokens(self):
        tokens = TOKENS_CSS.read_text(encoding="utf-8")
        assert "--bg-canvas: #f8fafc" in tokens or "#f8fafc" in tokens
        assert "--bg-surface: #ffffff" in tokens or "#ffffff" in tokens
        assert "--color-green-700: #15803d" in tokens
        assert "--color-green-800: #166534" in tokens
        assert "--color-wheat" in tokens
        assert "--color-amber" in tokens
        # Material Design 3 Core Roles
        assert "--md-sys-color-primary: #0b57d0" in tokens
        assert "--md-sys-color-primary-container: #d3e3fd" in tokens
        assert "--md-sys-color-surface: #fdfcff" in tokens
        assert "--md-sys-elevation-1" in tokens
        assert "--md-sys-shape-full: 9999px" in tokens

    def test_accessible_focus_and_reduced_motion(self):
        css = DASHBOARD_CSS.read_text(encoding="utf-8")
        assert ":focus-visible" in css
        assert "prefers-reduced-motion" in css
        assert "var(--md-sys-color-primary)" in css


class TestMaterialDesign3Specification:
    """Verifies that design.md adheres strictly to Material Design 3 Light Mode rules."""

    def test_design_docs_exist_and_contain_m3_tokens(self):
        root = Path(__file__).resolve().parent.parent
        design_md = root / "design.md"
        assert design_md.exists(), "design.md must exist in repository root"
        content = design_md.read_text(encoding="utf-8")

        # Key M3 Sections
        assert "Material Design 3" in content
        assert "Light Mode" in content
        assert "#0b57d0" in content  # Google Blue primary
        assert "#d3e3fd" in content  # Primary container
        assert "#fdfcff" in content  # Surface
        assert "M3 Elevation Levels" in content
        assert "M3 Corner Radii" in content
        assert "Typography Hierarchy" in content
        assert "Interactive Map" in content




class TestCompactTopBarAndSummaryMetrics:
    """Verifies compact top bar and meaningful summary metrics on Dashboard."""

    def test_top_bar_indicators_in_distribution(self):
        dashboard_html = (FRONTEND_DIST / "dashboard" / "index.html").read_text(encoding="utf-8")
        landing_html = (FRONTEND_DIST / "index.html").read_text(encoding="utf-8")

        for html in [dashboard_html, landing_html]:
            assert "DES APY 2022-23" in html
            assert "23/23 Districts" in html
            assert "PUNJAB GRAINWATCH" in html

    def test_summary_metrics_in_dashboard(self):
        html = (FRONTEND_DIST / "dashboard" / "index.html").read_text(encoding="utf-8")
        assert "Usable Observation Basins" in html
        assert "23 Districts • 11 Mandis" in html
        assert "Locations Flagged for Investigation" in html
        assert "0 Flagged" in html
        assert "District Geographic Coverage" in html
        assert "23 / 23 Districts" in html
        assert "Verified Physical Observations" in html
        assert "6,692" in html


class TestFourMeaningfulVisualizations:
    """Verifies that the 4 specific analytical charts exist and have documented provenance."""

    def test_charts_exist_in_source_component(self):
        source = (FRONTEND_SRC / "components" / "DashboardView.tsx").read_text(encoding="utf-8")

        # Chart 1: Historical Trend
        assert "Historical Wheat Productivity Series" in source
        assert "kg/ha" in source
        assert "Chart 1 Quality & Provenance Disclosure" in source

        # Chart 2: Basin Comparison
        assert "Cross-District Wheat Production Comparison" in source
        assert "Metric Tonnes" in source
        assert "Chart 2 Quality & Provenance Disclosure" in source

        # Chart 3: Evidence Breakdown
        assert "Screening Evidence Breakdown" in source
        assert "7-Point Eligibility Gate" in source
        assert "Chart 3 Quality & Provenance Disclosure" in source

        # Chart 4: Supply Coverage Matrix
        assert "Institutional Data Coverage & Freshness Matrix" in source
        assert "8 Dimensions" in source
        assert "Chart 4 Quality & Provenance Disclosure" in source

    def test_six_point_methodology_disclosures_present(self):
        source = (FRONTEND_SRC / "components" / "DashboardView.tsx").read_text(encoding="utf-8")
        assert "Question Answered:" in source
        assert "Source Dataset:" in source or "Source Datasets:" in source or "Source:" in source
        assert "Calculation:" in source
        assert "Supported Conclusion:" in source
        assert "Unsupported Conclusion:" in source


class TestLandingPageLivePreview:
    """Verifies the authentic interactive dashboard preview on the landing page."""

    def test_landing_preview_section(self):
        html = (FRONTEND_DIST / "index.html").read_text(encoding="utf-8")
        assert "Interactive Screening Workspace" in html
        assert "Ludhiana" in html
        assert "INSUFFICIENT DATA TO ASSESS RISK" in html
        assert "Open Full Interactive Dashboard" in html
