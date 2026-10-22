# System Architecture

## 1. Principles

- Source separation and immutable raw evidence.
- Reproducible, idempotent ingestion.
- Strict separation of raw, normalized, derived and synthetic data.
- Data contracts and provenance on every row/table.
- UI must not infer missing facts from absence.
- Optionality: do not introduce distributed systems or ML infrastructure before needed.

## 2. Proposed logical architecture

```text
Official sources / bundled evidence
            |
            v
Acquisition adapters + manual import manifest
            |
            v
Immutable raw store (file path + SHA-256 + retrieval metadata)
            |
            v
Schema validation -> normalization -> quality reports
            |
            v
PostgreSQL facts / dimensions (PostGIS only if needed)
            |
            v
Read/query layer (FastAPI)
            |
            v
Astro + React/TypeScript UI -> charts, maps, evidence details
            |
            v
User-visible provenance, freshness, uncertainty, data gaps
```

No model service is required for V1. Analytical features run as deterministic Python jobs first. Any future model must version inputs, parameters and outputs and include walk-forward/backtesting evidence.

## 3. Suggested technology choices

Use what the repository currently supports where possible. Greenfield default:
- Frontend shell: Astro with React + TypeScript islands for interactive dashboards.
- Styling: tokenized CSS/design system; utility CSS may be used if already configured.
- 3D: Three.js or React Three Fiber for one contained hero experience; static fallback.
- Backend: FastAPI, Pydantic schemas, SQLAlchemy/Alembic if SQL migrations are used.
- Data processing: Python, pandas, pyarrow where a tabular scale/format warrants it, GeoPandas/rasterio only for actual spatial/raster workflows.
- Database: PostgreSQL. PostGIS only when spatial joins/query operations are implemented.
- Charts/maps: select actively maintained libraries after verifying project setup and license; standardize on a small number.
- Testing: pytest for Python; frontend unit/component tests and Playwright or equivalent smoke tests if available.

Do not blindly install every suggested library. Check installed tools and skills, dependency footprint, current docs, licensing and Windows compatibility first.

## 4. Backend boundaries

- `ingestion/`: one adapter per provider/dataset, configurable timeouts, bounded retries, TLS verification, pagination and explicit auth state.
- `validation/`: schema and domain rules, units, dates, source/geography consistency, null/zero semantics, duplicates and hash verification.
- `normalization/`: map source-specific field names to canonical schema while preserving original values.
- `repositories/`: database/file queries only; no UI presentation code.
- `services/`: coverage summaries, trends, completeness and explainable anomaly logic.
- `api/`: versioned FastAPI routes and response models.
- `tests/`: fixture-based tests that never rely on current internet availability.

## 5. Frontend boundaries

- Shared design tokens, app shell and navigation.
- Page-level routes for overview, explorer, production/yield, market, weather, procurement/stocks, map, quality/readiness and methodology.
- Reusable provenance badge, source panel, date/coverage label, empty state, warning state, metric card, chart shell, table and map legend.
- All visual metrics must be sourced from API responses or a validated local data manifest, not copied into source code.
- Client-side 3D loads lazily after primary page content; avoid WebGL on unsupported devices.

## 6. Data model (conceptual)

- `source_registry`: source ID, organization, source URL, access method, terms/license, tested status, caveats.
- `dataset_registry`: dataset ID, source ID, path, schema version, row count, coverage, checksum, retrieval time, status.
- `production_district_season`: crop, district source/std IDs and vintages, season/year, area and production with units.
- `yield_district_year`: crop, district IDs/vintage, year, yield, unit.
- `mandi_daily`: market and commodity IDs, trade date, arrivals with unit (nullable), min/modal/max price with currency/unit, reporting status.
- `procurement_observation`: date/as-of date, agency, commodity form, measure and temporal basis, amount/unit, state/district/market level.
- `stock_observation`: as-of date, reporting geography, owner/agency, commodity form, measure, unit, temporal basis.
- `weather_daily`: station/coordinate, date, parameter, value, unit, quality/source.
- `district_geometry`: stable district ID, name, boundary vintage, geometry and source.
- `quality_issue`: dataset, rule, affected record/key, severity, first seen, resolution.
- `derived_feature` / `alert_candidate`: algorithm/version, input dataset versions, baseline/window, observed value, expected range, uncertainty, explanation and review status.

Store original source rows/payloads outside normalized tables. Enforce foreign keys only where identifiers have been validated. Do not force questionable district joins.

## 7. API surface (proposed)

- `GET /api/v1/health`
- `GET /api/v1/datasets`
- `GET /api/v1/datasets/{dataset_id}`
- `GET /api/v1/coverage`
- `GET /api/v1/production`
- `GET /api/v1/yields`
- `GET /api/v1/markets/prices`
- `GET /api/v1/weather`
- `GET /api/v1/procurement`
- `GET /api/v1/stocks`
- `GET /api/v1/geo/districts`
- `GET /api/v1/quality/issues`
- `GET /api/v1/methodology`

These are design targets, not claims that endpoints already exist. Add pagination/filter validation, predictable errors, and API schema docs. Do not return unsupported fields as zero.

## 8. Failure behavior

- Provider unavailable: display last verified retrieval timestamp and data stale status.
- Authorization/CAPTCHA required: show blocked, not provider-down.
- TLS error: preserve verification, explain local trust/transport error, stop and report.
- Partial data: record the exact scope and exclude unsupported values from aggregate claims.
- Schema drift: quarantine new response; do not silently ingest.
- Map join mismatch: show unmatched counts and preserve the source geography label.

## 9. Performance and reliability

- Cache validated static/slow-changing datasets.
- Avoid live provider calls on page load; use controlled ingestion tasks.
- Limit and lazy-load the 3D experience and maps.
- Keep queries bounded and add database indexes only from measured needs.
- Make ingestion reruns idempotent; capture checksums and response metadata.
