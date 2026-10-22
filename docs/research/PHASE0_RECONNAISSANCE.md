# Phase 0 Reconnaissance & Baseline Audit Report
## Punjab GrainWatch — System Baseline, Data Verification, & Mismatch Analysis

**Execution Timestamp:** 2026-10-22T07:22:00+05:30  
**Auditor:** Antigravity IDE Environment Engineer & Coding Agent  
**Workspace:** `B:\Projects\Punjab_GrainWatch_Project_Starter`  
**Phase Reference:** `PHASE-00-RECONNAISSANCE`  
**Status:** **COMPLETE — ALL GATES PASSED**  

---

## 1. Environment & Toolchain Inventory

The runtime environment was inspected via terminal execution without fabrication:

| Component | Path / Identification | Version | Verification Command |
| :--- | :--- | :---: | :--- |
| **Antigravity IDE** | `B:\Apps\Antigravity IDE\Antigravity IDE.exe` | `2.5.5.0` (Product `1.107.0`) | `(Get-Item ...).VersionInfo` |
| **Antigravity CLI** | `C:\Users\Acer\agy-scripts\agy.cmd` | `1.4.2` | `agy.cmd --version` |
| **Node.js** | `C:\Program Files\nodejs\node.exe` | `24.14.1` | `node --version` |
| **Python** | `C:\Users\Acer\AppData\Local\Programs\Python\Python313\python.exe` | `3.13.1` | `python --version` |
| **Git** | `C:\Program Files\Git\cmd\git.exe` | `2.55.0.3` | `git --version` |
| **Shell** | PowerShell 5.1 / Windows Terminal | Windows 11 AMD64 | `$PSVersionTable.PSVersion` |

### Application Entry Points Audit
Inspection of the project root confirms:
- **No pre-existing application code exists yet.** There are no `package.json`, `pyproject.toml`, `requirements.txt`, or application frameworks configured in the repository root.
- The project is currently a pristine documentation and evidence-starter package containing:
  - `AGENTS.md` (Governing non-negotiable agent instructions)
  - `docs/` (Canonical product specifications, PRD, architecture, schemas)
  - `docs/research/source_reports/` (Historical evidence and research reports)
  - `prompts/PHASED_BUILD_PLAN.md` (Step-by-step phased execution plan)
  - `data/manifests/STARTER_SOURCE_DROP_MANIFEST.json`
  - `data/inbox/gemini_phase5/phase5_acquisition/` (The extracted Phase 5 acquisition evidence)

---

## 2. Evidence Inventory & Checksum Verification

### Drop Manifest Verification (`STARTER_SOURCE_DROP_MANIFEST.json`)
Every file listed in `data/manifests/STARTER_SOURCE_DROP_MANIFEST.json` was independently inspected. The SHA-256 hash and byte size of every file was computed on disk:
- **Expected entries:** 49 files
- **Files matched:** 49 / 49 (100% exact match)
- **Files missing:** 0
- **Hash mismatches:** 0

### Provenance Manifest Verification (`PROVENANCE_MANIFEST.json`)
The manifest at `data/inbox/gemini_phase5/phase5_acquisition/PROVENANCE_MANIFEST.json` was similarly verified:
- **Expected entries:** 44 relative paths
- **Files matched:** 44 / 44 (100% exact match)
- **Hash mismatches:** 0

### Complete Physical File Breakdown (49 Assets)
- **Tabular Data (CSV):** 17 files
- **Metadata & Logs (JSON):** 18 files
- **Spatial Geometry (GeoJSON):** 1 file (`punjab_district_boundaries.geojson`, 3,974,131 bytes)
- **Satellite Raster (GeoTIFF):** 1 file (`S2B_43REP_20241005_B04_512px_window.tif`, 376,834 bytes)
- **Documentation & Reports (Markdown/Text):** 3 files
- **Acquisition & Build Scripts (Python):** 7 files
- **Acceptance Tests (Python/Pytest):** 2 files (`test_phase5_data.py`, `__pycache__`)

---

## 3. Tabular Dataset Schema & Record Count Audit

All 17 CSV files in `data/inbox/gemini_phase5/phase5_acquisition/` were parsed and audited:

