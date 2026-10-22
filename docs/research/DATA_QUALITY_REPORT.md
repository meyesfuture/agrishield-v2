# Comprehensive Data Quality & Validation Report
## Punjab GrainWatch — Phase 1 Evidence Audit

**Generated (UTC):** 2026-10-22T06:34:50.009015+00:00  
**Overall Validation Gate:** **PASSED**  
**Evidence Standard:** Strict Ground Truth (No Fabrication, No Hallucinated Metrics)

---

## 1. Executive Summary

This report establishes the baseline evidence catalog and data quality audit for the **Punjab GrainWatch** project. All 49 files in `data/inbox/gemini_phase5/phase5_acquisition/` have been cryptographically re-verified using SHA-256 digests against `STARTER_SOURCE_DROP_MANIFEST.json` (49/49 matches) and `PROVENANCE_MANIFEST.json` (44/44 matches).

The data validation pipeline executed source-specific parsing, schema compliance checks, candidate key uniqueness checks, null/zero semantic audits, and domain boundary assertions across all acquired datasets.

---

## 2. Critical Domain Assertions & Boundary Guardrails

The application enforces five non-negotiable empirical boundaries based on actual data contents:

| Assertion | Expected Condition | Observed Value | Validation Status |
| :--- | :--- | :--- | :--- |
| **Zero Grain Arrivals in Panel** | 0 wheat/paddy records | 0 wheat/paddy records (62 produce crops only) | **VERIFIED** |
| **Dhan Substring Disambiguation** | All 'dhan' matches are Coriander Green | Exactly 71 rows: `coriander green (hara dhaniya / ਹਰਾ ਧਨਿਆ )` | **VERIFIED** |
| **Paddy Price Feed Arrival Quantities** | 100% null arrival quantity | 53 out of 53 rows null (100.0%) | **VERIFIED** |
| **National Central Pool Stocks** | State column is null/NaN; national pool only | 100 out of 100 rows state=NaN (100.0%) | **VERIFIED** |
| **Procurement Snapshot Semantics** | Single position date; 3 distinct temporal bases | Single date `2025-05-15`; 3 bases (target, daily, cumulative) | **VERIFIED** |
| **Satellite Scene Coverage** | Single tile window; not a temporal time-series | 1 file `S2B_43REP_20241005_B04_512px_window.tif` (2024-10-05) | **VERIFIED** |

### Consequence for Analytics & Modeling
1. **No Grain Arrival Anomaly Detection:** Anomaly models cannot be trained or evaluated on `ARRIVALS_PANEL.csv` because it contains zero wheat or paddy grain rows. Non-grain APMC produce (cauliflower, tomato, apple) cannot serve as a proxy for staple grain flows.
2. **No Actor-Level Hoarding Claims:** The project explicitly forbids ranking named mandis, traders, or mills as "hoarders" or calculating actor-level hoarding probabilities.
3. **No Stock Disaggregation:** FCI Central Pool buffer stock data cannot be partitioned across Punjab districts without local facility registers.
4. **No Procurement Summing:** CFPP procurement rows cannot be summed across `measure_value`, as doing so improperly aggregates seasonal target estimates with daily and cumulative values.

---

## 3. Dataset Validation Profiles

### 3.1 Mandi Arrivals Panel (`punjab_mandi_arrivals_oct2026.csv` & `ARRIVALS_PANEL.csv`)
- **Row Count:** 3,892 rows (Identical SHA-256 for root duplicate)
- **Columns (16):** `observation_date`, `entry_date_raw`, `state`, `district_name`, `mandi_branch_name`, `commodity_name`, `arrival_quantity`, `arrival_unit`, `min_price`, `max_price`, `modal_price`, `price_unit`, `source_url`, `retrieval_date_utc`, `quality_flag`, `data_source`
- **Date Coverage:** 2026-10-01 to 2026-10-21 (21 calendar days)
- **Geographic Coverage:** 8 Punjab districts, 38 mandi branches
- **Commodities:** 62 distinct agricultural commodities (all horticulture, cash crops, vegetables; foodgrains routed separately)
- **Candidate Key:** `['observation_date', 'mandi_branch_name', 'commodity_name']` — **0 duplicate rows**
- **Price Sanity:** 0 violations (min_price <= modal_price <= max_price for all priced rows)

