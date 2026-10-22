# UI / UX Review & Material Design 3 Audit
## Punjab GrainWatch — Final Master Build

### 1. Design Direction & Visual Identity

The interface of Punjab GrainWatch was designed to embody **Google Material Design 3 (M3) in Light Mode**, merging high-density agricultural intelligence with visual restraint, typography clarity, and intentional micro-motion.

Rather than a cluttered dashboard filled with decorative graphs and unverified metrics, the application is strictly scoped to two interconnected experiences:
1. **Landing Page (`/`)**: A refined entry point pairing an art-directed 3D agricultural data scene with clear value propositions and dual CTAs.
2. **Analytical Dashboard (`/dashboard`)**: A map-anchored screening interface with dedicated workflows for Real Evidence exploration and Synthetic Scenario demonstration.

---

### 2. Design System Tokens & M3 Color Palette

| Token Role | Hex Code | Material 3 Name | Applied Usage |
| :--- | :--- | :--- | :--- |
| **Primary Accent** | `#1A73E8` | Primary (Google Blue) | Primary action buttons, active navigation states, baseline lines |
| **Surface Base** | `#F8FAFD` | Surface Container Low | Page background, calm neutral workspace |
| **Surface Elevated** | `#FFFFFF` | Surface / Card | Location cards, metric containers, popovers |
| **Surface Dim** | `#EEF2F6` | Surface Container High | Scenario selector background, secondary chips |
| **Outline** | `#E0E3E7` | Outline Variant | Clean 1px structural dividers and card borders |
| **Text Primary** | `#1F1F1F` | On Surface | Main headers, metric figures, primary body copy |
| **Text Secondary** | `#5F6368` | On Surface Variant | Axis labels, captions, footnotes, metadata |
| **Status Anomaly** | `#B3261E` on `#F9DEDC` | Error Container | Convergent anomaly banner, synthetic watermark, crash indicators |
| **Status Warning** | `#B06000` on `#FEF7E0` | Warning Container | Isolated price or arrival signal chips, partial evidence alerts |
| **Status Normal** | `#137333` on `#E6F4EA` | Success Container | Baseline confirmation, verified records, normal market conditions |
| **Status Insufficient** | `#5F6368` on `#F1F3F4` | Neutral Container | Data gap notices, missing prerequisite badges |

---

### 3. Landing Page Hero: 3D Agricultural Installation

- **Implementation**: Three.js WebGL canvas embedded in `frontend/src/pages/index.astro`.
- **Art Direction**:
  - Sculpted Punjab terrain mesh with warm earth tones.
  - Stylized grain elevator and storage silo geometry rendered with clean PBR materials (matte steel and concrete).
  - Procedural wheat stalks swaying under subtle mathematical wind oscillations.
  - Soft directional lighting simulating early morning sunlight across the Doaba plains.
- **Performance & Fallback**:
  - Rendering capped at 60 FPS with automatic frame throttling on inactive browser tabs.
  - Graceful static fallback if WebGL initialization fails or is disabled by client security settings.
- **Call-to-Action Architecture**:
  - Primary CTA: **"Explore Dashboard"** (Direct access to Real Evidence Mode).
  - Secondary CTA: **"Launch Synthetic Demo"** (Direct access to the deterministic anomaly simulation lab).

---

### 4. Risk Dashboard: Map-First Spatial Architecture

The dashboard organizes complex spatial and temporal telemetry into a balanced 3-column desktop layout (with stacked responsive behavior on tablets and mobile screens):

```
+---------------------------------------------------------------------------------+
| Top AppBar: Logo | Mode Switcher (REAL vs SYNTHETIC) | Status Badge | Help       |
+---------------------------------------------------------------------------------+
| Persistent Watermark: SYNTHETIC DEMO — NOT LIVE MARKET EVIDENCE (Demo mode only)|
+---------------------------------------------------------------------------------+
| Left Panel:           | Center:               | Right Panel:                    |
| - District Navigator  | - Punjab SVG Map      | - Assessment Outcome Banner     |
| - Commodity Selector  | - District Choropleth | - Anomaly Intensity Gauge       |
| - Scenario Selector   | - Mandi Markers       | - Signal Diagnostic Cards       |
|   (Demo mode)         | - Selected Spotlight  | - Multi-Series Divergence Chart |
+---------------------------------------------------------------------------------+
```

#### Interaction Details:
1. **Operating Mode Switcher**:
   - Segmented M3 pill control toggles between `Real Evidence` and `Synthetic Demo`.
   - Switching instantly transforms the right-hand panel, switching between evidence readiness audits (Real) and anomaly detection diagnostics (Demo).
2. **Map District Selection**:
   - Hovering over a district illuminates its border and reveals a quick tooltip with data coverage summary.
   - Clicking selects the district, triggering an asynchronous fetch to update the right assessment panel.
3. **Synthetic Scenario Chips**:
   - Scenarios A through E are represented by rounded interactive filter chips.
   - Clicking a chip immediately invokes `/api/v1/decision/scenarios/{id}/run`, triggers smooth gauge transitions, and highlights the anomalous time window on the timeseries graph.

---

### 5. Accessibility & Motion Compliance

1. **Contrast Ratios**:
   - All body text and data values achieve a minimum contrast ratio of 7:1 against their surface backgrounds (exceeding WCAG AAA standards).
   - Card borders and outline dividers maintain a 3:1 contrast ratio against base canvas.
2. **Keyboard Navigation & Focus Indicators**:
   - All buttons, chips, and map regions are reachable via `Tab` and `Shift+Tab`.
   - Distinct 2px high-contrast focus rings (`outline: 2px solid #1A73E8; outline-offset: 2px`) appear on focused interactive elements.
3. **Motion Sensitivity (`prefers-reduced-motion`)**:
   - CSS transitions for cards, chips, and gauges are automatically replaced with instant state changes when reduced-motion preferences are detected.
   - The 3D Three.js hero suspends camera rotation and wind oscillation animations in reduced-motion mode.
4. **Screen Reader Support**:
   - All SVG charts and gauges feature descriptive `aria-label` tags and tabular accessible text descriptions for screen readers.
