#!/usr/bin/env python3
"""Automated acceptance tests for Phase 5 data acquisition deliverables.

Verifies:
1. Presence of all required files.
2. Non-emptiness and valid CSV schemas.
3. Checksum integrity matching PROVENANCE_MANIFEST.json.
4. Correct units and value bounds.
5. Distinction between prices, arrivals, procurement, and weather.
"""
import csv
import hashlib
import json
from pathlib import Path
import pytest
import pandas as pd

ROOT = Path("B:/partial_farm_agychat/phase5_acquisition")


def test_required_top_level_files():
    required = [
        "DATA_INVENTORY.csv",
        "DATA_INVENTORY.json",
        "SOURCE_STATUS.csv",
        "SUPPLY_FLOW_COVERAGE_MATRIX.csv",
        "PROVENANCE_MANIFEST.json",
        "ARRIVALS_PANEL.csv",
    ]
    for fname in required:
        p = ROOT / fname
        assert p.exists(), f"Missing required file: {fname}"
        assert p.stat().st_size > 0, f"File {fname} is empty"


def test_provenance_manifest_integrity():
    manifest_path = ROOT / "PROVENANCE_MANIFEST.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "files" in data
    assert len(data["files"]) > 10
    
    # Verify checksum of DATA_INVENTORY.csv
    inv_entry = next((f for f in data["files"] if f["relative_path"] == "DATA_INVENTORY.csv"), None)
    assert inv_entry is not None
    inv_path = ROOT / "DATA_INVENTORY.csv"
    actual_hash = hashlib.sha256(inv_path.read_bytes()).hexdigest()
    assert inv_entry["sha256"] == actual_hash


def test_mandi_arrivals_panel():
    arrivals_path = ROOT / "ARRIVALS_PANEL.csv"
    df = pd.read_csv(arrivals_path)
    assert len(df) == 3892, f"Expected 3892 records, got {len(df)}"
    
    required_cols = [
        "observation_date", "district_name", "mandi_branch_name",
        "commodity_name", "arrival_quantity", "arrival_unit",
        "min_price", "max_price", "modal_price", "price_unit"
    ]
    for c in required_cols:
        assert c in df.columns, f"Missing column in arrivals panel: {c}"
        
    # Verify quantities are positive numbers
    assert (df["arrival_quantity"] > 0).all()
    # Verify price units
    assert (df["price_unit"] == "Rs./Quintal").all()
    assert (df["arrival_unit"] == "quintals").all()
    # Verify unique districts and dates
    assert df["district_name"].nunique() >= 8
    assert df["observation_date"].nunique() >= 20


def test_agmarknet_prices():
    prices_path = ROOT / "processed" / "agmarknet_punjab_daily_prices.csv"
    df = pd.read_csv(prices_path)
    assert len(df) > 0, "No Agmarknet price rows acquired"
    assert "modal_price" in df.columns
    assert (df["modal_price"] > 0).all()
    assert (df["price_unit"] == "Rs./Quintal").all()


def test_multi_zone_weather():
    weather_path = ROOT / "processed" / "punjab_multi_zone_daily_weather_2024_2025.csv"
    df = pd.read_csv(weather_path)
    assert len(df) == 3655, f"Expected 3655 weather observations, got {len(df)}"
    assert df["station_name"].nunique() == 5
    assert set(df["station_name"].unique()) == {"Ludhiana", "Bathinda", "Amritsar", "Patiala", "Hoshiarpur"}
    # Verify values are in reasonable meteorological ranges for Punjab
    assert df["temperature_mean_c"].min() > -5.0
    assert df["temperature_mean_c"].max() < 55.0
    assert df["precipitation_mm_day"].min() >= 0.0


def test_cfpp_procurement():
    proc_path = ROOT / "processed" / "cfpp_punjab_wheat_procurement_2025_26.csv"
    df = pd.read_csv(proc_path)
    assert len(df) == 3
    measures = df["measure_name"].tolist()
    assert "season_estimate" in measures
    assert "daily_procurement" in measures
    assert "progressive_procurement" in measures


def test_source_status_table():
    status_path = ROOT / "SOURCE_STATUS.csv"
    df = pd.read_csv(status_path)
    assert len(df) >= 8
    assert "operational_blockers" in df.columns
    assert "final_verdict" in df.columns


def test_supply_flow_coverage_matrix():
    cov_path = ROOT / "SUPPLY_FLOW_COVERAGE_MATRIX.csv"
    df = pd.read_csv(cov_path)
    assert len(df) == 8
    assert "reconciliation_readiness" in df.columns
    # Check that at least some elements are NO-GO
    verdicts = df["reconciliation_readiness"].str.upper().tolist()
    assert any("NO-GO" in v for v in verdicts)


if __name__ == "__main__":
    import sys
    pytest.main(["-v", __file__])
