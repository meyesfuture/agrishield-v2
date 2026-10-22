# Punjab grain supply data API audit

**Audit date:** 20 October 2026 (Asia/Kolkata)  
**Scope:** Punjab, India; wheat and paddy; discovery and access validation only. No anomaly model was built.

## Executive finding

Public official and institutional sources appear to cover many inputs, but critical mandi volume history is not established. CEDA's official API documentation describes a /agmarknet/quantities POST route. CEDA's portal requires registration for an API key. Neither that call nor multi-season wheat and paddy quantities could be tested in this runtime. AGMARKNET's site has arrival/price entry and public market information, but an official, documented bulk history API was not independently verified.

Two live API responses were validated from the Copernicus Data Space STAC service: the collections list and the Sentinel-2 Level-2A collection metadata endpoint returned parseable JSON. This confirms collection discovery through the web tool, not that Punjab scenes, raster assets, or a time series were obtained. Both local Python and PowerShell diagnostics failed DNS resolution for every target. The observed Python error was gaierror [Errno 11001] getaddrinfo failed; PowerShell said No such host is known. These are environment-level access failures and do not establish provider downtime.

Across the source discovery, 23 resources/endpoints are listed in the inventory. The Python and PowerShell diagnostics each attempted seven URLs (including two historical windows against NASA POWER), for 14 local request attempts; all stopped at local DNS resolution. The web fetch made four API URL attempts: two STAC endpoints returned valid JSON, while NASA POWER was inaccessible through that tool and CEDA returned an internal tool error. Thus one provider/source returned valid data through two endpoints. No mandi historical quantity endpoint returned data.

**Decision:** A monitoring prototype may be feasible after data retrieval is proven, but a defensible supply-volume reconciliation MVP cannot yet be declared ready. The missing proof is historical mandi arrival quantity by market and date across multiple Punjab markets and seasons, with documented units and reliable distinction between absent records and zero arrivals.

## Method

1. Started with independent web searches, prioritizing government portals, official provider docs, and institutional sources. Searched Punjab OGD/DES, AGMARKNET, CEDA, CFPP, Punjab Food/Civil Supplies and AePDS, DFPD/FCI, weather providers, Copernicus/Google Earth Engine, LGD, and boundary data.
2. Reviewed official documentation and catalog pages before constructing test requests. Third-party AGMARKNET wrappers were discovery leads only, not official specifications.
3. Ran small, serial local checks using Python's standard library against seven documented HTTPS URLs (including two NASA POWER historical windows). The runner logs DNS, response status, parse details, and bounded samples when it can connect. The run stopped at DNS resolution for all seven. PowerShell checks yielded resolver-level Access is denied.
4. Used the web fetch tool on official API URLs. It returned valid JSON for CDSE /v1/collections; NASA POWER was inaccessible through that tool, and CEDA's commodity route yielded an internal tool error. The web tool does not expose a numeric HTTP status, so none is claimed for its successful response.
5. Created reproducible scripts and logs. No authentication, CAPTCHA, or other access control was bypassed.

## Test evidence

| Endpoint | Attempt | Observed result | Interpretation |
|---|---|---|---|
| NASA POWER daily point, 2024-01-01 to 2024-01-03 | Local Python HTTPS diagnostic | DNS_FAILURE, gaierror: [Errno 11001] getaddrinfo failed | No provider response; not a NASA failure finding. |
| NASA POWER daily point, 2010-01-01 to 2010-01-03 | Local Python HTTPS diagnostic | Same DNS failure | Historical comparison was scripted but not obtained. |
| CDSE STAC /v1/collections | Local Python diagnostic | Same DNS failure | Local runtime could not resolve host. |
| CDSE STAC /v1/collections | Web fetch direct HTTPS | Valid application/json response; parsed collections envelope, Sentinel-2 L2A listed | VERIFIED_WORKING for public collection metadata via this path only. No status code surfaced. |
| CDSE STAC /v1/collections/sentinel-2-l2a | Web fetch direct HTTPS | Valid Collection JSON; Sentinel-2 Level-2A, global extent, temporal start 2015-06-27, B02/B03/B04/B08 at 10 m GSD | VERIFIED_WORKING for collection metadata. Does not establish Punjab scene availability or data asset access. |
| CHIRPS data directory | Local Python diagnostic | Same DNS failure | No provider response. |
| CEDA OpenAPI candidate | Local Python diagnostic | Same DNS failure | Candidate schema URL was not confirmed by docs. |
| CEDA /agmarknet/commodities | Web fetch direct HTTPS | Internal tool error | No provider HTTP response. |
| Punjab OGD crop catalog page | Local Python diagnostic | Same DNS failure | Page contents independently available in search/index; local request not completed. |
| CFPP home | Local Python diagnostic | Same DNS failure | Dashboard documented by page contents, but no endpoint data downloaded here. |

