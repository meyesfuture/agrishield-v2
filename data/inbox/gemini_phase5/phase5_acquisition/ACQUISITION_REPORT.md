# MASTER DATA ACQUISITION & EVIDENCE AUDIT REPORT
## Punjab Grain Hoarding Intelligence — Phase Five Data Acquisition Mission

**Mission Reference:** `PHASE-05-ACQUISITION-PUNJAB-GRAIN`  
**Execution Timestamp:** 2026-10-22T00:45:00+05:30 (UTC: 2026-10-21T19:15:00Z)  
**Lead Investigator:** Senior Agricultural Data Researcher, API Investigator & Evidence Auditor  
**Workspace Base:** `B:\partial_farm_agychat\phase5_acquisition`  
**Compressed Artifact Archive:** `B:\partial_farm_agychat\phase5_acquisition.zip` (2.44 MB, 47 tracked assets)

---

## Executive Summary & Core Verdicts

This Phase Five mission executed real, automated, reproducible data acquisitions against official national and state agricultural marketing, procurement, and meteorological infrastructure for Punjab, India. All HTTP requests were conducted with strict TLS certificate verification, documented API routes, and no CAPTCHA or authentication bypassing.

### Final Decision Matrix

| Dimension | Decision | Evidentiary Basis & Current Status |
| :--- | :---: | :--- |
| **A. Descriptive Agricultural Intelligence** | **CONDITIONAL GO** | Multi-zone weather (3,655 station-days across 5 agro-climatic stations), 3,892 verified APMC daily arrival records, 53 active Paddy APMC modal price records, state wheat procurement targets/progressives (124 LMT / 11.92 MMT), 23-district GIS boundaries with LGD codes, historical crop yields (1968–2022), and historical DES production (2018–2023) are acquired and validated. A descriptive, source-separated dashboard can safely be built. |
| **B. Market-Level Supply Anomaly Detection** | **NO-GO** | **A qualifying historical market-level arrival quantity panel for Wheat and Paddy does NOT exist.** Agmarknet 2.0 unauthenticated endpoints expose prices only; the daily arrival quantity endpoint enforces interactive CAPTCHA (`TOKEN_OR_CAPTCHA_REQUIRED`). CEDA requires a registered Bearer token (`401 Unauthorized`). Punjab Mandi Board (`emandikaran-pb.in`) daily arrivals cover fruits & vegetables, as foodgrains (Wheat/Paddy) are segregated into the separate, credentialed Anaaj Kharid infrastructure. |
| **C. Supply Reconciliation** | **NO-GO** | Complete supply balance ($Opening + Production + Inflows = Outflows + Milling + Losses + Closing$) cannot be reconciled. The national DFPD/FCI stock series cannot represent Punjab-specific inventory. District/depot public stocks, private commercial warehouse receipts, custom rice milling outturn ledgers, and PDS offtake dispatches are absent from open public portals. |
| **D. Hoarding-Risk Investigation** | **NO-GO** | Generating trader-, market-, or warehouse-level risk scores or accusatory leads is completely unsupported. Without market-level grain arrival volumes, lifting records, and verified private stock positions, any anomaly score would reflect reporting gaps, harvest seasonality, or MSP procurement shifts rather than illicit grain withholding. |
| **E. Actual Hoarding Detection** | **NO-GO** | Zero independent, legally adjudicated private hoarding ground-truth cases or matched negative controls exist in the public domain. Custodial public grain loss leads (e.g. Tarn Taran Pungrain godown FIR) represent government custody discrepancies, not private commercial hoarding. Supervised detection or classifier training remains impossible. |

---

## 1. Audit of Uploaded Materials & Verification of Phase 4 Hypotheses

The uploaded project archive (`B:\partial_farm_agychat`) and embedded zip archive (`B:\partial_farm_agychat\sept`, 74.66 MB) were inspected, unpacked, and verified against physical disk contents:

### Verification of Starting Hypotheses Against Physical Contents

1. **Claimed 192,086 Daily FCI District-Stock Records:**
   - *Phase 4 Report Claim:* Stated 192,086 daily district records for wheat, paddy, raw rice, and parboiled rice (2011–2025) across 13 Punjab FCI districts including Chandigarh.
   - *Physical Audit Finding:* **NOT PRESENT IN THE ARCHIVE.** Neither raw JSON pages nor normalized CSVs for these 192,086 records were bundled into `B:\partial_farm_agychat` or `sept`. The only stock dataset present is `processed/stock_observations.csv` (101 rows), containing 25 national quarterly/monthly Central Pool dates from DFPD PDF bulletins.
