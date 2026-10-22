# Go/no-go report

**Decision: NO-GO for a hoarding detection model or public anomaly dashboard. GO for a bounded data-access and validation pilot.**

## Why

The audit acquired a complete Survey of India reference map and a validated seven-day NASA POWER weather sample, and confirmed that Copernicus catalogue metadata responds. It did not acquire the core production, market, procurement, or stock observations. Procurement and stock sources had TLS or timeout failures; no Punjab image pixels or analysis-ready boundary vectors were acquired; and no independently verified private-hoarding labels were collected. The one official Indian Punjab ground-truth lead concerns missing government-custody wheat stock, a distinct problem class.

## Minimum gates before analysis

- Obtain several years of production rows and daily mandi arrivals/prices, with schema, units, dates, and district coverage checked.
- Obtain daily/weekly procurement by agency, grain form, and quantity basis; reconcile against mandi arrivals to avoid double-counting.
- Obtain dated stock and movement records with stock owner, rice/paddy basis, and source refresh/as-of times.
- Acquire historical weather and geospatial boundary files with vintage and checksum.
- Acquire multiple independently verified positive and negative event examples with case status and usable location/date, including a documented denominator.
- Complete one AOI/date-filtered satellite scene download and a field validation plan; no satellite signal alone can establish hoarding.

## Next actions

1. Re-run acquisition through a network path with a valid trusted certificate chain. Do not disable TLS verification. Resolve each TLS error and preserve subsequent run logs.
2. Request/obtain OGD API key and verify the actual crop dataset download; determine years, district codes, and revision status.
3. Inspect eNAM/Agmarknet, CFPP and FCI dashboard in the official browser or through documented API routes; capture actual CSV/JSON/PDF responses where permitted.
4. Request/obtain Punjab Food/Civil Supplies, Pungrain, police/vigilance and court records for stock declarations, inspections, seizures, and case outcomes.
5. Query Copernicus over Punjab for one identified Sentinel-2 L2A and Sentinel-1 pair, then download pixels and record product IDs/checksums.
6. Acquire official machine-readable boundary geometry or an appropriately licensed equivalent; use the Survey of India PDF only as a reference.

## Operating guardrails

Missing data remains null, not zero. Keep paddy distinct from milled rice and rice-equivalent procurement. Do not add mandi arrivals and procurement as independent supply. A residual, price movement, stock concentration, or satellite change is a screening signal only; it is not proof of hoarding or unlawful conduct.
