# Roadmap & Phase Status

## Phase 0 — Reconnaissance and skill audit [DONE]
- Inspect existing code, package files, environment, data tree, manifests and tests.
- Verify archive/files and source reports.
- Discover and read relevant installed skills, explicitly checking Gravitas and Ponytail.
- Output: `docs/research/PHASE0_RECONNAISSANCE.md`, `docs/research/SKILL_AUDIT.md`, `logs/phase_reports/PHASE_0_REPORT.md` and updated `PROJECT_STATE.md`.
- Gate: passed without modifying raw source files.

## Phase 1 — Data verification [DONE]
- Compute counts and schemas for every CSV/JSON/GeoJSON/raster/HTML/PDF.
- Recompute hash checks and coverage matrix; find contradictions between reports and files.
- Output: `data/manifests/dataset_catalog.csv`, `data/manifests/dataset_catalog.json`, `data/derived/quality_report.json`, `docs/research/DATA_QUALITY_REPORT.md`, `scripts/run_validation_pipeline.py`, `tests/test_data_integrity.py`.
- Gate: 16/16 pytest checks passed, all 5 critical domain boundaries verified, raw files 100% immutable, single-command pipeline idempotent.

## Phase 2 — Product foundation [DONE]
- Set up app shell, design tokens, navigation, route skeleton and error/empty/loading states.
- Built FastAPI backend with typed config, safe path containment, health/status/datasets/quality endpoints.
- Built Astro + React + TypeScript frontend with AppShell, DatasetExplorer, SystemHealthMonitor, and Methodology.
- Output: `backend/`, `frontend/`, `scripts/run_dev.ps1`, `tests/test_backend_api.py`.
- Gate: 25/25 pytest tests passed; frontend built cleanly in 0.93s; browser smoke test verified live interaction with zero console errors.

## Phase 3 — Data layer and API adapters [DONE]
- Built typed Pydantic domain schemas and repository/service boundaries for all active datasets.
- Implemented 13 versioned endpoints aligned with `docs/ARCHITECTURE.md` (`/coverage`, `/production`, `/yields`, `/markets/prices`, `/weather`, `/procurement`, `/stocks`, `/geo/districts`, `/geo/crosswalk`, `/sources`, `/quality/issues`, `/methodology`).
- Preserved strict null semantics (Malerkotla pre-split years, Agmarknet arrival quantities, DFPD stock states; null != 0).
- Implemented idempotent local import service (`ingestion_service.py`) and safe external connector interfaces (`connectors.py`).
- Output: `backend/schemas/`, `backend/services/`, `backend/ingestion/`, `backend/api/routes/`, `tests/test_domain_schemas.py`, `tests/test_idempotent_import.py`, `tests/test_data_layer_endpoints.py`.
- Gate: 55/55 pytest tests passed in 1.70s; raw files 100% immutable; zero live provider requests on page load.

## Phase 4 — Core dashboard [DONE]
- Built the complete main user flow across 9 dedicated routes with real validated values from FastAPI and physical catalog caches.
- Implemented: Overview (`/`), Dataset Explorer (`/datasets`), Production & Yield (`/production-yield`), Market Watch (`/market-watch`), Weather Context (`/weather`), Procurement & Stocks (`/procurement-stocks`), District Map (`/district-map`), Audit & Readiness (`/status`), and Methodology (`/methodology`).
- Displayed prominent, explicit data gap disclaimers: 0 wheat/paddy arrivals in APMC panel, 100% null arrival quantities in Agmarknet, national-only Central Pool buffer stocks, single-position non-summing procurement, and zero private hoarding labels.
- Added dynamic interactive filters with accessible table equivalents for all visual charts and maps.
- Exported client-side JSON downloads attaching SHA-256 digests, provenance metadata, and strict empirical caveats directly to user downloads.
- Output: `frontend/src/pages/`, `frontend/src/components/`, `frontend/src/styles/dashboard.css`, `frontend/public/data/`, `tests/test_phase4_dashboard.py`, `logs/phase_reports/PHASE_4_REPORT.md`.
- Gate: 87/87 pytest tests passed in 2.15s; 9/9 Astro static routes built cleanly in 1.48s; Browser subagent E2E smoke test passed with zero console errors.

## Phase 5 — 3D landing and motion polish [DONE]
- Implemented restrained Apple-inspired typography, Google Material clarity, selective glassmorphism, and agricultural token palette.
- Built procedural 3D WebGL agricultural silo & field hero scene (`Hero3DScene.tsx`) with stainless steel elevators, undulating alluvium terrain, floating wheat chaff particles, mouse parallax, and accessible static SVG blueprint fallback.
- Lazy-loaded Three.js dynamically to prevent bundler memory pressure and code-split the library cleanly; non-3D routes load in ~290 KB JS.
- Provided user-facing Play/Pause 3D motion controls (`aria-pressed`), high-contrast `:focus-visible` rings, and full `@media (prefers-reduced-motion: reduce)` overrides.
- Output: `frontend/src/components/Hero3DScene.tsx`, `frontend/src/styles/dashboard.css`, `frontend/src/pages/index.astro`, `tests/test_phase5_polish.py`, `logs/phase_reports/PHASE_5_REPORT.md`.
- Gate: 93/93 pytest tests passed in 2.05s; 9/9 Astro static routes built cleanly in 1.36s; Browser subagent E2E smoke test passed with zero console errors.

## Phase 6 — Transparent analytics and anomaly eligibility gates [DONE]
- Implemented explainable data completeness, freshness, schema validity, geographic coverage, and API-readiness metrics.
- Added documented 7-point eligibility gate (`CRIT-01` through `CRIT-07`) evaluating candidate streams before any statistical anomaly calculation.
- Verified and enforced strict zero grain arrival invariant (0 wheat/paddy rows), 100% null Agmarknet arrival quantities, national DFPD buffer stocks, and isolated procurement snapshots.
- Implemented `INSUFFICIENT EVIDENCE (BLOCKED)` and `STRICTLY FORBIDDEN` for private hoarding claims, actor-level rankings, or trader naming under AGENTS.md Rule 6.
- Created segregated Synthetic Demo Lab in `data/synthetic/` with prominent crimson watermarks, rolling 3-year median ±1.96 IQR bounds, and non-hoarding investigation protocols.
- Built dedicated `/analytics` route and interactive `AnalyticsGateView.tsx` with stream switcher and synthetic lab toggle.
- Output: `backend/schemas/analytics.py`, `backend/services/analytics_service.py`, `backend/api/routes/analytics.py`, `data/synthetic/scenario_hypothetical_wheat_dip.json`, `frontend/src/components/AnalyticsGateView.tsx`, `frontend/src/pages/analytics.astro`, `frontend/public/data/eligibility_gate.json`, `frontend/public/data/synthetic_scenario.json`, `tests/test_phase6_analytics.py`, `docs/ANALYTICS_AND_ALERTS.md`, `logs/phase_reports/PHASE_6_REPORT.md`.
- Gate: 108/108 pytest tests passed in 3.88s; 10/10 Astro static routes built cleanly in 2.20s; Browser E2E verification confirmed error-free rendering.


## Phase 7 — Hardening and release
- Tests, accessibility, security, performance, clean install, production build and presentation mode.
- Output: release report and known limitations.

## Phase gate protocol
Do one phase at a time. Mark `NOT STARTED`, `IN PROGRESS`, `BLOCKED` or `DONE` with evidence. Do not mark done because files were written; the acceptance tests must pass. Keep current status in `PROJECT_STATE.md`.