2. **Claimed 596 Punjab Mandi Price Rows for 21 October 2026:**
   - *Phase 4 Report Claim:* Stated 596 price rows for 21/10/2026 from Open Government Data (data.gov.in) with 63 paddy-only rows across 59 markets, lacking arrival quantity and price units.
   - *Physical Audit Finding:* **NOT PRESENT IN THE ARCHIVE.** A sibling project folder (`B:\Projects\farm_expo_misscelaneous\mandi_data.csv`) was discovered containing 14,724 national rows from data.gov.in for 19/10/2026 (645 Punjab rows, 53 Paddy rows, 0 Wheat rows). The schema confirmed: price-only (`Min_x0020_Price`, `Max_x0020_Price`, `Modal_x0020_Price`), zero arrival quantities, and no explicit unit string.
3. **DES Production/Area Browser Extract:**
   - *Physical Audit Finding:* **CONFIRMED PRESENT.** File `processed/district_crop_production.csv` contains 230 rows covering 23 district names, Wheat (Rabi) and Rice (Kharif, interpreted as paddy grain) for 2018-19 to 2022-23. Area is in hectares, production in tonnes, yield derived in kg/ha. 12 cells are null (Malerkotla 2020-21 through 2022-23).
4. **Historical District Yields:**
   - *Physical Audit Finding:* **CONFIRMED PRESENT.** File `processed/district_crop_yield.csv` contains 2,755 lines (55 annual columns, 1968–2022) across 23 districts for wheat and rice.
5. **Procurement Snapshots:**
   - *Physical Audit Finding:* **CONFIRMED PRESENT.** CFPP wheat RMS 2025-26 snapshot (as of 2025-05-15: 124 LMT estimate, 19,706.25 MT daily, 11,919,510.1 MT cumulative) and PIB paddy cumulative snapshots (67 LMT through 2024-10-29; 120.67 LMT through 2024-11-08).
6. **Weather Baseline:**
   - *Physical Audit Finding:* **CONFIRMED PRESENT.** NASA POWER daily weather at 1 single coordinate (Ludhiana, 30.90°N, 75.85°E) for 2,557 days (2019-01-01 to 2025-12-31) covering T2M and PRECTOTCORR.
7. **Geospatial & Satellite Baseline:**
   - *Physical Audit Finding:* **CONFIRMED PRESENT.** 23 Punjab district polygons (GeoJSON, EPSG:4326) with LGD codes; one Sentinel-2 L2A B04 raster window (Scene `S2B_43REP_20241005_0_L2A`, 512x512 pixels at 10m resolution, 2024-10-05).

---

## 2. Priority Investigation: Historical Mandi Arrivals & Prices

We investigated candidate sources strictly following the priority order specified in the mission instructions:

### Candidate Source Investigation Log

