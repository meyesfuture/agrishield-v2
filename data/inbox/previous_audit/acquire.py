#!/usr/bin/env python3
"""Small, dependency-free source access and response validation audit."""
from __future__ import annotations
import csv, hashlib, json, os, re, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
LOGS = ROOT / "logs"
RAW.mkdir(parents=True, exist_ok=True); LOGS.mkdir(parents=True, exist_ok=True)

# Public, bounded probes. Dynamic pages are endpoint checks, not harvested datasets.
SOURCES = [
 {"id":"crop_production_catalog","url":"https://punjab.data.gov.in/catalog/district-wise-season-wise-crop-production-statistics-0","kind":"catalog_page","topic":"District-season-year crop area and production; wheat and paddy candidate"},
 {"id":"agmarknet_dashboard","url":"https://www.enam.gov.in/web/dashboard/agmarknet","kind":"dashboard_page","topic":"Daily mandi arrivals and min/modal/max prices; Punjab wheat/paddy"},
 {"id":"punjab_mandi_board","url":"https://emandikaran-pb.in/","kind":"portal_page","topic":"Punjab market portal and trade/arrival reports"},
 {"id":"cfpp_procurement","url":"https://cfpp.nic.in/cfppui/reports/wpms_days_reports.html","kind":"dashboard_page","topic":"Daily/weekly procurement reporting and state procurement links"},
 {"id":"fci_annual_report","url":"https://fci.gov.in/fci-storage/storage/app/uploads/693a5c5db48ed1765432413.pdf","kind":"pdf","topic":"FCI annual procurement/sale and stock context"},
 {"id":"dfpd_stock_position","url":"https://dfpd.gov.in/WriteReadData/Other/e267d8dc-f22c-49d5-bf6e-e58497921b06.pdf","kind":"pdf","topic":"State-wise central pool stocks; rice and wheat"},
 {"id":"fci_iisfm_dashboard","url":"https://iisfm.nic.in/fcidashboard/FCIRegionDashboard.aspx?code=NF","kind":"dashboard_page","topic":"FCI allocation/offtake, procurement, storage, movement"},
 {"id":"imd_api_reference","url":"https://api.imd.gov.in/public/api_reference.html","kind":"documentation_page","topic":"Weather API coverage, field definitions, authentication/access"},
 {"id":"imd_state_rainfall","url":"https://api.imd.gov.in/api/v1/staterainfall","kind":"api_json","topic":"State rainfall API; current/historical coverage to validate"},
 {"id":"nasa_power_ludhiana_week","url":"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M%2CPRECTOTCORR&community=AG&longitude=75.8573&latitude=30.9000&start=20250101&end=20250107&format=JSON&time-standard=UTC","kind":"api_json","topic":"Documented NASA POWER point weather request; 7 days at approximate Ludhiana coordinates; T2M and PRECTOTCORR"},
 {"id":"ceda_agmarknet_docs","url":"https://api.ceda.ashoka.edu.in/documentation/","kind":"documentation_page","topic":"Official CEDA Agmarknet API documentation; route and schema verification only"},
 {"id":"sentinel_copernicus_catalog","url":"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$top=1","kind":"api_json","topic":"Sentinel-2 archive discovery/API; often requires account/token for data download"},
 {"id":"punjab_gis","url":"https://www.stategisportal.nic.in/stategisportal/Home/Map/3","kind":"gis_portal","topic":"Punjab administrative boundaries and reference layers"},
 {"id":"survey_of_india_map","url":"https://surveyofindia.gov.in/UserFiles/files/PUNJAB_STATE_MAP_ENGLISH_2025.pdf","kind":"pdf","topic":"Official Punjab district boundary reference map"},
 {"id":"punjab_india_stock_case","url":"https://tarntaran.nic.in/vb-arrests-pungrain-inspector-for-causing-losses-of-over-rs-1-24-crore/","kind":"district_press_release","topic":"Officially reported Punjab India stock discrepancy/FIR; related validation lead, not private hoarding label"},
]

def classify(body: bytes, content_type: str, kind: str):
    head = body[:4096].lstrip()
    note = ""
    if not body: return "empty", "empty response body"
    if "json" in content_type.lower() or head[:1] in (b"{", b"["):
        try:
            obj=json.loads(body.decode("utf-8-sig"))
            if isinstance(obj,list): return "json_array", f"valid JSON array; rows={len(obj)}"
            if isinstance(obj,dict): return "json_object", "valid JSON object; keys="+",".join(list(obj)[:30])
        except Exception as e: return "invalid_json", f"JSON parse failed: {type(e).__name__}"
    if "pdf" in content_type.lower() or body.startswith(b"%PDF-"):
        if b"%%EOF" in body[-4096:]: return "pdf", "PDF signature and EOF marker present; content not extracted"
        return "pdf_partial", "PDF signature present but EOF marker missing; likely truncated; not a valid acquired file"
    if "text/csv" in content_type.lower():
        return "csv_candidate", "CSV content type; schema/date/unit coverage needs parsing"
    if "html" in content_type.lower() or re.search(br"<html|<!doctype",head,re.I):
        return "html", "HTML page/dashboard; not treated as a data download"
    return "binary_or_text", "unclassified response; inspect manually"

