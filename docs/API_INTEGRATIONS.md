# API & Source Integration Register

**Status date:** 2026-10-22 (Phase 3 Data Layer implementation).
Statuses describe the verified tests and endpoints implemented in the Punjab GrainWatch application.

## 1. Connection and Ingestion Rules

- **Offline / Local Guarantee:** All client page views and API requests are served strictly from validated, provenance-preserving local stores; zero live provider requests occur during page load.
- **Credential Safety:** Keep credentials in environment variables or a local untracked `.env`; never commit secrets or tokens to Git or phase reports.
- **No CAPTCHA or Auth Bypass:** Do not attempt to bypass CAPTCHA, login, authorization, TLS checks, or provider access restrictions.
- **Adapter Standard:** Connectors (`backend/ingestion/connectors.py`) enforce timeout, bounded retry/backoff, explicit pagination, TLS verification (`verify=True`), response schema validation, and an opt-in manual/scheduled acquisition path.
- **Evidence-Based Registry Statuses:** Use exact standardized statuses:
  - `working-tested`: Verified working with acquired data.
  - `metadata-only`: Verified endpoint providing schema/filter catalogs only.
  - `blocked-auth`: Blocked due to missing user credentials / API key.
  - `blocked-captcha`: Blocked by interactive CAPTCHA challenge.
  - `unavailable`: Network, TLS trust, or institutional session restriction prevents access.
  - `stale`: Historical series exceeding freshness threshold without updates.
  - `not-tested`: Endpoint candidate not yet verified in runtime.

---

## 2. Tested External Sources

| Source ID | Name & URL | Category | Protocol | Auth Type | Live Status | Evidence Status | Acquired Observations & Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `emandikaran_pb` | Punjab Mandi Board (PSAMB)<br>`api.emandikaran-pb.in` | State APMC | REST GET | None | HTTP 200 | `working-tested` | 3,892 produce records. **Zero wheat/paddy records.** Foodgrains routed to Anaaj Kharid. |
| `agmarknet_v2_prices` | AGMARKNET 2.0 Weekly Prices<br>`api.agmarknet.gov.in` | Central Mandi | REST GET | None | HTTP 200 | `working-tested` | 53 daily Paddy modal prices. **Arrival quantity is 100% null.** |
| `agmarknet_v2_filters` | AGMARKNET 2.0 Master Filters<br>`api.agmarknet.gov.in` | Mandi Metadata | REST GET | None | HTTP 200 | `metadata-only` | 277 master records (245 Punjab markets, 22 districts, 605 commodities). |
| `cfpp_procurement` | Central Procurement Portal (CFPP)<br>`cfpp.nic.in` | Central Govt | HTTPS GET | None | HTTP 200 | `working-tested` | 3 state wheat measures (RMS 2025-26 as of 2025-05-15). **Non-summable temporal dimensions.** |
| `nasa_power_weather` | NASA POWER Agrometeorology<br>`power.larc.nasa.gov` | Open Weather | REST GET | None | HTTP 200 | `working-tested` | 3,655 station-days across 5 agro-climatic stations (2024-2025). 100% complete. |
| `data_gov_in_ogd` | OGD Platform India<br>`api.data.gov.in` | Open Data Portal | REST GET | API Key | HTTP 400 | `blocked-auth` | Blocked: requires API key. Next step: Register on data.gov.in and configure `DATA_GOV_IN_API_KEY`. |
| `des_agri_gov_in` | Directorate of Economics & Statistics<br>`data.desagri.gov.in` | Crop Statistics | HTTPS GET | None | SSL_ERROR | `unavailable` | Blocked: NIC root CA not in OS cert store. Next step: Install NIC root certificate; TLS bypass prohibited. |
| `ceda_ashoka_api` | Ashoka University CEDA<br>`api.ceda.ashoka.edu.in` | Research Portal | REST POST | Bearer Token | HTTP 401 | `blocked-auth` | Blocked: unauthorized without bearer token. Next step: Request academic API access token. |
| `enam_portal` | National Agriculture Market (e-NAM)<br>`enam.gov.in` | Trading Portal | HTTPS GET | Portal Login | HTTP 200 | `unavailable` | Static CMS landing page. Operational trade dashboards require authenticated participant session. |
| `anaajkharid_pb` | Punjab Anaaj Kharid Portal<br>`anaajkharid.in` | State Procurement | HTTPS GET | Agency Login | HTTP 404 | `unavailable` | Public link yields 404. Operational gatepass tracking restricted to licensed state agencies/millers. |