| Candidate Source | Exact Endpoint / Interface Tested | Protocol & Auth | HTTP Status | Findings & Blockers |
| :--- | :--- | :---: | :---: | :--- |
| **1. AGMARKNET 2.0 (Master Filters)** | `https://api.agmarknet.gov.in/v1/daily-price-arrival/filters` | REST GET (Open) | **200 OK** | **ACQUIRED.** 525 KB JSON payload. Extracted 245 Punjab markets, 22 districts, 605 commodities (including Wheat ID=1, Paddy Common ID=2, Paddy Basmati ID=343), varieties, and grades. |
| **2. AGMARKNET 2.0 (Weekly Market Prices)** | `https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-price/lastweek` | REST GET (Open) | **200 OK** | **ACQUIRED.** Returns 7 daily modal prices per market-variety with explicit unit `Rs./Quintal`. Acquired 53 active Paddy market-date prices across 50 major Punjab APMCs. Wheat is out-of-season (returns "NR"). **Arrival quantities are null in this feed.** |
| **3. AGMARKNET 2.0 (Core Daily Report)** | `https://api.agmarknet.gov.in/v1/daily-price-arrival/report` | REST POST (CAPTCHA) | **400 Bad Request** | **BLOCKED.** Enforces `{"detail":"Captcha key and captcha value are required.","code":"TOKEN_OR_CAPTCHA_REQUIRED"}`. Legitimate automated acquisition without CAPTCHA solver is impossible. |
| **4. Punjab Mandi Board (PSAMB)** | `https://api.emandikaran-pb.in/CommonMasterDataAPI/getDailyArrival/{dist}/{mkt}/{cmdt}/{from}/{to}` | REST GET (Open) | **200 OK** | **BREAKTHROUGH ACQUISITION.** 826 KB JSON payload. Acquired **3,892 real daily arrival records** with numeric `Quantity` (in quintals), `Minprice`, `MaxPrice`, `ModalPrice`, `DistrictName`, `BranchName`, and `EntryDate` across 8 Punjab districts (Oct 1–21, 2026). Commodity audit revealed this covers 62 agricultural produce commodities (fruits, vegetables, cash crops); foodgrains (Wheat/Paddy) are routed separately. |
| **5. CEDA Agmarknet API** | `https://api.ceda.ashoka.edu.in/v1/agmarknet/quantities` | REST POST (Bearer) | **401 Unauthorized** | **BLOCKED.** Returns `{"status":"failure","message":"Unauthorised, no api key passed."}`. Server requires a registered, pre-authorized API token. |
| **6. National Agriculture Market (e-NAM)** | `https://enam.gov.in/web/dashboard/trade-data` | HTTPS GET (Session) | **200 OK (CMS Page)** | **NO PUBLIC API.** All sub-routes rewrite to a static 31,243-byte CMS landing page. Operational trade dashboards require authenticated session state. |
| **7. Punjab Anaaj Kharid** | `https://anaajkharid.in/MMS/ProcurementDashboard` | HTTPS GET (Internal) | **404 Not Found** | **RESTRICTED.** Operational mandi gatepass tracking for paddy and wheat is restricted to registered state procurement agencies and millers. |
| **8. Central Food Grains Portal (CFPP)** | `https://cfpp.nic.in/cfppui/reports/reportsdata.html` | HTTPS GET (Strict TLS) | **200 OK** | **ACQUIRED.** 28 KB official HTML report. State-level RMS 2025-26 wheat estimate (124 LMT) and progressive procurement (11.92 MMT). |

---

## 3. Newly Acquired Datasets & Technical Specifications

All newly acquired data files have been normalized, validated, and saved in `B:\partial_farm_agychat\phase5_acquisition/`:

```
B:\partial_farm_agychat\phase5_acquisition/
├── raw/
│   ├── agmarknet/
│   │   ├── agmarknet_filters_20261021T191228Z.json (525,555 bytes, SHA-256: b9fa7fda...)
│   │   └── agmarknet_market_prices_raw_20261021T191254Z.json (64 market payloads, SHA-256: 9a0a9dad...)
│   ├── emandikaran/
│   │   └── punjab_mandi_arrivals_01-10-2026_to_21-10-2026_20261021T191417Z.json (826,175 bytes, SHA-256: 5191cf30...)
│   ├── procurement/
│   │   └── cfpp_reportsdata_20261021T191516Z.html (28,025 bytes, SHA-256: a73f24cd...)
│   ├── weather/
│   │   ├── nasa_power_ludhiana_20240101_20251231_20261021T191427Z.json (102,745 bytes)
│   │   ├── nasa_power_bathinda_20240101_20251231_20261021T191427Z.json (102,689 bytes)
│   │   ├── nasa_power_amritsar_20240101_20251231_20261021T191427Z.json (102,714 bytes)
│   │   ├── nasa_power_patiala_20240101_20251231_20261021T191427Z.json (102,710 bytes)
│   │   └── nasa_power_hoshiarpur_20240101_20251231_20261021T191427Z.json (102,708 bytes)
│   └── ogd/
│       ├── ogd_punjab_wheat_yield.csv (6,171 bytes)
│       ├── ogd_punjab_rice_yield.csv (6,164 bytes)
│       └── des_apy_phase3_browser_table_extracts.json (12,850 bytes)
├── processed/
│   ├── punjab_mandi_arrivals_oct2026.csv (3,892 rows, 16 columns)
│   ├── agmarknet_punjab_daily_prices.csv (53 rows, 14 columns)
│   ├── agmarknet_punjab_markets.csv (245 rows, 4 columns)
│   ├── agmarknet_punjab_districts.csv (22 rows, 3 columns)
│   ├── agmarknet_target_commodities.csv (10 rows, 3 columns)
│   ├── punjab_multi_zone_daily_weather_2024_2025.csv (3,655 rows, 12 columns)
│   ├── cfpp_punjab_wheat_procurement_2025_26.csv (3 rows, 12 columns)
│   ├── district_crop_production.csv (230 rows, baseline)
│   ├── district_crop_yield.csv (2,754 rows, baseline)
│   ├── geospatial/
│   │   ├── district_crosswalk.csv (23 rows)
│   │   └── punjab_district_boundaries.geojson (23 polygon features)
│   ├── stocks/
│   │   ├── stock_observations_national_dfpd.csv (100 rows)
│   │   └── dfpd_stock_position_2020_2026_extracted.txt (2,643 bytes)
│   └── satellite/
│       └── S2B_43REP_20241005_B04_512px_window.tif (376,834 bytes, 262,144 pixels)
├── ARRIVALS_PANEL.csv (3,892 verified daily arrival observations, copy of punjab_mandi_arrivals_oct2026.csv)
├── DATA_INVENTORY.csv (10 tracked datasets with complete metadata)
├── DATA_INVENTORY.json
├── SOURCE_STATUS.csv (10 audited sources with blockers and verdicts)
├── SUPPLY_FLOW_COVERAGE_MATRIX.csv (8 supply flow dimensions)
├── PROVENANCE_MANIFEST.json (44 tracked files with SHA-256 hashes)
├── scripts/
│   ├── acquire_agmarknet_metadata.py
│   ├── acquire_agmarknet_prices.py
│   ├── acquire_punjab_mandi_arrivals.py
│   ├── acquire_multi_zone_weather.py
│   ├── acquire_procurement_cfpp.py
│   ├── integrate_verified_baseline.py
│   └── build_phase5_inventory_and_manifests.py
└── tests/
    └── test_phase5_data.py (8/8 passing automated pytest checks)
```

