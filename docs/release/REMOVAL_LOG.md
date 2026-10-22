# Punjab GrainWatch Simplification & Removal Log

**Date:** 2026-10-22  
**Architect:** Senior Software Architect & Simplification Engineer  
**Status:** COMPLETED  
**Git Recovery Tag:** `pre-simplification-checkpoint` (Commit `28e4844`)

---

## 1. Overview of Removals

To fulfill the mission of focusing Punjab GrainWatch strictly on its core purpose—**exploring potential grain-hoarding risk locations across Punjab**—all peripheral standalone modules, redundant sub-dashboards, and secondary navigation destinations were audited and pruned.

The user-facing application was reduced from **10 disparate routes** to **2 primary experiences**:
1. **Landing Page (`/`):** Identity, mission, 3D agricultural visual, concise explainer, system boundaries, and primary CTA.
2. **Main Dashboard (`/dashboard`):** Interactive 23-district map with APMC mandi markers and selected-location assessment panel.

---

## 2. Detailed Removal Ledger

### 2.1 Removed Frontend Routes (`frontend/src/pages/`)

| Deleted Route File | Original URL | Why Removed | Disposition of Functionality |
| :--- | :--- | :--- | :--- |
| `frontend/src/pages/analytics.astro` | `/analytics` | Standalone gate matrix and experimental synthetic lab outside the 2-screen product scope. | Eligibility gate and evidence limitations are integrated directly into the Dashboard location assessment panel. |
| `frontend/src/pages/datasets.astro` | `/datasets` | Standalone technical dataset catalog and client-side JSON downloader; secondary developer utility. | Raw data and manifests remain preserved in `data/manifests/` and accessible via `/api/v1/datasets`. |
| `frontend/src/pages/district-map.astro`| `/district-map` | Redundant route; map was a secondary viewer. | Upgraded and merged into the primary product dashboard at `/dashboard.astro`. |
| `frontend/src/pages/market-watch.astro`| `/market-watch` | Standalone wholesale price table and price analytics workflow outside location screening scope. | Verified mandi prices for selected locations are presented directly in the Dashboard location panel. |
| `frontend/src/pages/methodology.astro` | `/methodology` | Standalone 8-rule narrative document that fragmented the user experience. | Core methodology and evidentiary boundaries are embedded directly into the Landing Page and location assessment panel. |
| `frontend/src/pages/procurement-stocks.astro` | `/procurement-stocks` | Macro national stock charts and single-snapshot procurement outside district-level screening. | Macro buffer stock data preserved in backend API `/api/v1/stocks` and `/api/v1/procurement`. |
| `frontend/src/pages/production-yield.astro` | `/production-yield` | Standalone historical crop production and yield charts. | District-level production and yield records are surfaced directly in the selected location details panel. |
| `frontend/src/pages/status.astro` | `/status` | Standalone telemetry monitoring and supply coverage matrix. | Health and status telemetry preserved in backend API `/api/v1/health` and `/api/v1/quality/summary`. |
| `frontend/src/pages/weather.astro` | `/weather` | Standalone NASA POWER station time-series viewer. | Station proximity and agro-climatic context surfaced in the Dashboard location panel. |

**Net Route Reduction:** 10 routes -> **2 routes** (80% reduction in route surface area).

---

### 2.2 Removed Exclusive Components (`frontend/src/components/`)

The following components were verified to be exclusive to the removed pages and were safely removed to eliminate dead code and bundler overhead:

| Removed Component | File Path | Lines Pruned | Rationale |
| :--- | :--- | :---: | :--- |
| `AnalyticsGateView.tsx` | `frontend/src/components/AnalyticsGateView.tsx` | 451 | Exclusive to removed `/analytics` route. Gate logic is preserved in `backend/services/analytics_service.py`. |
| `DatasetExplorer.tsx` | `frontend/src/components/DatasetExplorer.tsx` | 512 | Exclusive to removed `/datasets` route. |
| `DistrictMapView.tsx` | `frontend/src/components/DistrictMapView.tsx` | 352 | Superseded by `DashboardView.tsx` with enhanced location markers and assessment panel. |
| `MarketWatchView.tsx` | `frontend/src/components/MarketWatchView.tsx` | 290 | Exclusive to removed `/market-watch` route. |
| `ProcurementStocksView.tsx` | `frontend/src/components/ProcurementStocksView.tsx` | 315 | Exclusive to removed `/procurement-stocks` route. |
| `ProductionYieldView.tsx` | `frontend/src/components/ProductionYieldView.tsx` | 310 | Exclusive to removed `/production-yield` route. |
| `QualityReadinessView.tsx` | `frontend/src/components/QualityReadinessView.tsx` | 175 | Exclusive to removed `/status` route. |
| `SystemHealthMonitor.tsx` | `frontend/src/components/SystemHealthMonitor.tsx` | 310 | Exclusive to removed `/status` route. |
| `WeatherView.tsx` | `frontend/src/components/WeatherView.tsx` | 260 | Exclusive to removed `/weather` route. |

**Net Component Code Pruned:** 2,975 lines of exclusive UI code removed.

---

### 2.3 Pruned Navigation Links (`frontend/src/layouts/AppShell.astro`)

The top navigation header previously contained 10 disparate navigation links. It was simplified to **only 2 links**:
- `Home` (`href="/"`)
- `Dashboard` (`href="/dashboard"`)
- Primary Action button: `Open Dashboard →` (`href="/dashboard"`)

Removed Links:
- `href="/datasets"`
- `href="/production-yield"`
- `href="/market-watch"`
- `href="/weather"`
- `href="/procurement-stocks"`
- `href="/district-map"`
- `href="/status"`
- `href="/analytics"`
- `href="/methodology"`

---

## 3. Preservation Audit: What Was Strictly Kept

In accordance with non-negotiable instructions:
> *"Do not remove legitimate backend functionality, source data, acquisition scripts, API integrations, or research evidence simply because they are not visible in the UI."*

The following critical assets were **100% preserved**:
1. **Source Data (`data/inbox/`):** All 49 raw source files remain 100% unmodified with matching SHA-256 hashes.
2. **Catalog & Manifests (`data/manifests/`):** Complete dataset catalog (20 datasets) and starter source drop manifests.
3. **Data Validation Pipeline (`scripts/`):** Master validation script `scripts/run_validation_pipeline.py` and modular validators (`catalog_builder.py`, `integrity.py`, `quality_reporter.py`, `validators.py`).
4. **Backend API Endpoints (`backend/api/routes/`):** All 14 FastAPI routes remain active and operational (`health`, `datasets`, `quality`, `production`, `yields`, `prices`, `weather`, `procurement`, `stocks`, `geography`, `coverage`, `sources`, `methodology`, `analytics`).
5. **Static JSON Caches (`frontend/public/data/`):** All 11 verified physical caches remain intact (`production.json`, `yields.json`, `prices.json`, `weather.json`, `procurement.json`, `stocks.json`, `district_boundaries.json`, `district_crosswalk.json`, `coverage_matrix.json`, `sources.json`, `quality_issues.json`).
6. **Core UI Foundations (`frontend/src/components/`):**
   - `DashboardView.tsx`: The new unified interactive map and location assessment component.
   - `Hero3DScene.tsx`: The 3D agricultural silo visual with static SVG fallback and pause toggle.
   - `GuardrailBanner.astro`: Reusable limitation notice.
   - `StatusBadge.tsx`: Evidence status pill.
   - `MetricCard.astro`: Reusable metric card.
