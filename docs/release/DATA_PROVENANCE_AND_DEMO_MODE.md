# Data Provenance & Demo Mode Architecture
## Punjab GrainWatch — Final Master Build

### 1. The Real-Data Dilemma & Provenance Ground Truth

A core requirement of agricultural intelligence is data honesty. Across the Phase 1 through Phase 5 data acquisitions in the Punjab GrainWatch repository, rigorous auditing revealed critical structural boundaries in the available real-world public data:

1. **Agmarknet Mandi Arrivals**:
   - The acquired real mandi arrival dataset (`data/inbox/gemini_phase5/phase5_acquisition/mandi_arrivals_2024_2025.csv`) covers various agricultural commodities across Punjab mandis, but contains **0 records for wheat or paddy**.
   - Public daily Agmarknet arrivals for wheat and paddy are subject to seasonal procurement windows (Rabi marketing season April–May for wheat; Kharif marketing season October–November for paddy) and reporting latency.
2. **Wholesale Daily Prices vs. Arrival Volumes**:
   - While daily wholesale price records exist for key commodities across Punjab reporting centers (`daily_wholesale_prices_punjab_2024_2025.csv`), they do not include matching daily arrivals quantity at the same physical mandi gate.
3. **Storage & Stock Holdings**:
   - Real public stock figures are published by the Food Corporation of India (FCI) as **national and state-level macro totals** (`fci_central_pool_stocks_2020_2024.csv`), not disaggregated by individual private warehouse, silo, or trade licensee in Punjab.
4. **Absence of Ground-Truth Criminal Hoarding Labels**:
   - No public regulatory agency publishes verified, labelled datasets of prosecuted or convicted private grain-hoarding incidents with granular market-level features.

**Consequence**: Any algorithm that claims to detect actual illegal grain hoarding from this real-world public data alone is fabricating conclusions. In accordance with **AGENTS.md Rule 4 & Rule 6**, the Punjab GrainWatch application strictly respects this reality:
- In **REAL Evidence Mode**, the decision engine evaluates incoming telemetry against a strict 6-point eligibility gate.
- Because necessary grain arrival volumes and private stock records are absent, the engine reports `INSUFFICIENT_DATA` with a 28% data-sufficiency score, clearly enumerating what is present (prices, historical yields, weather) and what is missing (commodity-matched arrivals, private stock filings).

---

### 2. Isolated Deterministic Synthetic Scenario Lab

To prove that the anomaly detection engine functions correctly without contaminating real datasets, an isolated, deterministic synthetic scenario lab was engineered:

- **Source Code**: [`backend/services/synthetic_generator.py`](file:///B:/Projects/Punjab_GrainWatch_Project_Starter/backend/services/synthetic_generator.py)
- **Fixture Directory**: [`data/synthetic/scenarios/`](file:///B:/Projects/Punjab_GrainWatch_Project_Starter/data/synthetic/scenarios/)
- **Determinism**: Fixed random seed (`seed=42`) ensuring identical output on every run.
- **Physical Separation**: Synthetic scenarios are stored exclusively in `data/synthetic/` and are tagged with `data_mode="SYNTHETIC_DEMO"` and `is_synthetic=True`. They are never blended into real source files, manifests, or database tables.

#### Scenario Matrix

| Scenario ID | Name | Injected Pattern | Expected Engine Decision | Intensity Score |
| :--- | :--- | :--- | :--- | :--- |
| `scenario_a` | Normal Market Baseline | 60-day baseline + 7-day normal trading ($\pm 2\%$ price/arrival noise). | `NO_MATERIAL_ANOMALY` | 0.0 / 100 |
| `scenario_b` | Planted Convergent Anomaly | 60-day baseline + deliberate 50% price spike and 60% arrival crash in final 7 days. | `CONVERGENT_SUPPLY_ANOMALY` | > 85.0 / 100 |
| `scenario_c` | Price-Only Spike | 60-day baseline + 50% price spike with stable normal arrivals. | `PRICE_SIGNAL` | 45.0 / 100 |
| `scenario_d` | Arrival-Only Decline | 60-day baseline + 60% arrival decline with stable normal prices. | `ARRIVAL_SIGNAL` | 35.0 / 100 |
| `scenario_e` | Insufficient / Corrupted Data | Severely truncated 7-day series with missing arrival values. | `INSUFFICIENT_DATA` | None (null) |

---

### 3. Persistent Watermark & UI Safeguards

When operating in Synthetic Demo Mode, strict visual and ethical guardrails are enforced across the application:

1. **Global Persistent Banner**:
   - A bright red container banner (`#F9DEDC` background, `#B3261E` text and border) displays prominently at the top of the dashboard:
     ```
     SYNTHETIC DEMO — NOT LIVE MARKET EVIDENCE
     Illustrative test scenario active. Data is deterministically generated to demonstrate algorithm detection capabilities. Does not represent real market conditions, traders, or hoarding findings.
     ```
2. **Component-Level Badges**:
   - The selected location header, assessment outcome card, score gauge, and individual time-series charts all display explicit `SYNTHETIC DEMO` pill badges.
3. **Illustrative Geography Disclosure**:
   - The location identifier in synthetic scenarios (e.g., `DEMO-LDH-01`, `DEMO-PTA-01`) is prefixed and accompanied by an explicit disclosure that the market coordinates are used solely to orient the map and do not imply any irregularities at the actual physical mandi.
4. **Export & Screenshot Safety**:
   - Watermarks are embedded within the DOM containers and CSS print stylesheets so that any screenshot or PDF export preserves the synthetic disclosure.

---

### 4. Mode Switching Architecture

The frontend and backend maintain complete isolation between operating modes:

```mermaid
graph TD
    A[User Selects Mode in UI] -->|Mode = REAL| B[Fetch Real District Telemetry]
    A -->|Mode = SYNTHETIC_DEMO| C[Fetch Synthetic Scenario Fixture]
    
    B --> D[Backend /api/v1/decision/assess]
    D --> E[Eligibility Gate Validation]
    E -->|Fails Gate: Missing Arrivals| F[Return INSUFFICIENT_DATA with 28% Readiness]
    
    C --> G[Backend /api/v1/decision/scenarios/{id}/run]
    G --> H[Deterministic Anomaly Engine]
    H -->|Calculate MAD & Robust Z-Scores| I[Return Dynamic Assessment: CONVERGENT, SIGNAL, or NORMAL]
    
    F --> J[Frontend Displays Gaps & 4 Real Metric Charts]
    I --> K[Frontend Displays Anomaly Breakdown & Divergence Chart]
```

- **Zero Silent Fallback**: If real data fails an eligibility check, it **never** falls back to synthetic fixtures. It reports an honest empty/insufficient state.
- **Dynamic Calculation**: Synthetic demo results are computed on-the-fly by the backend Python service (`decision_engine.py`) upon request, proving the statistical pipeline functions end-to-end.
