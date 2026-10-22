#!/usr/bin/env python3
"""Acquire and normalize Punjab Mandi Board daily arrival records.

Source: Punjab Mandi Board (PSAMB) e-Mandikaran API
Endpoint: https://api.emandikaran-pb.in/CommonMasterDataAPI/getDailyArrival/{districtid}/{branchid}/{commodityid}/{fromdate}/{todate}

Retrieves daily market arrival records including arrival quantity,
min price, max price, modal price, branch name, district name, and entry date.

Saves raw JSON response and normalized ARRIVALS_PANEL.csv.
"""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "raw" / "emandikaran"
PROC_DIR = ROOT / "processed"
LOG_DIR = ROOT / "logs"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://api.emandikaran-pb.in/CommonMasterDataAPI/getDailyArrival"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PunjabGrainAudit/2.0",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://emandikaran-pb.in",
    "Referer": "https://emandikaran-pb.in/Home/MandiArrival"
}


def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    # Query current month window (01-10-2026 to 21-10-2026) across all districts (0) and all branches (0)
    from_date = "01-10-2026"
    to_date = "21-10-2026"
    url = f"{BASE_URL}/0/0/0/{from_date}/{to_date}"
    
    print(f"Connecting to Punjab Mandi Board API: {url}...")
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, verify=True)
        r.raise_for_status()
        raw_bytes = r.content
        sha256 = hashlib.sha256(raw_bytes).hexdigest()
        
        raw_path = RAW_DIR / f"punjab_mandi_arrivals_{from_date}_to_{to_date}_{timestamp}.json"
        raw_path.write_bytes(raw_bytes)
        print(f"Saved raw response to {raw_path} ({len(raw_bytes):,} bytes, SHA-256: {sha256})")
        
        payload = r.json()
        records = payload.get("responseData", [])
        print(f"Total raw records received: {len(records):,}")
        
        # Normalize into clean tabular records
        normalized_rows = []
        for rec in records:
            # Parse EntryDate: format DD/MM/YYYY
            raw_date = rec.get("EntryDate", "")
            obs_date = ""
            if raw_date:
                try:
                    dt = datetime.strptime(raw_date, "%d/%m/%Y")
                    obs_date = dt.strftime("%Y-%m-%d")
                except ValueError:
                    obs_date = raw_date
                    
            normalized_rows.append({
                "observation_date": obs_date,
                "entry_date_raw": raw_date,
                "state": "Punjab",
                "district_name": rec.get("DistrictName", "").strip(),
                "mandi_branch_name": rec.get("BranchName", "").strip(),
                "commodity_name": rec.get("CommodityName", "").strip(),
                "arrival_quantity": rec.get("Quantity"),
                "arrival_unit": "quintals",  # Official Punjab APMC reporting standard
                "min_price": rec.get("Minprice"),
                "max_price": rec.get("MaxPrice"),
                "modal_price": rec.get("ModalPrice"),
                "price_unit": "Rs./Quintal",
                "source_system": "Punjab Mandi Board (PSAMB) e-Mandikaran",
                "source_endpoint": BASE_URL,
                "retrieval_date_utc": timestamp,
                "scope_note": "State marketing authority daily arrival report; covers regulated APMC arrivals in Punjab."
            })
            
        # Write normalized CSV
        out_csv = PROC_DIR / "punjab_mandi_arrivals_oct2026.csv"
        fields = [
            "observation_date", "entry_date_raw", "state", "district_name",
            "mandi_branch_name", "commodity_name", "arrival_quantity", "arrival_unit",
            "min_price", "max_price", "modal_price", "price_unit",
            "source_system", "source_endpoint", "retrieval_date_utc", "scope_note"
        ]
        with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(normalized_rows)
            
        print(f"Wrote {len(normalized_rows):,} normalized arrival records to {out_csv}")
        
        # Calculate summary statistics
        districts = set(r["district_name"] for r in normalized_rows)
        branches = set(r["mandi_branch_name"] for r in normalized_rows)
        commodities = set(r["commodity_name"] for r in normalized_rows)
        dates = set(r["observation_date"] for r in normalized_rows)
        
        log_entry = {
            "source": "Punjab Mandi Board e-Mandikaran Daily Arrival API",
            "url": url,
            "status": "SUCCESS",
            "timestamp_utc": timestamp,
            "raw_file": str(raw_path.relative_to(ROOT)),
            "processed_file": str(out_csv.relative_to(ROOT)),
            "sha256": sha256,
            "total_records": len(normalized_rows),
            "date_range": [min(dates), max(dates)] if dates else [],
            "unique_dates_count": len(dates),
            "unique_districts_count": len(districts),
            "unique_branches_count": len(branches),
            "unique_commodities_count": len(commodities),
            "districts_list": sorted(list(districts)),
            "commodity_scope": "Agricultural produce traded in Punjab APMC yards (fruits, vegetables, cash crops). Foodgrains (Wheat/Paddy) are routed separately through Anaaj Kharid / central procurement portal."
        }
        
    except Exception as exc:
        print(f"Acquisition error: {exc}")
        log_entry = {
            "source": "Punjab Mandi Board e-Mandikaran Daily Arrival API",
            "url": url,
            "status": "FAILURE",
            "timestamp_utc": timestamp,
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        }
        
    log_file = LOG_DIR / "punjab_mandi_arrivals_acquisition.json"
    log_file.write_text(json.dumps(log_entry, indent=2), encoding="utf-8")
    print(f"Saved run summary to {log_file}")


if __name__ == "__main__":
    main()
