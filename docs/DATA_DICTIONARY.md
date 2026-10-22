# Canonical Data Dictionary & Schema Rules

**Schema Version:** 1.1.0 (Phase 1 Validated Empirical Alignment)  
**Last Updated:** 2026-10-22  
**Validation Status:** Validated against actual files in `data/inbox/gemini_phase5/phase5_acquisition/`

The Phase 5 source report and original dictionary are preserved in `docs/research/source_reports/`. Changes here require a decision-log entry and schema version increment.

---

## Decision Log

### `DECISION-20261022-01`: Alignment of Canonical Dictionary with Observed Physical Schemas
- **Context:** Phase 0 reconnaissance and Phase 1 data validation proved that physical files in `data/inbox/gemini_phase5/phase5_acquisition/processed/` contain specific field names, null patterns, and unit representations that differed from theoretical specification sketches.
- **Decision:** Document both the canonical domain target model and the verified physical CSV schema mapping for every dataset, without modifying immutable source files.
- **Key Empirical Alignments:**
  1. `mandi_arrivals`: Actual file columns are `observation_date`, `entry_date_raw`, `state`, `district_name`, `mandi_branch_name`, `commodity_name`, `arrival_quantity`, `arrival_unit`, `min_price`, `max_price`, `modal_price`, `price_unit`, `source_system`, `source_endpoint`, `retrieval_date_utc`, `scope_note`. Verified 0 wheat/paddy grain records; 71 dhan matches are Coriander Green (*Hara Dhaniya*). Audited 3 rows with `modal_price == 0.0` as explicit clerk sentinels for "not reported".
  2. `agmarknet_daily_prices`: Actual columns include `arrival_quantity`, which is 100.0% null (53/53 rows). Feed is modal price only.
  3. `crop_yield`: Merged file contains 2,530 OGD rows and 224 DES APY derived rows. OGD rows populate `source_year_label` with `agricultural_year` null; DES rows populate `agricultural_year` with `source_year_label` null. Coalescing these yields a unique candidate key (`['source_id', 'district_original', 'crop_original', 'year_key_coalesced']`).
  4. `crop_production`: Exactly 6 rows have null `area_value`, `production_value`, and `yield_value` due to newly bifurcated districts (Fazilka, Pathankot, SAS Nagar) in early source tables. `calendar_year` is 100% null (agricultural year used).
  5. `stock_observations`: All 100 rows have `state` as null/NaN and `geographic_coverage` as `India Central Pool`. Represents national aggregate buffer stock, not Punjab warehouse inventories.
  6. `procurement`: All 3 rows share the single position date `2025-05-15` across 3 distinct temporal bases (`seasonal_target_estimate`, `single_day`, `cumulative_season_to_date`). They cannot be summed as a time series.

---

## 1. Dataset `mandi_daily` / Mandi Arrivals Panel

**Primary Physical Source:** `data/inbox/gemini_phase5/phase5_acquisition/processed/punjab_mandi_arrivals_oct2026.csv`  
**Byte-Identical Copy:** `data/inbox/gemini_phase5/phase5_acquisition/ARRIVALS_PANEL.csv`  
**Row Count:** 3,892 rows | **Candidate Key:** `['observation_date', 'mandi_branch_name', 'commodity_name']` (0 duplicates)

| Field Name | Physical Type | Null Count | Description & Constraints |
| :--- | :--- | :--- | :--- |
| `observation_date` | String (ISO 8601) | 0 | Date of mandi arrival (`2026-10-01` to `2026-10-21`). |
| `entry_date_raw` | String | 0 | Source date string from e-Mandikaran portal. |
| `state` | String | 0 | State name (`PUNJAB`). |
| `district_name` | String | 0 | Reporting district (8 districts represented). |
| `mandi_branch_name` | String | 0 | Specific APMC mandi yard or sub-yard (38 mandis). |
| `commodity_name` | String | 0 | Commodity name. **62 produce items; 0 wheat/paddy grains.** |
| `arrival_quantity` | Float | 0 | Arrival volume in specified unit (all > 0). |
| `arrival_unit` | String | 0 | Unit of measurement (`quintals`). |
| `min_price` | Float | 0 | Minimum transaction price in Rs./Quintal. |
| `max_price` | Float | 0 | Maximum transaction price in Rs./Quintal. |
| `modal_price` | Float | 0 | Modal price in Rs./Quintal. **Note: 3 rows have 0.0 as explicit sentinel for "not reported".** |
| `price_unit` | String | 0 | Currency unit (`Rs./Quintal`). |
| `source_system` | String | 0 | Originating system (`e-Mandikaran Punjab`). |
| `source_endpoint` | String | 0 | API endpoint route. |
| `retrieval_date_utc` | String (ISO 8601) | 0 | Extraction timestamp (`2026-10-21T19:14:17Z`). |
| `scope_note` | String | 0 | Provenance note on APMC produce coverage. |

