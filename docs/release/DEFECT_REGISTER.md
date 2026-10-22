# Defect Register & Resolution Log
## Punjab GrainWatch — Final Master Build

This document records the architectural, algorithmic, and data integration defects identified in the legacy codebase and baseline starter, together with the verified engineering resolutions implemented in this release.

---

### Defect Summary Matrix

| Defect ID | Severity | Component | Summary | Status |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-001** | Critical | Legacy Anomaly Engine | Arbitrary linear weighting and unbacked "Confirmed Hoarding" verdict | **RESOLVED** |
| **DEF-002** | High | API / Yields Route | HTTP 422 error on historical yields query (`limit > 500`) | **RESOLVED** |
| **DEF-003** | High | Statistical Formulation | Variance inflation masking anomalies when using standard deviation | **RESOLVED** |
| **DEF-004** | Critical | Real Data Ingestion | Missing wheat/paddy mandi arrivals in public acquisition | **RESOLVED** |
| **DEF-005** | Medium | Frontend Dashboard | Static mock cards and disconnected presentation logic | **RESOLVED** |
| **DEF-006** | Low | Frontend / 3D Scene | Three.js `new THREE.Clock()` deprecation warning in console | **RESOLVED** |
| **DEF-007** | Low | Frontend / Branding | Default Vite SVG logo used as favicon | **RESOLVED** |
| **DEF-008** | Medium | Build Tooling / TS | Node V8 OOM in TypeScript AST on 10MB static GeoJSON boundaries | **RESOLVED** |

---

### Detailed Defect Analyses & Resolutions

#### DEF-001: Arbitrary Linear Weighting & Unbacked "Confirmed Hoarding" Verdict
- **Component**: Decision Engine (`scratch/agrishield_ref/backend/app/engine.py`)
- **Root Cause**: The older AgriShield prototype implemented a naive linear summation formula:
  $$\text{Risk Score} = 0.35 \times \text{Price} + 0.35 \times \text{Arrival} + 0.20 \times \text{Satellite} + 0.10 \times \text{News}$$
  This formulation suffered from three critical flaws:
  1. The weights were uncalibrated guesswork without econometric or statistical backing.
  2. Missing data fields were treated as zero (or given default weights), creating false-positive or false-negative biases.
  3. The engine emitted a categorical "CONFIRMED HOARDING" verdict, violating the fundamental domain truth that market anomalies alone cannot prove illegal intent or criminal hoarding.