### 3.2 AGMARKNET Paddy Daily Prices (`agmarknet_punjab_daily_prices.csv`)
- **Row Count:** 53 rows
- **Columns (14):** `observation_date`, `state`, `state_id`, `market_id`, `market_name`, `commodity_id`, `commodity_name`, `variety`, `arrival_quantity`, `min_price`, `modal_price`, `max_price`, `source_url`, `retrieval_date_utc`
- **Date Coverage:** 2026-10-13 to 2026-10-19 (7 days)
- **Geographic Coverage:** 50 APMCs across 22 districts
- **Commodity:** Paddy(Common)
- **Candidate Key:** `['observation_date', 'market_id', 'commodity_id']` — **0 duplicate rows**
- **Arrival Volume Null Rate:** **100.0% (53 / 53 rows null)**. Feed provides modal prices only (Rs. 2,320 / quintal MSP benchmark).

### 3.3 CFPP Wheat Procurement Snapshot (`cfpp_punjab_wheat_procurement_2025_26.csv`)
- **Row Count:** 3 rows
- **Columns (12):** `observation_date`, `state`, `commodity`, `season`, `measure_name`, `measure_value`, `measure_unit`, `temporal_basis`, `reporting_agency`, `source_url`, `retrieval_date_utc`, `quality_note`
- **Observation Date:** `2025-05-15` (Single date position)
- **Measures Reported:**
  1. `season_estimate`: 124.00 LMT (`seasonal_target_estimate`)
  2. `daily_procurement`: 19,706.25 MT (`single_day`)
  3. `progressive_procurement`: 11,919,510.10 MT (`cumulative_season_to_date`)
- **Candidate Key:** `['observation_date', 'measure_name']` — **0 duplicate rows**

### 3.4 National Foodgrain Stock Observations (`stock_observations_national_dfpd.csv`)
- **Row Count:** 100 rows
- **Columns (15):** `source_id`, `observation_date`, `geographic_coverage`, `state`, `agency`, `commodity_original`, `commodity_standard`, `grain_form`, `measure_name`, `measure_value`, `measure_unit`, `observation_type`, `source_url`, `raw_file`, `quality_note`
- **Date Coverage:** 2020-01-01 to 2026-01-01 (quarterly / monthly buffer norms)
- **Geographic Coverage:** `India Central Pool` (100% of rows)
- **State Null Count:** **100 / 100 rows null (100.0%)**
- **Commodity Breakdown:** Wheat (50 rows), Rice (50 rows)
- **Candidate Key:** `['observation_date', 'commodity_standard', 'measure_name']` — **0 duplicate rows**

### 3.5 NASA POWER Multi-Zone Weather (`punjab_multi_zone_daily_weather_2024_2025.csv`)
- **Row Count:** 3,655 rows
- **Columns (12):** `observation_date`, `state`, `station_name`, `agro_climatic_zone`, `latitude`, `longitude`, `temperature_mean_c`, `precipitation_mm_day`, `relative_humidity_pct`, `source_dataset`, `source_url`, `retrieval_date_utc`
- **Stations (5):** Amritsar (731 days), Bathinda (731 days), Hoshiarpur (731 days), Ludhiana (731 days), Patiala (731 days)
- **Date Coverage:** 2024-01-01 to 2025-12-31 (731 calendar days, includes leap year 2024)
- **Missing Values:** **0 nulls across all columns (0.0%)**
- **Candidate Key:** `['observation_date', 'station_name']` — **0 duplicate rows**

### 3.6 District Crop Production (`district_crop_production.csv`)
- **Row Count:** 230 rows
- **Columns (21):** `source_id`, `state`, `district_original`, `district_id`, `district_id_candidate`, `district_mapping_status`, `crop_original`, `crop_standard`, `season`, `agricultural_year`, `calendar_year`, `area_value`, `area_unit`, `production_value`, `production_unit`, `yield_value`, `yield_unit`, `observation_status`, `source_url`, `source_file`, `quality_note`
- **Temporal Coverage:** 5 agricultural years (2018-19 to 2022-23)
- **Geographic Coverage:** 23 Punjab districts
- **Crops:** Wheat (115 rows), Paddy grain interpretation (115 rows)
- **Null Semantics:** Exactly 6 rows have null area/production/yield due to newly bifurcated districts (Fazilka, Pathankot, SAS Nagar) in early source tables. `calendar_year` is 100% null (agricultural year standard used).
- **Candidate Key:** `['district_original', 'crop_standard', 'agricultural_year']` — **0 duplicate rows**

