#!/usr/bin/env python3
"""Acquire and parse official CFPP procurement records for Punjab.

Source: Central Food Grains Procurement Portal (CFPP) / WPMS
Endpoint: https://cfpp.nic.in/cfppui/reports/reportsdata.html
TLS verification: Strict enabled.

Extracts state-level wheat procurement estimates, daily procurement,
and progressive procurement to date, along with reporting position dates.
"""
import csv
import hashlib
import json
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "raw" / "procurement"
PROC_DIR = ROOT / "processed"
LOG_DIR = ROOT / "logs"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://cfpp.nic.in/cfppui/reports/reportsdata.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PunjabGrainAudit/2.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}


def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_entry = {
        "source": "Central Food Grains Procurement Portal (CFPP)",
        "url": URL,
        "method": "GET",
        "retrieved_utc": timestamp,
        "tls_verification": "enabled",
    }
    
    print(f"Connecting to CFPP at {URL}...")
    try:
        r = requests.get(URL, headers=HEADERS, timeout=20, verify=True)
        r.raise_for_status()
        raw_bytes = r.content
        sha256 = hashlib.sha256(raw_bytes).hexdigest()
        
        raw_path = RAW_DIR / f"cfpp_reportsdata_{timestamp}.html"
        raw_path.write_bytes(raw_bytes)
        print(f"Saved raw HTML: {raw_path} ({len(raw_bytes):,} bytes, SHA-256: {sha256})")
        
        tables = pd.read_html(StringIO(r.text), flavor="lxml")
        if not tables:
            raise RuntimeError("No tables found in CFPP response")
            
        df = tables[0]
        # Locate Punjab row
        punjab_rows = df[df.iloc[:, 1].astype(str).str.contains("Punjab", case=False, na=False)]
        if punjab_rows.empty:
            raise RuntimeError("Punjab row not found in CFPP table")
            
        row = punjab_rows.iloc[0]
        raw_pos_date = str(row.iloc[5]).strip()
        try:
            pos_date = datetime.strptime(raw_pos_date, "%d/%m/%Y").date().isoformat()
        except ValueError:
            pos_date = raw_pos_date
            
        season_estimate_lmt = float(str(row.iloc[2]).replace(",", ""))
        daily_procurement_mt = float(str(row.iloc[3]).replace(",", ""))
        progressive_procurement_mt = float(str(row.iloc[4]).replace(",", ""))
        
        observations = [
            {
                "observation_date": pos_date,
                "state": "Punjab",
                "commodity": "Wheat",
                "season": "RMS 2025-26",
                "measure_name": "season_estimate",
                "measure_value": season_estimate_lmt,
                "measure_unit": "Lakh Metric Tonnes (LMT)",
                "temporal_basis": "seasonal_target_estimate",
                "reporting_agency": "Central Food Grains Procurement Portal (CFPP)",
                "source_url": URL,
                "retrieval_date_utc": timestamp,
                "quality_note": "Official state seasonal procurement target estimate."
            },
            {
                "observation_date": pos_date,
                "state": "Punjab",
                "commodity": "Wheat",
                "season": "RMS 2025-26",
                "measure_name": "daily_procurement",
                "measure_value": daily_procurement_mt,
                "measure_unit": "Metric Tonnes (MT)",
                "temporal_basis": "single_day",
                "reporting_agency": "Central Food Grains Procurement Portal (CFPP)",
                "source_url": URL,
                "retrieval_date_utc": timestamp,
                "quality_note": f"Single-day procurement quantity on position date {pos_date}."
            },
            {
                "observation_date": pos_date,
                "state": "Punjab",
                "commodity": "Wheat",
                "season": "RMS 2025-26",
                "measure_name": "progressive_procurement",
                "measure_value": progressive_procurement_mt,
                "measure_unit": "Metric Tonnes (MT)",
                "temporal_basis": "cumulative_season_to_date",
                "reporting_agency": "Central Food Grains Procurement Portal (CFPP)",
                "source_url": URL,
                "retrieval_date_utc": timestamp,
                "quality_note": f"Cumulative season-to-date procurement through {pos_date}."
            }
        ]
        
        out_csv = PROC_DIR / "cfpp_punjab_wheat_procurement_2025_26.csv"
        fields = [
            "observation_date", "state", "commodity", "season", "measure_name",
            "measure_value", "measure_unit", "temporal_basis", "reporting_agency",
            "source_url", "retrieval_date_utc", "quality_note"
        ]
        with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(observations)
            
        print(f"Wrote {len(observations)} normalized procurement records to {out_csv}")
        
        log_entry.update({
            "status": "SUCCESS",
            "http_status": r.status_code,
            "raw_file": str(raw_path.relative_to(ROOT)),
            "processed_file": str(out_csv.relative_to(ROOT)),
            "sha256": sha256,
            "position_date": pos_date,
            "season_estimate_lmt": season_estimate_lmt,
            "progressive_procurement_mt": progressive_procurement_mt
        })
        
    except Exception as exc:
        print(f"Procurement acquisition error: {exc}")
        log_entry.update({
            "status": "FAILURE",
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        })
        
    log_file = LOG_DIR / "cfpp_procurement_acquisition.json"
    log_file.write_text(json.dumps(log_entry, indent=2), encoding="utf-8")
    print(f"Saved run summary to {log_file}")


if __name__ == "__main__":
    main()
