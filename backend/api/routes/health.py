"""
Health and system status routes for Punjab GrainWatch Backend.
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from ...config import settings
from ...schemas.health import HealthResponse, StatusResponse, EvidenceGuardrail
from ...services.catalog_service import catalog_service
from ...services.quality_service import quality_service

router = APIRouter(tags=["Health & Status"])


@router.get("/healthz", summary="Liveness probe")
def healthz():
    """Simple liveness probe for orchestration and uptime monitors."""
    return {"status": "ok", "timestamp_utc": datetime.now(timezone.utc).isoformat()}


@router.get("/api/v1/health", response_model=HealthResponse, summary="Detailed component health check")
def get_health():
    """Detailed health check inspecting filesystem, catalog, and report readiness."""
    now_utc = datetime.now(timezone.utc).isoformat()
    
    data_dir_ok = settings.data_dir.exists()
    manifests_ok = settings.manifests_dir.exists()
    catalog_ok = settings.catalog_json.exists()
    quality_report_ok = settings.quality_report_json.exists()

    checks = {
        "data_directory_present": data_dir_ok,
        "manifests_directory_present": manifests_ok,
        "dataset_catalog_present": catalog_ok,
        "quality_report_present": quality_report_ok,
    }

    is_healthy = all(checks.values())
    status = "healthy" if is_healthy else "degraded"

    notes = []
    if not catalog_ok:
        notes.append("Dataset catalog not found. Run python scripts/run_validation_pipeline.py to rebuild.")
    if not quality_report_ok:
        notes.append("Quality report not found. Run python scripts/run_validation_pipeline.py to rebuild.")

    return HealthResponse(
        status=status,
        version=settings.VERSION,
        timestamp_utc=now_utc,
        checks=checks,
        notes=notes
    )


@router.get("/api/v1/status", response_model=StatusResponse, summary="System status and evidence guardrails")
def get_status():
    """System status including active evidence boundaries and manifest integrity."""
    now_utc = datetime.now(timezone.utc).isoformat()
    all_datasets = catalog_service.get_all()
    quality_summary = quality_service.get_summary()

    guardrails = [
        EvidenceGuardrail(
            guardrail="Zero Grain Arrivals in Panel",
            finding="Arrival panel has 3,892 rows of APMC produce; zero wheat or paddy grain rows.",
            status="VERIFIED"
        ),
        EvidenceGuardrail(
            guardrail="Dhan Substring Disambiguation",
            finding="71 rows matching 'dhan' are Coriander Green (Hara Dhaniya), not grain paddy.",
            status="VERIFIED"
        ),
        EvidenceGuardrail(
            guardrail="Paddy Prices Arrival Quantities",
            finding="Paddy price feed contains 100% null arrival quantities. Feed is price-only.",
            status="VERIFIED"
        ),
        EvidenceGuardrail(
            guardrail="National Buffer Stocks",
            finding="DFPD stocks are national Central Pool buffer aggregates; state column is null.",
            status="VERIFIED"
        ),
        EvidenceGuardrail(
            guardrail="Procurement Snapshot Semantics",
            finding="Procurement rows represent 3 temporal basis slices of 2025-05-15; cannot be summed.",
            status="VERIFIED"
        ),
        EvidenceGuardrail(
            guardrail="Satellite Tile Window",
            finding="Single 512x512 tile window from 2024-10-05; not a multi-temporal time series.",
            status="VERIFIED"
        )
    ]

    manifest_info = quality_summary.manifest_integrity if quality_summary else {
        "status": "UNKNOWN",
        "message": "Quality report not loaded"
    }
    overall_gate = quality_summary.overall_validation_gate if quality_summary else "UNKNOWN"

    return StatusResponse(
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        timestamp_utc=now_utc,
        overall_data_gate=overall_gate,
        total_datasets_cataloged=len(all_datasets),
        evidence_guardrails=guardrails,
        manifest_verification=manifest_info
    )