**Critical Evidence Rule:** Never infer wheat/paddy grain arrivals from this panel. The 71 rows matching the substring `dhan` are strictly `CORIANDER GREEN (HARA DHANIYA / ਹਰਾ ਧਨਿਆ )`.

---

## 2. Dataset `agmarknet_punjab_daily_prices`

**Primary Physical Source:** `data/inbox/gemini_phase5/phase5_acquisition/processed/agmarknet_punjab_daily_prices.csv`  
**Row Count:** 53 rows | **Candidate Key:** `['observation_date', 'market_id', 'commodity_id']` (0 duplicates)

| Field Name | Physical Type | Null Count | Description & Constraints |
| :--- | :--- | :--- | :--- |
| `observation_date` | String (ISO 8601) | 0 | Price quote date (`2026-10-13` to `2026-10-19`). |
| `state` | String | 0 | State name (`Punjab`). |
| `state_id` | Integer | 0 | AGMARKNET internal state ID (`28`). |
| `market_id` | Integer | 0 | Regulated market entity ID (50 APMCs). |
| `market_name` | String | 0 | Market name. |
| `commodity_id` | Integer | 0 | AGMARKNET commodity identifier (`24` for Paddy). |
| `commodity_name` | String | 0 | Commodity name (`Paddy(Common)`). |
| `variety` | String | 0 | Commercial variety (e.g. `Other`, `Basmati`). |
| `arrival_quantity` | Float | **53 (100%)** | **100% NULL.** Feed provides prices only. |
| `min_price` | Float | 0 | Minimum price (Rs./Quintal). |
| `modal_price` | Float | 0 | Modal price (Rs./Quintal). Validated range Rs. 2,300 - 2,360. |
| `max_price` | Float | 0 | Maximum price (Rs./Quintal). |
| `source_url` | String | 0 | AGMARKNET weekly price endpoint. |
| `retrieval_date_utc` | String (ISO 8601) | 0 | Extraction timestamp (`2026-10-21T19:12:54Z`). |

**Critical Evidence Rule:** Never infer arrival quantity from prices. Null arrivals must remain null in all presentation and analytics layers.

---

## 3. Dataset `procurement_observation`

**Primary Physical Source:** `data/inbox/gemini_phase5/phase5_acquisition/processed/cfpp_punjab_wheat_procurement_2025_26.csv`  
**Row Count:** 3 rows | **Candidate Key:** `['observation_date', 'measure_name']` (0 duplicates)

| Field Name | Physical Type | Null Count | Description & Constraints |
| :--- | :--- | :--- | :--- |
| `observation_date` | String (ISO 8601) | 0 | Position date (`2025-05-15`). Single date snapshot. |
| `state` | String | 0 | State name (`Punjab`). |
| `commodity` | String | 0 | Commodity (`Wheat`). |
| `season` | String | 0 | Marketing season (`RMS 2025-26`). |
| `measure_name` | String | 0 | `season_estimate`, `daily_procurement`, `progressive_procurement`. |
| `measure_value` | Float | 0 | Quantitative measure value. |
| `measure_unit` | String | 0 | `Lakh Metric Tonnes (LMT)` or `Metric Tonnes (MT)`. |
| `temporal_basis` | String | 0 | `seasonal_target_estimate`, `single_day`, `cumulative_season_to_date`. |
| `reporting_agency` | String | 0 | `Central Food Grains Procurement Portal (CFPP)`. |
| `source_url` | String | 0 | Official portal URL. |
| `retrieval_date_utc` | String (ISO 8601) | 0 | Extraction timestamp (`2026-10-21T19:15:16Z`). |
| `quality_note` | String | 0 | Contextual explanation of measure basis. |

**Critical Evidence Rule:** Never sum these 3 rows as a time series. They represent 3 concurrent temporal perspectives of a single date.

---

## 4. Dataset `stock_observation` / DFPD National Stocks

**Primary Physical Source:** `data/inbox/gemini_phase5/phase5_acquisition/processed/stocks/stock_observations_national_dfpd.csv`  
**Row Count:** 100 rows | **Candidate Key:** `['observation_date', 'commodity_standard', 'measure_name']` (0 duplicates)

| Field Name | Physical Type | Null Count | Description & Constraints |
| :--- | :--- | :--- | :--- |
| `source_id` | String | 0 | Source identifier (`dfpd_monthly_foodgrain_bulletin`). |
| `observation_date` | String (ISO 8601) | 0 | Observation date (`2020-01-01` to `2026-01-01`). |
| `geographic_coverage`| String | 0 | Exclusively `India Central Pool` for all 100 rows. |
| `state` | String | **100 (100%)**| **100% NULL.** National buffer stock only. |
| `agency` | String | 0 | Custodian agency (`FCI / Central Pool`). |
| `commodity_original` | String | 0 | Source commodity label (`Wheat`, `Rice`). |
| `commodity_standard` | String | 0 | Standardized commodity (`wheat`, `rice`). |
| `grain_form` | String | 0 | Form of grain (`raw_grain`, `milled_cereal`). |
| `measure_name` | String | 0 | `actual_central_pool_stock` (50) or `foodgrain_stocking_norm` (50). |
| `measure_value` | Float | 0 | Stock quantity in LMT. |
| `measure_unit` | String | 0 | Unit (`Lakh Metric Tonnes (LMT)`). |
| `observation_type` | String | 0 | `observed_stock` or `policy_norm`. |
| `source_url` | String | 0 | DFPD publication URL. |
| `raw_file` | String | 0 | Source bulletin extract filename. |
| `quality_note` | String | 0 | Notes on buffer norm revisions. |

