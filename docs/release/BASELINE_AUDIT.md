# Baseline Audit: Punjab GrainWatch / AgriShield Architectural Analysis

**Audit Date:** 2026-10-22  
**Auditor:** Principal Software & Data Engineer, Antigravity AI  
**Scope:** Current Punjab GrainWatch workspace vs. Legacy AgriShield reference repository (`https://github.com/meyesfuture/agrishield`)

---

## 1. Executive Summary

This audit establishes the empirical baseline of Punjab GrainWatch before implementing the final decision engine, synthetic scenario lab, and end-to-end anomaly detection pipeline.

The fundamental defect in both the legacy AgriShield codebase and the initial Punjab GrainWatch starter is **the absence of a functioning, defensible, end-to-end decision engine**:
1. **In AgriShield (`legacy`):** An ad-hoc weighted formula (35% price, 35% arrival, 20% satellite, 10% news) was arbitrarily defined in prototype documentation without empirical calibration. It assumed continuous arrival quantities and local stock observations that did not exist in real public feeds, and it conflated statistical variance with "hoarding risk."
2. **In Punjab GrainWatch Starter (`pre-refactor`):** The application rightfully implemented strict governance gates (AGENTS.md Rule 6) that blocked all real data from computing a hoarding score due to empirical data gaps (zero wheat/paddy arrivals, 100% null Agmarknet arrival volumes). However, it lacked an active backend decision service to compute statistical anomalies when compatible data *is* provided, and its synthetic demonstration was a static JSON file rather than an algorithmic calculation.

---

## 2. Comparative Codebase Analysis

| Dimension | Legacy AgriShield (`agrishield_ref`) | Punjab GrainWatch Starter (`current`) | Required Final State |
| :--- | :--- | :--- | :--- |
| **Frontend Stack** | Vite + React + Tailwind + Lucide | Astro + React + TypeScript + M3 Vanilla CSS | Astro + React + TypeScript + Google Material 3 Light Mode |
| **Backend Stack** | FastAPI + SQLite (SQLAlchemy) | FastAPI + Pydantic v2 + Validated File Stores | FastAPI + Pydantic v2 + Deterministic Services |
| **Decision Logic** | `app/engine.py` using arbitrary weights (`price*0.35 + arrival*0.35 + sat*0.20 + news*0.10`) | Static `AnalyticsEligibilityService` returning hardcoded gate blocks | Dedicated `DecisionEngineService` using robust statistics (MAD / robust Z-scores) |
| **Decision States** | Binary alert levels (`normal`, `elevated`, `critical`) | Hardcoded `"INSUFFICIENT DATA TO ASSESS RISK"` | 5 Semantic States (`INSUFFICIENT_DATA`, `NO_MATERIAL_ANOMALY`, `PRICE_SIGNAL`, `ARRIVAL_SIGNAL`, `CONVERGENT_SUPPLY_ANOMALY`) |
| **Synthetic Demo** | Static SQLite database seeded with fixed values | 1 static JSON fixture (`scenario_hypothetical_wheat_dip.json`) | Deterministic multi-scenario generator (A–E) dynamically evaluated by the backend engine |
| **Real Data Integrity** | Conflated missing arrivals with normal; ignored data gaps | Fully audited Phase 1 manifests; explicit null preservation | Preserved Phase 1 manifests; real mode explicitly diagnoses missing prerequisites |
| **Evidentiary Governance** | Implied hoarding detection from price/satellite signals alone | Enforced Rule 6 (Anomaly != Hoarding), but lacked dynamic demonstration | Rule 6 enforced: engine detects *supply anomalies*, explicitly caveats that hoarding cannot be inferred |

---

## 3. Root Cause Trace: The Decision Chain Disconnect

Tracing the complete decision chain reveals why the current application cannot make a defensible decision:

```
[Input Data] 
  ├── Real APMC: 3,892 rows, but 0 wheat/paddy (62 produce crops only)
  ├── Real AGMARKNET: 53 paddy modal prices, but arrival quantities are 100% null
  └── Real Stocks: 100 Central Pool rows, but state is 100% null (national aggregate only)
         ↓
[Validation Layer]
  └── Correctly identifies that staple grain arrivals & local stocks are missing
         ↓
[Eligibility Gate]
  └── Blocks all real streams with "INELIGIBLE (BLOCKED)"
         ↓
[Backend Decision Engine (Missing Link)]
  └── NO algorithmic service exists to:
        (a) Evaluate statistical deviation on time-series inputs
        (b) Differentiate between price-only spikes, arrival-only drops, and convergent anomalies
        (c) Accept synthetic scenario inputs to prove the detection logic works
         ↓
[API Layer]
  └── Only exposes static eligibility reports and one raw JSON fixture
         ↓
[Frontend Dashboard]
  └── Renders a static hardcoded card: "INSUFFICIENT DATA TO ASSESS RISK"
      Cannot run or demonstrate anomaly detection algorithms in action!
```

---

## 4. Key Architectural Deficiencies to Resolve

1. **Missing Backend Decision Service:**
   - Need `backend/services/decision_engine.py` and `backend/schemas/decision.py`.
   - Must implement robust statistics: Median and Median Absolute Deviation (MAD), robust Z-scores, configurable minimum observation thresholds (e.g. 14 baseline points), and multi-signal convergence rules.

2. **Missing Deterministic Synthetic Scenario Suite:**
   - Need `backend/services/synthetic_generator.py` generating 5 distinct scenarios:
     - **Scenario A:** Normal baseline with random seed variation -> `NO_MATERIAL_ANOMALY`.
     - **Scenario B:** Planted convergent anomaly (price surge + arrival collapse) -> `CONVERGENT_SUPPLY_ANOMALY`.
     - **Scenario C:** Price-only spike without arrival collapse -> `PRICE_SIGNAL`.
     - **Scenario D:** Arrival-only drop without price surge -> `ARRIVAL_SIGNAL`.
     - **Scenario E:** Corrupted / truncated data (<14 points, missing dates) -> `INSUFFICIENT_DATA`.

3. **Missing Interactive Frontend Modes:**
   - Need clear top-level mode toggle in `DashboardView.tsx`: **Real Evidence Mode** vs. **Synthetic Demo Mode**.
   - In Demo Mode: full scenario selector, call backend `/api/v1/decision/scenarios/{id}/run`, render live calculated results, dynamic signal breakdowns, and interactive time-series charts with baseline vs anomaly bands.
   - Persistent watermark banner: `SYNTHETIC DEMO — NOT LIVE MARKET EVIDENCE`.

4. **Preservation Invariant:**
   - Real-data catalogs, checksums, and existing 120 tests must remain passing.
   - Zero synthetic rows in real data files.

---

## 5. Next Steps
Proceed directly to Step 2: Implement the typed decision schemas, deterministic synthetic generator, core decision engine, and REST API endpoints.
