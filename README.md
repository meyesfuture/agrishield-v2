# Punjab GrainWatch

**Purpose:** An honest, reproducible, evidence-based agricultural intelligence platform for monitoring Punjab foodgrain and produce supply chains, market prices, buffer stocks, production, yields, and agroclimatological context.

> **Scope Boundary & Evidence Guardrails:**  
> The current evidence supports a source-separated descriptive dashboard and data-quality/boundary-audit system. It does **not** support claims that private grain hoarding is detected. Under the [`AGENTS.md`](AGENTS.md) protocol, the system strictly forbids computing actor-level hoarding probabilities, ranking named mandis or traders as hoarders, or substituting non-grain APMC produce for staple grain arrivals.

---

## 1. Verified Evidence Invariants (Phase 1 Baseline)

1. **Zero Foodgrain Arrivals in Panel:** The acquired 3,892-row mandi arrival panel from e-Mandikaran covers 62 APMC produce crops (vegetables, fruits, cash crops) and contains **zero wheat or paddy grain records**. The 71 rows matching the substring `dhan` were verified as Coriander Green (*Hara Dhaniya*).
2. **Paddy Prices Lack Arrival Quantities:** AGMARKNET 2.0 daily price quotes (53 rows) have **100% null arrival quantities**. The feed reports modal prices (Rs. 2,320 MSP benchmark) only; volumes cannot be inferred.
3. **National Buffer Stocks:** DFPD stock positions (100 rows, 2020–2026) represent the **India Central Pool** total buffer aggregate (state is null/NaN). Facility-level warehouse stocks are unpublished in open portals.
4. **Procurement Snapshot Semantics:** CFPP wheat procurement (3 rows) represents a **single observation date (`2025-05-15`)** across 3 distinct temporal dimensions (`seasonal_target_estimate`, `single_day`, `cumulative_season_to_date`). These rows cannot be summed as a time series.
5. **Satellite Coverage:** Copernicus Sentinel-2B imagery consists of a **single 512×512 tile window (`2024-10-05`)**, not a temporal monitoring series.

---

## 2. Technology Stack

- **Frontend:** [Astro](https://astro.build/) (v7.4) + [React](https://react.dev/) (v19) + [TypeScript](https://www.typescriptlang.org/) (v5.7) with custom design tokens (`tokens.css`) adhering to Apple typographic restraint and Material clarity.
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (v0.141) + [Uvicorn](https://www.uvicorn.org/) (v0.52) + [Pydantic](https://docs.pydantic.dev/) (v2.11) with typed configuration, safe path containment, and secret-scrubbed logging.
- **Data Engine:** Python standard library + pandas, with deterministic validation scripts and cryptographic SHA-256 manifest verification.
- **Testing:** [pytest](https://docs.pytest.org/) with local session fixtures and zero external network dependencies.

---

## 3. Directory Layout

```text
Punjab_GrainWatch_Project_Starter/
├── backend/                  # FastAPI backend service
│   ├── api/routes/           # Health, status, datasets, quality endpoints
│   ├── schemas/              # Pydantic request/response models
│   ├── services/             # Catalog and quality data services
│   ├── config.py             # Typed settings and safe path containment
│   ├── logger.py             # Structured, secret-scrubbed logging
│   └── main.py               # FastAPI application entry point
├── frontend/                 # Astro + React + TypeScript application
│   ├── src/
│   │   ├── components/       # MetricCard, GuardrailBanner, DatasetExplorer, StatusBadge
│   │   ├── layouts/          # AppShell layout with navigation & accessibility
│   │   ├── pages/            # Overview (/), Datasets (/datasets), Status (/status), Methodology (/methodology)
│   │   └── styles/           # Design system CSS tokens (tokens.css)
│   ├── public/               # Static assets & fallback catalog JSON
│   ├── astro.config.mjs      # Astro configuration with React integration
│   └── package.json          # Frontend dependencies
├── data/
│   ├── inbox/                # Immutable source drops (Gemini Phase 5 acquisition)
│   ├── manifests/            # STARTER_SOURCE_DROP_MANIFEST.json, dataset_catalog.csv, dataset_catalog.json
│   └── derived/              # quality_report.json
├── docs/                     # Canonical system documentation and specifications
│   ├── ARCHITECTURE.md       # System architecture and layer contracts
│   ├── DATA_DICTIONARY.md    # Canonical data dictionary (v1.1.0 with DECISION-20261022-01)
│   ├── PROJECT_STATE.md      # Handoff state and session persistence
│   └── research/             # PHASE0_RECONNAISSANCE.md, DATA_QUALITY_REPORT.md
├── scripts/
│   ├── data_validation/      # Modular integrity and validation engine
│   ├── run_validation_pipeline.py # Master pipeline execution script
│   └── run_dev.ps1           # Windows PowerShell development orchestrator
└── tests/
    ├── conftest.py           # Pytest shared local fixtures
    ├── test_data_integrity.py# 16 unit tests for evidence boundaries & manifests
    └── test_backend_api.py   # 9 unit tests for FastAPI health, config & catalog
```

---

## 4. Quick Start & Local Development

### Prerequisites
- Python 3.13+
- Node.js v20+ and npm

### Step 1: Rebuild Data Catalog & Quality Report
Run the Phase 1 repeatable validation pipeline:
```powershell
python scripts/run_validation_pipeline.py
```
*Verifies 49/49 manifest checksums, enforces critical domain assertions, and outputs `dataset_catalog.csv` and `quality_report.json`.*

### Step 2: Run Automated Tests
Execute the comprehensive test suite (25 tests):
```powershell
pytest -v
```

### Step 3: Start Development Servers

#### Option A: One-Command PowerShell Runner
```powershell
.\scripts\run_dev.ps1 -Mode all
```

#### Option B: Separate Terminals

**Terminal 1 — FastAPI Backend:**
```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Astro Frontend:**
```powershell
npm run dev --prefix frontend
```

---

## 5. Endpoints & Access URLs

| Interface | URL | Description |
| :--- | :--- | :--- |
| **Frontend Overview** | `http://localhost:4321/` | Executive landing page with KPI cards and guardrails |
| **Dataset Explorer** | `http://localhost:4321/datasets` | Interactive catalog with search, status filters & inspector |
| **Audit & Status** | `http://localhost:4321/status` | Real-time backend telemetry, latency & assertions checklist |
| **Methodology** | `http://localhost:4321/methodology` | Evidentiary governance rules and data invariants |
| **FastAPI Swagger Docs**| `http://127.0.0.1:8000/docs` | Interactive OpenAPI documentation |
| **Backend Health** | `http://127.0.0.1:8000/api/v1/health` | Component health check (catalog, report, data dirs) |
| **Backend Status** | `http://127.0.0.1:8000/api/v1/status` | System status and active evidence guardrails |
| **Datasets API** | `http://127.0.0.1:8000/api/v1/datasets` | Catalog listing with `?status=`, `?commodity=`, `?search=` |
| **Quality API** | `http://127.0.0.1:8000/api/v1/quality/summary` | Full audit report summary and manifest integrity |
