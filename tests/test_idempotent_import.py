"""
Tests for idempotent data import and provenance verification.
Ensures that running the import audit multiple times produces identical outcomes,
validates checksums, and does not alter raw source files in data/inbox/.
"""

import json
from pathlib import Path
import pytest

from backend.config import settings
from backend.services.ingestion_service import ingestion_service, compute_sha256


def test_idempotent_import_audit_execution():
    """Import audit must run successfully and report all active datasets as validated."""
    report1 = ingestion_service.run_import_audit()
    assert report1["idempotent"] is True
    assert report1["source_files_preserved"] is True
    assert report1["datasets_verified"] == 6
    assert report1["all_schemas_valid"] is True

    # Rerun to test idempotency
    report2 = ingestion_service.run_import_audit()
    assert report2["datasets_verified"] == 6
    assert report2["all_schemas_valid"] is True

    # Compare checksums between run 1 and run 2
    hashes1 = {o["dataset_id"]: o["sha256_hash"] for o in report1["outcomes"]}
    hashes2 = {o["dataset_id"]: o["sha256_hash"] for o in report2["outcomes"]}
    assert hashes1 == hashes2


def test_source_files_in_inbox_remain_unmodified():
    """Verify that source files under data/inbox/ remain strictly unchanged."""
    active_paths = [
        settings.production_csv,
        settings.yield_csv,
        settings.prices_csv,
        settings.weather_csv,
        settings.procurement_csv,
        settings.stocks_csv,
        settings.boundaries_geojson,
    ]

    hashes_before = {p: compute_sha256(p) for p in active_paths if p.exists()}

    # Trigger import audit
    ingestion_service.run_import_audit()

    hashes_after = {p: compute_sha256(p) for p in active_paths if p.exists()}

    for p in active_paths:
        if p.exists():
            assert hashes_before[p] == hashes_after[p], f"File modified: {p}"


def test_derived_manifest_persisted():
    """The derived import audit manifest must be written to data/derived/."""
    manifest_path = settings.derived_dir / "import_audit_manifest.json"
    assert manifest_path.exists()

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["idempotent"] is True
    assert data["datasets_verified"] == 6
    assert len(data["outcomes"]) == 6
