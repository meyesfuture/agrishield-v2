"""
Pytest unit and data integrity test suite for Punjab GrainWatch.
Enforces non-negotiable empirical boundaries, manifest integrity,
schema constraints, null/zero semantics, and candidate key uniqueness.
"""

from pathlib import Path
import json
import pandas as pd
import pytest

from scripts.data_validation.integrity import (
    compute_sha256,
    verify_starter_drop_manifest,
    verify_provenance_manifest,
)
from scripts.data_validation.validators import (
    validate_mandi_arrivals,
    validate_agmarknet_prices,
    validate_procurement,
    validate_national_stocks,
    validate_weather,
    validate_crop_production,
    validate_crop_yield,
    validate_geospatial,
    validate_satellite,
    validate_legacy_audit,
)
from scripts.data_validation.config import (
    WORKSPACE_ROOT,
    PHASE5_DIR,
    PROCESSED_DIR,
    PREVIOUS_AUDIT_DIR,
    CATALOG_CSV,
    CATALOG_JSON,
    QUALITY_REPORT_JSON,
    QUALITY_REPORT_MD,
)


# =====================================================================
# 1. Manifest Cryptographic Integrity Tests
# =====================================================================

def test_starter_manifest_all_49_files_match_sha256_and_size():
    """All 49 files from starter source drop must match their manifest SHA-256 and size."""
    res = verify_starter_drop_manifest()
    assert res["status"] == "PASSED", f"Starter drop manifest mismatches: {res['mismatches']}"
    assert res["total_files"] == 49
    assert res["passed"] == 49
    assert res["failed"] == 0
    assert res["missing"] == 0


def test_provenance_manifest_all_44_files_match():
    """All 44 provenance entries must match their registered SHA-256 and bytes."""
    res = verify_provenance_manifest()
    assert res["status"] == "PASSED", f"Provenance manifest mismatches: {res['mismatches']}"
    assert res["total_files"] == 44
    assert res["passed"] == 44
    assert res["failed"] == 0
    assert res["missing"] == 0


# =====================================================================
# 2. Critical Boundary Assertions: Mandi Arrivals Panel
# =====================================================================

def test_arrival_panel_has_zero_wheat_or_paddy_grain_records(arrivals_df):
    """
    NON-NEGOTIABLE GUARDRAIL: The 3,892-row arrival panel has ZERO wheat/paddy grain records.
    Anomaly models MUST NOT be trained on this panel for grain hoarding detection.
    """
    assert len(arrivals_df) == 3892
    commodities_lower = arrivals_df["commodity_name"].dropna().astype(str).str.lower()

    grain_keywords = ["wheat", "gehun", "kanak", "paddy", "chawal", "rice"]
    for kw in grain_keywords:
        matching = arrivals_df[commodities_lower.str.contains(kw, na=False)]
        assert len(matching) == 0, f"Unexpected grain records found for keyword '{kw}': {len(matching)} rows"


def test_arrival_panel_dhan_substring_matches_are_coriander_green(arrivals_df):
    """
    DISAMBIGUATION ASSERTION: Exactly 71 rows in the arrival panel match the substring 'dhan'.
    All 71 rows are Coriander Green (Hara Dhaniya / ਹਰਾ ਧਨਿਆ), NOT grain paddy.
    """
    commodities_lower = arrivals_df["commodity_name"].dropna().astype(str).str.lower()
    dhan_rows = arrivals_df[commodities_lower.str.contains("dhan", na=False)]
    assert len(dhan_rows) == 71, f"Expected exactly 71 dhan matches, got {len(dhan_rows)}"

    unique_dhan = dhan_rows["commodity_name"].unique().tolist()
    assert len(unique_dhan) == 1
    commodity_str = unique_dhan[0].lower()
    assert "coriander green" in commodity_str
    assert "hara dhaniya" in commodity_str


