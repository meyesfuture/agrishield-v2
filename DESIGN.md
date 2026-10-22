# Material Design 3 (M3) Design System Specification: Punjab GrainWatch

**Standard:** Google Material Design 3 (M3) Light Mode Specification  
**Design Direction:** Google-style Blue Accents, Restrained Agricultural Domain Identity, Neutral Tonal Surfaces  
**Reference Implementations:** [Material Design 3 Guidelines](https://m3.material.io/) & [skydashnet/material-design-3-ui-skill](https://github.com/skydashnet/material-design-3-ui-skill)  
**Status:** Living Design System Source of Truth  

---

## 1. Design System Overview & Architectural Guardrails

Punjab GrainWatch is a focused agricultural intelligence screening tool designed to help users explore potential grain-hoarding risk locations across Punjab with rigorous evidentiary governance.

### Core M3 Principles Applied:
1. **Light Mode First:** Built exclusively in high-clarity Material Light theme (`#fdfcff` / `#f8f9fa` canvas with `#ffffff` container surfaces). Zero dark mode or muddy slate surfaces.
2. **Google-Style Primary Blue Accents:** Uses Google's canonical primary blue (`#0b57d0` / `#1a73e8`) for primary actions, navigational focus, and system-level cues, harmonized with agricultural green (`#15803d`) and wheat gold (`#d97706`) secondary/tertiary domain semantics.
3. **Tonal Elevation over Harsh Drop Shadows:** Uses M3 surface elevation levels (`surfaceContainerLowest`, `surfaceContainerLow`, `surfaceContainer`, `surfaceContainerHigh`) with subtle ambient shadows instead of heavy, distracting drop shadows.
4. **Purposeful Components:** Components are chosen strictly by behavior and user task (Filled Buttons for primary actions, Filter Chips for discrete dimensions, Outlined Cards for content grouping).
5. **Strict Evidence Invariant (AGENTS.md Rule 6):** Anomaly != Hoarding. Locations without sufficient arrival quantities and stock telemetry display the M3 Amber Alert badge: `INSUFFICIENT DATA TO ASSESS RISK`.

---

## 2. Complete Material Design 3 Color Token Architecture

The color system follows the M3 tonal role families: Primary (Google Blue), Secondary (Agricultural Green), Tertiary (Wheat Gold), Neutral Surfaces, and Semantic Feedback.

### A. Primary Role Family (Google Blue)
| M3 Token | CSS Variable | Hex Value | Usage / Role |
| :--- | :--- | :--- | :--- |
| `md.sys.color.primary` | `--md-sys-color-primary` | `#0b57d0` | Primary actions, active navigation states, primary focus rings |
| `md.sys.color.on-primary` | `--md-sys-color-on-primary` | `#ffffff` | High-contrast text/icons on primary fill |
| `md.sys.color.primary-container` | `--md-sys-color-primary-container` | `#d3e3fd` | Prominent tonal container emphasis (e.g. selected pills) |
| `md.sys.color.on-primary-container` | `--md-sys-color-on-primary-container` | `#041e49` | Text/icons on primary container |

### B. Secondary Role Family (Agricultural Domain Green)
| M3 Token | CSS Variable | Hex Value | Usage / Role |
| :--- | :--- | :--- | :--- |
| `md.sys.color.secondary` | `--md-sys-color-secondary` | `#15803d` | High-production choropleth scale, verified evidence highlights |
| `md.sys.color.on-secondary` | `--md-sys-color-on-secondary` | `#ffffff` | Text on secondary buttons/badges |
| `md.sys.color.secondary-container` | `--md-sys-color-secondary-container` | `#dcfce7` | Soft agricultural container tint |
| `md.sys.color.on-secondary-container` | `--md-sys-color-on-secondary-container` | `#052e16` | Text on secondary container |

### C. Tertiary Role Family (Wheat Gold Accent)
| M3 Token | CSS Variable | Hex Value | Usage / Role |
| :--- | :--- | :--- | :--- |
| `md.sys.color.tertiary` | `--md-sys-color-tertiary` | `#d97706` | APMC mandi marker pins, wheat yield callouts |
| `md.sys.color.on-tertiary` | `--md-sys-color-on-tertiary` | `#ffffff` | Text on tertiary pins |
| `md.sys.color.tertiary-container` | `--md-sys-color-tertiary-container` | `#fef3c7` | Warm container background for grain observations |
| `md.sys.color.on-tertiary-container` | `--md-sys-color-on-tertiary-container` | `#451a03` | Text on tertiary container |

### D. Neutral Surface Family (M3 Light Surfaces)
| M3 Token | CSS Variable | Hex Value | Usage / Role |
| :--- | :--- | :--- | :--- |
| `md.sys.color.surface` | `--md-sys-color-surface` | `#fdfcff` | Default background surface |
| `md.sys.color.surface-dim` | `--md-sys-color-surface-dim` | `#ded8e1` | Recessed canvas elements |
| `md.sys.color.surface-bright` | `--md-sys-color-surface-bright` | `#fdfcff` | High-luminance cards and popovers |
| `md.sys.color.surface-container-lowest` | `--md-sys-color-surface-container-lowest` | `#ffffff` | Pure white card surfaces and panels |
| `md.sys.color.surface-container-low` | `--md-sys-color-surface-container-low` | `#f8f9fa` | Subtle elevated containers |
| `md.sys.color.surface-container` | `--md-sys-color-surface-container` | `#f1f3f4` | Toolbar background, default container |
| `md.sys.color.surface-container-high` | `--md-sys-color-surface-container-high` | `#e8eaed` | Hovered card state, modal surfaces |
| `md.sys.color.surface-container-highest` | `--md-sys-color-surface-container-highest` | `#dadce0` | Dividers, search bars, active chips |
| `md.sys.color.on-surface` | `--md-sys-color-on-surface` | `#1f1f1f` | Primary text and headings (WCAG AAA contrast) |
| `md.sys.color.on-surface-variant` | `--md-sys-color-on-surface-variant` | `#444746` | Secondary labels, captions, metadata |
| `md.sys.color.outline` | `--md-sys-color-outline` | `#747775` | Input borders, card outlines |
| `md.sys.color.outline-variant` | `--md-sys-color-outline-variant` | `#c4c7c5` | Subtle dividers, inactive borders |

### E. Semantic Feedback Family
| State | Container Color | Text / Accent Color | Purpose |
| :--- | :--- | :--- | :--- |
| **Error / Blocked** | `#fef2f2` (`--md-sys-color-error-container`) | `#ba1a1a` (`--md-sys-color-error`) | Critical data gaps, blocked APIs |
| **Warning / Insufficient** | `#fffbeb` (`--md-sys-color-warning-container`) | `#b45309` (`--md-sys-color-warning`) | "Insufficient data to assess risk" alert |
| **Success / Verified** | `#f0fdf4` (`--md-sys-color-success-container`) | `#166534` (`--md-sys-color-success`) | 100% verified boundaries & DES APY records |
| **Info / Derived** | `#f0f9ff` (`--md-sys-color-info-container`) | `#0369a1` (`--md-sys-color-info`) | Historical derived yield averages |

---

## 3. Typography Hierarchy (M3 Type Scale)

The typography scale utilizes Google's standard M3 semantic roles with legible system font stacks (`Google Sans, Roboto, -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif`):

| Role | Token | Size | Line Height | Weight | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display Medium** | `--md-sys-typescale-display-medium` | `45px` (2.8rem) | `52px` | 800 | Landing Page Hero Headline |
| **Headline Large** | `--md-sys-typescale-headline-large` | `32px` (2.0rem) | `40px` | 700 | Main Section Headings |
| **Headline Medium**| `--md-sys-typescale-headline-medium`| `28px` (1.75rem)| `36px` | 700 | Dashboard Page Title |
| **Title Large**    | `--md-sys-typescale-title-large`    | `22px` (1.375rem)| `28px` | 600 | Card Titles, Map Panel Header |
| **Title Medium**   | `--md-sys-typescale-title-medium`   | `16px` (1.0rem) | `24px` | 600 | Location Name, Chart Titles |
| **Body Large**     | `--md-sys-typescale-body-large`     | `16px` (1.0rem) | `24px` | 400 | Landing Lead Paragraph |
| **Body Medium**    | `--md-sys-typescale-body-medium`    | `14px` (0.875rem)| `20px` | 400 | Primary descriptive text, summaries |
| **Body Small**     | `--md-sys-typescale-body-small`     | `12px` (0.75rem)| `16px` | 400 | Table data, footnotes |
| **Label Large**    | `--md-sys-typescale-label-large`    | `14px` (0.875rem)| `20px` | 600 | Buttons, Filter Pills |
| **Label Medium**   | `--md-sys-typescale-label-medium`   | `12px` (0.75rem)| `16px` | 600 | Status Badges, Tooltips |
| **Label Small**    | `--md-sys-typescale-label-small`    | `11px` (0.6875rem)| `16px` | 700 | Metric Subtitles, LGD Tags |

---

## 4. Shape & Elevation System

Consistent corner radii and subtle tonal elevation replace ad-hoc styling:

### A. M3 Corner Radii
- `extra-small` (`4px`): Table cells, mini badges
- `small` (`8px`): Select inputs, text fields, notification toasts
- `medium` (`12px`): Cards, assessment panel, map container, chart cards
- `large` (`16px`): Dialogs, modal sheets
- `full` (`9999px`): M3 Filled Buttons, Filter Chips, Status Pills, FABs

### B. M3 Elevation Levels
- **Level 0 (Flat):** `box-shadow: none; background: var(--md-sys-color-surface);`
- **Level 1 (Default Cards):** `box-shadow: 0 1px 2px rgba(0,0,0,0.06), 0 1px 3px 1px rgba(0,0,0,0.04); background: var(--md-sys-color-surface-container-lowest);`
- **Level 2 (Hovered Cards / Toolbar):** `box-shadow: 0 2px 6px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04); background: var(--md-sys-color-surface-container-lowest);`
- **Level 3 (Floating Tooltips):** `box-shadow: 0 4px 8px 3px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.04); background: #ffffff;`

---

## 5. Interaction States & Accessibility Invariants

1. **State Layers:**
   - **Hover:** 8% opacity overlay of the primary accent color.
   - **Focus (`:focus-visible`):** High-contrast `2px solid #0b57d0` outline with `2px` offset on all keyboard-navigable elements.
   - **Active / Pressed:** 12% opacity overlay.
2. **Reduced Motion Override:**
   - All CSS animations, Three.js rotations, and transitions strictly honor `@media (prefers-reduced-motion: reduce)`.
3. **WCAG 2.2 AA Contrast Compliance:**
   - All body text (`#1f1f1f`) achieves ≥ 7.0:1 contrast ratio against `#ffffff` and `#f8f9fa` backgrounds.
   - Secondary text (`#444746`) achieves ≥ 4.5:1 contrast ratio.
   - Warning amber text (`#b45309`) achieves ≥ 4.5:1 contrast against `#fffbeb`.

---

## 6. Component Guidelines for Punjab GrainWatch

### Top Bar
- Flat M3 Top App Bar with `md.sys.color.surface` background, fine `outline-variant` divider, and pill-shaped coverage indicators.

### Summary Metrics Cards
- 4 clean M3 Level 1 cards with Google-style typography, displaying genuine data derived from DES APY and AGMARKNET.

### Interactive Map
- SVG choropleth mapping all 23 districts in EPSG:4326.
- Interactive mode toggle: Wheat Production (MT) vs. Screening Evidence Status.
- APMC Mandi pins plotted at verified centroids.

### Selected-Location Assessment Panel
- M3 Warning Container banner displaying: **`INSUFFICIENT DATA TO ASSESS RISK`**.
- Multi-indicator sufficiency gauge (28% completeness).
- Verified observations (Production, Yield, Prices, Weather).

### Four Meaningful Analytical Charts
- Chart 1: Historical Wheat Productivity Series (1968–2023) in kg/ha.
- Chart 2: Cross-District Production Comparison (Top Basins) in MT.
- Chart 3: Location Evidence Breakdown (6 required streams).
- Chart 4: Institutional Supply Coverage Matrix (8 dimensions).
- Every chart includes the mandatory 6-point methodology & provenance disclosure.
