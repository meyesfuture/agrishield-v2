# Research & Feasibility — Current Evidence

## Decision summary

- **Conditional GO:** source-separated descriptive agricultural intelligence dashboard and data-access/validation pilot.
- **NO-GO currently:** market-level wheat/paddy supply anomaly ranking, a complete supply balance, actor-level risk scoring, and validated hoarding detection.

## Why

Phase 5 acquired useful contextual evidence and reusable acquisition scripts. The public Mandi Board arrival API yielded 3,892 records, but they are fruit/vegetable/other produce—not wheat/paddy. AGMARKNET's weekly endpoint yielded paddy prices (arrival field null) and the core arrival endpoint requires CAPTCHA. CEDA returns unauthorized without its token. Procurement is state-aggregate and one reporting position. The stock file is national. Private inventory, milling and movement/outflow data are absent. There is no independent, legally adjudicated private-hoarding dataset with matched compliant controls.

## What the available files can support

- Crop production/yield trend views with missing-cell and district-vintage warnings.
- Paddy market-price views over the dates actually present.
- Weather charts for five point locations in 2024–2025.
- Procurement context with clear reporting level/date/temporal basis.
- National stock context, labelled national.
- District map, after validating geometry and crosswalk.
- Dataset quality/provenance, API readiness and coverage dashboard.
- Example-only synthetic scenario clearly labelled as synthetic.

## What is missing for grain supply monitoring

1. Historical daily wheat/paddy arrivals by market and date, with stable IDs, units and reporting/missingness semantics.
2. Compatible procurement by day/agency/commodity basis, and overlap handling with arrivals.
3. Dated Punjab/district/depot inventories and movement/outflow series.
4. Paddy-to-rice milling/outturn and relevant distribution/dispatch records where needed.
5. Mapped facilities/markets with reviewed boundary-vintage joins.
6. Independent positive and negative inspection/incident evidence with verified legal status and denominator.

## Satellite feasibility

The bundle includes one Sentinel-2 B04 10m window, not a repeated scene series. Satellite data may eventually inform crop condition/harvest timing or large exposed-yard changes; it cannot see indoor stock through a roof and alone cannot show concealment or illegal intent. Do not create a warehouse detector from this single raster.

## Highest-value next acquisition

Get authorized historical wheat/paddy grain arrival quantities. For AGMARKNET, use legitimate supported access or official exports rather than attempting CAPTCHA bypass. For CEDA, register for a token and verify current schema. For Punjab grain procurement/inventory flows, use authorized official reports/requests where public bulk interfaces are not available. If those cannot be obtained, continue the descriptive dashboard and be explicit about the limitation.