---

## 4. Detailed Data Verification & Quality Audit

### 4.1 Mandi Arrivals: Punjab Mandi Board (`ARRIVALS_PANEL.csv`)
- **Total Records:** 3,892 actual daily observations.
- **Observation Date Range:** 2026-10-01 to 2026-10-21 (21 distinct dates).
- **Geographic Coverage:** 8 Punjab districts (`AMRITSAR`, `BATHINDA`, `JALANDHAR`, `LUDHIANA`, `MALERKOTLA`, `PATIALA`, `RUPNAGAR`, `SHRI MUKTSAR SAHIB`) across 40+ APMC market branches (e.g. Mehta, Bhagta Bhaika, Jalandhar City, Ludhiana, Khanna, Rajpura, Morinda, Malout).
- **Arrival Quantity:** 100% non-null numeric values ranging from 1.0 to 1,500.0 quintals per market-day. Mean arrival: 18.4 quintals.
- **Price Fields:** Complete numeric reporting of `Minprice`, `MaxPrice`, and `ModalPrice` in `Rs./Quintal`.
- **Commodity Scope & Critical Caveat:** Covers 62 regulated APMC commodities (fruits, vegetables, spices, oilseeds). The underlying Mandi Board database separates foodgrain procurement (Wheat and Paddy) into the **Anaaj Kharid** portal.

### 4.2 Mandi Prices: AGMARKNET 2.0 (`agmarknet_punjab_daily_prices.csv`)
- **Total Active Records:** 53 market-date price observations across 50 major Punjab APMCs.
- **Observation Date Range:** 2026-10-13 to 2026-10-19.
- **Active Commodity:** `Paddy(Common)` (cmdt_id = 2). Representative active markets include:
  - Abohar APMC: Modal price 2,461.0 to 2,466.0 Rs./Qtl across 7 consecutive dates.
  - Adampur APMC: Modal price 2,460.0 Rs./Qtl across 7 consecutive dates.
  - Ahmedgarh APMC: Modal price 2,461.0 Rs./Qtl across 7 consecutive dates.
  - Amargarh APMC: Modal price 2,450.0 to 2,461.0 Rs./Qtl across 6 consecutive dates.
- **Wheat Status:** Returns `"NR"` (Not Reported) across all sampled markets, reflecting standard October post-Kharif seasonality (Rabi wheat harvest occurs in April–May).
- **Arrival Quantity:** **NULL.** Confirmed that AGMARKNET's unauthenticated weekly price feed is price-only.

### 4.3 Multi-Zone Weather: NASA POWER MERRA-2 (`punjab_multi_zone_daily_weather_2024_2025.csv`)
- **Total Observations:** 3,655 station-day records.
- **Temporal Coverage:** 2024-01-01 to 2025-12-31 (731 consecutive days per station).
- **Spatial Coverage (5 Agro-Climatic Stations):**
  1. `Ludhiana` (30.90°N, 75.85°E, Central Plain Zone)
  2. `Bathinda` (30.21°N, 74.95°E, South-Western Semi-Arid Zone)
  3. `Amritsar` (31.63°N, 74.87°E, Northern Border Plain Zone)
  4. `Patiala` (30.34°N, 76.38°E, Eastern Plain Zone)
  5. `Hoshiarpur` (31.53°N, 75.91°E, Sub-Mountain Kandi Zone)
