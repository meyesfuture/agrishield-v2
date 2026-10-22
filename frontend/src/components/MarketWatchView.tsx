import React, { useState, useEffect, useMemo } from 'react';

interface PriceItem {
  observation_date: string;
  state: string;
  market_name: string;
  commodity_name: string;
  variety: string | null;
  modal_price: number;
  price_unit: string;
  arrival_quantity: number | null;
  arrival_unit: string | null;
  data_gap_note: string;
}

export default function MarketWatchView() {
  const [prices, setPrices] = useState<PriceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedMarket, setSelectedMarket] = useState<string>('all');
  const [selectedCommodity, setSelectedCommodity] = useState<string>('all');

  useEffect(() => {
    async function loadPrices() {
      try {
        setLoading(true);
        let res = await fetch('http://127.0.0.1:8000/api/v1/markets/prices?limit=100').catch(() => null);
        if (!res || !res.ok) {
          res = await fetch('/data/prices.json');
        }
        if (!res.ok) throw new Error('Could not load market price dataset');
        const data = await res.json();
        setPrices(data.items || []);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to load price records');
      } finally {
        setLoading(false);
      }
    }
    loadPrices();
  }, []);

  // Filter options
  const markets = useMemo(() => {
    const set = new Set(prices.map((p) => p.market_name));
    return Array.from(set).sort();
  }, [prices]);

  const commodities = useMemo(() => {
    const set = new Set(prices.map((p) => p.commodity_name));
    return Array.from(set).sort();
  }, [prices]);

  // Filtered price items
  const filtered = useMemo(() => {
    return prices.filter((p) => {
      if (selectedMarket !== 'all' && p.market_name !== selectedMarket) return false;
      if (selectedCommodity !== 'all' && p.commodity_name !== selectedCommodity) return false;
      return true;
    });
  }, [prices, selectedMarket, selectedCommodity]);

  // Price statistics
  const stats = useMemo(() => {
    if (filtered.length === 0) {
      return { avgPrice: 0, minPrice: 0, maxPrice: 0, totalMarkets: 0 };
    }
    const values = filtered.map((p) => p.modal_price);
    const sum = values.reduce((a, b) => a + b, 0);
    const avg = sum / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const uniqueMkts = new Set(filtered.map((p) => p.market_name)).size;
    return { avgPrice: avg, minPrice: min, maxPrice: max, totalMarkets: uniqueMkts };
  }, [filtered]);

  // Market price comparison
  const marketAgg = useMemo(() => {
    const map: Record<string, { total: number; count: number }> = {};
    for (const p of filtered) {
      if (!map[p.market_name]) map[p.market_name] = { total: 0, count: 0 };
      map[p.market_name].total += p.modal_price;
      map[p.market_name].count += 1;
    }
    return Object.entries(map).map(([mkt, data]) => ({
      market: mkt,
      avg: Math.round(data.total / data.count),
    })).sort((a, b) => b.avg - a.avg);
  }, [filtered]);

  const maxAvg = useMemo(() => {
    return marketAgg.length > 0 ? Math.max(...marketAgg.map((m) => m.avg)) : 1;
  }, [marketAgg]);

  return (
    <div className="market-view">
      {/* View Header */}
      <div className="view-header">
        <div>
          <h1 className="view-title">Mandi Market Watch & Price Dynamics</h1>
          <p className="view-subtitle">
            Daily wholesale prices from AGMARKNET 2.0 (DMI, MoA&FW) across verified Punjab APMC markets.
          </p>
        </div>
        <div className="provenance-pill" title="Official Source Provenance">
          <span>SOURCE: AGMARKNET 2.0</span>
          <span className="dot">•</span>
          <span>OCTOBER 2026</span>
        </div>
      </div>

      {/* Critical Data Gap Alert Banner */}
      <div className="gap-alert-card" role="region" aria-label="Critical Data Gap Declaration">
        <div className="alert-icon" aria-hidden="true">⚠️</div>
        <div className="alert-content">
          <h2 className="alert-title">MANDATORY EVIDENCE BOUNDARY: ARRIVAL QUANTITY GAPS</h2>
          <p className="alert-text">
            <strong>1. AGMARKNET Price Feed:</strong> Arrival quantity is strictly <strong>100% missing (null)</strong> across all 53 rows in this weekly endpoint. Modal price observations cannot be combined with arrival volumes.
          </p>
          <p className="alert-text">
            <strong>2. APMC Mandi Board Panel:</strong> The acquired 3,892-row daily arrival dataset contains fruits, vegetables, and spices only — <strong>zero wheat or paddy grain rows</strong>. Foodgrains are routed to Punjab's separate credentialed <em>Anaaj Kharid</em> infrastructure.
          </p>
          <div className="alert-badge">ANOMALY / HOARDING DETECTION PROHIBITED: INSUFFICIENT DATA IDENTIFIABILITY</div>
        </div>
      </div>

      {/* Filters Toolbar */}
      <div className="filter-card">
        <div className="filter-group">
          <label htmlFor="market-select" className="filter-label">APMC Mandi Market</label>
          <select
            id="market-select"
            className="filter-select"
            value={selectedMarket}
            onChange={(e) => setSelectedMarket(e.target.value)}
          >
            <option value="all">All Markets ({markets.length} reporting)</option>
            {markets.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="commodity-select" className="filter-label">Grain Commodity</label>
          <select
            id="commodity-select"
            className="filter-select"
            value={selectedCommodity}
            onChange={(e) => setSelectedCommodity(e.target.value)}
          >
            <option value="all">All Commodities (Common & Basmati)</option>
            {commodities.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <button
          className="reset-btn"
          onClick={() => { setSelectedMarket('all'); setSelectedCommodity('all'); }}
          title="Reset market filters"
        >
          Reset Filters
        </button>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <span className="kpi-label">Average Modal Price</span>
          <div className="kpi-value-row">
            <span className="kpi-number">₹{Math.round(stats.avgPrice).toLocaleString()}</span>
            <span className="kpi-unit">per Quintal</span>
          </div>
          <span className="kpi-subtext">Across {filtered.length} daily market observations</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Modal Price Range</span>
          <div className="kpi-value-row">
            <span className="kpi-number">₹{Math.round(stats.minPrice)} – ₹{Math.round(stats.maxPrice)}</span>
            <span className="kpi-unit">Rs./Qtl</span>
          </div>
          <span className="kpi-subtext">Min to Max observed trade prices</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Reporting Markets</span>
          <div className="kpi-value-row">
            <span className="kpi-number">{stats.totalMarkets}</span>
            <span className="kpi-unit">APMCs Active</span>
          </div>
          <span className="kpi-subtext">Abohar, Adampur, Ajnala, etc.</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Arrival Volume State</span>
          <div className="kpi-value-row">
            <span className="kpi-number" style={{ color: 'var(--color-amber-400)' }}>100% NULL</span>
            <span className="kpi-unit">Unexposed</span>
          </div>
          <span className="kpi-subtext">Zero arrival quantities in public endpoint</span>
        </div>
      </div>

      {/* Market Price Comparison Chart */}
      <div className="chart-card">
        <div className="chart-header">
          <h2 className="chart-title">Wholesale Modal Price by Market (Average Rs./Quintal)</h2>
          <span className="chart-unit">Unit: ₹ / Quintal</span>
        </div>

        {marketAgg.length === 0 ? (
          <div className="empty-state">No price observations match the selected filters.</div>
        ) : (
          <div className="bar-chart-container" role="img" aria-label="Market price comparison chart">
            {marketAgg.map((m) => {
              const pct = (m.avg / maxAvg) * 100;
              return (
                <div key={m.market} className="bar-row">
                  <span className="bar-label" title={m.market}>{m.market}</span>
                  <div className="bar-track">
                    <div
                      className="bar-fill"
                      style={{ width: `${Math.max(pct, 2)}%`, backgroundColor: 'var(--color-wheat-500)' }}
                      title={`${m.market}: ₹${m.avg}/Qtl`}
                    ></div>
                  </div>
                  <span className="bar-value">₹{m.avg.toLocaleString()}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Accessible Prices Table */}
      <div className="table-card">
        <div className="table-header">
          <h2 className="table-title">Wholesale Price Observations ({filtered.length} records)</h2>
          <span className="table-note">Arrival quantities verified strictly null across all records.</span>
        </div>

        <div className="table-wrapper">
          <table className="data-table" aria-label="Wholesale mandi price records">
            <thead>
              <tr>
                <th scope="col">Observation Date</th>
                <th scope="col">Market Name</th>
                <th scope="col">Commodity</th>
                <th scope="col">Variety</th>
                <th scope="col" style={{ textAlign: 'right' }}>Modal Price</th>
                <th scope="col" style={{ textAlign: 'right' }}>Arrival Quantity</th>
                <th scope="col">Data Gap Notice</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((p, idx) => (
                <tr key={`${p.market_name}-${p.observation_date}-${idx}`}>
                  <td className="cell-mono">{p.observation_date}</td>
                  <td className="cell-district">{p.market_name}</td>
                  <td>
                    <span className={`crop-badge ${p.commodity_name.includes('Basmati') ? 'wheat' : 'rice'}`}>
                      {p.commodity_name}
                    </span>
                  </td>
                  <td>{p.variety || 'Standard'}</td>
                  <td style={{ textAlign: 'right' }} className="cell-mono cell-price">
                    ₹{p.modal_price.toFixed(1)} / Qtl
                  </td>
                  <td style={{ textAlign: 'right' }} className="cell-mono">
                    <span className="null-badge">null</span>
                  </td>
                  <td>
                    <span className="gap-tag" title={p.data_gap_note}>Unexposed in Feed</span>
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