def test_arrival_panel_zero_semantics_unreported_modal_price(arrivals_df):
    """
    ZERO SEMANTICS AUDIT: Exactly 3 rows have modal_price=0.0 as an explicit sentinel
    for 'not reported' by mandi clerks. For all positive modal prices, min <= modal <= max.
    """
    zero_modal = arrivals_df[arrivals_df["modal_price"] == 0.0]
    assert len(zero_modal) == 3, f"Expected exactly 3 unreported modal sentinels, got {len(zero_modal)}"

    # Positive prices sanity
    positive_prices = arrivals_df[
        (arrivals_df["modal_price"] > 0) &
        (arrivals_df["min_price"] > 0) &
        (arrivals_df["max_price"] > 0)
    ]
    invalid_prices = positive_prices[
        (positive_prices["min_price"] > positive_prices["modal_price"]) |
        (positive_prices["modal_price"] > positive_prices["max_price"])
    ]
    assert len(invalid_prices) == 0, f"Found {len(invalid_prices)} price sanity violations"


def test_arrival_panel_root_duplicate_identity():
    """ARRIVALS_PANEL.csv at acquisition root is an exact byte-for-byte copy of processed arrivals."""
    root_file = PHASE5_DIR / "ARRIVALS_PANEL.csv"
    proc_file = PROCESSED_DIR / "punjab_mandi_arrivals_oct2026.csv"
    assert root_file.exists() and proc_file.exists()
    assert compute_sha256(root_file) == compute_sha256(proc_file)
    assert root_file.stat().st_size == proc_file.stat().st_size


# =====================================================================
# 3. Critical Boundary Assertions: AGMARKNET Paddy Prices
# =====================================================================

def test_paddy_daily_prices_arrival_quantities_are_100pct_null(prices_df):
    """
    CRITICAL GAP: 100% of rows in agmarknet_punjab_daily_prices.csv have null arrival quantities.
    Arrival volume CANNOT be inferred from price observations.
    """
    assert len(prices_df) == 53
    null_arrivals = prices_df["arrival_quantity"].isna().sum()
    assert null_arrivals == 53, f"Expected 53 null arrivals, got {null_arrivals}"


def test_paddy_daily_prices_modal_prices_are_positive(prices_df):
    """Paddy modal prices must be positive and within realistic APMC range."""
    modal_prices = prices_df["modal_price"].dropna()
    assert len(modal_prices) == 53
    assert (modal_prices > 0).all()
    assert modal_prices.min() >= 1500
    assert modal_prices.max() <= 5000


# =====================================================================
# 4. Critical Boundary Assertions: DFPD National Stocks
# =====================================================================

def test_national_stocks_state_is_strictly_null(stocks_df):
    """
    GEOGRAPHIC GRANULARITY GUARDRAIL: Stock observations represent national Central Pool.
    The 'state' column is NaN/null for all 100 rows. No Punjab district breakdown exists.
    """
    assert len(stocks_df) == 100
    assert (stocks_df["geographic_coverage"] == "India Central Pool").all()
    null_states = stocks_df["state"].isna().sum()
    assert null_states == 100, f"Expected 100 null state rows, got {null_states}"


# =====================================================================
# 5. Critical Boundary Assertions: CFPP Procurement Snapshot
# =====================================================================

def test_procurement_snapshot_semantics_cannot_be_summed(procurement_df):
    """
    TEMPORAL BASIS ASSERTION: Exactly 3 rows for a single date (2025-05-15) representing
    3 distinct temporal dimensions. They CANNOT be summed as a time series.
    """
    assert len(procurement_df) == 3
    dates = procurement_df["observation_date"].unique().tolist()
    assert dates == ["2025-05-15"]

    temporal_bases = set(procurement_df["temporal_basis"].tolist())
    expected_bases = {"seasonal_target_estimate", "single_day", "cumulative_season_to_date"}
    assert temporal_bases == expected_bases

    # Summing across measures inappropriately mixes units (LMT + MT) and temporal bases
    naive_sum = procurement_df["measure_value"].sum()
    assert naive_sum > 11_000_000, f"Summing produced {naive_sum}, which is invalid as a time series"


# =====================================================================
# 6. Critical Boundary Assertions: Sentinel-2 Satellite Tile
# =====================================================================

def test_satellite_is_single_scene_window():
    """The satellite raster is a single 512x512 tile window from 2024-10-05, not a time series."""
    sat_dir = PROCESSED_DIR / "satellite"
    files = [p.name for p in sat_dir.iterdir() if p.is_file()]
    assert len(files) == 1
    assert files[0] == "S2B_43REP_20241005_B04_512px_window.tif"
    tif_file = sat_dir / files[0]
    assert tif_file.stat().st_size == 376834


# =====================================================================
# 7. Complete Weather Panel Assertions
# =====================================================================

