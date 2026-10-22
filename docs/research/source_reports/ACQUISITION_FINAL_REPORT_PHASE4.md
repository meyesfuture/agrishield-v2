# Punjab Grain Hoarding Intelligence — Phase Four acquisition audit

**Run:** `20261021T154253Z` (UTC)  
**Latest authoritative audit:** this timestamped run; Phase One–Three reports and source artifacts remain under `../../reports/`, `../../raw/` and `../../processed/` and are preserved.

## What this run newly acquired

1. **FCI district stock position:** 192,086 actual daily district records for the Punjab FCI region across wheat, paddy, raw rice and parboiled rice, in source-reported quintals. The dates span 2011–2025 depending on commodity; the feed includes 13 source district names including Chandigarh. All raw API pages, pagination offsets, checksums and a normalized table are retained. Source-code and total-field caveats are material.
2. **OGD mandi prices:** 596 actual Punjab price rows for 21/10/2026. 63 wheat/paddy-labeled rows are paddy-only across 59 market names. This is a price-only, one-day dataset; the schema has no arrival quantity and no stated price unit.
3. **DES original CSV route:** official resource page and direct CSV URL were located. The actual CSV was **not** acquired: direct HTTPS GET timed out with TLS verification enabled, HEAD timed out at 25 seconds, and the trusted browser reported `ERR_CONNECTION_TIMED_OUT`. Existing 230-row DES browser extract remains separate and partial.

## Existing evidence revalidated

The package already contains production and area browser extracts for 23 district names, wheat/Rabi and rice/Kharif, 2018-19–2022-23; historical OGD yield files; procurement snapshots; national DFPD/FCI stocks; NASA POWER 2019–2025 at one Ludhiana-area point; 23 machine-readable district polygons with LGD codes and mixed vintages; and one real Sentinel-2 B04 raster window with 262,144 readable pixels. Existing test suite results and new Phase Four checks are in `FINAL_ACCEPTANCE_TESTS.md`.

## Answers to the project decisions

- A source-separated descriptive dashboard is a **CONDITIONAL GO**.
- Market-level supply anomaly detection is **NO-GO** because a qualifying arrival panel still does not exist.
- A supply balance residual is **NO-GO** because flows, processing, outflows and compatible inventories are incomplete; the new FCI feed supports only carefully qualified stock trends.
- Actual hoarding detection is **NO-GO** because no independent confirmed labels, controls or private inventory evidence exist.

No model, residual, risk score or hoarding label was created. See `GO_NO_GO_REPORT.md`, `SUPPLY_RECONCILIATION_FEASIBILITY.md`, `HOARDING_DETECTION_FEASIBILITY.md`, and `NEXT_ACTIONS.md`.
