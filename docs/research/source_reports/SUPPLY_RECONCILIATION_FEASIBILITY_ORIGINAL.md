# Supply reconciliation feasibility

## Current result: not yet computable

The sources are plausible, but this run acquired no observations for production, mandi arrivals, procurement, stocks, movement, or historical weather. There is not yet enough validated time-series data to calculate a Punjab grain balance or an anomaly score.

## Accounting frame

For each commodity, geography, season, and period, build a balance only after validating coverage and units:

`opening_stock + production + inward_movement + imports = consumption/use + outward_movement + losses + closing_stock + unexplained_residual`

Use a source-specific boundary between public and private stocks. If private stocks are not observed, the residual is not a direct estimate of hoarding. It can reflect measurement gaps, timing, unrecorded movement, milling conversion, seed/feed use, post-harvest losses, or boundary mismatches.

## Double-count and unit rules

- Mandi arrivals are not additive to procurement when government purchases occur within those arrivals. Use procurement as a channel/overlap attribute or reconcile by transaction records, not a separate supply inflow.
- Paddy production and procurement should use paddy mass. Custom milled rice is a later conversion flow. Rice-equivalent procurement must remain separately tagged and not be treated as paddy tonnes.
- Keep daily, cumulative, seasonal, fiscal-year, and as-of stock measures distinct. Never sum a cumulative procurement series across dates.
- Match data to stable district/mandi IDs and historical boundary vintages. Aggregate only after the crosswalk is reviewed.
- Preserve explicit reporting zeros; map missing/non-reporting cells to null.
- Convert quintal, bag, tonne, and LMT only with documented factors and known bag weights.

## Minimum viable panel

At least five to ten years of district-season production estimates, daily mandi arrivals/prices across the procurement season, daily or weekly procurement by agency and grain form, monthly/as-of stocks and movements, dated weather covariates, and facility/mandi coordinates. Maintain a data coverage matrix before modeling. A primary balance should run monthly/seasonal at district or state level with uncertainty bands and explicit residuals.

## Feasibility blockers

1. Obtain OGD production rows (including older district vintages), not just metadata.
2. Obtain comparable historical mandi observations with field definitions and missingness.
3. Obtain state/district procurement by agency with dates and separate paddy vs rice-equivalent quantities.
4. Obtain stock snapshots plus evacuation/movement series with reporting dates and agency ownership.
5. Establish private-storage/warehouse registry coverage and an independently validated incident set.

Until these are resolved, descriptive source coverage is feasible; causal inference or hoarding detection is premature.
