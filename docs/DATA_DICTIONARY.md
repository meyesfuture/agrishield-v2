# Canonical Data Dictionary & Schema Rules

This is the app's canonical contract. The Phase 5 source report and original dictionary are preserved in `docs/research/source_reports/`; changes here require a decision-log entry and schema version increment.

## Dataset `production_district_season`

Required fields: `source_id`, `source_record_id`, `district_name_source`, `district_id_vintage`, `district_name_std` (nullable until reviewed), `district_mapping_status`, `crop_source`, `crop_std` (`wheat`, `paddy`, `rice` distinct), `season_year`, `season_code`, `area_value`, `area_unit`, `production_value`, `production_unit`, `estimate_status`, `published_at`, `retrieved_at_utc`, `source_url`, `raw_sha256`.

## Dataset `yield_district_year`

`source_id`, `source_record_id`, source/std district names and ID vintage, crop source/std, year/season label, yield value/unit, source URL, retrieval timestamp and raw checksum. Preserve the distinction between an observed published yield and a yield calculated from area/production.

## Dataset `mandi_daily`

`source_id`, `market_id`, `market_name_source`, `district_id_vintage`, `trade_date`, `commodity_id`, `commodity_name_source`, `commodity_std`, `variety`, `arrivals_value` (nullable), `arrivals_unit` (nullable), `min_price`, `modal_price`, `max_price`, `price_currency`, `price_unit`, `reported_arrival_status`, `retrieved_at_utc`, `source_url`, `raw_sha256`.

Never infer arrival from price. Do not treat APMC non-grain produce arrivals as wheat/paddy grain arrivals. Price observations with null arrival quantity remain useful price observations only.

## Dataset `procurement_observation`

`source_id`, `season_code`, `season_year`, `observation_date`, `as_of_date`, `geography_id`, `agency`, `commodity_form` (`wheat`, `paddy`, `rice/CMR`), `measure_name`, `quantity_value`, `quantity_unit`, `quantity_basis` (`wheat_mass`, `paddy_mass`, `rice_equivalent`, `bags`), `temporal_basis` (`daily`, `cumulative`, `estimate`, `snapshot`), `farmers_count`, `retrieved_at_utc`, `source_url`, `raw_sha256`.

Never mix cumulative totals with daily observations. Paddy procurement is not rice output. Keep source-reported unit and basis exactly.

## Dataset `stock_observation`

`source_id`, `as_of_date`, `reporting_date`, `geography_id`, `geography_level`, `agency_or_owner`, `facility_id`, `commodity_form`, `stock_value`, `stock_unit`, `capacity_value`, `capacity_unit`, `measure_type`, `quantity_basis`, `retrieved_at_utc`, `source_url`, `raw_sha256`.

Stock is a point-in-time inventory; inflow/offtake/dispatch are flows; capacity is not inventory. National Central Pool data must be labelled national, not Punjab-specific.

## Dataset `weather_daily`

`source_id`, `station_id`, `station_name`, `latitude`, `longitude`, `district_mapping_status`, `date`, `variable`, `value`, `unit`, `observation_or_forecast`, `time_standard`, `quality_flag`, `retrieved_at_utc`, `raw_sha256`.

## Dataset `ground_truth_event`

`event_id`, `event_date`, `location_text`, district ID/vintage, optional controlled-access coordinates, commodity form, quantity/unit, `event_type` (`inspection`, `seizure`, `stock_mismatch`, `charge`, `conviction`, `case_dismissed`, `cleared`, `other`), `legal_status`, `label_confidence`, primary source URL, independent corroboration URL, source excerpt, coder/reviewer and timestamps, raw checksum. Allegations and adjudicated outcomes must be separate classes.

## Universal rules

- Unknown is null, never zero.
- Dates use ISO 8601; preserve reporting date, event date and retrieval time independently.
- Preserve source names and original values.
- Keep paddy vs milled rice and source units separate.
- Every row traces to source and input checksum.