Python output is in logs/test_results.json and logs/test_results.csv. PowerShell output is in logs/powershell/test_results.json and logs/powershell/test_results.csv. The independent web-fetch result summary and a clearly labeled structured excerpt are in logs. Full sample bodies are produced only when local scripts receive a response; no local request returned one. The web tool showed truncated payloads, so no full raw response is represented as captured.

### Confirmed from official documentation/page contents

- Punjab OGD's DES district/season/crop/year production catalog describes crop area in hectares and production in tonnes, and offers Catalog API and ZIP download. The page was updated in 2021; that does not guarantee the latest observation reaches 2021.
- CEDA documents Agmarknet commodities, geographies, markets, prices, and quantities endpoints. Its API portal presents key registration with email OTP. Route documentation confirms a candidate quantity API, not its complete year/market coverage.
- NASA POWER Daily API documentation says daily time series are available from 1981 to near real time, with JSON/CSV formats and point requests. Daily product is gridded (roughly 0.5 degree); parameter units must be read from response metadata.
- CHIRPS is gridded rainfall beginning in 1981. UCSB describes 0.05 degree data and public-domain status; the current notice recommends CHIRPS v3 and says v2 production ends after December 2026.
- CDSE documents public STAC endpoints and Sentinel-2 L2A collection. STAC discovery does not prove Punjab scene availability or imagery access.
- LGD assigns location codes intended for interoperability. Current codes alone do not settle district splits/renames in historical series.
- CFPP's official home page shows a current procurement-season dashboard and past-season navigation. Current page data are not a historical dataset test.

### Not verified here

- Row-level production values, latest year in Punjab OGD/DES APY, or district completeness.
- CEDA/AGMARKNET prices or quantities, quantity unit, pagination, zeros/nulls, retention, or market coverage.
- Whether mandi arrivals and procurement overlap for a specific measure; do not add until semantics are reconciled.
- Procurement and lifting history by district/market, stocks, or downloadable machine-readable Punjab reports.
- Satellite scene coverage over Punjab for crop-season windows, asset permissions, or crop classification accuracy.
- Public transport/movement API with aggregate inter-market grain flows.

## Source findings

The detailed one-row-per-resource register is api_inventory.csv.

### Production and markets

