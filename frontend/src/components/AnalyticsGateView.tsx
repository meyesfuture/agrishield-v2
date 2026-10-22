import React, { useState, useEffect } from 'react';

export interface EligibilityCheckItem {
  criteria_id: string;
  criteria_name: string;
  required_standard: string;
  current_evidence: string;
  passed: boolean;
  blocking_reason?: string | null;
}

export interface DatasetEligibilityResult {
  dataset_id: string;
  stream_name: string;
  commodity: string;
  temporal_granularity: string;
  eligible_for_grain_anomaly: boolean;
  eligibility_verdict: string;
  passed_criteria_count: number;
  failed_criteria_count: number;
  criteria_checks: EligibilityCheckItem[];
  missing_prerequisites: string[];
  handling_policy: string;
}

export interface ReadinessMetrics {
  completeness_score_pct: number;
  freshness_status: string;
  schema_validity_pct: number;
  geographic_coverage_pct: number;
  commodity_coverage_state: string;
  api_readiness_tested_count: number;
  api_blocked_count: number;
}

export interface EligibilityGateResponse {
  overall_analytics_eligibility: string;
  overall_hoarding_detection_eligibility: string;
  audit_timestamp_utc: string;
  total_streams_evaluated: number;
  eligible_streams_count: number;
  readiness_metrics: ReadinessMetrics;
  stream_evaluations: DatasetEligibilityResult[];
  mandatory_governance_rules: string[];
}

export interface SyntheticScenario {
  scenario_id: string;
  title: string;
  evidence_level: string;
  is_synthetic: boolean;
  synthetic_warning: string;
  governance_notice: string;
  methodology: {
    model_name: string;
    model_version: string;
    baseline_window_years: number;
    confidence_interval: string;
    target_commodity: string;
    unit: string;
    investigation_prompt_threshold: string;
    candidate_disposition: string;
  };
  market_context: {
    hypothetical_market: string;
    district: string;
    timeframe: string;
    simulated_cause: string;
  };
  time_series: Array<{
    date: string;
    expected_median_qtl: number;
    lower_bound_95_qtl: number;
    upper_bound_95_qtl: number;
    observed_arrival_qtl: number;
    residual_pct: number;
    is_anomaly_candidate: boolean;
    status_label: string;
  }>;
  investigation_protocol: {
    action_prompt: string;
    strictly_forbidden_actions: string[];
  };
}

