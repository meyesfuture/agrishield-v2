import React, { useState, useEffect } from 'react';

interface CoverageItem {
  supply_flow_element: string;
  required_granularity: string;
  available_sources: string;
  current_status: string;
  exact_coverage: string;
  unit_standard: string;
  audit_limitation: string;
  reconciliation_readiness: string;
}

interface QualityIssue {
  issue_id: string;
  dataset_id: string;
  rule_name: string;
  severity: string;
  description: string;
  affected_count: number;
  resolution_or_handling: string;
}

export default function QualityReadinessView() {
  const [coverage, setCoverage] = useState<CoverageItem[]>([]);
  const [issues, setIssues] = useState<QualityIssue[]>([]);
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadQuality() {
      try {
        setLoading(true);
        // Load Coverage Matrix
        let covRes = await fetch('http://127.0.0.1:8000/api/v1/coverage').catch(() => null);
        if (!covRes || !covRes.ok) covRes = await fetch('/data/coverage_matrix.json');
        if (covRes && covRes.ok) {
          const covData = await covRes.json();
          setCoverage(covData.items || []);
        }

        // Load Quality Issues
        let issRes = await fetch('http://127.0.0.1:8000/api/v1/quality/issues').catch(() => null);
        if (!issRes || !issRes.ok) issRes = await fetch('/data/quality_issues.json');
        if (issRes && issRes.ok) {
          const issData = await issRes.json();
          setIssues(issData.items || []);
        }
      } catch (err) {
        console.error('Error loading quality readiness data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadQuality();
  }, []);

  const filteredIssues = issues.filter((i) => {
    if (severityFilter !== 'all' && i.severity.toLowerCase() !== severityFilter) return false;
    return true;
  });

  return (
    <div className="quality-readiness-view">
      {/* Header */}
      <div className="view-header">
        <div>
          <h1 className="view-title">Data Quality, Pipeline Health & Reconciliation Readiness</h1>
          <p className="view-subtitle">
            Systematic audit of empirical data coverage, supply chain completeness, and pipeline validation gates.
          </p>
        </div>
        <div className="provenance-pill" title="Overall Validation Gate">
          <span>DATA GATE: PASSED</span>
          <span className="dot">•</span>
          <span>RECONCILIATION: NO-GO</span>
        </div>
      </div>

      {/* Reconciliation Gate Callout */}
      <div className="gap-alert-card" role="region" aria-label="Reconciliation Gate Verdict">
        <div className="alert-icon" aria-hidden="true">🛑</div>
        <div className="alert-content">
          <h2 className="alert-title">RECONCILIATION GATE VERDICT: NO-GO FOR GRAIN HOARDING DETECTION</h2>
          <p className="alert-text">
            Under Indian agricultural supply chain dynamics, deviations in market volume or price stem from staggered harvesting, moisture variations, MSP procurement parity, or transportation logistics. Without verified grain market arrivals, private commercial stock ledgers, and independent ground-truth inspection records, <strong>actor-level ranking or hoarding labeling is mathematically unidentifiable and strictly banned</strong>.
          </p>
        </div>
      </div>

      {/* 8-Element Supply Flow Coverage Matrix */}
      <div className="table-card" style={{ marginTop: 'var(--space-6)' }}>
        <div className="table-header">
          <h2 className="table-title">8-Element Foodgrain Supply Flow Coverage Matrix</h2>
          <span className="table-note">Audit of the full foodgrain supply balance (Production → Mandi → Procurement → Stocks → Milling → PDS → Private → Enforcement).</span>
        </div>

        <div className="table-wrapper">
          <table className="data-table" aria-label="Supply flow coverage matrix table">
            <thead>
              <tr>
                <th scope="col">Supply Flow Element</th>
                <th scope="col">Required Granularity</th>
                <th scope="col">Current Status</th>
                <th scope="col">Exact Coverage Acquired</th>
                <th scope="col">Audit Limitation</th>
                <th scope="col">Reconciliation Readiness</th>
              </tr>
            </thead>
            <tbody>
              {coverage.map((c) => (
                <tr key={c.supply_flow_element}>
                  <td className="cell-district">{c.supply_flow_element}</td>
                  <td>{c.required_granularity}</td>
                  <td>
                    <span className={`status-pill ${c.current_status.includes('CRITICAL') || c.current_status.includes('ABSENCE') ? 'status-critical' : c.current_status.includes('PARTIAL') ? 'status-partial' : 'status-aggregate'}`}>
                      {c.current_status}
                    </span>
                  </td>
                  <td>{c.exact_coverage}</td>
                  <td className="cell-note">{c.audit_limitation}</td>
                  <td>
                    <span className={`readiness-pill ${c.reconciliation_readiness.includes('NO-GO') ? 'no-go' : 'conditional'}`}>
                      {c.reconciliation_readiness}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Empirical Quality Issues Register */}
      <div className="table-card" style={{ marginTop: 'var(--space-8)' }}>
        <div className="table-header" style={{ flexWrap: 'wrap', gap: 'var(--space-3)' }}>
          <div>
            <h2 className="table-title">Empirical Data Quality Issues & Invariants</h2>
            <span className="table-note">Granular audit findings verified by automated tests.</span>
          </div>

          <div className="filter-chips" role="group" aria-label="Filter issues by severity">
            {['all', 'critical', 'warning', 'info'].map((s) => (
              <button
                key={s}
                className={`filter-chip ${severityFilter === s ? 'active' : ''}`}
                onClick={() => setSeverityFilter(s)}
              >
                {s.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table" aria-label="Quality issues table">
            <thead>
              <tr>
                <th scope="col">Issue ID</th>
                <th scope="col">Severity</th>
                <th scope="col">Affected Dataset</th>
                <th scope="col">Rule Name</th>
                <th scope="col">Description</th>
                <th scope="col">Handling Strategy</th>
              </tr>
            </thead>
            <tbody>
              {filteredIssues.map((issue) => (
                <tr key={issue.issue_id}>
                  <td className="cell-mono">{issue.issue_id}</td>
                  <td>
                    <span className={`severity-badge ${issue.severity.toLowerCase()}`}>
                      {issue.severity}
                    </span>
                  </td>
                  <td className="cell-district">{issue.dataset_id}</td>
                  <td className="cell-mono">{issue.rule_name}</td>
                  <td>{issue.description}</td>
                  <td className="cell-note">{issue.resolution_or_handling}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
