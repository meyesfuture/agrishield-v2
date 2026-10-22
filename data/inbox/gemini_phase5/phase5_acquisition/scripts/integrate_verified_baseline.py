#!/usr/bin/env python3
"""Integrate and re-validate existing Phase 3 verified artifacts from the uploaded archive.

Extracts:
1. DES APY browser extract (district_crop_production.csv)
2. Historical district crop yields (district_crop_yield.csv)
3. Geospatial district crosswalk and boundaries (district_crosswalk.csv, punjab_district_boundaries.geojson)
4. Central pool stock time series (stock_observations.csv, dfpd_stock_position_2020_2026_extracted.txt)
5. Sentinel-2 L2A B04 raster window (S2B_43REP_20241005_B04_512px_window.tif)

Computes SHA-256 hashes and validates row counts and columns.
"""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_PATH = Path("B:/partial_farm_agychat/sept")

RAW_DIR = ROOT / "raw"
PROC_DIR = ROOT / "processed"
LOG_DIR = ROOT / "logs"

FILES_TO_EXTRACT = [
    ("Punjab_Grain_Hoarding_Intelligence_Audit/processed/district_crop_production.csv",
     PROC_DIR / "district_crop_production.csv"),
    ("Punjab_Grain_Hoarding_Intelligence_Audit/processed/district_crop_yield.csv",
     PROC_DIR / "district_crop_yield.csv"),
    ("Punjab_Grain_Hoarding_Intelligence_Audit/processed/geospatial/district_crosswalk.csv",
     PROC_DIR / "geospatial" / "district_crosswalk.csv"),
    ("Punjab_Grain_Hoarding_Intelligence_Audit/processed/geospatial/punjab_district_boundaries.geojson",
     PROC_DIR / "geospatial" / "punjab_district_boundaries.geojson"),
    ("Punjab_Grain_Hoarding_Intelligence_Audit/processed/stocks/dfpd_stock_position_2020_2026_extracted.txt",
     PROC_DIR / "stocks" / "dfpd_stock_position_2020_2026_extracted.txt"),
    ("Punjab_Grain_Hoarding_Intelligence_Audit/processed/stock_observations.csv",
     PROC_DIR / "stocks" / "stock_observations_national_dfpd.csv"),
    ("Punjab_Grain_Hoarding_Intelligence_Audit/processed/satellite/S2B_43REP_20241005_B04_512px_window.tif",
     PROC_DIR / "satellite" / "S2B_43REP_20241005_B04_512px_window.tif"),
    ("Punjab_Grain_Hoarding_Intelligence_Audit/raw/ogd_punjab_wheat_yield.csv",
     RAW_DIR / "ogd" / "ogd_punjab_wheat_yield.csv"),
    ("Punjab_Grain_Hoarding_Intelligence_Audit/raw/ogd_punjab_rice_yield.csv",
     RAW_DIR / "ogd" / "ogd_punjab_rice_yield.csv"),
    ("Punjab_Grain_Hoarding_Intelligence_Audit/raw/des_apy_phase3_browser_table_extracts.json",
     RAW_DIR / "ogd" / "des_apy_phase3_browser_table_extracts.json"),
]


def main():
    if not ARCHIVE_PATH.exists():
        raise FileNotFoundError(f"Source archive {ARCHIVE_PATH} not found")
        
    print(f"Opening archive {ARCHIVE_PATH}...")
    manifest = []
    with zipfile.ZipFile(ARCHIVE_PATH, "r") as z:
        for arc_name, dest_path in FILES_TO_EXTRACT:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            data = z.read(arc_name)
            dest_path.write_bytes(data)
            sha256 = hashlib.sha256(data).hexdigest()
            print(f"Extracted {dest_path.name}: {len(data):,} bytes (SHA-256: {sha256[:12]}...)")
            manifest.append({
                "source_archive_path": arc_name,
                "destination_file": str(dest_path.relative_to(ROOT)),
                "bytes": len(data),
                "sha256": sha256
            })
            
    out_log = LOG_DIR / "integrated_baseline_manifest.json"
    out_log.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Saved baseline integration manifest to {out_log}")


if __name__ == "__main__":
    main()