- [Punjab OGD: district-wise, season-wise crop production statistics](https://punjab.data.gov.in/catalog/district-wise-season-wise-crop-production-statistics-0) — DES attribution; district/crop/season/year; area (ha), production (tonnes); Catalog API and ZIP. Useful annual baseline if vintage coverage and district boundary history are checked.
- [DES APY reports](https://data.desagri.gov.in/website/crops-apy-report-web) — interactive state/district/crop/season/year report selection for area, production, yield; format and vintages remain unverified.
- [AGMARKNET official portal](https://agmarknet.gov.in/home) and [AGMARKNET operational SOP](https://www.agmarknet.gov.in/DailyDataEntry/Docs/SOP_DEO.pdf) — support that prices and arrivals are maintained. Arrival quantity is essential; price-only series cannot reconcile grain volume.
- [e-NAM trade details](https://www.enam.gov.in/web/dashboard/trade-data) has state/APMC/commodity and date-range filters and lists arrivals, traded quantity, unit, date and min/modal/max prices. This is a promising official interface for historical observations, but the page's visible controls are not proof of an open API, export, date retention or complete Punjab market coverage; none was submitted or extracted here. Treat as a high-priority manual/browser test.
- [CEDA Agmarknet API docs](https://api.ceda.ashoka.edu.in/documentation/) and [CEDA API portal](https://api.ceda.ashoka.edu.in/) — docs list GET commodities/geographies and POST markets/prices/quantities. Key registration is shown on portal. Schemas, parameters, and historic coverage require review after authentication.
- [Data.gov.in](https://www.data.gov.in/) and Punjab catalog are promising catalog/API channels, but no exact AGMARKNET resource ID or response was confirmed here. Confirm particular resource, API key, query limits and terms.
- Third-party Agmarknet wrappers exposed candidate routes but are not official documented endpoints and were not called.

### Procurement, stocks, allocations

- [CFPP](https://cfpp.nic.in/) reports current procurement and has past-season navigation. No documented API was found. Procurement is a high-value comparator, but could overlap market arrivals.
- [Punjab AePDS](https://epos.punjab.gov.in/) exposes public stock, allocation and sales reports with month/year selectors. PDS distribution is downstream context, not Punjab grain stocks.
- [DFPD](https://dfpd.gov.in/) food bulletins include statewise allocation/offtake and stock tables in historical downloadable bulletins. This is manual PDF/table extraction, not a verified API.
- [FCI](https://fci.gov.in/) has official stock/procurement reporting, but no tested open historical API was found. Reconcile rice vs paddy-equivalent before combining.
- Punjab Anaaj Kharid is an official operational procurement application/site; accessible material did not establish an open public API.

### Weather and satellite

- [NASA POWER Daily API docs](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) give a documented JSON/CSV request format and long daily coverage. Test request uses Ludhiana-area coordinates, T2M and PRECTOTCORR; check response units. Weather is contextual, not a direct crop-loss estimate.
- [IMD Current Weather API documentation](https://mausam.imd.gov.in/imd_latest/contents/api.pdf) lists station observations (time UTC, temperature, rainfall, humidity, wind, pressure) but says the user's public IP must be whitelisted. The documented endpoint is current weather, not a demonstrated historical archive. It was not tested.
- [CHIRPS v3 UCSB documentation](https://www.chc.ucsb.edu/data/chirps3) describes 1981-to-near-present rainfall at 0.05-degree resolution, daily/pentad/monthly products, and public-domain/CC BY 4.0 licensing. Its daily products are disaggregated from pentad totals (with alternative reanalysis-based and satellite-based methods); daily dates are consistent labels, not uniform station observation windows. These are estimates, not gauge truth.
- [Copernicus STAC docs](https://documentation.dataspace.copernicus.eu/APIs/STAC.html) document the collections endpoint, item search and Sentinel-2 L2A. Collection metadata returned valid JSON in web fetch. Crop condition requires cloud screening, crop masks, phenology, spatial processing and local validation.
- [CDSE API documentation](https://documentation.dataspace.copernicus.eu/APIs/) — use official registration/terms for assets where required.
- [Google Earth Engine Sentinel-2 SR Harmonized catalog](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED) is a processing environment requiring project/account and terms. No GEE call was attempted.
- ISRO/NRSC Bhuvan was investigated, but a stable, documented, unrestricted crop-season time-series API suitable for repeatable Punjab crop area/condition was not established.

### Geography, calendars, transport

- [LGD, Ministry of Panchayati Raj](https://panchayat.gov.in/en/lgd/) documents unique location codes. Some lookups use CAPTCHA; use public exports/APISetu where accessible. Reconcile district reorganizations.
- [OGD Admin Boundaries catalog](https://www.data.gov.in/catalog/admin-boundaries) lists state, district and block boundary downloads. Survey of India vector products are an alternative. Confirm boundary vintage, fields and license.
- Crop calendars appear in department/research publications, but no authoritative machine-readable Punjab district calendar API was established. Use a cited PAU/department calendar and preserve season definitions.
- Transport policies/tenders describe operations, but no public aggregate movement API or consistent open market-to-market freight series was discovered.

## Data integrity requirements for future work

- Preserve original commodity, variety, market ID/name, district/state, date, source, unit and extraction timestamp.
- Store arrivals and min/max/modal price separately. Do not infer quantity from prices.
- Distinguish arrival, procurement, lifting, stock, and milled output. Do not sum overlapping flows. Paddy procurement is not rice stock; conversion requires documented recovery and lag.
- Store missing, suppressed, unreported and explicit zero distinctly. Validate unit changes.
- Join markets to LGD/admin boundaries by stable IDs when possible; retain manual crosswalks for renames/splits.
- Keep wheat/paddy separate from flour/milled rice.
- Check license and redistribution terms for each resource.
- Weather/satellite can prompt human review but cannot establish losses, concealment or wrongdoing by themselves.

## Highest-value next step

First test the e-NAM trade details page with two historical date windows and Punjab wheat/paddy filters: its visible table explicitly lists arrivals, traded quantity, unit, date and market. Determine whether results paginate/export and whether all relevant mandis are covered. In parallel, register for a CEDA API key, retrieve its schema through the official documentation interface, and test /agmarknet/quantities for Punjab wheat and paddy across two seasons and two historical years. Record market IDs, units, dates, pagination, null/zero semantics and raw responses. If history is missing, request official AGMARKNET/state marketing board bulk arrival extracts. Establish the OGD/DES production panel and one daily weather series.