def test_weather_complete_2_year_panel_zero_nulls(weather_df):
    """Weather panel covers exactly 5 stations, 731 days each (leap year 2024 + 2025), with 0% nulls."""
    assert len(weather_df) == 3655
    stations = weather_df["station_name"].value_counts().to_dict()
    assert len(stations) == 5
    for st, count in stations.items():
        assert count == 731, f"Station {st} has {count} rows, expected 731"

    # 0% nulls across all 12 columns
    for col in weather_df.columns:
        null_count = weather_df[col].isna().sum()
        assert null_count == 0, f"Weather column {col} has {null_count} nulls"


# =====================================================================
# 8. Candidate Key Uniqueness Tests
# =====================================================================

def test_candidate_keys_unique_across_all_datasets(
    arrivals_df,
    prices_df,
    procurement_df,
    stocks_df,
    weather_df,
    production_df,
    yield_df,
    crosswalk_df,
):
    """All core datasets have verified unique candidate keys with 0 duplicates."""
    # 1. Arrivals
    assert arrivals_df.duplicated(subset=["observation_date", "mandi_branch_name", "commodity_name"]).sum() == 0

    # 2. Prices
    assert prices_df.duplicated(subset=["observation_date", "market_id", "commodity_id"]).sum() == 0

    # 3. Procurement
    assert procurement_df.duplicated(subset=["observation_date", "measure_name"]).sum() == 0

    # 4. Stocks
    assert stocks_df.duplicated(subset=["observation_date", "commodity_standard", "measure_name"]).sum() == 0

    # 5. Weather
    assert weather_df.duplicated(subset=["observation_date", "station_name"]).sum() == 0

    # 6. Production
    assert production_df.duplicated(subset=["district_original", "crop_standard", "agricultural_year"]).sum() == 0

    # 7. Yield (with coalesced year key)
    year_coalesced = yield_df["agricultural_year"].combine_first(yield_df["source_year_label"].astype(str))
    yield_keyed = yield_df.assign(year_key=year_coalesced)
    assert yield_keyed.duplicated(subset=["source_id", "district_original", "crop_original", "year_key"]).sum() == 0

    # 8. Geospatial Crosswalk
    assert crosswalk_df.duplicated(subset=["district_source_name_apy"]).sum() == 0


# =====================================================================
# 9. Legacy and Missing Audit Tests
# =====================================================================

def test_historical_codex_audit_folder_is_absent():
    """Historical codex audit folder is physically absent and must not be synthesized."""
    codex_dir = WORKSPACE_ROOT / "data" / "inbox" / "historical_codex_audit"
    assert not codex_dir.exists(), "Unexpected directory found: historical_codex_audit"


def test_legacy_audit_csv_syntax_errors():
    """Previous audit CSV files contain unquoted commas on lines 10/11 violating RFC 4180."""
    legacy_res = validate_legacy_audit(PREVIOUS_AUDIT_DIR)
    assert legacy_res["status"] == "QUARANTINED_WITH_SYNTAX_ERRORS"
    assert len(legacy_res["syntax_errors"]) == 2
    err_files = [e["file"] for e in legacy_res["syntax_errors"]]
    assert "DATA_COVERAGE_MATRIX.csv" in err_files
    assert "DATA_SOURCE_REGISTER.csv" in err_files


# =====================================================================
# 10. Pipeline Outputs and Idempotency Tests
# =====================================================================

def test_dataset_catalog_reproducible_and_valid():
    """The generated dataset catalog exists, has all required fields, and is non-empty."""
    assert CATALOG_CSV.exists()
    assert CATALOG_JSON.exists()
    assert QUALITY_REPORT_JSON.exists()
    assert QUALITY_REPORT_MD.exists()

    df_cat = pd.read_csv(CATALOG_CSV)
    assert len(df_cat) == 20
    required_cols = [
        "dataset_id", "file_path", "format", "source_name", "source_url",
        "sha256", "size_bytes", "row_count", "schema_columns", "date_range",
        "geography_level", "geographic_coverage", "commodity_coverage", "units",
        "retrieval_timestamp_utc", "evidence_status", "licensing_access_notes",
        "caveats", "last_validation_result"
    ]
    for col in required_cols:
        assert col in df_cat.columns, f"Missing required catalog column: {col}"
