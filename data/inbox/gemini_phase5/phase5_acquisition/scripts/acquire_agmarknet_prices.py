#!/usr/bin/env python3
"""Acquire real multi-market, multi-date mandi prices from AGMARKNET 2.0.

Queries the official /prices-and-arrivals/market-price/lastweek endpoint
for major Punjab APMCs across Paddy(Common) (ID=2), Paddy(Basmati) (ID=343),
and Wheat (ID=1).

Normalizes observations into long-format records with:
- observation_date
- market_id, market_name
- state_id, state_name
- commodity_id, commodity_name
- variety
- modal_price (with unit Rs./Quintal)
- source URL and provenance
"""
import csv
import hashlib
import json
import time
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

BASE_URL = "https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-price/lastweek"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PunjabGrainAudit/2.0",
    "Content-Type": "application/json",
    "Origin": "https://agmarknet.gov.in",
    "Referer": "https://agmarknet.gov.in/"
}

# Major grain markets in Punjab
TARGET_COMMODITIES = [
    (2, "Paddy(Common)"),
    (343, "Paddy(Basmati)"),
    (1, "Wheat")
]


def main():
    mkt_csv = PROC_DIR / "agmarknet_punjab_markets.csv"
    if not mkt_csv.exists():
        raise RuntimeError("Punjab markets reference CSV missing. Run acquire_agmarknet_metadata.py first.")
        
    markets = []
    with mkt_csv.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            markets.append({"id": int(r["market_id"]), "name": r["market_name"]})

    # Pick top 50 diverse markets across Punjab districts
    selected_markets = markets[:50]
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_responses = []
    observations = []
    
    print(f"Beginning price acquisition across {len(selected_markets)} Punjab markets and {len(TARGET_COMMODITIES)} commodities...")
    
    total_calls = 0
    success_calls = 0
    active_observations = 0
    
    for m in selected_markets:
        m_id = m["id"]
        m_name = m["name"]
        for c_id, c_name in TARGET_COMMODITIES:
            total_calls += 1
            url = f"{BASE_URL}?marketId={m_id}&stateId=28&commodityId={c_id}&includeExcel=false"
            try:
                r = requests.get(url, headers=HEADERS, timeout=15, verify=True)
                if r.status_code == 200:
                    success_calls += 1
                    resp_json = r.json()
                    raw_responses.append({
                        "market_id": m_id,
                        "market_name": m_name,
                        "commodity_id": c_id,
                        "commodity_name": c_name,
                        "response": resp_json
                    })
                    
                    data_rows = resp_json.get("data", [])
                    cols = resp_json.get("columns", [])
                    # Extract date keys from columns (format: YYYY-MM-DD)
                    date_keys = [c["key"] for c in cols if c["key"] not in ("variety", "unitOfPrice")]
                    
                    for row in data_rows:
                        variety = row.get("variety", "Standard")
                        unit = row.get("unitOfPrice", "Rs./Quintal")
                        for dt in date_keys:
                            price_val = row.get(dt)
                            if price_val not in (None, "NR", ""):
                                try:
                                    price_num = float(price_val)
                                    observations.append({
                                        "observation_date": dt,
                                        "state": "Punjab",
                                        "state_id": 28,
                                        "market_id": m_id,
                                        "market_name": m_name,
                                        "commodity_id": c_id,
                                        "commodity_name": c_name,
                                        "variety": variety,
                                        "modal_price": price_num,
                                        "price_unit": unit,
                                        "arrival_quantity": None,
                                        "arrival_unit": None,
                                        "source_endpoint": BASE_URL,
                                        "retrieval_date_utc": timestamp
                                    })
                                    active_observations += 1
                                except ValueError:
                                    pass
            except Exception as e:
                print(f"  Warning: failed {m_name} / {c_name}: {e}")
            time.sleep(0.05)  # respectful delay

    # Save Raw JSON
    raw_path = RAW_DIR / f"agmarknet_market_prices_raw_{timestamp}.json"
    raw_path.write_text(json.dumps(raw_responses, indent=2), encoding="utf-8")
    raw_sha256 = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    print(f"Saved raw responses: {raw_path} ({len(raw_responses)} responses, SHA-256: {raw_sha256})")
    
    # Save Normalized Panel CSV
    out_csv = PROC_DIR / "agmarknet_punjab_daily_prices.csv"
    fields = [
        "observation_date", "state", "state_id", "market_id", "market_name",
        "commodity_id", "commodity_name", "variety", "modal_price", "price_unit",
        "arrival_quantity", "arrival_unit", "source_endpoint", "retrieval_date_utc"
    ]
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(observations)
        
    print(f"Successfully normalized {len(observations)} market-date price observations to {out_csv}")
    
    # Write summary log
    log_summary = {
        "source": "AGMARKNET 2.0 Market Price API",
        "timestamp_utc": timestamp,
        "markets_queried": len(selected_markets),
        "commodities_queried": [c[1] for c in TARGET_COMMODITIES],
        "total_requests": total_calls,
        "successful_requests": success_calls,
        "active_price_observations": len(observations),
        "raw_file": str(raw_path.relative_to(ROOT)),
        "processed_file": str(out_csv.relative_to(ROOT)),
        "sha256": raw_sha256
    }
    log_file = LOG_DIR / "agmarknet_price_acquisition.json"
    log_file.write_text(json.dumps(log_summary, indent=2), encoding="utf-8")
    print(f"Logged summary to {log_file}")


if __name__ == "__main__":
    main()
