#!/usr/bin/env python3
"""Acquire multi-zone historical daily weather observations for Punjab from NASA POWER.

Expands beyond the initial single-point Ludhiana coverage to cover 5 representative
Punjab agro-climatic stations:
1. Ludhiana (Central Plain Zone, lat 30.90, lon 75.85)
2. Bathinda (South-Western Semi-Arid Zone, lat 30.21, lon 74.95)
3. Amritsar (Northern Plain / Border Zone, lat 31.63, lon 74.87)
4. Patiala (Eastern Plain Zone, lat 30.34, lon 76.38)
5. Hoshiarpur (Sub-Mountain Kandi Zone, lat 31.53, lon 75.91)

Acquires daily:
- T2M (Temperature at 2 Meters, °C)
- PRECTOTCORR (Precipitation Corrected, mm/day)
- RH2M (Relative Humidity at 2 Meters, %)

Saves raw JSON payloads and normalized weather panel CSV.
"""
import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "raw" / "weather"
PROC_DIR = ROOT / "processed"
LOG_DIR = ROOT / "logs"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
HEADERS = {"User-Agent": "PunjabGrainAcquisition/2.0 (NASA POWER multi-zone audit)"}

STATIONS = [
    {"station_name": "Ludhiana", "zone": "Central Plain Zone", "latitude": 30.90, "longitude": 75.85},
    {"station_name": "Bathinda", "zone": "South-Western Semi-Arid Zone", "latitude": 30.21, "longitude": 74.95},
    {"station_name": "Amritsar", "zone": "Northern Plain Border Zone", "latitude": 31.63, "longitude": 74.87},
    {"station_name": "Patiala", "zone": "Eastern Plain Zone", "latitude": 30.34, "longitude": 76.38},
    {"station_name": "Hoshiarpur", "zone": "Sub-Mountain Kandi Zone", "latitude": 31.53, "longitude": 75.91},
]

START_DATE = "20240101"
END_DATE = "20251231"


def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    all_observations = []
    station_logs = []
    
    print(f"Beginning multi-zone NASA POWER acquisition for {len(STATIONS)} stations ({START_DATE} to {END_DATE})...")
    
    for st in STATIONS:
        s_name = st["station_name"]
        lat = st["latitude"]
        lon = st["longitude"]
        zone = st["zone"]
        
        params = "T2M,PRECTOTCORR,RH2M"
        url = f"{BASE_URL}?parameters={params}&community=AG&longitude={lon}&latitude={lat}&start={START_DATE}&end={END_DATE}&format=JSON"
        
        print(f"Querying station: {s_name} ({lat}°N, {lon}°E)...")
        try:
            r = requests.get(url, headers=HEADERS, timeout=30, verify=True)
            r.raise_for_status()
            raw_bytes = r.content
            sha256 = hashlib.sha256(raw_bytes).hexdigest()
            
            raw_file = RAW_DIR / f"nasa_power_{s_name.lower()}_{START_DATE}_{END_DATE}_{timestamp}.json"
            raw_file.write_bytes(raw_bytes)
            
            data = r.json()
            param_data = data.get("properties", {}).get("parameter", {})
            t2m_dict = param_data.get("T2M", {})
            prec_dict = param_data.get("PRECTOTCORR", {})
            rh_dict = param_data.get("RH2M", {})
            
            all_dates = sorted(set(t2m_dict.keys()) | set(prec_dict.keys()) | set(rh_dict.keys()))
            
            for d_str in all_dates:
                # convert YYYYMMDD to YYYY-MM-DD
                obs_date = f"{d_str[:4]}-{d_str[4:6]}-{d_str[6:]}"
                t2m_val = t2m_dict.get(d_str)
                prec_val = prec_dict.get(d_str)
                rh_val = rh_dict.get(d_str)
                
                # Check for fill values (-999.0 in NASA POWER)
                t2m = float(t2m_val) if t2m_val not in (None, -999.0) else None
                prec = float(prec_val) if prec_val not in (None, -999.0) else None
                rh = float(rh_val) if rh_val not in (None, -999.0) else None
                
                all_observations.append({
                    "observation_date": obs_date,
                    "state": "Punjab",
                    "station_name": s_name,
                    "agro_climatic_zone": zone,
                    "latitude": lat,
                    "longitude": lon,
                    "temperature_mean_c": t2m,
                    "precipitation_mm_day": prec,
                    "relative_humidity_pct": rh,
                    "source_dataset": "NASA POWER MERRA-2 (temporal/daily/point)",
                    "source_url": url,
                    "retrieval_date_utc": timestamp
                })
                
            print(f"  Received {len(all_dates)} days for {s_name} (SHA-256: {sha256[:12]}...)")
            station_logs.append({
                "station_name": s_name,
                "latitude": lat,
                "longitude": lon,
                "status": "SUCCESS",
                "days_count": len(all_dates),
                "raw_file": str(raw_file.relative_to(ROOT)),
                "sha256": sha256
            })
            
        except Exception as exc:
            print(f"  Error acquiring {s_name}: {exc}")
            station_logs.append({
                "station_name": s_name,
                "latitude": lat,
                "longitude": lon,
                "status": "FAILURE",
                "error": str(exc)
            })
            
        time.sleep(1)  # respectful delay between API calls

    # Write normalized CSV
    out_csv = PROC_DIR / "punjab_multi_zone_daily_weather_2024_2025.csv"
    fields = [
        "observation_date", "state", "station_name", "agro_climatic_zone",
        "latitude", "longitude", "temperature_mean_c", "precipitation_mm_day",
        "relative_humidity_pct", "source_dataset", "source_url", "retrieval_date_utc"
    ]
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_observations)
        
    print(f"Wrote {len(all_observations):,} multi-zone weather observations to {out_csv}")
    
    # Save log
    log_summary = {
        "source": "NASA POWER API Temporal Daily Point",
        "timestamp_utc": timestamp,
        "date_range": [f"{START_DATE[:4]}-{START_DATE[4:6]}-{START_DATE[6:]}", f"{END_DATE[:4]}-{END_DATE[4:6]}-{END_DATE[6:]}"],
        "stations_count": len(STATIONS),
        "total_observations": len(all_observations),
        "processed_file": str(out_csv.relative_to(ROOT)),
        "stations": station_logs
    }
    log_path = LOG_DIR / "nasa_power_multi_zone_acquisition.json"
    log_path.write_text(json.dumps(log_summary, indent=2), encoding="utf-8")
    print(f"Saved run summary to {log_path}")


if __name__ == "__main__":
    main()