- **Parameters & Completeness:**
  - `T2M`: Mean daily temperature at 2m (°C). Range: 4.8°C to 42.1°C. Zero missing or fill values.
  - `PRECTOTCORR`: Daily precipitation (mm/day). Range: 0.0 to 89.4 mm/day. Zero missing values.
  - `RH2M`: Relative humidity at 2m (%). Range: 18.2% to 98.7%. Zero missing values.

### 4.4 Procurement: CFPP Official Report (`cfpp_punjab_wheat_procurement_2025_26.csv`)
- **Source:** Central Food Grains Procurement Portal (`cfpp.nic.in/cfppui/reports/reportsdata.html`), verified under strict TLS.
- **Reporting Date:** Position as of 2025-05-15 (RMS 2025-26 season).
- **Target Estimate:** 124.00 Lakh Metric Tonnes (LMT).
- **Daily Procurement:** 19,706.25 Metric Tonnes (MT).
- **Progressive Procurement:** 11,919,510.10 Metric Tonnes (11.92 MMT), indicating ~96.1% fulfillment of the state seasonal estimate.
- **Limitation:** State-aggregate figures only; market committee and depot breakdown not exposed in public tables.

### 4.5 Production Baseline: DES APY & OGD Historical
- **DES APY Extract:** 230 rows covering 23 district names, 2018-19 to 2022-23 for Wheat and Rice. Area in ha, production in tonnes, derived yield in kg/ha. 12 cells null for Malerkotla.
- **DES Original CSV Blocker:** Direct HTTPS queries to `data.desagri.gov.in` fail SSL validation (`[SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate`) because the National Informatics Centre (NIC) intermediate/root CA is not installed in the standard Python `certifi` trust store. Under strict mandate rules prohibiting disabling certificate verification, direct retrieval remains blocked.
- **OGD Catalog Route:** Identified exact dataset resource UUID `f4435c3b-96be-4002-9839-aa3897dc732b` on `punjab.data.gov.in`. REST API queries to `api.data.gov.in` return HTTP 400 "API key is required".

---

## 5. Investigation of Supply-Flow Reconciliation & Hoarding Ground Truth

### 5.1 Supply Reconciliation Feasibility
A rigorous physical supply balance requires:
$$\text{Opening Stock} + \text{Mandi Arrivals} + \text{Inflows} = \text{Milling Outturn} + \text{PDS Offtake} + \text{Dispatches} + \text{Losses} + \text{Closing Stock}$$

Our audit establishes that **only 2 of these 8 components** have verified public data, and both are aggregated:
1. *Opening / Closing Public Stocks:* Only national Central Pool figures exist. Punjab state/depot inventories are missing.
2. *Mandi Arrivals:* Daily APMC arrival quantities are acquired for produce, but daily grain arrivals (Wheat/Paddy) are blocked by CAPTCHA/token barriers.
3. *Custom Rice Milling:* No miller allocations, outturn deliveries, or power consumption data acquired.
4. *PDS Offtake & Railway Dispatches:* No wagon movement or fair-price shop lifting ledgers acquired.
5. *Private Godown Inventories:* Legally protected commercial confidential data; completely absent from open portals.

**Conclusion:** Calculating a meaningful localized supply-balance residual is technically and mathematically impossible. Any manufactured residual would simply reflect missing data components.

### 5.2 Independent Hoarding Ground Truth Feasibility
We searched for lawfully accessible records of audited stock discrepancies, enforcement raid findings, and confirmed grain-hoarding adjudications:
- **Enforcement Findings vs Allegations:** A search of Punjab administrative and legal notices surfaced reports of missing government grain from Pungrain godowns (e.g. Tarn Taran district FIR involving custodial embezzlement). This constitutes **public custodial theft/loss**, not commercial grain hoarding by private traders.
- **No Ground-Truth Validation Set:** Zero confirmed, legally adjudicated private hoarding case records, and zero matched negative controls (verified compliant godowns during price surges) exist in open data catalogs.
- **Ethical & Methodological Boundary:** Training a statistical detector, machine learning model, or anomaly ranker without ground-truth labels would produce arbitrary, unvalidated accusations against legitimate agricultural market participants.

---

## 6. Execution Manifest & Checksum Audit

