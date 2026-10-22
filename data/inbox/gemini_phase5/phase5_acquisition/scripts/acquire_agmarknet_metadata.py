#!/usr/bin/env python3
"""Acquire and parse official AGMARKNET 2.0 metadata filters.

Retrieves states, districts, markets, commodities, varieties, and grades.
Saves raw JSON to raw/agmarknet/ and normalized CSVs to processed/.
"""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "raw" / "agmarknet"
PROC_DIR = ROOT / "processed"
LOG_DIR = ROOT / "logs"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://api.agmarknet.gov.in/v1/daily-price-arrival/filters"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PunjabGrainAudit/2.0",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://agmarknet.gov.in",
    "Referer": "https://agmarknet.gov.in/"
}


def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_entry = {
        "source": "AGMARKNET 2.0 Filters API",
        "url": URL,
        "method": "GET",
        "retrieved_utc": timestamp,
        "tls_verification": "enabled",
    }
    
    print(f"Connecting to {URL}...")
    try:
        r = requests.get(URL, headers=HEADERS, timeout=30, verify=True)
        r.raise_for_status()
        raw_bytes = r.content
        sha256 = hashlib.sha256(raw_bytes).hexdigest()
        
        raw_path = RAW_DIR / f"agmarknet_filters_{timestamp}.json"
        raw_path.write_bytes(raw_bytes)
        print(f"Saved raw response: {raw_path} ({len(raw_bytes):,} bytes, SHA-256: {sha256})")
        
        data = r.json().get("data", {})
        
        # 1. Filter Punjab Markets
        markets = data.get("market_data", [])
        punjab_markets = [m for m in markets if m.get("state_id") == 28]
        
        # 2. Filter Punjab Districts
        districts = data.get("district_data", [])
        punjab_districts = [d for d in districts if d.get("state_id") == 28]
        
        # 3. Filter Target Commodities
        commodities = data.get("cmdt_data", [])
        target_commodities = [
            c for c in commodities
            if any(w in str(c.get("cmdt_name", "")).lower() for w in ["wheat", "paddy", "rice"])
        ]
        
        # Save Normalized Punjab Markets CSV
        mkt_path = PROC_DIR / "agmarknet_punjab_markets.csv"
        with mkt_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["market_id", "market_name", "state_id", "district_id"])
            writer.writeheader()
            for m in punjab_markets:
                writer.writerow({
                    "market_id": m.get("id"),
                    "market_name": m.get("mkt_name"),
                    "state_id": m.get("state_id"),
                    "district_id": m.get("district_id")
                })
        print(f"Wrote {len(punjab_markets)} Punjab markets to {mkt_path}")
        
        # Save Normalized Punjab Districts CSV
        dist_path = PROC_DIR / "agmarknet_punjab_districts.csv"
        with dist_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["district_id", "district_name", "state_id"])
            writer.writeheader()
            for d in punjab_districts:
                writer.writerow({
                    "district_id": d.get("id"),
                    "district_name": d.get("district_name"),
                    "state_id": d.get("state_id")
                })
        print(f"Wrote {len(punjab_districts)} Punjab districts to {dist_path}")

        # Save Normalized Target Commodities CSV
        cmdt_path = PROC_DIR / "agmarknet_target_commodities.csv"
        with cmdt_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["cmdt_id", "cmdt_name", "cmdt_group_id"])
            writer.writeheader()
            for c in target_commodities:
                writer.writerow({
                    "cmdt_id": c.get("cmdt_id"),
                    "cmdt_name": c.get("cmdt_name"),
                    "cmdt_group_id": c.get("cmdt_group_id")
                })
        print(f"Wrote {len(target_commodities)} target commodities to {cmdt_path}")
        
        log_entry.update({
            "status": "SUCCESS",
            "http_status": r.status_code,
            "raw_file": str(raw_path.relative_to(ROOT)),
            "sha256": sha256,
            "total_markets_india": len(markets),
            "punjab_markets_count": len(punjab_markets),
            "punjab_districts_count": len(punjab_districts),
            "target_commodities_count": len(target_commodities),
        })
        
    except Exception as exc:
        print(f"Error during acquisition: {exc}")
        log_entry.update({
            "status": "FAILURE",
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        })
        
    log_path = LOG_DIR / "agmarknet_metadata_acquisition.json"
    log_path.write_text(json.dumps(log_entry, indent=2), encoding="utf-8")
    print(f"Logged run summary to {log_path}")


if __name__ == "__main__":
    main()
