# Product Requirements Document — Punjab GrainWatch

**Status:** Draft v1, grounded in the Phase 5 evidence package. **Primary goal:** deliver a functional, demonstrable agricultural intelligence product; do not imply validated hoarding detection.

## 1. Product summary

Punjab GrainWatch brings public agricultural evidence into one auditable interface. It helps a user explore district-level crop production/yield, dated market price observations, weather context, government procurement snapshots, national stock context, geography and the readiness/quality of each dataset. It should make data gaps as visible as charted values.

## 2. Problem

Agricultural supply-chain evidence is fragmented across different agencies, time scales, commodity definitions and geographic schemes. Dataset titles and API documentation can overstate practical availability: a route may expose prices without arrivals, national stocks instead of Punjab inventory, or produce arrivals that exclude wheat and paddy. Users need traceable data and clear coverage diagnostics before attempting supply reconciliation.

## 3. Users

- Student/hackathon demonstrator operating the application locally.
- Reviewer/mentor checking whether data claims are supported.
- Analyst exploring production, market, weather and procurement evidence.
- Future authorized investigator, only after lawful access to relevant stock/flow records and validated incident outcomes.

## 4. Goals

- Present all currently verified datasets with sources, coverage, units and limitations.
- Make data freshness, missingness, geographical mismatches and API blockers visible.
- Provide useful charts/maps for production, yield, weather, paddy prices, procurement context and national stocks.
- Build a reproducible data ingestion/normalization path with immutable raw inputs and checksums.
- Support carefully qualified statistical stock/price anomalies only where comparable observations and adequate history exist.
- Provide a polished, responsive product with a 3D landing hero, premium motion, accessible controls and graceful fallbacks.
- Explain exactly what must be acquired to advance toward wheat/paddy supply anomaly analysis.

## 5. Non-goals for V1

- Proving or predicting illegal hoarding.
- Ranking traders, mandis or warehouses as hoarders.
- Inferring private inventory from national stock totals, weather, prices or satellite imagery.
- Treating all APMC arrivals as grain arrivals.
- Summing mandi arrivals and government procurement as independent inflows where they overlap.
- Claiming a model is accurate without a valid, independent evaluation set.
- Bypassing CAPTCHA, login, API keys, terms of use or TLS checks.

## 6. V1 product areas

1. **Landing / Overview:** project premise, coverage counters, latest data dates, status of key evidence gates and links to explore.
2. **Data Explorer:** searchable dataset registry with source, grain/crop, date coverage, geography, units, row count, update time, quality flags and raw/derived provenance.
3. **Crop Production & Yield:** district/crop/season/year charts with missing cells and district-vintage notes visible.
4. **Market Watch:** verified paddy modal prices and market coverage. Do not display arrival quantities when the source field is null.
5. **Weather Context:** five-station daily series for temperature, precipitation and humidity over 2024–2025; clearly state these are point/station proxies rather than district crop-loss records.
6. **Procurement & Stocks:** three state-level wheat procurement metrics from the cited reporting position and national Central Pool stocks. Show reporting level and as-of date prominently.
7. **Geospatial Explorer:** 23 district polygons with known vintage/crosswalk caveats; avoid unsupported market-to-district joins.
8. **Quality & Readiness:** supply-flow coverage matrix, source connectivity tests, nulls/unit checks and explicit blockers.
9. **Alert Lab:** only validated non-accusatory descriptive anomalies if time-series requirements pass; synthetic demonstrations, if any, are unmistakably marked `SYNTHETIC`.
10. **Evidence & Methods:** source references, methodologies, data definitions, decisions, limitations and changelog.

## 7. Current accepted evidence (from Phase 5 package)

- APMC arrivals panel: 3,892 records across 62 produce commodities, 8 districts, 16 branches, covering 2026-10-01 through 2026-10-21; quantities in quintals. The report states no daily wheat/paddy arrival records are present.
- AGMARKNET weekly prices: 53 paddy modal-price observations, 2026-10-13 through 2026-10-19; price unit Rs./quintal; arrival quantities null. Wheat is out of season in this sample.
- Weather: 3,655 station-days, five locations, daily 2024–2025, with T2M, precipitation and relative humidity variables.
- Production extract: 230 rows for wheat/Rabi and rice/Kharif, 23 district names, 2018–19 to 2022–23; 12 missing values noted in the source report.
- Yield files: historical wheat/rice yield history labelled 1968–2022; normalize only after examining actual schema and geography vintage.
- Procurement: three Punjab state-aggregate wheat RMS 2025–26 metrics from a May 15, 2025 position.
- Stocks: 100 rows in the extracted national Central Pool dataset, 25 dates, 2020–2026; not Punjab-disaggregated.
- Geography: 23 district polygons/crosswalk entries with historical-vintage limitations.
- Satellite: one 512×512 10 m Sentinel-2 B04 raster window dated 2024-10-05, not enough for warehouse or time-series detection.

Counts above are the acquisition report's summary. The implementation must re-compute counts, dates, commodity coverage and nulls directly from files and log any mismatch.

## 8. UX requirements

- Clear navigation and one obvious primary action per view.
- Every chart has title, unit, period, geography, source and definition of the measure.
- Empty or unavailable data shows a helpful explanation, not a zero-valued chart.
- Each metric states its geographic level and `as-of` date.
- Mobile/tablet/desktop responsive; keyboard accessible; appropriate color contrast.
- Motion is purposeful and has reduced-motion alternatives.
- 3D hero must not delay key dashboard content or block navigation.

## 9. Success metrics for V1

- Every displayed metric traces to a specific source file/record or documented transformation.
- All dataset counts shown in UI are generated from validated inventory, not hardcoded marketing copy.
- No unsupported wheat/paddy arrival data is displayed.
- Missing values remain null and explicit zero remains zero.
- All ingestion and transformation steps are repeatable and idempotent.
- Main flows and API endpoints have tests; build and production preview succeed on the target environment.
- A reviewer can reach each dataset's provenance and caveats within two interactions.

## 10. Release gates

V1 descriptive dashboard: go after data validation and end-to-end tests. Grain supply anomaly: do not enable until comparable wheat/paddy arrival quantities across sufficient dates/markets are validated and model evaluation is documented. Hoarding detection: out of scope until independent, legally vetted positive and negative case evidence and relevant stock-flow data are available.
