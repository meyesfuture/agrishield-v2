# Punjab GrainWatch Simplification Test & Verification Results

**Execution Date:** 2026-10-22  
**Test Harness:** pytest 9.1.1, Python 3.13.14, Node v20+, Astro 7.4.2  
**Overall Status:** ALL CHECKS PASSED (112/112 Pytest Tests Passed, 0 Typecheck Errors, 2 Static Routes Built Cleanly)

---

## 1. Automated Test Execution Ledger

| Test Suite / Command | Scope & Purpose | Tests Executed | Passed | Failed | Exit Code | Duration |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `python scripts/run_validation_pipeline.py` | Data validation, hash re-verification, domain boundaries | 5 steps | 5 | 0 | 0 | 5.2s |
| `pytest tests/test_data_integrity.py` | Manifest hashes, null semantics, produce crop verification | 16 | 16 | 0 | 0 | 0.82s |
| `pytest tests/test_backend_api.py` | FastAPI health, status, config, CORS, path containment | 9 | 9 | 0 | 0 | 0.45s |
| `pytest tests/test_domain_schemas.py` | Pydantic model validation & unit preservation | 6 | 6 | 0 | 0 | 0.28s |
| `pytest tests/test_idempotent_import.py` | Idempotent import service & raw file immutability | 3 | 3 | 0 | 0 | 0.19s |
| `pytest tests/test_data_layer_endpoints.py`| All 14 FastAPI endpoints, parameter filters, query bounds | 21 | 21 | 0 | 0 | 0.65s |
| `pytest tests/test_phase4_dashboard.py` | Two-screen route build, removed routes absent, cache integrity | 27 | 27 | 0 | 0 | 0.48s |
| `pytest tests/test_phase5_polish.py` | Design tokens, focus visible, reduced motion, hero visual | 6 | 6 | 0 | 0 | 0.22s |
| `pytest tests/test_phase6_analytics.py` | 7-point eligibility gates, anti-hoarding rules, synthetic isolation | 15 | 15 | 0 | 0 | 0.72s |
| `pytest tests/test_simplified_product.py` | Two-experience scope, landing page CTA, map, risk assessment | 9 | 9 | 0 | 0 | 0.38s |
| **Full Pytest Suite (`pytest tests/ -v`)** | Complete repository-wide regression gate | **112** | **112** | **0** | **0** | **2.33s** |
| `npm run check --prefix frontend` | TypeScript and Astro diagnostics across all files | 10 files | 10 | 0 | 0 | 9.8s |
| `npm run build --prefix frontend` | Astro static production bundle compiler | 2 routes | 2 | 0 | 0 | 1.08s |

---

## 2. Browser & Visual Verification Audit

Live end-to-end browser verification was conducted using the automated browser subagent on `http://127.0.0.1:4321/`:

### 2.1 Landing Page Verification (`http://127.0.0.1:4321/`)
- **Headline & Branding:** Verified prominent title: *"Explore Potential Grain-Hoarding Risk Locations Across Punjab"*.
- **Primary Call to Action:** Verified primary CTA button `Open Dashboard` (`href="/dashboard"`).
- **3D Agricultural Visual:** Procedural stainless steel silos and wheat chaff particles rendered cleanly with accessible pause toggle.
- **3-Step Explainer:** Verified cards for *Geospatial Mapping*, *7-Point Qualification Gate*, and *Explainable Assessment*.
- **Evidentiary Limitations:** Prominently displays four core boundary cards (Statistical Anomaly != Hoarding, 0 Wheat/Paddy Market Arrivals, 100% Null Arrival Quantities, Unmeasured Private Inventories).
- **Artifact:** `simplified_landing_page.png`.

### 2.2 Main Dashboard Verification (`http://127.0.0.1:4321/dashboard`)
- **Map Rendering:** Verified full SVG choropleth of Punjab rendering all 23 official district boundary polygons.
- **Location Markers:** Verified APMC mandi markers plotted at verified locations (e.g. Abohar, Adampur, Ajnala).
- **Interactive Selection:**
  - Default selection loads `Ludhiana District`.
  - Clicking on `Fazilka` updates map highlight and dynamically refreshes the location panel.
- **Hoarding Risk Evaluation Panel:**
  - Displays badge: **`INSUFFICIENT DATA TO ASSESS RISK`**.
  - Clearly explains why risk cannot be computed (0 foodgrain arrival rows, 100% null volume gap in Agmarknet, unmeasured private storage).
  - Confirms Rule 6 notice: statistical anomaly != illegal hoarding.
- **Verified Observations:**
  - Displays verified Wheat & Rice production figures (DES APY 2022-23).
  - Displays verified AGMARKNET daily wholesale modal price quotes (Rs. 2,461/Qtl for Abohar).
- **Artifacts:** `simplified_dashboard_overview.png`, `simplified_location_assessment.png`.
- **Console Errors:** Exactly `0` console errors recorded during navigation and interaction.
- **Session Recording:** `simplified_product_verification_1792644177577.webp`.

---

## 3. Core Invariant Assertions

| Invariant Requirement | Test Evidence | Verdict |
| :--- | :--- | :---: |
| **No Fabricated Risk Scores** | Location panel displays "INSUFFICIENT DATA TO ASSESS RISK"; no numerical hoarding probabilities exist. | **PASSED** |
| **No Actor-Level Rankings** | Zero trader scorecards, hoarder leaderboards, or APMC culpability ranks in code or templates. | **PASSED** |
| **No Removed Routes in Dist** | `tests/test_phase4_dashboard.py` explicitly tests that all 9 removed routes do not exist in `dist/`. | **PASSED** |
| **Minimal Navigation** | Top navigation bar contains strictly `Home` (`/`) and `Dashboard` (`/dashboard`). | **PASSED** |
| **Preservation of Raw Inputs** | Recomputed SHA-256 digests across 49 raw source files in `data/inbox/` show 100% hash match. | **PASSED** |
| **Preservation of Backend APIs** | All 14 FastAPI endpoints tested and verified with HTTP 200 responses. | **PASSED** |
| **No Hardcoded Dataset Counts** | Catalog counts generated deterministically via `scripts/run_validation_pipeline.py`. | **PASSED** |
| **No Committed Secrets** | Regex audit confirms zero exposed API keys, bearer tokens, or passwords; `.env.example` is template-only. | **PASSED** |
| **Safe TLS Settings** | Zero instances of `verify=False` or SSL bypasses in codebase. | **PASSED** |
| **Bounded Retries & Containment**| Connectors enforce `max_retries=3`, `timeout_seconds=10.0`, and path traversal protection in `config.py`. | **PASSED** |

---

## 4. Known Limitations & Unverified Items

1. **Staple Foodgrain Market Arrivals:** The acquired APMC daily panel contains 62 produce crops with zero wheat or paddy rows. Accessing daily foodgrain arrivals requires credentialed access to Punjab's Anaaj Kharid infrastructure.
2. **Wholesale Arrival Volumes:** Public AGMARKNET daily feeds report modal prices with 100% null arrival volumes. Quantities cannot be derived from prices.
3. **Private Warehouse Inventories:** Commercial silo and private trader holdings are unpublished in open portals. Full supply balance equations remain uncomputable.
4. **Environment Portability:** Windows PowerShell native environment was fully tested. Linux native deployment without WSL was not tested directly due to operating in a Windows workspace.
