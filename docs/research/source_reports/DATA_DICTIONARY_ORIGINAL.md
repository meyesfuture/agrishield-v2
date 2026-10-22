# Data dictionary and normalization contract

No normalized analytical observations have been created yet. This defines the fields and rules required for future `processed/` tables.

## Core tables

### `production_district_season.csv`

`source_id`, `source_record_id`, `district_name_source`, `district_id_vintage`, `district_name_std`, `crop_source`, `crop_std` (`wheat`, `paddy`, `rice` kept distinct), `season_year`, `season_code`, `area_value`, `area_unit`, `production_value`, `production_unit`, `estimate_status`, `published_at`, `retrieved_at_utc`, `source_url`, `raw_sha256`.

Do not derive paddy mass from rice procurement without an explicit milling recovery assumption and separate derived field.

### `mandi_daily.csv`

`source_id`, `market_id`, `market_name_source`, `district_id_vintage`, `trade_date`, `commodity_std`, `variety`, `arrivals_value`, `arrivals_unit`, `min_price`, `modal_price`, `max_price`, `price_currency`, `price_unit`, `reported_trade_or_arrival`, `retrieved_at_utc`, `source_url`, `raw_sha256`.

Keep arrivals (physical inflow to market) distinct from procurement (government purchase); they may overlap in the same grain and must not be added as independent production.

### `procurement_daily.csv`

`source_id`, `season_code`, `season_year`, `date`, `district_id_vintage`, `mandi_id`, `agency`, `commodity_form` (`wheat`, `paddy`, `rice/CMR`), `quantity_value`, `quantity_unit`, `quantity_basis` (`paddy_mass`, `rice_equivalent`, `wheat_mass`, `bags`), `farmers_count`, `cumulative_flag`, `retrieved_at_utc`, `source_url`, `raw_sha256`.

Never aggregate day-level observations with cumulative totals. Keep paddy procurement as paddy unless the source explicitly reports rice-equivalent (CMR); do not mix these.

### `stocks_movement.csv`

`source_id`, `as_of_date`, `reporting_date`, `geography_id`, `agency_or_owner`, `facility_id`, `commodity_form`, `stock_value`, `stock_unit`, `capacity_value`, `capacity_unit`, `inflow`, `outflow`, `loss_or_gain`, `allocation`, `offtake`, `quantity_basis`, `retrieved_at_utc`, `source_url`, `raw_sha256`.

Stock is a point-in-time inventory. Inflow, offtake, and dispatch are flows. Storage capacity is not stock. Preserve stock owner and whether unmilled paddy is excluded.

### `weather_daily.csv`

`source_id`, `station_id`, `station_name`, `latitude`, `longitude`, `district_id_vintage`, `date`, `variable`, `value`, `unit`, `observation_or_forecast`, `time_standard`, `quality_flag`, `retrieved_at_utc`, `raw_sha256`.

### `ground_truth_events.csv`

`event_id`, `event_date`, `location_text`, `district_id_vintage`, `latitude`, `longitude`, `commodity_form`, `quantity_value`, `quantity_unit`, `event_type` (`inspection`, `seizure`, `stock_mismatch`, `charge`, `conviction`, `case_dismissed`, `other`), `legal_status`, `label_confidence`, `primary_source_url`, `independent_corroboration_url`, `source_quote_or_excerpt`, `coder`, `coded_at`, `raw_sha256`.

Do not use a press report as a confirmed illegal-hoarding label unless status and legal basis are verified. Store allegations separately from adjudicated outcomes.

## General null, units, and dates

- Blank/unknown/unreported is null, never numeric zero. Store explicit source zero as 0 and preserve original source text.
- Preserve original value and unit alongside any converted value. Conversions require an explicit `conversion_factor`, source, and formula.
- Store dates as ISO 8601. Keep marketing season separate from calendar and fiscal years.
- Retain source geography names and boundary vintage; districts have changed over time.
- Every row must trace to a source URL, retrieval timestamp, and raw file checksum.