| Relative Path | Rows | Cols | Size (Bytes) | SHA-256 (prefix) | Domain / Grain |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `ARRIVALS_PANEL.csv` | 3,892 | 16 | 1,359,489 | `eaa8eaaca088...` | Daily APMC mandi arrivals (Oct 1–21, 2026) |
| `DATA_INVENTORY.csv` | 10 | 17 | 7,065 | `32111c4ba518...` | Catalog of 10 evaluated data sources |
| `SOURCE_STATUS.csv` | 10 | 12 | 3,738 | `14cb68698223...` | API connectivity & authentication status |
| `SUPPLY_FLOW_COVERAGE_MATRIX.csv` | 8 | 8 | 3,803 | `c457aa74f7c3...` | 8-dimension supply-chain coverage matrix |
| `processed/agmarknet_punjab_daily_prices.csv` | 53 | 14 | 10,561 | `29c5c159d1a7...` | Agmarknet 2.0 daily modal prices for Paddy |
| `processed/agmarknet_punjab_districts.csv` | 22 | 3 | 418 | `e255d77b3963...` | Master list of 22 Punjab Agmarknet districts |
| `processed/agmarknet_punjab_markets.csv` | 245 | 4 | 7,863 | `61f8d0aff0a3...` | Master list of 245 Punjab APMC markets |
| `processed/agmarknet_target_commodities.csv` | 10 | 3 | 219 | `5e3c54384c3e...` | Target grain/mandi commodity registry |
| `processed/cfpp_punjab_wheat_procurement_2025_26.csv` | 3 | 12 | 996 | `7731bc98a8d7...` | State wheat procurement snapshot (2025-05-15) |
| `processed/district_crop_production.csv` | 230 | 21 | 100,088 | `bd545ff36267...` | 23 districts x 5 years (DES APY 2018–2023) |
| `processed/district_crop_yield.csv` | 2,754 | 16 | 834,355 | `09f170bb3761...` | Long-format historical yield (1968–2022) |
| `processed/geospatial/district_crosswalk.csv` | 23 | 5 | 3,824 | `a9f9ffc21602...` | APY to LGD district boundary crosswalk |
| `processed/punjab_mandi_arrivals_oct2026.csv` | 3,892 | 16 | 1,359,489 | `eaa8eaaca088...` | Identical copy of `ARRIVALS_PANEL.csv` |
| `processed/punjab_multi_zone_daily_weather_2024_2025.csv` | 3,655 | 12 | 1,132,183 | `ef7e77faa87a...` | 5 stations x 731 days (NASA POWER 2024–2025) |
| `processed/stocks/stock_observations_national_dfpd.csv` | 100 | 15 | 42,031 | `21c173141c3a...` | DFPD Central Pool national foodgrain stocks |
| `raw/ogd/ogd_punjab_rice_yield.csv` | 23 | 56 | 6,164 | `b42efba747a1...` | Wide format historical rice yield (1968–2022) |
| `raw/ogd/ogd_punjab_wheat_yield.csv` | 23 | 56 | 6,171 | `958fe37e224a...` | Wide format historical wheat yield (1968–2022) |

---

## 4. Critical Evidence Audit & Empirical Mismatch Analysis

In strict accordance with `AGENTS.md` ("Do not equate absence with zero... No hoarding conclusions... Null is not zero"), the physical contents of the datasets were subjected to forensic scrutiny. The findings establish definitive boundaries for application modeling:

### Mismatch 1: Produce vs. Foodgrain Arrivals in Mandi Panel
- **Dataset:** `ARRIVALS_PANEL.csv` (3,892 rows)
- **Claimed Scope:** Market arrival quantities across Punjab APMCs.
- **Empirical Reality:** 
  - There are **exactly 62 unique commodities** in this file.
  - Every single commodity is a fruit, vegetable, or perishable cash crop (e.g., Onion Dry, Tomato, Potato, Radish, Cauliflower, Bottle Gourd, Garlic Dry, Apple).
  - A regex search for `dhan` initially flags 71 rows; inspection reveals all 71 rows are **CORIANDER GREEN (HARA DHANIYA)**.
  - **There are 0 rows of Wheat (Kanak/Gehun) and 0 rows of Paddy (Dhan/Rice).**
- **Root Cause Identified:** The Punjab Mandi Board (`emandikaran-pb.in`) public daily arrival API only handles general agricultural produce. Foodgrain transactions (Wheat and Paddy) under the Minimum Support Price (MSP) regime are managed via the dedicated state **Anaaj Kharid** portal, which is credentialed for official procurement agencies and commission agents (arhtiyas).
- **Enforced Boundary:** **DO NOT compute grain arrival velocity, supply-demand balances, or hoarding scores from this dataset.** It is strictly a non-grain agricultural produce price/arrival reference.

### Mismatch 2: Paddy Price Feed Arrival Quantities Are 100% Null
- **Dataset:** `processed/agmarknet_punjab_daily_prices.csv` (53 rows)
- **Commodity Breakdown:** Paddy(Common): 48 rows, Paddy(Basmati): 5 rows.
- **Inspection of `arrival_quantity`:**
  - Non-null count: **0** (0.0%)
  - Null count: **53** (100.0%)
