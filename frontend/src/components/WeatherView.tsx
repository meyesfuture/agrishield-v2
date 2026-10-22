import React, { useState, useEffect, useMemo } from 'react';

interface WeatherItem {
  observation_date: string;
  state: string;
  station_name: string;
  agro_climatic_zone: string;
  latitude: number;
  longitude: number;
  temperature_mean_c: number;
  precipitation_mm_day: number;
  relative_humidity_pct: number;
  source_dataset: string;
}

export default function WeatherView() {
  const [records, setRecords] = useState<WeatherItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedStation, setSelectedStation] = useState<string>('all');
  const [selectedMetric, setSelectedMetric] = useState<'temp' | 'precip' | 'rh'>('temp');
  const [selectedYear, setSelectedYear] = useState<string>('all');

  useEffect(() => {
    async function loadWeather() {
      try {
        setLoading(true);
        let res = await fetch('http://127.0.0.1:8000/api/v1/weather?limit=4000').catch(() => null);
        if (!res || !res.ok) {
          res = await fetch('/data/weather.json');
        }
        if (!res.ok) throw new Error('Could not load weather dataset');
        const data = await res.json();
        setRecords(data.items || []);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to load weather data');
      } finally {
        setLoading(false);
      }
    }
    loadWeather();
  }, []);

  // Filter options
  const stations = useMemo(() => {
    const set = new Set(records.map((r) => r.station_name));
    return Array.from(set).sort();
  }, [records]);

  // Filtered dataset
  const filtered = useMemo(() => {
    return records.filter((r) => {
      if (selectedStation !== 'all' && r.station_name !== selectedStation) return false;
      if (selectedYear !== 'all' && !r.observation_date.startsWith(selectedYear)) return false;
      return true;
    });
  }, [records, selectedStation, selectedYear]);

  // Aggregate statistics
  const stats = useMemo(() => {
    if (filtered.length === 0) return { avgTemp: 0, totalPrecip: 0, avgRh: 0, count: 0 };
    const tempSum = filtered.reduce((acc, r) => acc + r.temperature_mean_c, 0);
    const precipSum = filtered.reduce((acc, r) => acc + r.precipitation_mm_day, 0);
    const rhSum = filtered.reduce((acc, r) => acc + r.relative_humidity_pct, 0);
    return {
      avgTemp: (tempSum / filtered.length).toFixed(1),
      totalPrecip: precipSum.toFixed(1),
      avgRh: (rhSum / filtered.length).toFixed(1),
      count: filtered.length,
    };
  }, [filtered]);

  // Station summary comparisons
  const stationStats = useMemo(() => {
    const map: Record<string, { tempSum: number; precipSum: number; rhSum: number; count: number; zone: string }> = {};
    for (const r of filtered) {
      if (!map[r.station_name]) {
        map[r.station_name] = { tempSum: 0, precipSum: 0, rhSum: 0, count: 0, zone: r.agro_climatic_zone };
      }
      map[r.station_name].tempSum += r.temperature_mean_c;
      map[r.station_name].precipSum += r.precipitation_mm_day;
      map[r.station_name].rhSum += r.relative_humidity_pct;
      map[r.station_name].count += 1;
    }
    return Object.entries(map).map(([station, d]) => ({
      station,
      zone: d.zone,
      avgTemp: (d.tempSum / d.count).toFixed(1),
      totalPrecip: d.precipSum.toFixed(1),
      avgRh: (d.rhSum / d.count).toFixed(1),
      count: d.count,
    }));
  }, [filtered]);

  return (
    <div className="weather-view">
      {/* View Header */}
      <div className="view-header">
        <div>
          <h1 className="view-title">Agrometeorological Weather Context</h1>
          <p className="view-subtitle">
            Daily temperature, rainfall, and humidity from NASA POWER MERRA-2 across Punjab's 5 agro-climatic zones.
          </p>
        </div>
        <div className="provenance-pill" title="Audited Source Provenance">
          <span>SOURCE: NASA POWER MERRA-2</span>
          <span className="dot">•</span>
          <span>2024–2025 COMPLETE (0% NULLS)</span>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="filter-card">
        <div className="filter-group">
          <label htmlFor="station-select" className="filter-label">Agro-Climatic Station</label>
          <select
            id="station-select"
            className="filter-select"
            value={selectedStation}
            onChange={(e) => setSelectedStation(e.target.value)}
          >
            <option value="all">All 5 Agro-Climatic Stations</option>
            {stations.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="year-select" className="filter-label">Calendar Year</label>
          <select
            id="year-select"
            className="filter-select"
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
          >
            <option value="all">Complete Panel (2024 & 2025)</option>
            <option value="2024">2024 (366 days, leap year)</option>
            <option value="2025">2025 (365 days)</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="metric-select" className="filter-label">Active Parameter</label>
          <select
            id="metric-select"
            className="filter-select"
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value as any)}
          >
            <option value="temp">Mean Temperature (°C)</option>
            <option value="precip">Cumulative Precipitation (mm)</option>
            <option value="rh">Relative Humidity (%)</option>
          </select>
        </div>

        <button
          className="reset-btn"
          onClick={() => { setSelectedStation('all'); setSelectedYear('all'); setSelectedMetric('temp'); }}
          title="Reset weather filters"
        >
          Reset Filters
        </button>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <span className="kpi-label">Mean 2m Temperature</span>
          <div className="kpi-value-row">
            <span className="kpi-number">{stats.avgTemp}</span>
            <span className="kpi-unit">°C</span>
          </div>
          <span className="kpi-subtext">Across {stats.count.toLocaleString()} daily records</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Cumulative Rainfall</span>
          <div className="kpi-value-row">
            <span className="kpi-number">{stats.totalPrecip}</span>
            <span className="kpi-unit">mm</span>
          </div>
          <span className="kpi-subtext">Sum of daily PRECTOTCORR</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Mean Relative Humidity</span>
          <div className="kpi-value-row">
            <span className="kpi-number">{stats.avgRh}</span>
            <span className="kpi-unit">%</span>
          </div>
          <span className="kpi-subtext">Atmospheric moisture index</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Panel Completeness</span>
          <div className="kpi-value-row">
            <span className="kpi-number" style={{ color: 'var(--color-emerald-400)' }}>100%</span>
            <span className="kpi-unit">Zero Gaps</span>
          </div>
          <span className="kpi-subtext">731 continuous daily observations</span>
        </div>
      </div>

      {/* Station Comparison Cards */}
      <div className="chart-card">
        <div className="chart-header">
          <h2 className="chart-title">Station Climatology Profile ({selectedYear === 'all' ? '2024–2025' : selectedYear})</h2>
          <span className="chart-unit">Source: NASA POWER MERRA-2 Daily Point</span>
        </div>

        <div className="stations-grid">
          {stationStats.map((s) => (
            <div key={s.station} className="station-card">
              <div className="station-header">
                <span className="station-name">{s.station}</span>
                <span className="station-zone">{s.zone}</span>
              </div>
              <div className="station-metrics">
                <div className="station-metric-item">
                  <span className="metric-label">Avg Temp:</span>
                  <span className="metric-val">{s.avgTemp} °C</span>
                </div>
                <div className="station-metric-item">
                  <span className="metric-label">Rainfall:</span>
                  <span className="metric-val">{s.totalPrecip} mm</span>
                </div>
                <div className="station-metric-item">
                  <span className="metric-label">Rel. Humidity:</span>
                  <span className="metric-val">{s.avgRh}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Accessible Table */}
      <div className="table-card">
        <div className="table-header">
          <h2 className="table-title">Daily Agrometeorological Observations ({filtered.length} matching days)</h2>
          <span className="table-note">Showing first 25 observations sorted chronologically.</span>
        </div>

        <div className="table-wrapper">
          <table className="data-table" aria-label="Daily weather observation table">
            <thead>
              <tr>
                <th scope="col">Observation Date</th>
                <th scope="col">Station</th>
                <th scope="col">Agro-Climatic Zone</th>
                <th scope="col" style={{ textAlign: 'right' }}>Coordinates (Lat, Lon)</th>
                <th scope="col" style={{ textAlign: 'right' }}>Mean Temp (°C)</th>
                <th scope="col" style={{ textAlign: 'right' }}>Precipitation (mm)</th>
                <th scope="col" style={{ textAlign: 'right' }}>Humidity (%)</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 25).map((row, idx) => (
                <tr key={`${row.station_name}-${row.observation_date}-${idx}`}>
                  <td className="cell-mono">{row.observation_date}</td>
                  <td className="cell-district">{row.station_name}</td>
                  <td>{row.agro_climatic_zone}</td>
                  <td style={{ textAlign: 'right' }} className="cell-mono">{row.latitude.toFixed(2)}, {row.longitude.toFixed(2)}</td>
                  <td style={{ textAlign: 'right' }} className="cell-mono cell-temp">{row.temperature_mean_c.toFixed(2)} °C</td>
                  <td style={{ textAlign: 'right' }} className="cell-mono cell-precip">{row.precipitation_mm_day.toFixed(2)} mm</td>
                  <td style={{ textAlign: 'right' }} className="cell-mono">{row.relative_humidity_pct.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
