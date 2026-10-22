# Analytics, Anomaly Screening & Hoarding Claim Boundaries

## Current eligibility

- Descriptive production/yield/weather/price and source-level procurement/stock displays: **conditional go**, after per-file validation.
- Historical grain market arrival anomaly detection: **no-go** because the currently acquired daily arrival panel contains no wheat/paddy grain arrivals and the AGMARKNET price feed has null arrival quantities.
- Full supply reconciliation: **no-go** because comparable Punjab stocks, milling, movement/outflows and private inventory are not present.
- Private grain-hoarding detector: **no-go** because verified independent positive labels and inspected compliant controls are absent.

## Future statistical screening gate

Only after the relevant grain-arrival dataset is verified:
1. Require comparable market × date × commodity observations, clear units, stable IDs and documented reporting gaps.
2. Check seasonality and source reporting rules before fitting a baseline.
3. Start with descriptive medians/seasonal baselines and prediction intervals before complex ML.
4. Use time-ordered walk-forward evaluation and market/location-separated checks where appropriate.
5. Report data coverage, false alerts per market-period, uncertainty and alert-review burden. Don't report classification accuracy if no valid labels exist.
6. Store model version, inputs, feature window, expected range, observed value, residual and review outcome.
7. Label outputs `statistical anomaly candidate`, never `hoarding detected`.

## Accounting guardrails

A candidate grain balance might be represented as:

`opening stock + production + inward movement = use/consumption + outward movement + losses + closing stock + unexplained residual`

This is not computable until matched definitions, boundaries, units and temporal bases exist. The residual is not a direct hoarding estimate: timing, reporting gaps, private/alternate markets, milling recovery, seed/feed use, inter-state movement and boundary mismatches can all contribute.

- Mandi arrivals and procurement may overlap; do not double-count.
- Paddy and milled rice are distinct. Conversion requires documented recovery assumptions and lag.
- National Central Pool stocks are not Punjab-specific stocks.
- One-off procurement snapshots cannot be interpolated into daily flow.
- Weather and satellite imagery provide context, not proof of concealment or intent.

## Synthetic demo policy

A synthetic “what-if” simulation is allowed to demonstrate how a future system could show an unusual drop. The UI must label it `SYNTHETIC EXAMPLE — NOT REAL DATA`; put it in `data/synthetic/`; and exclude it from real coverage metrics and evaluation.
