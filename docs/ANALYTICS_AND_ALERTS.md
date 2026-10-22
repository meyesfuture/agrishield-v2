# Analytics, Anomaly Screening & Hoarding Claim Boundaries

## 1. Operational Eligibility Status (Phase 6)

Under Phase 6 governance and AGENTS.md Rule 6, all automated statistical anomaly screening for Punjab foodgrain supply is rigorously evaluated via a 7-point eligibility gate before execution.

| Data Stream | Commodity Scope | Temporal Granularity | Spatial Identity | Gate Status | Operational Handling Policy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Punjab Mandi Board (PSAMB) e-Mandikaran** | 62 Produce Commodities | Daily (Oct 2026) | APMC Mandis | **INELIGIBLE (BLOCKED)** | `DISPLAY_AS_DESCRIPTIVE_PRODUCE_ONLY`. Exactly zero wheat/paddy rows. Grain anomaly algorithms strictly blocked. |
| **AGMARKNET 2.0 Wholesale Prices** | Paddy (Common & Basmati) | Daily Quotes (Oct 2026) | APMC Mandis | **INELIGIBLE (BLOCKED)** | `DISPLAY_MODAL_PRICES_ONLY`. Arrival quantities are 100% unexposed (null). Cannot infer volume from price. |
| **DFPD Central Pool Stocks** | Wheat & Rice Reserves | Monthly (2020–2026) | National Aggregate | **INELIGIBLE (BLOCKED)** | `DISPLAY_AS_NATIONAL_MACRO_CONTEXT_ONLY`. State column is 100% null. Cannot downscale to Punjab silos. |
| **CFPP RMS 2025-26 Procurement** | Wheat Procurement | Single Snapshot (2025-05-15) | State Aggregate | **INELIGIBLE (BLOCKED)** | `DISPLAY_AS_ISOLATED_SNAPSHOT_ONLY`. Cannot interpolate single point into daily flow series. |

**Overall Screening Verdict:** `INSUFFICIENT EVIDENCE (BLOCKED)`  
**Private Hoarding Detection:** `STRICTLY FORBIDDEN` (Rule 6: Statistical Anomaly != Hoarding; Missing Denominator & Verified Controls).

---

## 2. The 7-Point Statistical Anomaly Screening Eligibility Gate

Any candidate dataset must pass all seven mandatory empirical gates prior to statistical anomaly model fitting:

1. **CRIT-01: Commodity Appropriateness**  
   *Requirement:* Must represent target staple foodgrain (Wheat or Paddy), not non-grain produce or substitute crops.  
   *Current Status:* Mandi arrival panel contains 3,892 produce records (fruits, vegetables, spices); exactly 0 wheat or paddy records.

2. **CRIT-02: Temporal Granularity & Continuity**  
   *Requirement:* Continuous daily or weekly market observation sequence with exposed physical volume metrics.  
   *Current Status:* AGMARKNET price feed contains wholesale prices, but arrival volumes are 100% null. Procurement contains only 1 date.

3. **CRIT-03: Sufficient Historical Depth**  
   *Requirement:* Minimum 36 consecutive months (3 annual crop cycles) to establish robust seasonal baseline medians.  
   *Current Status:* Mandi arrivals cover a single 14-day operational slice (October 2026). Zero multi-year depth.

4. **CRIT-04: Physical Unit Consistency**  
   *Requirement:* Explicitly declared physical mass units (Metric Quintals or Lakh Metric Tonnes) without ambiguous packaging units.  
   *Current Status:* Passed where physical quantities are reported.

5. **CRIT-05: Missingness & Zero Semantics**  
   *Requirement:* Strict preservation of nulls, clerk sentinels, and non-reporting periods without coercing missing values to 0.0.  
   *Current Status:* Verified and enforced across all domain schemas.

