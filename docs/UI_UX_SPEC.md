# UI/UX & Visual Design Specification

## Product character

Blend Apple's editorial restraint and high-quality spatial polish with Google's Material clarity and understandable information hierarchy. The result should feel like a premium scientific/agricultural intelligence product, not a generic admin template.

## Visual principles

- Typography: clear scale, confident display headline, legible compact data typography; use system fonts or properly licensed local fonts.
- Layout: strong spacing rhythm, clear navigation, restrained borders, layered depth and consistent alignment.
- Color: warm grain/earth neutrals with a restrained green and blue information palette. Do not rely on color alone for severity/status; combine text/icons/patterns.
- Glassmorphism: use selectively on hero/navigation/floating overlays. Ensure contrast and readability against dynamic backgrounds.
- Charts: contextual legends, units, dates, missingness, data-source attribution and methodology entry point. Avoid decorative charts without meaning.
- Interaction: every clickable object needs an obvious affordance, focus state, disabled state, hover/pressed state and keyboard support.
- Density: optimize for data exploration; don't force important tables into tiny cards.

## Page map

1. Landing / Overview: full-bleed but controlled 3D grain-field/silo hero; purpose and evidence boundary; summary coverage tiles; data readiness strip; primary `Explore evidence` action.
2. Overview dashboard: latest dataset date, coverage counters, data source statuses, crop and weather highlights.
3. Data Explorer: global search, commodity/date/geography/source filters, detail drawer with schema, source, units, quality issues and download/export where licensing permits.
4. Production & Yield: district/season/crop filters, time series, district comparison and missing-data indicators.
5. Market Watch: paddy modal price observations, no invented arrival series, explicit 7-day period and Rs./quintal.
6. Weather: station selector and variables across five points with observation period and source.
7. Procurement & Stocks: as-of labels, geography level (state or national), grain-form definitions and prominent caveats.
8. District Map: selectable 23 district polygons; show unmapped/old-boundary caveats, don't infer mandi locations.
9. Data Quality & Coverage: required vs acquired panels, blocked sources, test timestamps, missing fields and gaps to eligibility.
10. Methodology / About: definitions, formulas, source list, version, limitations and current GO/NO-GO gate.

## Motion system

- Motion should support continuity: route/page entrance, content reveal, hover feedback, chart transitions, map selection and loading state.
- Use a limited consistent duration/easing scale defined in design tokens.
- Do not animate every number continuously or loop motion without meaning.
- Respect `prefers-reduced-motion`; disable parallax, long transitions and continuous rotation when requested.
- Avoid motion that delays chart readability, causes layout shift or blocks controls.

## Accessibility and resilience

- WCAG-minded contrast, visible focus, semantic landmarks, headings, labels and keyboard navigation.
- Provide table/list alternatives for chart/map insights.
- Handle loading, empty, stale, error, partial and permission-blocked states distinctly.
- Keep critical page content usable if 3D, maps or third-party APIs fail.
- Responsive behavior for desktop, tablet and mobile; test minimum supported viewport.

## Component checklist

`AppShell`, `TopNav`, `SideNav`/mobile nav, `Hero3D`, `MetricCard`, `CoverageBadge`, `SourceProvenance`, `AsOfLabel`, `ChartFrame`, `FilterBar`, `DataTable`, `QualityIssueList`, `EmptyState`, `ErrorState`, `StaleDataBanner`, `SyntheticDataBanner`, `MethodologyDrawer`, `DistrictMap`, `FooterStatus`.