### 3.7 District Crop Yield (`district_crop_yield.csv`)
- **Row Count:** 2,754 rows
- **Columns (16):** `source_id`, `state`, `district_original`, `district_id`, `district_id_candidate`, `crop_original`, `crop_standard`, `season`, `agricultural_year`, `source_year_label`, `yield_value`, `yield_unit`, `observation_status`, `source_url`, `source_file`, `quality_note`
- **Sources Breakdown:**
  - `ogd_punjab_yield_wheat`: 1,265 rows (OGD historical, 1968-2022)
  - `ogd_punjab_yield_rice`: 1,265 rows (OGD historical, 1968-2022)
  - `des_apy_query_phase3_derived_yield`: 224 rows (DES APY derived, 2018-2023)
- **Schema Drift & Coalesced Key:** OGD rows record year in `source_year_label` (`agricultural_year` is null). DES rows record year in `agricultural_year` (`source_year_label` is null). Coalescing year produces 0 duplicates across `['source_id', 'district_original', 'crop_original', 'year_key_coalesced']`.

### 3.8 Punjab District Boundaries & Crosswalk
- **Boundaries GeoJSON (`punjab_district_boundaries.geojson`):** 23 features, EPSG:4326 WGS84 coordinates, 100% valid polygon geometries.
- **Crosswalk (`district_crosswalk.csv`):** 23 rows mapping APY source district names to standard boundary geometries and LGD candidate IDs. Candidate key is unique with 0 duplicate rows.

### 3.9 Sentinel-2 Satellite Tile (`S2B_43REP_20241005_B04_512px_window.tif`)
- **File Size:** 376,834 bytes
- **Scene Date:** `2024-10-05`
- **Specifications:** Sentinel-2B, Tile 43REP, Band 04 (Red, 10m spatial resolution), 512x512 pixels window.
- **Evidence Limitation:** Verified as a single spatial snapshot window, not a continuous multi-temporal monitoring series.

---

## 4. Manifest & Checksum Audit

All 49 files from the Phase 5 acquisition drop were verified:

- **Manifest File:** `data/manifests/STARTER_SOURCE_DROP_MANIFEST.json`
- **Total Registered Files:** 49
- **SHA-256 Checksum Matches:** 49 / 49 (100.0%)
- **Byte Size Matches:** 49 / 49 (100.0%)
- **Missing or Corrupted Files:** 0
- **Source Drop Directory:** `data/inbox/gemini_phase5/phase5_acquisition/` (Raw files strictly preserved and unmodified)

---

## 5. Quarantined Legacy Audit & Missing Historical Assets

### 5.1 Quarantined Files in `data/inbox/previous_audit/`
Inspection of `data/inbox/previous_audit/` revealed two malformed CSV files:
1. `DATA_COVERAGE_MATRIX.csv`: Unquoted commas on line 10 violate RFC 4180 parsing rules.
2. `DATA_SOURCE_REGISTER.csv`: Unquoted commas on line 11 violate RFC 4180 parsing rules. Referenced raw source files are absent from disk.

These files have been marked `stale` / `quarantined` and are isolated from the production catalog.

### 5.2 Explicitly Missing Data Assets
1. **Historical Codex Audit Folder:** Not present in repository workspace. Verified absent and recorded as `missing`; never synthesized.
2. **Anaaj Kharid Real-Time Daily Grain Arrivals:** Requires Punjab Government credentials / CAPTCHA bypass; recorded as `blocked`.
3. **FCI Punjab District-Level Silo Stocks:** Unpublished in open data portals; recorded as `missing`.

---

## 6. Next Steps for Phase 2

1. Preserve all raw files under `data/inbox/`.
2. Reference the generated machine-readable catalog at `data/manifests/dataset_catalog.csv` and `data/manifests/dataset_catalog.json` for all downstream app services.
3. Advance to **Phase 2 — Application Foundation**: establish clean backend routing and dataset registry endpoints without fabricated anomaly scores.
