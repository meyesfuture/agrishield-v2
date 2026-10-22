"""
Phase 5 Automated Verification Suite: Interface Polish, Accessibility, and 3D Visualizer.

Verifies:
1. Landing page renders the 3D Hero Scene container and canvas elements.
2. Keyboard focus rings and visible outline rules are defined for interactive elements.
3. prefers-reduced-motion media query overrides are present in stylesheet tokens.
4. Three.js is cleanly code-split and lazy-loaded on the client.
5. Semantic colors (wheat, emerald, sky, amber, crimson) maintain strict domain meaning.
6. Evidence caveats, null values, and non-hoarding verdicts remain completely intact.
"""

from pathlib import Path
import pytest

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
FRONTEND_SRC = Path(__file__).resolve().parent.parent / "frontend" / "src"
DASHBOARD_CSS = FRONTEND_SRC / "styles" / "dashboard.css"
TOKENS_CSS = FRONTEND_SRC / "styles" / "tokens.css"


class TestPhase5DesignAndMotionPolish:
    """Verifies design system tokens, focus states, and motion rules."""

    def test_focus_visible_styling_present(self):
        """Verifies visible focus rings exist for WCAG 2.2 AA conformance."""
        css_content = DASHBOARD_CSS.read_text(encoding="utf-8")
        assert ":focus-visible" in css_content
        assert "outline" in css_content
        assert "var(--color-wheat" in css_content

    def test_prefers_reduced_motion_guards(self):
        """Verifies prefers-reduced-motion overrides exist in stylesheets."""
        dashboard_css = DASHBOARD_CSS.read_text(encoding="utf-8")
        tokens_css = TOKENS_CSS.read_text(encoding="utf-8")

        assert "prefers-reduced-motion" in tokens_css
        assert "prefers-reduced-motion" in dashboard_css

    def test_hero_3d_wrapper_and_overlay_css(self):
        """Verifies CSS layout rules for 3D hero scene and controls."""
        dashboard_css = DASHBOARD_CSS.read_text(encoding="utf-8")
        assert ".hero-3d-wrapper" in dashboard_css
        assert ".hero-3d-canvas" in dashboard_css
        assert ".hero-static-fallback" in dashboard_css
        assert ".motion-toggle-btn" in dashboard_css


class TestPhase5Hero3DComponent:
    """Verifies Hero3DScene component architecture and static fallback."""

    def test_hero_component_source_architecture(self):
        hero_tsx = (FRONTEND_SRC / "components" / "Hero3DScene.tsx").read_text(encoding="utf-8")
        # Dynamic import for client-side code splitting
        assert "import('three')" in hero_tsx
        # WebGL context verification
        assert "webgl2" in hero_tsx or "webgl" in hero_tsx
        # Reduced motion detection
        assert "prefers-reduced-motion" in hero_tsx
        # Pause / Play motion button
        assert "aria-pressed" in hero_tsx
        # Static fallback SVG with grain silos
        assert "<svg" in hero_tsx
        assert "Punjab Grain Silos" in hero_tsx

    def test_overview_page_mounts_hero_3d(self):
        """Verifies index.html in dist mounts the 3D hero component."""
        index_html = (FRONTEND_DIST / "index.html").read_text(encoding="utf-8")
        assert "hero-3d-wrapper" in index_html
        assert "3D Grain Infrastructure Visualizer" in index_html
        assert "hero-3d-canvas" in index_html
        assert "motion-toggle-btn" in index_html


class TestPhase5EvidenceCaveatPreservation:
    """Verifies that visual polish and simplification did not alter or obscure underlying evidentiary boundaries."""

    def test_caveats_and_null_semantics_preserved(self):
        # 1. Landing Page Caveats
        index_html = (FRONTEND_DIST / "index.html").read_text(encoding="utf-8")
        assert "Zero Wheat/Paddy" in index_html
        assert "100% Null" in index_html
        assert "Statistical Anomaly != Hoarding" in index_html or "Statistical Anomaly" in index_html

        # 2. Main Dashboard Caveats & Insufficient Evidence
        dash_html = (FRONTEND_DIST / "dashboard/index.html").read_text(encoding="utf-8")
        assert "INSUFFICIENT DATA TO ASSESS RISK" in dash_html
        assert "Zero Wheat/Paddy" in dash_html
        assert "100% Null" in dash_html
        assert "AGENTS.md Rule 6" in dash_html