6. **CRIT-06: Geographic & Market Identity**  
   *Requirement:* Identifiable APMC market yards linked to administrative district boundaries.  
   *Current Status:* DFPD national stocks lack state/depot disaggregation (100% null state column). Procurement lacks mandi-level disaggregation.

7. **CRIT-07: Compatible Comparison Basis**  
   *Requirement:* Matched baseline catchment matching current market boundaries without cross-commodity or spatial distortions.  
   *Current Status:* Failed for all current streams due to missing matched baselines.

---

## 3. Mathematical Specification for Future Eligible Screening

When multi-year staple foodgrain daily arrivals become available, the system will apply robust non-parametric estimation:

### 3.1 Non-Parametric Seasonal Baseline
To prevent distortions from heavy-tailed agricultural distributions, the baseline expectation $\hat{A}_{m,d}$ for market $m$ on day-of-season $d$ is estimated using rolling multi-year median:
$$\hat{A}_{m,d} = \operatorname{median} \{ A_{m,d,y} \mid y \in \{Y-3, Y-2, Y-1\} \}$$

### 3.2 Empirical Prediction Band
The 95% empirical prediction interval is computed via the Interquartile Range (IQR):
$$IQR_{m,d} = Q_3(A_{m,d}) - Q_1(A_{m,d})$$
$$\text{Lower Bound}_{95\%} = \max\left(0, \hat{A}_{m,d} - 1.96 \cdot \frac{IQR_{m,d}}{1.349}\right)$$
$$\text{Upper Bound}_{95\%} = \hat{A}_{m,d} + 1.96 \cdot \frac{IQR_{m,d}}{1.349}$$

### 3.3 Candidate Screening Threshold
An observation is flagged as an **Anomaly Candidate for Human Audit** if and only if:
1. Daily arrival residual $\Delta\% < -30\%$ below median for $\ge 3$ consecutive reporting days, AND
2. Observed arrival falls strictly below $\text{Lower Bound}_{95\%}$.

### 3.4 Candidate Metadata Schema
Every candidate record must record:
- `candidate_id`: UUID
- `market_id`, `district_id`, `commodity_name`
- `observation_date`: YYYY-MM-DD
- `observed_value_qtl`: Float
- `baseline_median_qtl`: Float
- `prediction_interval_95`: `[lower_bound, upper_bound]`
- `algorithm_version`: e.g., `v1.0.0-median-iqr`
- `candidate_disposition`: `HUMAN_AUDIT_REQUIRED` (Never proof of intent)

---

## 4. Accounting Guardrails & Prohibitions

A physical grain supply reconciliation equation is:
$$\text{Opening Stock} + \text{Production} + \text{Inflows} = \text{Procurement} + \text{Private Milling} + \text{Losses} + \text{Closing Stock} + \text{Residual}$$

The residual cannot be computed without synchronized denominators. Under AGENTS.md Rule 6, the following actions are **strictly prohibited**:
1. **Never claim hoarding detected:** A negative arrival residual may reflect rain-delayed harvesting, transport strikes, road blockages, farmer storage in village kothis, or moisture-rejection at mandi gates.
2. **Never rank named actors or traders:** No trader risk scores, hoarder leaderboards, or APMC culpability indices.
3. **Never substitute proxies:** Do not use prices as arrival quantities, national stocks as Punjab stocks, or single-day procurement snapshots as continuous flow.
4. **Never train ML without verified ground truth:** Supervised classification requires independently audited positive and negative controls with leakage-free spatial-temporal cross-validation.

---

## 5. Synthetic Demo Lab Protocol

To demonstrate what-if simulation safely without contaminating production telemetry:
- All counterfactual datasets reside strictly in `data/synthetic/`.
- Every payload must contain `"is_synthetic": true` and `"evidence_level": "synthetic demo"`.
- Every visual screen and data download must carry prominent crimson watermarks: `SYNTHETIC EXAMPLE — NOT REAL DATA`.
- Synthetic records are strictly excluded from dataset catalogs, summary scorecards, and default application routes.
