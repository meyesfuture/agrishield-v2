# Testing & Acceptance Criteria

## Data checks

- Archive integrity and manifest hashes verified.
- Each dataset's row count, columns, dates, geography and commodity composition are recomputed from actual file content.
- Phase 5 APMC arrival dataset must be tested for wheat/paddy rows. Current reported result is zero; the UI must not represent its 3,892 produce-arrival rows as grain arrivals.
- AGMARKNET paddy price feed keeps arrivals null and unit Rs./Quintal.
- Weather point series have no duplicate station-date keys; units and missing/sentinel values are checked.
- Production/yield data check null counts, duplicate keys, crop aliases, units and historical district mapping.
- Procurement daily/cumulative/snapshot values are not summed together.
- National stock geography label remains national.
- GeoJSON CRS, geometry validity, LGD identifiers and feature count are verified.
- Single satellite raster is validated for readable pixels, CRS, transform and no-data metadata, but is not presented as time-series proof.

## Backend checks

- Unit tests for adapters using stored fixtures, schema validators and transformations.
- API pagination, invalid filters, missing data and blocked-source errors return predictable responses.
- Ingestion is idempotent and writes manifests/checksums.
- TLS verification is enabled.
- Secrets never appear in logs or source control.

## Frontend checks

- Every route renders loading, empty, partial, stale and error states.
- Charts show units, period, geography, source and null-data semantics.
- Filters update rendered data; sorting/pagination works on tables where present.
- 3D fallback and reduced-motion behavior work.
- Keyboard navigation, focus, contrast, screen size responsiveness and browser console are checked.
- No synthetic data appears without a visible synthetic banner.

## Release checks

- Clean install instructions tested from the documented working directory.
- Lint, typecheck, backend tests, frontend tests and build all complete with recorded outputs.
- Production build starts and core flows pass a smoke test.
- README and `PROJECT_STATE.md` are updated.
- Report counts are regenerated rather than pasted from an old run.

## Hard no-go checks

Fail the release if the app claims validated hoarding detection; shows prices as arrivals; labels national stocks as Punjab stocks; converts nulls to zeros; adds procurement to arrivals without overlap handling; fabricates data; or conceals blocked APIs.
