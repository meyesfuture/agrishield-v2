# Punjab GrainWatch Decision Engine & Anomaly Detection Specification

**Document Version:** 2.1.0  
**Effective Date:** 2026-10-22  
**Implementation Modules:** [`backend/services/decision_engine.py`](file:///B:/Projects/Punjab_GrainWatch_Project_Starter/backend/services/decision_engine.py), [`backend/schemas/decision.py`](file:///B:/Projects/Punjab_GrainWatch_Project_Starter/backend/schemas/decision.py), [`backend/api/routes/decision.py`](file:///B:/Projects/Punjab_GrainWatch_Project_Starter/backend/api/routes/decision.py)

---

## 1. Overview & Architectural Purpose

The Punjab GrainWatch Decision Engine is a dedicated, deterministic backend service designed to screen agricultural supply flows for statistically unusual divergence patterns.

### Core Governance Principles (AGENTS.md Rule 6)
1. **Statistical Anomaly != Proof of Hoarding:** Market data alone cannot establish illegal intent, concealment, or criminal conduct. A statistical divergence is strictly an investigative prompt directing administrative resources to inspect gate passes, storage facilities, and transportation manifests.
2. **No Fabricated Scores on Incomplete Data:** If minimum history, paired volume series, or local inventories are missing, the engine deterministically outputs `INSUFFICIENT_DATA`. It never manufactures a risk score or imputes missing values as zeros.
3. **No Actor-Level Accusations:** Actor-level risk scoring, trader rankings, or private warehouse naming are prohibited without verified authoritative administrative findings.
4. **Segregated Evidence Modes:** Real evidence evaluation and synthetic demonstration scenarios operate under strict isolation.

---

## 2. Statistical Methodology

### Why Robust Statistics (MAD) Over Classical Z-Scores
Classical estimators (sample mean $\mu$ and sample standard deviation $\sigma$) are inherently vulnerable to masking and swamping: extreme supply anomalies inflate $\mu$ and $\sigma$, thereby diluting the normalized divergence of the anomaly itself.

The Decision Engine employs **Median Absolute Deviation (MAD)**:
1. **Historical Baseline Median:**
   $$\tilde{X} = \text{median}(X_{\text{baseline}})$$
2. **Median Absolute Deviation (MAD):**
   $$\text{MAD} = \text{median}(|X_i - \tilde{X}|)$$
3. **Normal-Consistent Scale Factor:**
   $$\hat{\sigma}_{\text{robust}} = 1.4826 \times \text{MAD}$$
4. **Robust Z-Score ($Z_{\text{robust}}$):**
   $$Z_{\text{robust}} = \frac{X_{\text{current}} - \tilde{X}}{\hat{\sigma}_{\text{robust}}}$$
5. **Percentage Deviation ($\Delta_{\%}$):**
   $$\Delta_{\%} = \left(\frac{X_{\text{current}} - \tilde{X}}{\tilde{X}}\right) \times 100\%$$

---

## 3. Configurable Thresholds & Decision Rules

| Parameter | Configured Value | Statistical Rationale |
| :--- | :--- | :--- |
| **Minimum Baseline Observations** | `14 points` | Minimum sample size to estimate non-parametric median and MAD stably |
| **Price Deviation Threshold** | `+20.0%` & $Z_{\text{robust}} \ge 2.0$ | Statistically significant wholesale price inflation above historical median |
| **Arrival Deviation Threshold** | `-25.0%` & $Z_{\text{robust}} \le -2.0$ | Severe contraction in physical mandi arrivals below expected baseline |
| **Evaluation Window** | `Latest 14 points` | Compares recent operational window against pre-divergence baseline |

### Decision Outcomes State Machine

```
                              [Daily Market Observations]
                                           │
                           Has >= 14 Paired Observations?
                                    ├── NO ──> [INSUFFICIENT_DATA] (Score: None)
                                    └── YES
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
             Price Surge?                                Arrival Collapse?
    (Δ% >= +20% & Z_rob >= 2.0)                 (Δ% <= -25% & Z_rob <= -2.0)
         │               │                           │                 │
        YES              NO                         YES                NO
         │               │                           │                 │
         └───────┬───────┴─────────────┬─────────────┴─────────────────┘
                 │                     │
        Both Anomalous?       Only Price Anomalous?       Only Arrival?       Neither?
                 │                     │                        │                 │
                 ▼                     ▼                        ▼                 ▼
          [CONVERGENT_           [PRICE_SIGNAL]         [ARRIVAL_SIGNAL]    [NO_MATERIAL_
         SUPPLY_ANOMALY]        (Intensity Score)       (Intensity Score)      ANOMALY]
        (Combined Score)                                                    (Score: 0.0)
```

---

## 4. Structured Output Contract

Every assessment produces a fully typed JSON response conforming to `DecisionAssessmentResponse`:

```json
{
  "assessment_id": "ASSESS-1792647961",
  "assessment_timestamp_utc": "2026-10-22T05:46:01Z",
  "evidence_mode": "SYNTHETIC_DEMO",
  "scenario_id": "scenario_b_convergent_anomaly",
  "location_id": "scenario_b_convergent_anomaly",
  "location_name": "Khanna Grain Mandi (Synthetic)",
  "geographic_granularity": "mandi",
  "canonical_commodity": "Wheat (Common Foodgrain)",
  "observation_date": "2026-10-15",
  "baseline_interval": "2026-09-01 to 2026-09-30",
  "decision_status": "CONVERGENT_SUPPLY_ANOMALY",
  "status_label": "CONVERGENT SUPPLY ANOMALY DETECTED",
  "human_explanation": "Statistical convergence detected for Wheat (Common Foodgrain) in Khanna Grain Mandi (Synthetic). Wholesale prices increased by +49.1% (Robust Z = +3.82) while arrival volumes collapsed by -63.5% (Robust Z = -4.12) against historical median baseline. Pattern warrants on-site administrative verification.",
  "anomaly_intensity_score": 93.8,
  "signals": {
    "price": {
      "signal_type": "price",
      "status": "ANOMALOUS",
      "observed_value": 3168.4,
      "baseline_median": 2125.0,
      "deviation_pct": 49.1,
      "robust_z_score": 3.82,
      "unit": "Rs./Quintal",
      "contribution_pct": 50.0,
      "explanation": "Price deviation of +49.1% vs baseline median (Rs. 2125.0/Qtl)."
    },
    "arrival": {
      "signal_type": "arrival",
      "status": "ANOMALOUS",
      "observed_value": 912.5,
      "baseline_median": 2500.0,
      "deviation_pct": -63.5,
      "robust_z_score": -4.12,
      "unit": "Quintals",
      "contribution_pct": 50.0,
      "explanation": "Arrival volume deviation of -63.5% vs baseline median (2500.0 Qtl)."
    }
  },
  "evidence_coverage": {
    "required_streams": ["Wholesale Price", "Arrival Quantity", "Historical Depth"],
    "verified_streams": ["Wholesale Price", "Arrival Quantity", "Historical Depth"],
    "sufficiency_pct": 100.0
  },
  "unavailable_signals": [],
  "data_quality_warnings": [],
  "eligibility_gate_passed": true,
  "methodology_version": "v2.1.0-robust-mad",
  "threshold_config_version": "v2.1.0-config",
  "recommended_action": "Recommend prompt administrative investigation. Co-occurrence of abnormal price inflation and severe arrival volume contraction warrants field audit of mandi gate passes, storage facilities, and inter-district transport manifests. Note: Rule 6 strictly dictates this anomaly is an investigation prompt, not legal confirmation of intentional hoarding.",
  "legal_caveat": "Under AGENTS.md Rule 6, a statistical anomaly is an investigative screening prompt only. It does NOT establish criminal intent, concealment, or the fact of hoarding."
}
```
