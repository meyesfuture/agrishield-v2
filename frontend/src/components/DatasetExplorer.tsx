import React, { useState, useEffect, useMemo } from 'react';
import { StatusBadge } from './StatusBadge';

export interface DatasetItem {
  dataset_id: string;
  file_path: string;
  format: string;
  source_name: string;
  source_url: string;
  sha256: string;
  size_bytes: number;
  row_count: number;
  schema_columns: string;
  date_range: string;
  geography_level: string;
  geographic_coverage: string;
  commodity_coverage: string;
  units: string;
  retrieval_timestamp_utc: string;
  evidence_status: string;
  licensing_access_notes: string;
  caveats: string;
  last_validation_result: string;
}

export const DatasetExplorer: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeStatus, setActiveStatus] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedDataset, setSelectedDataset] = useState<DatasetItem | null>(null);
  const [dataSourceMode, setDataSourceMode] = useState<'API' | 'STATIC_FALLBACK'>('API');

  // Load datasets on mount
  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    setLoading(true);
    setError(null);
    try {
      // First attempt: live FastAPI backend
      const res = await fetch('http://127.0.0.1:8000/api/v1/datasets', {
        headers: { Accept: 'application/json' },
      });
      if (res.ok) {
        const data = await res.json();
        setDatasets(data.items || []);
        setDataSourceMode('API');
        setLoading(false);
        return;
      }
      throw new Error(`API returned HTTP ${res.status}`);
    } catch (apiErr) {
      // Fallback: local static Phase 1 catalog
      try {
        const fallbackRes = await fetch('/data/dataset_catalog.json');
        if (fallbackRes.ok) {
          const fallbackData = await fallbackRes.json();
          setDatasets(fallbackData);
          setDataSourceMode('STATIC_FALLBACK');
          setLoading(false);
          return;
        }
      } catch (fallbackErr) {
        setError('Failed to load dataset catalog from both backend API and static catalog.');
        setLoading(false);
      }
    }
  };

  // Status categories with counts
  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = { ALL: datasets.length };
    datasets.forEach((d) => {
      const s = (d.evidence_status || 'other').toUpperCase();
      counts[s] = (counts[s] || 0) + 1;
    });
    return counts;
  }, [datasets]);

  // Filtered dataset list
  const filteredDatasets = useMemo(() => {
    return datasets.filter((item) => {
      // Status filter
      if (activeStatus !== 'ALL') {
        if (item.evidence_status.toUpperCase() !== activeStatus) return false;
      }
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesId = item.dataset_id.toLowerCase().includes(q);
        const matchesSource = item.source_name.toLowerCase().includes(q);
        const matchesCommodity = item.commodity_coverage.toLowerCase().includes(q);
        const matchesGeo = item.geographic_coverage.toLowerCase().includes(q);
        const matchesCaveat = item.caveats.toLowerCase().includes(q);
        if (!matchesId && !matchesSource && !matchesCommodity && !matchesGeo && !matchesCaveat) {
          return false;
        }
      }
      return true;
    });
  }, [datasets, activeStatus, searchQuery]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Control Bar: Search and Status Filters */}
      <div
        style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--space-4)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-4)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
          <div style={{ flex: '1 1 300px', position: 'relative' }}>
            <input
              type="text"
              placeholder="Search datasets, commodities, APMCs, caveats..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Search datasets"
              style={{
                width: '100%',
                padding: '0.65rem 1rem',
                backgroundColor: 'var(--bg-canvas)',
                border: '1px solid var(--border-medium)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: 'var(--text-sm)',
              }}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
              Source Mode:
            </span>
            <span
              style={{
                fontSize: '0.7rem',
                fontWeight: 600,
                padding: '0.15rem 0.5rem',
                borderRadius: 'var(--radius-full)',
                backgroundColor: dataSourceMode === 'API' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                color: dataSourceMode === 'API' ? 'var(--color-emerald-400)' : 'var(--color-amber-400)',
                border: `1px solid ${dataSourceMode === 'API' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
              }}
            >
              {dataSourceMode === 'API' ? '● Live Backend API' : '○ Static Phase 1 Catalog'}
            </span>
          </div>
        </div>

        {/* Status Filter Chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }} role="tablist" aria-label="Filter by evidence status">
          {['ALL', 'OBSERVED', 'DERIVED', 'METADATA ONLY', 'BLOCKED', 'STALE', 'MISSING'].map((statusKey) => {
            const count = statusCounts[statusKey] || 0;
            const isSelected = activeStatus === statusKey;
            return (
              <button
                key={statusKey}
                onClick={() => setActiveStatus(statusKey)}
                role="tab"
                aria-selected={isSelected}
                style={{
                  background: isSelected ? 'var(--color-slate-700)' : 'transparent',
                  color: isSelected ? 'var(--color-wheat-400)' : 'var(--text-secondary)',
                  border: `1px solid ${isSelected ? 'var(--color-wheat-500)' : 'var(--border-subtle)'}`,
                  padding: '0.35rem 0.75rem',
                  borderRadius: 'var(--radius-full)',
                  fontSize: 'var(--text-xs)',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  transition: 'all var(--transition-fast)',
                }}
              >
                <span>{statusKey}</span>
                <span
                  style={{
                    fontSize: '0.65rem',
                    background: isSelected ? 'var(--color-wheat-500)' : 'rgba(255, 255, 255, 0.08)',
                    color: isSelected ? 'var(--color-slate-950)' : 'var(--text-muted)',
                    padding: '0.1rem 0.35rem',
                    borderRadius: 'var(--radius-full)',
                  }}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div style={{ textAlign: 'center', padding: 'var(--space-12)', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-2)' }}>Loading Verified Datasets...</div>
          <div style={{ fontSize: 'var(--text-xs)' }}>Inspecting catalog manifest and schema signatures</div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div
          style={{
            padding: 'var(--space-6)',
            backgroundColor: 'var(--status-missing-bg)',
            border: '1px solid var(--status-missing-border)',
            borderRadius: 'var(--radius-lg)',
            textAlign: 'center',
          }}
        >
          <div style={{ color: 'var(--color-crimson-400)', fontWeight: 600, marginBottom: 'var(--space-2)' }}>
            Catalog Retrieval Error
          </div>
          <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            {error}
          </div>
          <button
            onClick={fetchDatasets}
            style={{
              padding: '0.5rem 1rem',
              background: 'var(--color-crimson-500)',
              color: 'var(--color-white)',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && filteredDatasets.length === 0 && (
        <div
          style={{
            textAlign: 'center',
            padding: 'var(--space-12)',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
          }}
        >
          <div style={{ fontSize: 'var(--text-xl)', color: 'var(--text-secondary)', marginBottom: 'var(--space-2)' }}>
            No matching datasets found
          </div>
          <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginBottom: 'var(--space-4)' }}>
            Try clearing the search query or selecting "ALL" status category.
          </div>
          <button
            onClick={() => {
              setSearchQuery('');
              setActiveStatus('ALL');
            }}
            style={{
              padding: '0.4rem 0.9rem',
              background: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-medium)',
              color: 'var(--text-primary)',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer',
            }}
          >
            Reset Filters
          </button>
        </div>
      )}

      {/* Datasets Table */}
      {!loading && !error && filteredDatasets.length > 0 && (
        <div
          style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            overflowX: 'auto',
          }}
        >
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              textAlign: 'left',
              fontSize: 'var(--text-xs)',
            }}
          >
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-medium)', backgroundColor: 'var(--bg-surface-elevated)' }}>
                <th style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)', fontWeight: 600 }}>DATASET ID</th>
                <th style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)', fontWeight: 600 }}>STATUS</th>
                <th style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)', fontWeight: 600 }}>ROWS</th>
                <th style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)', fontWeight: 600 }}>COMMODITY COVERAGE</th>
                <th style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)', fontWeight: 600 }}>GEOGRAPHY</th>
                <th style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)', fontWeight: 600 }}>CHECKSUM (SHA-256)</th>
                <th style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)', fontWeight: 600, textAlign: 'right' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {filteredDatasets.map((item) => (
                <tr
                  key={item.dataset_id}
                  style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    transition: 'background var(--transition-fast)',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-surface-hover)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                >
                  <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    <div>{item.dataset_id}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 400 }}>{item.source_name}</div>
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <StatusBadge status={item.evidence_status} size="sm" />
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'var(--font-mono)' }}>
                    {item.row_count > 0 ? item.row_count.toLocaleString() : 'N/A'}
                  </td>
                  <td style={{ padding: '0.75rem 1rem', maxWidth: '240px', lineHeight: 1.4 }}>
                    {item.commodity_coverage}
                  </td>
                  <td style={{ padding: '0.75rem 1rem', maxWidth: '200px', lineHeight: 1.4 }}>
                    {item.geographic_coverage}
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {item.sha256.startsWith('N/A') ? item.sha256 : `${item.sha256.substring(0, 10)}...`}
                  </td>
                  <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                    <button
                      onClick={() => setSelectedDataset(item)}
                      style={{
                        padding: '0.35rem 0.75rem',
                        background: 'var(--bg-surface-elevated)',
                        border: '1px solid var(--border-medium)',
                        color: 'var(--color-wheat-400)',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        transition: 'all var(--transition-fast)',
                      }}
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Dataset Detail Modal / Drawer */}
      {selectedDataset && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 'var(--space-4)',
            zIndex: 999,
          }}
          onClick={() => setSelectedDataset(null)}
        >
          <div
            style={{
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-strong)',
              borderRadius: 'var(--radius-xl)',
              maxWidth: '680px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: 'var(--space-6)',
              boxShadow: var_shadow_lg,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-4)' }}>
              <div>
                <h3 id="modal-title" style={{ fontSize: 'var(--text-lg)', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 'var(--space-1)' }}>
                  {selectedDataset.dataset_id}
                </h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <StatusBadge status={selectedDataset.evidence_status} size="sm" />
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>Format: {selectedDataset.format}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedDataset(null)}
                aria-label="Close dialog"
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  fontSize: '1.25rem',
                  cursor: 'pointer',
                  padding: 'var(--space-1)',
                }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', fontSize: 'var(--text-xs)', lineHeight: 1.6 }}>
              {/* Caveats Box */}
              <div style={{ padding: 'var(--space-3)', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: 'var(--radius-md)' }}>
                <strong style={{ color: 'var(--color-amber-400)', display: 'block', marginBottom: '4px' }}>EVIDENCE CAVEAT & CONSTRAINTS:</strong>
                <span style={{ color: 'var(--text-primary)' }}>{selectedDataset.caveats}</span>
              </div>

              {/* Physical Properties */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)', display: 'block' }}>Physical File Path:</span>
                  <code style={{ color: 'var(--text-primary)', wordBreak: 'break-all' }}>{selectedDataset.file_path}</code>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)', display: 'block' }}>Row Count:</span>
                  <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{selectedDataset.row_count > 0 ? selectedDataset.row_count.toLocaleString() : 'N/A'}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)', display: 'block' }}>Date Range:</span>
                  <span style={{ color: 'var(--text-primary)' }}>{selectedDataset.date_range}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)', display: 'block' }}>Units:</span>
                  <span style={{ color: 'var(--text-primary)' }}>{selectedDataset.units}</span>
                </div>
              </div>

              {/* SHA-256 */}
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block' }}>SHA-256 Checksum:</span>
                <code style={{ color: 'var(--color-emerald-400)', wordBreak: 'break-all', fontSize: '0.7rem' }}>
                  {selectedDataset.sha256}
                </code>
              </div>

              {/* Schema Columns */}
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Schema / Columns:</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                  {selectedDataset.schema_columns.split(';').map((col, idx) => (
                    <span
                      key={idx}
                      style={{
                        background: 'var(--bg-surface-elevated)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '2px 6px',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.65rem',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      {col.trim()}
                    </span>
                  ))}
                </div>
              </div>

              {/* Licensing & Access Notes */}
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block' }}>Access & Licensing:</span>
                <span style={{ color: 'var(--text-secondary)' }}>{selectedDataset.licensing_access_notes}</span>
              </div>
            </div>

            <div style={{ marginTop: 'var(--space-6)', textAlign: 'right' }}>
              <button
                onClick={() => setSelectedDataset(null)}
                style={{
                  padding: '0.5rem 1.25rem',
                  background: 'var(--bg-surface-elevated)',
                  border: '1px solid var(--border-medium)',
                  color: 'var(--text-primary)',
                  borderRadius: 'var(--radius-md)',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const var_shadow_lg = '0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -4px rgba(0, 0, 0, 0.5)';