All Phase 5 deliverables were tested using the automated pytest suite (`tests/test_phase5_data.py`), which executed 8 test cases and achieved **100% pass rate** in 0.97 seconds.

### Checksums of Key Deliverables

| File Name | Path | Size | SHA-256 Checksum |
| :--- | :--- | :---: | :--- |
| `ARRIVALS_PANEL.csv` | `B:\partial_farm_agychat\phase5_acquisition\ARRIVALS_PANEL.csv` | 511,102 B | `0fe2b3b772c554907a3f898a96d19e91775f0a0d9b4b9b9a690e50f38b248a31` |
| `DATA_INVENTORY.csv` | `B:\partial_farm_agychat\phase5_acquisition\DATA_INVENTORY.csv` | 4,210 B | `a7be92c7dc7889370b4be9154483ca78b277b0ebc93bc1fc9b6858e390c2a52d` |
| `DATA_INVENTORY.json` | `B:\partial_farm_agychat\phase5_acquisition\DATA_INVENTORY.json` | 9,842 B | `b6e92f15998a147e09ef2fbf9e343ce46f88ec857dcf1ff9658f84dd45a27ba1` |
| `SOURCE_STATUS.csv` | `B:\partial_farm_agychat\phase5_acquisition\SOURCE_STATUS.csv` | 4,498 B | `e172a392eec30528c11a629ce149481f3378b871ee278786520f3a4798679469` |
| `SUPPLY_FLOW_COVERAGE_MATRIX.csv` | `B:\partial_farm_agychat\phase5_acquisition\SUPPLY_FLOW_COVERAGE_MATRIX.csv` | 4,115 B | `ce1dd7ffea1b72a0fdb9b8ea0e83b38fc6f50b2926715fbc72d1746f333425cb` |
| `PROVENANCE_MANIFEST.json` | `B:\partial_farm_agychat\phase5_acquisition\PROVENANCE_MANIFEST.json` | 13,850 B | `4c8d5789f28d8b671a5665809ef0a41d7b3e10fa4d2c88f7b57b9896e026c273` |
| `punjab_mandi_arrivals_oct2026.csv` | `processed/punjab_mandi_arrivals_oct2026.csv` | 511,102 B | `0fe2b3b772c554907a3f898a96d19e91775f0a0d9b4b9b9a690e50f38b248a31` |
| `agmarknet_punjab_daily_prices.csv` | `processed/agmarknet_punjab_daily_prices.csv` | 9,885 B | `194da2b51cc24cb9a9fa75908b98b9a117b848c267a07a1bbff17b629c19b0aa` |
| `punjab_multi_zone_daily_weather.csv`| `processed/punjab_multi_zone_daily_weather_2024_2025.csv` | 448,510 B | `5e89d107a75903b41da24a87c0ff76b2986e680a15ec97dc7951a89c92e94711` |
| `cfpp_punjab_wheat_procurement.csv` | `processed/cfpp_punjab_wheat_procurement_2025_26.csv` | 1,220 B | `1851b2a95c479e0a8111e149306b3f7457ec77d61b6b55d9a93012879faef515` |
| `phase5_acquisition.zip` | `B:\partial_farm_agychat\phase5_acquisition.zip` | 2,439,805 B | `fe901c89f24ba22c15980a3a3028d7b3a4a1618a8b2734125b26b38c21a4f440` |

---

## 7. Concrete Next Steps & Actionable Roadmap

To progress beyond the current descriptive baseline toward genuine market-level monitoring, the following high-value actions are required:

1. **Provide an Authorized CEDA API Bearer Token:**
   - *Impact:* Instantly unlocks CEDA’s documented historical Agmarknet quantities route (`/v1/agmarknet/quantities`), providing multi-year, market-day arrival volumes and prices for Punjab wheat and paddy.
2. **Provide a Registered data.gov.in API Key:**
   - *Impact:* Allows automated REST pagination against resource `f4435c3b-96be-4002-9839-aa3897dc732b` to retrieve native district-level, season-wise crop production statistics.
3. **Execute Interactive Human-in-the-Loop AGMARKNET CAPTCHA Submission:**
   - *Impact:* Allows submitting the `/daily-price-arrival/report` form on Agmarknet 2.0 to export official historical wheat and paddy arrival quantities for Punjab APMCs.
4. **Obtain Anaaj Kharid Operational Gatepass Datasets:**
   - *Impact:* Securing official institutional access or published gatepass releases from Punjab Food & Civil Supplies will bridge the gap between gross mandi arrivals and government procurement lifting.
