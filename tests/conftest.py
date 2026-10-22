"""
Pytest configuration and shared local fixtures for Punjab GrainWatch test suite.
All tests use local files and synthetic local fixtures only; zero internet dependencies.
"""

import sys
import json
from pathlib import Path

# Add project root to sys.path for test execution
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import pytest

from scripts.data_validation.config import (
    WORKSPACE_ROOT,
    PHASE5_DIR,
    PROCESSED_DIR,
    STARTER_DROP_MANIFEST,
    PROVENANCE_MANIFEST,
    CATALOG_CSV,
    CATALOG_JSON,
    QUALITY_REPORT_JSON,
    QUALITY_REPORT_MD,
)


@pytest.fixture(scope="session")
def workspace_root():
    return WORKSPACE_ROOT


@pytest.fixture(scope="session")
def starter_manifest():
    assert STARTER_DROP_MANIFEST.exists(), f"Missing manifest: {STARTER_DROP_MANIFEST}"
    with open(STARTER_DROP_MANIFEST, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def provenance_manifest():
    assert PROVENANCE_MANIFEST.exists(), f"Missing manifest: {PROVENANCE_MANIFEST}"
    with open(PROVENANCE_MANIFEST, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def arrivals_df():
    path = PROCESSED_DIR / "punjab_mandi_arrivals_oct2026.csv"
    assert path.exists(), f"Missing arrivals dataset: {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def prices_df():
    path = PROCESSED_DIR / "agmarknet_punjab_daily_prices.csv"
    assert path.exists(), f"Missing prices dataset: {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def procurement_df():
    path = PROCESSED_DIR / "cfpp_punjab_wheat_procurement_2025_26.csv"
    assert path.exists(), f"Missing procurement dataset: {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def stocks_df():
    path = PROCESSED_DIR / "stocks" / "stock_observations_national_dfpd.csv"
    assert path.exists(), f"Missing stocks dataset: {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def weather_df():
    path = PROCESSED_DIR / "punjab_multi_zone_daily_weather_2024_2025.csv"
    assert path.exists(), f"Missing weather dataset: {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def production_df():
    path = PROCESSED_DIR / "district_crop_production.csv"
    assert path.exists(), f"Missing production dataset: {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def yield_df():
    path = PROCESSED_DIR / "district_crop_yield.csv"
    assert path.exists(), f"Missing yield dataset: {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def boundaries_geojson():
    path = PROCESSED_DIR / "geospatial" / "punjab_district_boundaries.geojson"
    assert path.exists(), f"Missing boundaries geojson: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def crosswalk_df():
    path = PROCESSED_DIR / "geospatial" / "district_crosswalk.csv"
    assert path.exists(), f"Missing crosswalk: {path}"
    return pd.read_csv(path)