---

## 3. Implemented Versioned API Surface (`/api/v1`)

Aligned strictly with `docs/ARCHITECTURE.md`. All endpoints enforce pagination (`limit`, `offset`), typed Pydantic models, and strict null preservation.

| Method | Endpoint | Query Filters | Response Schema | Description & Invariants |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/healthz` | — | `{"status": "ok", "timestamp_utc": str}` | Fast liveness probe. |
| `GET` | `/api/v1/health` | — | `HealthResponse` | Component health check (catalog, quality report, data directory). |
| `GET` | `/api/v1/status` | — | `StatusResponse` | Verified critical guardrails and system gate status (`PASSED`). |
| `GET` | `/api/v1/datasets` | `category`, `status`, `search`, `limit`, `offset` | `DatasetListResponse` | Machine-readable dataset catalog (20 verified datasets). |
| `GET` | `/api/v1/datasets/{dataset_id}` | — | `DatasetDetailResponse` | Detailed dataset metadata, columns, and disk existence. |
| `GET` | `/api/v1/coverage` | — | `CoverageMatrixResponse` | 8-element Grain Supply Flow Coverage Matrix. Verdict: **NO-GO**. |
| `GET` | `/api/v1/production` | `district`, `crop`, `agricultural_year`, `limit`, `offset` | `ProductionListResponse` | District crop production & area (230 rows). 6 null cells preserved for Malerkotla pre-split years. |
| `GET` | `/api/v1/yields` | `district`, `crop`, `year_from`, `year_to`, `limit`, `offset` | `YieldListResponse` | Historical district crop yield observations (2,754 rows, 1968-2022). |
| `GET` | `/api/v1/markets/prices` | `market_name`, `commodity`, `date_from`, `date_to`, `limit`, `offset` | `PriceListResponse` | Daily mandi wholesale prices (53 rows). **Invariant:** `arrival_quantity` is 100% null (never 0.0). |
| `GET` | `/api/v1/weather` | `station_name`, `date_from`, `date_to`, `limit`, `offset` | `WeatherListResponse` | Daily multi-zone agrometeorological series (3,655 rows, 2024-2025). |
| `GET` | `/api/v1/procurement` | `commodity`, `measure_name` | `ProcurementResponse` | Wheat procurement snapshot (RMS 2025-26). **Invariants:** `cannot_be_summed=true`, `is_time_series=false`. |
| `GET` | `/api/v1/stocks` | `commodity`, `measure_name`, `observation_type`, `limit`, `offset` | `StockResponse` | Central Pool stocks (100 rows). **Invariants:** `geographic_scope="National Central Pool only"`, `state=null`. |
| `GET` | `/api/v1/geo/districts` | `name` | `DistrictBoundaryCollection` | GeoJSON FeatureCollection of 23 Punjab district boundaries (EPSG:4326). |
| `GET` | `/api/v1/geo/districts/{district_id}` | — | `DistrictBoundaryFeature` | Single district GeoJSON polygon feature by district or LGD ID. |
| `GET` | `/api/v1/geo/crosswalk` | `match_status`, `limit`, `offset` | `DistrictCrosswalkResponse` | Statistical to geospatial administrative crosswalk with Sangrur/Malerkotla temporal notes. |
| `GET` | `/api/v1/sources` | `category`, `status` | `SourceRegistryResponse` | External provider status registry with evidence-based status counts. |
| `GET` | `/api/v1/sources/{source_id}` | — | `SourceRegistryItem` | Provider operational details, verified technical blockers, and legitimate next steps. |
| `GET` | `/api/v1/quality/summary` | `reload` | `QualitySummaryResponse` | Validation pipeline gate summary, critical assertions, and quarantined files. |
| `GET` | `/api/v1/quality/issues` | `severity`, `dataset_id`, `limit`, `offset` | `QualityIssuesResponse` | Granular data quality issues (foodgrain arrival absence, clerk sentinels, null quantities). |
| `GET` | `/api/v1/methodology` | — | `MethodologyResponse` | Analytical charter, anti-hoarding policies, data contracts, and evidence hierarchy. |
