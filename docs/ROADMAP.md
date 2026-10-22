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

## Phase 4 — Core dashboard
- Production/yield, paddy price, weather, procurement/stocks context and district map.
- Output: functional charts, filters, map and caveat labels.

## Phase 5 — 3D landing and motion polish
- Implement restrained grain/silo hero, reduced-motion and WebGL fallbacks, meaningful micro-interactions.
- Output: premium visual system while preserving legibility and performance.

## Phase 6 — Data quality and exploratory analysis
- Coverage matrix, missingness panels, unit checks, source readiness. Only implement anomaly candidates if evidence gates pass.
- Output: clear conditional GO/NO-GO summary.

## Phase 7 — Hardening and release
- Tests, accessibility, security, performance, clean install, production build and presentation mode.
- Output: release report and known limitations.

## Phase gate protocol
Do one phase at a time. Mark `NOT STARTED`, `IN PROGRESS`, `BLOCKED` or `DONE` with evidence. Do not mark done because files were written; the acceptance tests must pass. Keep current status in `PROJECT_STATE.md`.