def validate_nasa_daily(body: bytes, url: str) -> str:
    """Check a small POWER daily response against its requested date and parameter contract."""
    obj=json.loads(body.decode("utf-8-sig"))
    q=parse_qs(urlparse(url).query)
    start=datetime.strptime(q["start"][0],"%Y%m%d").date()
    end=datetime.strptime(q["end"][0],"%Y%m%d").date()
    expected={(start.fromordinal(n)).strftime("%Y%m%d") for n in range(start.toordinal(),end.toordinal()+1)}
    params=obj["properties"]["parameter"]
    metadata=obj["parameters"]
    req=set(q["parameters"][0].split(","))
    details=[]
    for name in sorted(req):
        vals=params[name]
        dates=set(vals)
        nonnull=sum(v is not None and v not in (-999,-999.0,"-999","") for v in vals.values())
        unit=metadata[name]["units"]
        details.append(f"{name}: {len(dates)} dates ({min(dates)}..{max(dates)}), non-null={nonnull}, unit={unit}")
        if dates != expected: raise ValueError(f"{name} dates do not match requested coverage")
    if req != set(params): raise ValueError("Returned parameter set does not match request")
    if obj["header"].get("time_standard") != "UTC": raise ValueError("Time standard does not match request")
    return f"Schema valid; requested/returned parameters={','.join(sorted(req))}; expected dates={len(expected)}; " + "; ".join(details) + "; time_standard=UTC"

def main():
    rows=[]; stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for src in SOURCES:
        start=time.time(); retrieved=datetime.now(timezone.utc).isoformat(timespec="seconds")
        row={**src,"retrieved_utc":retrieved,"http_status":"","content_type":"","bytes":"","sha256":"","saved_path":"","response_class":"","validation":"","error":""}
        try:
            req=Request(src["url"],headers={"User-Agent":"Punjab-Grain-Audit/1.0 (reproducible public-source feasibility check)","Accept":"application/json,text/csv,application/pdf,text/html,*/*"})
            with urlopen(req,timeout=15) as resp:
                body=resp.read(100_000_001); row["http_status"]=resp.status
                row["content_type"]=resp.headers.get("Content-Type",""); row["bytes"]=len(body)
                row["response_class"],row["validation"]=classify(body,row["content_type"],src["kind"])
                if src["id"]=="nasa_power_ludhiana_week" and row["response_class"]=="json_object":
                    try: row["validation"]=validate_nasa_daily(body,src["url"])
                    except Exception as e: row["response_class"]="invalid_dataset"; row["validation"]=f"NASA POWER schema/coverage validation failed: {type(e).__name__}: {e}"
                row["sha256"]=hashlib.sha256(body).hexdigest()
                if len(body)>100_000_000:
                    row["response_class"]="oversize_response"; row["validation"]="Response exceeded 100 MB safety cap; payload not saved"
                if row["response_class"] in ("pdf","json_array","json_object","csv_candidate"):
                    ext={"pdf":"pdf","json_array":"json","json_object":"json","csv_candidate":"csv"}[row["response_class"]]
                    path=RAW/f"{src['id']}__{stamp}.{ext}"; path.write_bytes(body); row["saved_path"]=path.relative_to(ROOT).as_posix()
        except HTTPError as e:
            row["http_status"]=e.code; row["error"]=f"HTTPError: {e.reason}"
        except URLError as e: row["error"]=f"URLError: {e.reason}"
        except Exception as e: row["error"]=f"{type(e).__name__}: {e}"
        row["elapsed_seconds"]=round(time.time()-start,2); rows.append(row)
        print(f"{src['id']}: HTTP {row['http_status'] or 'n/a'} | {row['response_class'] or 'unavailable'} | {row['error']}")
    out=LOGS/f"acquisition_log__{stamp}.csv"
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (LOGS/f"run_summary__{stamp}.json").write_text(json.dumps({"run_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"python":os.sys.version,"source_count":len(rows),"successful_http":sum(bool(r['http_status']) and str(r['http_status']).startswith('2') for r in rows),"saved_payloads":sum(bool(r['saved_path']) for r in rows),"log":out.relative_to(ROOT).as_posix(),"rows":rows},indent=2),encoding="utf-8")
    print(f"Log: {out.relative_to(ROOT)}")
if __name__=="__main__": main()