- **Empirical Reality:** The public Agmarknet 2.0 weekly query endpoint (`/prices-and-arrivals/market-price/lastweek`) provides modal prices in `Rs./Quintal` across Punjab markets, but **leaves arrival quantity completely blank/null**.
- **Enforced Boundary:** Null arrival volume must be explicitly displayed as `Not Reported` in the UI; it must **never** be coerced to zero or used to imply a supply stoppage.

### Mismatch 3: Stock Positions Are National Central Pool, Not Punjab-Specific
- **Dataset:** `processed/stocks/stock_observations_national_dfpd.csv` (100 rows)
- **Columns:** `geographic_coverage`, `state`, `commodity_standard`, `measure_name`, `measure_value`, `quality_note`
- **Empirical Reality:**
  - `geographic_coverage` is exclusively `'India Central Pool'`.
  - `state` is null (`NaN`).
  - Dates: 25 snapshot dates (2020-01-01 to 2026-01-01) comparing actual stocks vs national stocking norms.
- **Enforced Boundary:** This dataset represents national buffer stocks held by the Food Corporation of India across all states. **It cannot be used as Punjab regional inventory.** Attempting to calculate local warehouse stock drawdown from this data is an evidentiary violation.

### Mismatch 4: Procurement Data is a Single State Snapshot
- **Dataset:** `processed/cfpp_punjab_wheat_procurement_2025_26.csv` (3 rows)
- **Empirical Reality:** Represents a single snapshot date (`2025-05-15`) for RMS 2025-26:
  - Season Target Estimate: 124.00 LMT (Lakh Metric Tonnes)
  - Daily Procurement: 19,706.25 MT
  - Progressive Cumulative Procurement: 11,919,510.10 MT (~11.92 MMT)
- **Enforced Boundary:** There is no district-by-district breakdown or daily continuous procurement time series in the acquired data.

### Mismatch 5: Operational API Blockers
Inspection of `SOURCE_STATUS.csv` and source logs verifies four external data routes are blocked without unauthorized workarounds:
1. **AGMARKNET 2.0 Core Reports (`/daily-price-arrival/report`):** Returns HTTP 400 (`TOKEN_OR_CAPTCHA_REQUIRED`). Bypassing CAPTCHA violates Rule 7.
2. **CEDA Ashoka API (`/v1/agmarknet/quantities`):** Returns HTTP 401 Unauthorized (`Unauthorised, no api key passed`). Requires paid/registered bearer token.
3. **Open Government Data (`data.gov.in`):** Returns HTTP 400 (`API key is required`).
4. **Directorate of Economics & Statistics (`data.desagri.gov.in`):** Fails TLS handshake due to untrusted NIC root certificate in standard Python cert stores. Disabling SSL verification violates Rule 7.

---

## 5. Architectural & Implementation Strategy

### Stack Decision: Greenfield Implementation
Because no pre-existing application code exists in the repository, we follow `docs/ARCHITECTURE.md` and the greenfield defaults:
- **Data Engineering & Normalization Layer:** Python 3.13 (`pandas`, `pydantic`, `pytest`, `geojson`).
- **Backend API Service:** FastAPI + Uvicorn serving normalized read-only JSON endpoints with transparent metadata, provenance headers, and status flags.
- **Frontend Presentation Layer:** Astro + React + TypeScript with vanilla CSS design tokens (Apple restrained typography + Google Material structural clarity).
- **Visual & Motion Layer:** Emil Kowalski animation standards (sub-300ms, cubic-bezier, `@starting-style`, GPU-only transforms) + Three.js contained 3D hero with static SVG fallback.
- **Testing Gate:** Pytest for data fixtures and API endpoints; Playwright for end-to-end UI verification.

---

## 6. Phase 1 Implementation Plan

Phase 1 will establish the authoritative data layer and automated validation gate:

1. **Build `tools/data_catalog.py`:** Repeatable script to compute exact row counts, columns, date coverage, commodities, null percentages, geographic coverage, units, and SHA-256 hashes for all 49 files.
2. **Generate `data/manifests/dataset_catalog.csv`:** Normalized catalog capturing dataset ID, file path, format, row count, observation status (`observed`, `derived`, `metadata only`, `blocked`), unit, date range, and checksum.
3. **Create `data/manifests/data_quality_report.json`:** Machine-readable validation ledger verifying zero wheat/paddy in `ARRIVALS_PANEL.csv`, 100% null arrivals in Paddy prices, national geography for stocks, and 23-district boundary alignment.
4. **Write Automated Acceptance Test Suite:** Create `tests/test_data_integrity.py` with pytest assertions verifying every data constraint and preventing hardcoded falsified statistics.
5. **Update State & Phase Report:** Document results in `docs/PROJECT_STATE.md` and `logs/phase_reports/PHASE_1_REPORT.md`.
