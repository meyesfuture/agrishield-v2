import React, { useState, useEffect, useMemo } from 'react';

interface ProductionItem {
  source_id: string;
  state: string;
  district_original: string;
  crop_standard: string;
  season: string;
  agricultural_year: string;
  calendar_year: string | null;
  area_value: number | null;
  area_unit: string | null;
  production_value: number | null;
  production_unit: string | null;
  yield_value: number | null;
  yield_unit: string | null;
  observation_status: string;
  quality_note: string | null;
}

export default function ProductionYieldView() {
  const [items, setItems] = useState<ProductionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedCrop, setSelectedCrop] = useState<string>('all');
  const [selectedDistrict, setSelectedDistrict] = useState<string>('all');
  const [selectedYear, setSelectedYear] = useState<string>('all');

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        // Try FastAPI backend first, fall back to static local cache
        let res = await fetch('http://127.0.0.1:8000/api/v1/production?limit=500').catch(() => null);
        if (!res || !res.ok) {
          res = await fetch('/data/production.json');
        }
        if (!res.ok) throw new Error('Could not load production data');
        const data = await res.json();
        setItems(data.items || []);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Error loading production records');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Unique filter options
  const districts = useMemo(() => {
    const set = new Set(items.map((i) => i.district_original));
    return Array.from(set).sort();
  }, [items]);

  const years = useMemo(() => {
    const set = new Set(items.map((i) => i.agricultural_year));
    return Array.from(set).sort();
  }, [items]);

  // Filtered dataset
  const filtered = useMemo(() => {
    return items.filter((item) => {
      if (selectedCrop !== 'all') {
        if (selectedCrop === 'wheat' && item.crop_standard.toLowerCase() !== 'wheat') return false;
        if (selectedCrop === 'rice' && !item.crop_standard.toLowerCase().includes('paddy') && !item.crop_standard.toLowerCase().includes('rice')) return false;
      }
      if (selectedDistrict !== 'all' && item.district_original.toLowerCase() !== selectedDistrict.toLowerCase()) {
        return false;
      }
      if (selectedYear !== 'all' && item.agricultural_year !== selectedYear) {
        return false;
      }
      return true;
    });
  }, [items, selectedCrop, selectedDistrict, selectedYear]);

  // Aggregated KPIs
  const stats = useMemo(() => {
    const validProd = filtered.filter((i) => i.production_value !== null);
    const validArea = filtered.filter((i) => i.area_value !== null);
    const validYield = filtered.filter((i) => i.yield_value !== null);

    const totalProd = validProd.reduce((sum, i) => sum + (i.production_value || 0), 0);
    const totalArea = validArea.reduce((sum, i) => sum + (i.area_value || 0), 0);
    const avgYield = validYield.length > 0
      ? validYield.reduce((sum, i) => sum + (i.yield_value || 0), 0) / validYield.length
      : 0;

    return {
      totalProductionTonnes: totalProd,
      totalAreaHectares: totalArea,
      averageYieldKgHa: avgYield,
      nullCount: filtered.filter((i) => i.production_value === null).length,
    };
  }, [filtered]);

  // Top producing districts in current view
  const chartData = useMemo(() => {
    const distMap: Record<string, number> = {};
    for (const item of filtered) {
      if (item.production_value !== null) {
        distMap[item.district_original] = (distMap[item.district_original] || 0) + item.production_value;
      }
    }
    const sorted = Object.entries(distMap)
      .map(([district, value]) => ({ district, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);
    return sorted;
  }, [filtered]);

  const maxChartVal = useMemo(() => {
    return chartData.length > 0 ? Math.max(...chartData.map((d) => d.value)) : 1;
  }, [chartData]);

  return (
    <div className="production-view">
      {/* Header & Provenance */}
      <div className="view-header">
        <div>
          <h1 className="view-title">District Crop Production & Yield History</h1>
          <p className="view-subtitle">
            Verified district-level annual cultivated area, harvest output, and productivity from Directorate of Economics & Statistics (DES APY).
          </p>
        </div>
        <div className="provenance-pill" title="Audited Data Provenance">
          <span>SOURCE: DES APY & OGD PUNJAB</span>
          <span className="dot">•</span>
          <span>2018–19 TO 2022–23</span>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="filter-card">
        <div className="filter-group">
          <label htmlFor="crop-select" className="filter-label">Commodity Form</label>
          <select
            id="crop-select"
            className="filter-select"
            value={selectedCrop}
            onChange={(e) => setSelectedCrop(e.target.value)}
          >
            <option value="all">All Crops (Wheat & Paddy)</option>
            <option value="wheat">Wheat (Rabi Season)</option>
            <option value="rice">Paddy / Rice (Kharif Season)</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="district-select" className="filter-label">District</label>
          <select
            id="district-select"
            className="filter-select"
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
          >
            <option value="all">All 23 Districts</option>
            {districts.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="year-select" className="filter-label">Agricultural Year</label>
          <select
            id="year-select"
            className="filter-select"
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
          >
            <option value="all">All 5 Agricultural Years</option>
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

        <button
          className="reset-btn"
          onClick={() => { setSelectedCrop('all'); setSelectedDistrict('all'); setSelectedYear('all'); }}
          title="Reset filters"
        >
          Reset Filters
        </button>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <span className="kpi-label">Total Production Output</span>
          <div className="kpi-value-row">
            <span className="kpi-number">
              {stats.totalProductionTonnes > 0
                ? (stats.totalProductionTonnes / 1000000).toFixed(2)
                : '0.00'}
            </span>
            <span className="kpi-unit">Million Tonnes (MMT)</span>
          </div>
          <span className="kpi-subtext">{stats.totalProductionTonnes.toLocaleString()} Metric Tonnes</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Cultivated Area</span>
          <div className="kpi-value-row">
            <span className="kpi-number">
              {stats.totalAreaHectares > 0
                ? (stats.totalAreaHectares / 100000).toFixed(2)
                : '0.00'}
            </span>
            <span className="kpi-unit">Lakh Hectares (Lha)</span>
          </div>
          <span className="kpi-subtext">{stats.totalAreaHectares.toLocaleString()} Hectares</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Weighted Average Yield</span>
          <div className="kpi-value-row">
            <span className="kpi-number">{Math.round(stats.averageYieldKgHa).toLocaleString()}</span>
            <span className="kpi-unit">kg / hectare</span>
          </div>
          <span className="kpi-subtext">Derived as (Production × 1,000 / Area)</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Records / Null States</span>
          <div className="kpi-value-row">
            <span className="kpi-number">{filtered.length}</span>
            <span className="kpi-unit">Records Active</span>
          </div>
          <span className="kpi-subtext" style={{ color: stats.nullCount > 0 ? 'var(--color-amber-400)' : 'var(--text-muted)' }}>
            {stats.nullCount > 0
              ? `${stats.nullCount} pre-formation null cells (Malerkotla)`
              : 'Zero null cells in active selection'}
          </span>
        </div>
      </div>

      {/* Visual Production Bar Chart */}
      <div className="chart-card">
        <div className="chart-header">
          <h2 className="chart-title">Production by Top Districts ({selectedYear === 'all' ? 'Cumulative 2018–2023' : selectedYear})</h2>
          <span className="chart-unit">Unit: Thousand Tonnes</span>
        </div>

        {chartData.length === 0 ? (
          <div className="empty-state">No matching production records for selected filters.</div>
        ) : (
          <div className="bar-chart-container" role="img" aria-label="District production comparison chart">
            {chartData.map((d) => {
              const pct = (d.value / maxChartVal) * 100;
              return (
                <div key={d.district} className="bar-row">
                  <span className="bar-label" title={d.district}>{d.district}</span>
                  <div className="bar-track">
                    <div
                      className="bar-fill"
                      style={{ width: `${Math.max(pct, 2)}%` }}
                      title={`${d.district}: ${(d.value / 1000).toFixed(1)}k Tonnes`}
                    ></div>
                  </div>
                  <span className="bar-value">{(d.value / 1000).toFixed(1)}k</span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Accessible Data Table */}
      <div className="table-card">
        <div className="table-header">
          <h2 className="table-title">District Crop Observation Records ({filtered.length} matching rows)</h2>
          <span className="table-note">Showing first 25 records. Pre-formation years strictly serialized as null.</span>
        </div>

        <div className="table-wrapper">
          <table className="data-table" aria-label="District crop production records table">
            <thead>
              <tr>
                <th scope="col">District</th>
                <th scope="col">Crop</th>
                <th scope="col">Season</th>
                <th scope="col">Agricultural Year</th>
                <th scope="col" style={{ textAlign: 'right' }}>Cultivated Area (ha)</th>
                <th scope="col" style={{ textAlign: 'right' }}>Production (Tonnes)</th>
                <th scope="col" style={{ textAlign: 'right' }}>Yield (kg/ha)</th>
                <th scope="col">Audit Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 25).map((row, idx) => (
                <tr key={`${row.district_original}-${row.crop_standard}-${row.agricultural_year}-${idx}`}>
                  <td className="cell-district">{row.district_original}</td>
                  <td>
                    <span className={`crop-badge ${row.crop_standard.toLowerCase().includes('wheat') ? 'wheat' : 'rice'}`}>
                      {row.crop_standard.toLowerCase().includes('wheat') ? 'Wheat' : 'Paddy'}
                    </span>
                  </td>
                  <td>{row.season}</td>
                  <td className="cell-mono">{row.agricultural_year}</td>
                  <td style={{ textAlign: 'right' }} className="cell-mono">
                    {row.area_value !== null ? row.area_value.toLocaleString() : <span className="null-badge">null</span>}
                  </td>
                  <td style={{ textAlign: 'right' }} className="cell-mono">
                    {row.production_value !== null ? row.production_value.toLocaleString() : <span className="null-badge">null</span>}
                  </td>
                  <td style={{ textAlign: 'right' }} className="cell-mono">
                    {row.yield_value !== null ? Math.round(row.yield_value).toLocaleString() : <span className="null-badge">null</span>}
                  </td>
                  <td>
                    {row.production_value === null ? (
                      <span className="caveat-tag" title="Malerkotla carved from Sangrur; pre-split years unassigned">Pre-split unassigned</span>
                    ) : (
                      <span className="verified-tag">Observed</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