**Critical Evidence Rule:** National Central Pool buffer stock must always be labelled national. It does NOT represent grain stored within Punjab silos or warehouses.

---

## 5. Dataset `weather_daily` / NASA POWER Multi-Zone

**Primary Physical Source:** `data/inbox/gemini_phase5/phase5_acquisition/processed/punjab_multi_zone_daily_weather_2024_2025.csv`  
**Row Count:** 3,655 rows | **Candidate Key:** `['observation_date', 'station_name']` (0 duplicates)

| Field Name | Physical Type | Null Count | Description & Constraints |
| :--- | :--- | :--- | :--- |
| `observation_date` | String (ISO 8601) | 0 | Calendar date (`2024-01-01` to `2025-12-31`, 731 days). |
| `state` | String | 0 | State (`Punjab`). |
| `station_name` | String | 0 | Station: `Amritsar`, `Bathinda`, `Hoshiarpur`, `Ludhiana`, `Patiala`. |
| `agro_climatic_zone` | String | 0 | Agro-climatic sub-region classification. |
| `latitude` | Float | 0 | Station latitude coordinate. |
| `longitude` | Float | 0 | Station longitude coordinate. |
| `temperature_mean_c` | Float | 0 | Mean daily surface temperature in °C (-5.0 to 45.0). |
| `precipitation_mm_day`| Float | 0 | Daily precipitation in mm (all >= 0.0). |
| `relative_humidity_pct`| Float | 0 | Daily relative humidity percentage (0.0 to 100.0). |
| `source_dataset` | String | 0 | `NASA POWER Agroclimatology`. |
| `source_url` | String | 0 | NASA POWER API endpoint. |
| `retrieval_date_utc` | String (ISO 8601) | 0 | Extraction timestamp. |

---

## 6. Dataset `production_district_season`

**Primary Physical Source:** `data/inbox/gemini_phase5/phase5_acquisition/processed/district_crop_production.csv`  
**Row Count:** 230 rows | **Candidate Key:** `['district_original', 'crop_standard', 'agricultural_year']` (0 duplicates)

- **Coverage:** 23 Punjab districts, 2 crops (`wheat`, `paddy_grain_interpretation`), 5 agricultural years (`2018-19` to `2022-23`).
- **Null Semantics:** Exactly 6 rows have null `area_value`, `production_value`, and `yield_value` due to newly created districts (Fazilka, Pathankot, SAS Nagar) in early source tables. `calendar_year` is 100% null (all 230 rows).

---

## 7. Dataset `yield_district_year`

**Primary Physical Source:** `data/inbox/gemini_phase5/phase5_acquisition/processed/district_crop_yield.csv`  
**Row Count:** 2,754 rows | **Candidate Key:** `['source_id', 'district_original', 'crop_original', 'year_key_coalesced']` (0 duplicates)

- **Sources:**
  - `ogd_punjab_yield_wheat`: 1,265 rows (1968-2022, kg/ha)
  - `ogd_punjab_yield_rice`: 1,265 rows (1968-2022, kg/ha)
  - `des_apy_query_phase3_derived_yield`: 224 rows (2018-2023, kg/ha derived)
- **Schema Drift Note:** OGD rows populate `source_year_label` with `agricultural_year` null; DES APY derived rows populate `agricultural_year` with `source_year_label` null. Coalescing these two columns resolves 0 duplicate candidate keys.

---

## 8. Dataset `satellite_scene`

**Primary Physical Source:** `data/inbox/gemini_phase5/phase5_acquisition/processed/satellite/S2B_43REP_20241005_B04_512px_window.tif`  
**Specifications:** Single GeoTIFF file (376,834 bytes), Sentinel-2B Tile 43REP, Band 04 (Red, 10m), acquisition date `2024-10-05`, 512x512 pixels window.  
**Critical Evidence Rule:** Single snapshot window only. Does not constitute a multi-temporal monitoring series.

---

## Universal Invariants

1. **Unknown is Null, Never Zero:** When a value is missing or unobserved, it is stored as `null`/`NaN`. A value of `0.0` represents an explicit observation or source clerk sentinel.
2. **ISO 8601 Dates:** All dates are formatted as `YYYY-MM-DD` and timestamps as `YYYY-MM-DDTHH:MM:SSZ`.
3. **Immutability of Source Files:** Raw acquisition files under `data/inbox/` are read-only and never modified or overwritten.
4. **No Hoarding Inference:** Statistical discrepancies in prices, weather, or produce arrivals do not constitute proof of hoarding.