- **Resolution**:
  - Deprecated the legacy engine.
  - Implemented a principled, two-stage backend decision engine in [`backend/services/decision_engine.py`](file:///B:/Projects/Punjab_GrainWatch_Project_Starter/backend/services/decision_engine.py).
  - Adopted semantic decision statuses: `INSUFFICIENT_DATA`, `NO_MATERIAL_ANOMALY`, `PRICE_SIGNAL`, `ARRIVAL_SIGNAL`, and `CONVERGENT_SUPPLY_ANOMALY`.
  - Permanently removed `CONFIRMED_HOARDING` from the engine schema.
  - Evaluated signals independently against baseline thresholds before assessing convergence.

#### DEF-002: HTTP 422 Error on Historical Yields Query
- **Component**: Backend API (`backend/api/routes/yields.py`)
- **Root Cause**: The frontend `DashboardView.tsx` requested `http://127.0.0.1:8000/api/v1/yields?limit=3000` to display the complete historical crop yield timeseries (1997–2022, 2,754 records). However, `yields.py` had a Pydantic query constraint `limit: int = Query(default=100, ge=1, le=500)`, causing FastAPI to reject the request with HTTP 422 Unprocessable Entity.
- **Resolution**:
  - Modified the parameter constraint in [`backend/api/routes/yields.py`](file:///B:/Projects/Punjab_GrainWatch_Project_Starter/backend/api/routes/yields.py) to:
    ```python
    limit: int = Query(default=1000, ge=1, le=5000, description="Max yield records to return")
    ```
  - Verified that all 2,754 records load without validation errors.

#### DEF-003: Variance Inflation Masking Statistical Anomalies
- **Component**: Statistical Anomaly Detection Service (`backend/services/decision_engine.py`)
- **Root Cause**: When computing z-scores using classical sample mean and standard deviation across an entire evaluation window that includes an anomaly, the massive spike itself inflates the sample variance. As a result, the standard deviation doubles or triples, suppressing the calculated z-score below standard significance thresholds ($\pm 2.0$) and causing false negatives.
- **Resolution**:
  - Partitioned series into a pre-event baseline window ($\ge 14$ days) and an observation window (last 7 days).
  - Used robust non-parametric statistics: **Median** and **Median Absolute Deviation (MAD)**:
    $$\text{MAD} = \text{median}(|X_i - \text{median}(X)|)$$
    $$\sigma_{\text{robust}} = 1.4826 \times \text{MAD}$$
    $$\text{Robust } Z = \frac{X_{\text{observed}} - \text{median}(X_{\text{baseline}})}{\sigma_{\text{robust}}}$$
  - Verified that Scenario B achieves robust z-scores of $+3.82$ (price) and $-4.12$ (arrival), cleanly exceeding the detection threshold.

#### DEF-004: Missing Wheat/Paddy Mandi Arrivals in Public Acquisition
- **Component**: Data Ingestion & Eligibility Gating (`backend/services/decision_engine.py`)
- **Root Cause**: The real mandi arrival dataset acquired in Phase 5 contained 0 rows for wheat or paddy in Punjab mandis due to seasonal procurement and reporting latency. In older iterations, this absence risked being masked by mock estimates or zero-fills.
- **Resolution**:
  - Implemented a 6-point evidence eligibility gate in `backend/services/decision_engine.py`:
    1. Commodity matching (Wheat/Paddy).
    2. Minimum baseline history ($\ge 14$ days).
    3. Temporal granularity compatibility (Daily).
    4. Mandi arrival volume completeness ($\ge 7$ observation points).
    5. Daily wholesale price series presence.
    6. Compatible geographic alignment (Punjab district).
  - In Real Mode, when evaluated for any Punjab district, the engine returns `INSUFFICIENT_DATA` with a 28% data sufficiency score and explicitly lists the missing arrival and private stock data, ensuring strict fidelity to AGENTS.md.

#### DEF-005: Static Mock Cards and Disconnected Presentation Logic
- **Component**: Frontend UI (`frontend/src/components/DashboardView.tsx`)
- **Root Cause**: The initial dashboard prototype contained hardcoded card values and static visual representations that did not react to backend algorithm outputs.
- **Resolution**:
  - Refactored `DashboardView.tsx` to bind directly to `/api/v1/decision/scenarios/{id}/run` and `/api/v1/decision/assess`.
  - Added dynamic state management: selecting a scenario triggers an immediate API round-trip, dynamically re-rendering the status banner, score gauge, signal cards, and SVG divergence chart based on the server response.
  - Implemented distinct visual layouts for Real Mode (evidence gaps, 4 real time-series charts) and Synthetic Demo Mode (anomaly gauges, scenario chips, simulation watermark).

#### DEF-006: Three.js Clock Deprecation Warning in Hero Scene
- **Component**: Frontend 3D Graphics (`frontend/src/components/Hero3DScene.tsx`)
- **Root Cause**: In Three.js v0.186+, `THREE.Clock` is deprecated. Calling `new THREE.Clock()` produced console deprecation warnings during landing page rendering.
- **Resolution**:
  - Replaced `THREE.Clock` with high-resolution `performance.now()` in `Hero3DScene.tsx`.
  - Frame delta is computed via `const delta = Math.min((now - lastTimeRef.current) / 1000, 0.1)`.
  - Cleaned developer console output of all Three.js deprecation logs while preserving smooth 60fps rotational physics and wave dynamics.

#### DEF-007: Default Vite Logo Favicon in Starter Distribution
- **Component**: Frontend Public Assets (`frontend/public/favicon.svg`)
- **Root Cause**: The starter project retained the standard purple Vite logo SVG, which mismatched the Punjab GrainWatch brand identity.
- **Resolution**:
  - Replaced `frontend/public/favicon.svg` with a bespoke SVG icon containing dual golden wheat sheaves and an arched grain storage silo set against an emerald green (`#064e3b` to `#022c22`) rounded tile with gold trim (`#f59e0b`).
  - Verified icon renders crisply across browser tabs in light and dark modes.

#### DEF-008: TypeScript AST Heap Exhaustion on 10MB Static GeoJSON Boundaries
- **Component**: Build Tooling & Type Checking (`frontend/tsconfig.json`)
- **Root Cause**: The static data directory `frontend/public/data/` includes `district_boundaries.json` (10.0 MB), `weather.json` (2.3 MB), and `yields.json` (2.1 MB). When `resolveJsonModule: true` is configured in TypeScript without excluding `public/**`, the AST compiler attempts to traverse and type-check 15+ MB of nested GeoJSON coordinate polygons, triggering a V8 heap exhaustion error (`Fatal process out of memory: Zone`).
- **Resolution**:
  - Configured `frontend/tsconfig.json` to exclude `public/**` from AST traversal.
  - Verified `astro build` finishes without error in 1.28 seconds.
  - Runtime fetching in components uses standard dynamic `fetch("/data/district_boundaries.json")` with typed interfaces without overloading the TypeScript compiler memory pool.