export const AnalyticsGateView: React.FC = () => {
  const [gateData, setGateData] = useState<EligibilityGateResponse | null>(null);
  const [syntheticData, setSyntheticData] = useState<SyntheticScenario | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStreamId, setSelectedStreamId] = useState<string>('punjab_mandi_arrivals_oct2026');
  const [activeTab, setActiveTab] = useState<'eligibility_matrix' | 'synthetic_lab'>('eligibility_matrix');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch Eligibility Gate Response
        let egResponse: EligibilityGateResponse | null = null;
        try {
          const res = await fetch('http://127.0.0.1:8000/api/v1/analytics/eligibility-gate');
          if (res.ok) {
            egResponse = await res.json();
          }
        } catch {
          // fallback to static cache
        }

        if (!egResponse) {
          const resStatic = await fetch('/data/eligibility_gate.json');
          if (resStatic.ok) {
            egResponse = await resStatic.json();
          }
        }

        setGateData(egResponse);

        // Fetch Synthetic Scenario
        let synResponse: SyntheticScenario | null = null;
        try {
          const res = await fetch('http://127.0.0.1:8000/api/v1/analytics/synthetic-scenario');
          if (res.ok) {
            synResponse = await res.json();
          }
        } catch {
          // fallback to static cache
        }

        if (!synResponse) {
          const resStatic = await fetch('/data/synthetic_scenario.json');
          if (resStatic.ok) {
            synResponse = await resStatic.json();
          }
        }

        setSyntheticData(synResponse);
      } catch (err: any) {
        setError(err.message || 'Failed to load analytics eligibility data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const selectedStream = gateData?.stream_evaluations.find(s => s.dataset_id === selectedStreamId) || gateData?.stream_evaluations[0];

  return (
    <div className="analytics-view">
      {/* Header */}
      <div className="view-header">
        <div>
          <h1 className="view-title">Transparent Analytics & Anomaly Screening Eligibility</h1>
          <p className="view-subtitle">
            Strict 7-point empirical qualification gate governing statistical calculations under AGENTS.md Rule 6 and PRD §7.
          </p>
        </div>
        <div className="provenance-pill" title="Audited Governance Standard">
          <span>GOVERNANCE: AGENTS.MD RULE 6</span>
          <span className="dot">•</span>
          <span>EMPIRICAL GATES</span>
        </div>
      </div>

      {/* Global Verdict Banner */}
      <div className="gap-alert-card" role="region" aria-label="Official Analytics Readiness Verdict">
        <div className="alert-icon" aria-hidden="true">🛡️</div>
        <div className="alert-content">
          <h2 className="alert-title">OVERALL SCREENING VERDICT: INSUFFICIENT EVIDENCE (BLOCKED)</h2>
          <p className="alert-text">
            <strong>1. Grain Anomaly Screening:</strong> <code>BLOCKED</code>. The acquired mandi arrival panel covers 62 produce crops with
            <strong> zero wheat or paddy records</strong>. The AGMARKNET price feed has <strong>100% null arrival volumes</strong>.
            Statistical anomaly detection cannot be performed on unobserved volumes.
          </p>
          <p className="alert-text">
            <strong>2. Private Hoarding Claims:</strong> <code>STRICTLY FORBIDDEN</code>. Statistical anomalies are strictly investigation prompts.
            Without continuous grain arrivals, verified private facility stocks, and adjudicated positive/negative controls, actor-level ranking is legally and mathematically invalid.
          </p>
          <div className="alert-badge" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', borderColor: 'rgba(239, 68, 68, 0.4)' }}>
            ELIGIBLE STREAMS: 0 / 4 EVALUATED • HOARDING CLAIMS PROHIBITED
          </div>
        </div>
      </div>

      {/* View Mode Navigation Tabs */}
      <div className="view-tabs" role="tablist" aria-label="Analytics view modes">
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === 'eligibility_matrix'}
          className={`tab-btn ${activeTab === 'eligibility_matrix' ? 'active' : ''}`}
          onClick={() => setActiveTab('eligibility_matrix')}
        >
          <span>7-Point Eligibility Gate Matrix (Real Data)</span>
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === 'synthetic_lab'}
          className={`tab-btn synthetic-tab ${activeTab === 'synthetic_lab' ? 'active' : ''}`}
          onClick={() => setActiveTab('synthetic_lab')}
        >
          <span className="warning-dot">●</span>
          <span>Synthetic Counterfactual Lab (Demonstration Only)</span>
        </button>
      </div>

      {activeTab === 'eligibility_matrix' ? (
        <>
          {/* Explainable Quality & Readiness Metrics */}
          {gateData && (
            <div className="kpi-grid">
              <div className="kpi-card">
                <span className="kpi-label">Schema Validity</span>
                <div className="kpi-value-row">
                  <span className="kpi-number">{gateData.readiness_metrics.schema_validity_pct.toFixed(1)}%</span>
                  <span className="kpi-unit">Verified</span>
                </div>
                <span className="kpi-subtext">All 20 assets match canonical data dictionary</span>
              </div>

              <div className="kpi-card">
                <span className="kpi-label">Cell Completeness</span>
                <div className="kpi-value-row">
                  <span className="kpi-number">{gateData.readiness_metrics.completeness_score_pct.toFixed(1)}%</span>
                  <span className="kpi-unit">Non-Null</span>
                </div>
                <span className="kpi-subtext">Preserves explicit nulls (absence != zero)</span>
              </div>

              <div className="kpi-card">
                <span className="kpi-label">Geographic Coverage</span>
                <div className="kpi-value-row">
                  <span className="kpi-number">23 / 23</span>
                  <span className="kpi-unit">Districts</span>
                </div>
                <span className="kpi-subtext">100% matched to LGD administrative crosswalk</span>
              </div>

              <div className="kpi-card">
                <span className="kpi-label">API Feeds Status</span>
                <div className="kpi-value-row">
                  <span className="kpi-number">{gateData.readiness_metrics.api_readiness_tested_count} Working</span>
                  <span className="kpi-unit">/ {gateData.readiness_metrics.api_blocked_count} Blocked</span>
                </div>
                <span className="kpi-subtext">Zero live external requests on page load</span>
              </div>
            </div>
          )}

          {/* 7-Point Eligibility Gate Section */}
          <div className="table-card">
            <div className="table-header">
              <div>
                <h2 className="table-title">Stream-Level Calculation Qualification Gate</h2>
                <span className="table-note">Every data stream must satisfy all 7 criteria before statistical models can run.</span>
              </div>

              {/* Stream Selector */}
              {gateData && (
                <div className="filter-group">
                  <label htmlFor="stream-selector" className="filter-label">Audited Data Stream:</label>
                  <select
                    id="stream-selector"
                    className="filter-select"
                    value={selectedStreamId}
                    onChange={(e) => setSelectedStreamId(e.target.value)}
                  >
                    {gateData.stream_evaluations.map((stream) => (
                      <option key={stream.dataset_id} value={stream.dataset_id}>
                        {stream.stream_name} ({stream.eligibility_verdict})
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {selectedStream && (
              <div className="stream-detail-card">
                <div className="stream-header-row">
                  <div>
                    <h3 className="stream-title">{selectedStream.stream_name}</h3>
                    <p className="stream-meta">
                      <strong>Target Commodity:</strong> {selectedStream.commodity} • <strong>Granularity:</strong> {selectedStream.temporal_granularity}
                    </p>
                  </div>
                  <div className="stream-badge-row">
                    <span className="eligibility-status-badge blocked">
                      {selectedStream.eligibility_verdict} ({selectedStream.passed_criteria_count} Passed / {selectedStream.failed_criteria_count} Failed)
                    </span>
                  </div>
                </div>

                {/* 7 Criteria Checklist Table */}
                <div className="table-wrapper">
                  <table className="data-table" aria-label="Eligibility criteria checklist table">
                    <thead>
                      <tr>
                        <th scope="col" style={{ width: '80px' }}>Criteria ID</th>
                        <th scope="col" style={{ width: '180px' }}>Requirement</th>
                        <th scope="col">Evidentiary Standard</th>
                        <th scope="col">Observed Dataset Evidence</th>
                        <th scope="col" style={{ width: '90px' }}>Status</th>
                        <th scope="col">Blocking Reason / Handling Policy</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedStream.criteria_checks.map((crit) => (
                        <tr key={crit.criteria_id}>
                          <td><code>{crit.criteria_id}</code></td>
                          <td><strong>{crit.criteria_name}</strong></td>
                          <td>{crit.required_standard}</td>
                          <td>{crit.current_evidence}</td>
                          <td>
                            <span className={`status-pill ${crit.passed ? 'pass' : 'fail'}`}>
                              {crit.passed ? 'PASS' : 'FAIL'}
                            </span>
                          </td>
                          <td>
                            {crit.blocking_reason ? (
                              <span className="blocking-text">{crit.blocking_reason}</span>
                            ) : (
                              <span className="pass-text">Requirement satisfied for this dimension</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Missing Prerequisites Box */}
                <div className="missing-prerequisites-box">
                  <h4>Missing Prerequisites Required Before Calculation:</h4>
                  <ul>
                    {selectedStream.missing_prerequisites.map((req, idx) => (
                      <li key={idx}>{req}</li>
                    ))}
                  </ul>
                  <div className="handling-policy-row">
                    <strong>Enforced Policy:</strong> <code>{selectedStream.handling_policy}</code>
                  </div>
                </div>
              </div>
            )}
          </div>
        </>
      ) : (
        /* Strictly Segregated Synthetic Counterfactual Lab */
        <div className="synthetic-lab-wrapper">
          <div className="synthetic-watermark-banner" role="alert">
            <span className="watermark-badge">⚠️ SYNTHETIC DEMONSTRATION ONLY</span>
            <p className="watermark-text">
              <strong>STRICT ISOLATION NOTICE:</strong> The metrics below are 100% synthetically generated to illustrate how a seasonal prediction
              band would flag an arrival dip if continuous daily grain data were present. Under AGENTS.md Rule 4 & 5, this scenario is strictly
              segregated and never merged into official Punjab supply statistics.
            </p>
          </div>

          {syntheticData && (
            <>
              {/* Scenario Context Card */}
              <div className="filter-card">
                <div className="scenario-meta">
                  <h3>{syntheticData.title}</h3>
                  <p>
                    <strong>Catchment:</strong> {syntheticData.market_context.district} • <strong>Anonymized Mandi:</strong> {syntheticData.market_context.hypothetical_market}
                  </p>
                  <p>
                    <strong>Baseline Algorithm:</strong> {syntheticData.methodology.model_name} ({syntheticData.methodology.model_version})
                  </p>
                  <p>
                    <strong>Detection Rule:</strong> {syntheticData.methodology.investigation_prompt_threshold}
                  </p>
                </div>
                <div className="disposition-pill">
                  <span>DISPOSITION: {syntheticData.methodology.candidate_disposition}</span>
                </div>
              </div>

              {/* Synthetic Simulation Table */}
              <div className="table-card">
                <div className="table-header">
                  <div>
                    <h2 className="table-title">Simulated Daily Observations & Residuals (October 2026)</h2>
                    <span className="table-note">Demonstration of ±1.96 IQR seasonal prediction band</span>
                  </div>
                </div>

                <div className="table-wrapper">
                  <table className="data-table" aria-label="Synthetic counterfactual simulation table">
                    <thead>
                      <tr>
                        <th scope="col">Date</th>
                        <th scope="col" style={{ textAlign: 'right' }}>Expected Median (Qtl)</th>
                        <th scope="col" style={{ textAlign: 'right' }}>95% Lower Band</th>
                        <th scope="col" style={{ textAlign: 'right' }}>95% Upper Band</th>
                        <th scope="col" style={{ textAlign: 'right' }}>Simulated Observed (Qtl)</th>
                        <th scope="col" style={{ textAlign: 'right' }}>Residual (%)</th>
                        <th scope="col">Status Disposition</th>
                      </tr>
                    </thead>
                    <tbody>
                      {syntheticData.time_series.map((row) => (
                        <tr key={row.date} className={row.is_anomaly_candidate ? 'highlighted-row' : ''}>
                          <td><code>{row.date}</code></td>
                          <td style={{ textAlign: 'right' }}>{row.expected_median_qtl.toLocaleString()}</td>
                          <td style={{ textAlign: 'right' }}>{row.lower_bound_95_qtl.toLocaleString()}</td>
                          <td style={{ textAlign: 'right' }}>{row.upper_bound_95_qtl.toLocaleString()}</td>
                          <td style={{ textAlign: 'right', fontWeight: 700 }}>
                            {row.observed_arrival_qtl.toLocaleString()}
                          </td>
                          <td style={{ textAlign: 'right', color: row.residual_pct < -30 ? '#f87171' : 'inherit' }}>
                            {row.residual_pct.toFixed(1)}%
                          </td>
                          <td>
                            <span className={`status-pill ${row.is_anomaly_candidate ? 'fail' : 'pass'}`}>
                              {row.status_label}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Non-Hoarding Protocol Notice */}
                <div className="missing-prerequisites-box" style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}>
                  <h4 style={{ color: '#f87171' }}>Strict Non-Hoarding Protocol Enforced:</h4>
                  <ul>
                    {syntheticData.investigation_protocol.strictly_forbidden_actions.map((act, idx) => (
                      <li key={idx} style={{ color: 'var(--text-secondary)' }}>{act}</li>
                    ))}
                  </ul>
                  <p style={{ marginTop: 'var(--space-2)', fontSize: '0.75rem', color: 'var(--color-wheat-400)' }}>
                    <strong>Next Valid Investigation Step:</strong> {syntheticData.investigation_protocol.action_prompt}
                  </p>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default AnalyticsGateView;
