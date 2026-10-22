# API & Source Integration Register

**Status date:** based on the bundled Phase 5 evidence dated 2026-10-22. Statuses describe the tests documented in this artifact and must be reproduced in the current runtime before being treated as live-current.

## Connection rules

- Keep credentials in environment variables or a local untracked `.env`; never add keys to Git or reports.
- Do not bypass CAPTCHA, login, authorization, TLS checks or provider restrictions.
- Every adapter must have a time limit, bounded retry/backoff, pagination handling, response-size limit, schema validation, source metadata and an explicit failure status.
- Use precise states: `VERIFIED_DATA_ACQUIRED`, `VERIFIED_ENDPOINT_ONLY`, `BLOCKED_AUTH`, `BLOCKED_CAPTCHA`, `TLS_OR_NETWORK_FAILURE`, `SCHEMA_MISMATCH`, `NOT_TESTED`, `STALE_DATA`.
- A provider page or metadata API working does not prove that a data endpoint works.

## Tested sources

### AGMARKNET 2.0 — filter/master metadata
- Method: GET
- Endpoint: `https://api.agmarknet.gov.in/v1/daily-price-arrival/filters`
- Phase 5 report: HTTP 200, filters/masters returned; source reported 245 Punjab markets, 22 districts and 605 commodities nationally/in filters.
- Use: controlled lookup tables; refresh and compare schema.
- Does not provide actual historical wheat/paddy arrival quantities by itself.

### AGMARKNET 2.0 — weekly market price feed
- Method: GET
- Endpoint: `https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-price/lastweek`
- Phase 5 report: HTTP 200; weekly data over seven daily dates, price unit `Rs./Quintal`; 53 active paddy prices in the Punjab extract, wheat out-of-season in that run; arrival quantity null.
- Use: paddy price dashboard with clear date/unit/source labels.
- Do not infer arrivals from prices.

### AGMARKNET 2.0 — daily arrival report
- Method: POST
- Endpoint: `https://api.agmarknet.gov.in/v1/daily-price-arrival/report`
- Phase 5 result: HTTP 400 `TOKEN_OR_CAPTCHA_REQUIRED` / CAPTCHA fields required.
- Status: `BLOCKED_CAPTCHA`. Do not attempt bypass. Continue only through a legitimate provider-supported route or manual authorized download.

### Punjab Mandi Board / e-Mandikaran APMC arrivals
- Pattern: `https://api.emandikaran-pb.in/CommonMasterDataAPI/getDailyArrival/{dist}/{mkt}/{cmdt}/{from}/{to}`
- Phase 5 report: HTTP 200; 3,892 daily arrivals with quantities in quintals for Oct 1–21, 2026, across 8 districts, 16 branches and 62 produce commodities.
- Critical restriction: the acquired set contains **zero wheat/paddy daily grain-arrival rows**; foodgrains are routed to separate credentialed Anaaj Kharid infrastructure.
- Use: demonstrate source ingestion only for verified commodity scope, not grain supply model input.

### CEDA AGMARKNET quantities
- Documented source: `https://api.ceda.ashoka.edu.in/documentation/`
- Candidate endpoint reported: `https://api.ceda.ashoka.edu.in/v1/agmarknet/quantities`
- Phase 5 result: HTTP 401, API key missing.
- Status: `BLOCKED_AUTH`; use only after registering and receiving an authorized bearer token. Never hardcode the key.
- The precise schema/request contract must be verified from current official documentation before implementation.

### NASA POWER daily point weather
- Official docs: `https://power.larc.nasa.gov/docs/services/api/temporal/daily/`
- API base: `https://power.larc.nasa.gov/api/temporal/daily/point`
- Phase 5 files: five points (Ludhiana, Bathinda, Amritsar, Patiala, Hoshiarpur), 2024-01-01 through 2025-12-31, 731 dates per point; 3,655 station-days. Variables documented: T2M (°C), PRECTOTCORR (mm/day), RH2M (%).
- Use: weather context only; validate parameter names, metadata and missing/sentinel values directly from JSON.

### CFPP wheat procurement
- Page: `https://cfpp.nic.in/cfppui/reports/reportsdata.html`
- Phase 5 acquired public HTML and derived three state-level measures for Punjab wheat RMS 2025–26, position as of 2025-05-15: estimate 124 LMT, daily procurement 19,706.25 MT, progressive procurement about 11.92 million MT.
- Use: as-of labelled state aggregate context only; not daily district grain flow.

### OGD/DES production and yield
- DES catalog: `https://data.desagri.gov.in/website/apy-query-report-web`
- Punjab OGD catalog: `https://punjab.data.gov.in/catalog/district-wise-season-wise-crop-production-statistics-0`
- Phase 5 production extract: 230 rows across 23 source district names, wheat/Rabi and rice/Kharif, 2018–19 through 2022–23; partial browser extract, with missing cells/vintage caveats.
- Historical yield: packaged wheat and rice files labelled 1968–2022.
- Use: only after reading actual schema/headers and auditing the production file for missing values and district mapping.

### Boundary data
- Packaged: `processed/geospatial/punjab_district_boundaries.geojson`, 23 features with LGD identifiers, boundary vintage through 2024 per report, GeoJSON likely EPSG:4326.
- Verify CRS, feature count, IDs, geometry validity and source attribution before plotting or joining.

### National stocks
- Packaged: `processed/stocks/stock_observations_national_dfpd.csv`, 100 rows, 25 quarterly/monthly dates, national Central Pool wheat/rice stocks/norms, 2020–2026.
- Use: national context only. Never relabel as Punjab inventory.

### Satellite
- Packaged: `processed/satellite/S2B_43REP_20241005_B04_512px_window.tif`; one 512×512 Band 04 window, 10 m, dated 2024-10-05.
- This is a single raster window, not a repeat-observation warehouse dataset. Validate CRS/geotransform/no-data and do not claim private stock detection.

## Required adapter contract

Each provider adapter must return `{status, source_id, requested_at_utc, request_parameters, http_status, data_path, raw_sha256, row_count, schema_version, coverage, limitations, error_class}`. Redact secrets and sensitive headers. Use fixtures for tests; tests must not depend on internet availability.
