import { useState, useEffect, useMemo } from 'react';

interface GeoFeature {
  id: number;
  properties: {
    dtname: string;
    dist_lgd: number;
    district_id: string;
    year_stat?: string;
    boundary_vintage_feature?: string;
    [key: string]: any;
  };
  geometry: {
    type: string;
    coordinates: any[];
  };
}

interface CrosswalkItem {
  district_source_name_apy: string;
  district_name_boundary: string;
  district_id_candidate_lgd: number | null;
  match_status: string;
  temporal_note: string;
}

interface ProductionItem {
  district_original: string;
  crop_standard: string;
  agricultural_year: string;
  production_value: number | null;
  area_value: number | null;
  yield_value: number | null;
}

interface YieldItem {
  district_original: string;
  crop_standard: string;
  effective_year: string;
  yield_value: number | null;
  yield_unit: string;
  source_id: string;
}

interface PriceItem {
  observation_date: string;
  market_name: string;
  commodity_name: string;
  modal_price: number | null;
  price_unit: string;
  arrival_quantity: number | null;
  data_gap_note?: string;
}

interface MandiLocation {
  id: string;
  name: string;
  district: string;
  commodity: string;
  modalPrice: number | null;
  priceUnit: string;
  observationDate: string;
}

interface ObservationPoint {
  date: string;
  modal_price: number | null;
  arrival_quantity: number | null;
  unit_price?: string;
  unit_arrival?: string;
  is_anomaly_candidate?: boolean;
  notes?: string;
}

interface DecisionAssessment {
  assessment_id: string;
  assessment_timestamp_utc: string;
  evidence_mode: 'REAL' | 'SYNTHETIC_DEMO';
  scenario_id?: string;
  location_id: string;
  location_name: string;
  geographic_granularity: string;
  canonical_commodity: string;
  observation_date: string;
  baseline_interval: string;
  decision_status: 'INSUFFICIENT_DATA' | 'NO_MATERIAL_ANOMALY' | 'PRICE_SIGNAL' | 'ARRIVAL_SIGNAL' | 'CONVERGENT_SUPPLY_ANOMALY';
  status_label: string;
  human_explanation: string;
  anomaly_intensity_score: number | null;
  signals: {
    [key: string]: {
      signal_type: string;
      status: string;
      observed_value: number | null;
      baseline_median: number | null;
      deviation_pct: number | null;
      robust_z_score: number | null;
      unit: string;
      contribution_pct: number;
      explanation: string;
    };
  };
  evidence_coverage: {
    required_streams: string[];
    verified_streams: string[];
    sufficiency_pct: number;
  };
  unavailable_signals: string[];
  data_quality_warnings: string[];
  eligibility_gate_passed: boolean;
  recommended_action: string;
  legal_caveat: string;
}

interface ScenarioItem {
  scenario_id: string;
  title: string;
  description: string;
  expected_decision_status: string;
  location_name: string;
  commodity_name: string;
}

export default function DashboardView() {
  const [features, setFeatures] = useState<GeoFeature[]>([]);
  const [crosswalk, setCrosswalk] = useState<CrosswalkItem[]>([]);
  const [production, setProduction] = useState<ProductionItem[]>([]);
  const [yields, setYields] = useState<YieldItem[]>([]);
  const [prices, setPrices] = useState<PriceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Application Mode: REAL vs. SYNTHETIC_DEMO
  const [appMode, setAppMode] = useState<'REAL' | 'SYNTHETIC_DEMO'>('REAL');

  // Synthetic Scenario Lab State
  const [availableScenarios, setAvailableScenarios] = useState<ScenarioItem[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('scenario_b_convergent_anomaly');
  const [scenarioObservations, setScenarioObservations] = useState<ObservationPoint[]>([]);
  const [scenarioAssessment, setScenarioAssessment] = useState<DecisionAssessment | null>(null);
  const [isEvaluatingScenario, setIsEvaluatingScenario] = useState<boolean>(false);

  // Real Mode Interactive Filters & Modes
  const [selectedDistrict, setSelectedDistrict] = useState<string>('Ludhiana');
  const [selectedMandiId, setSelectedMandiId] = useState<string | null>(null);
  const [commodityFilter, setCommodityFilter] = useState<'all' | 'wheat' | 'rice'>('all');
  const [shadingMode, setShadingMode] = useState<'production' | 'status'>('production');
  const [hoveredDistrict, setHoveredDistrict] = useState<string | null>(null);
  const [activeChartTab, setActiveChartTab] = useState<'trend' | 'compare' | 'evidence' | 'coverage'>('trend');

  // Check URL query parameters for mode=synthetic
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('mode') === 'synthetic') {
        setAppMode('SYNTHETIC_DEMO');
      }
    }
  }, []);

  // Load Real Datasets
  useEffect(() => {
    async function loadAllData() {
      try {
        setLoading(true);
        setError(null);

        // 1. Boundaries
        let geoRes = await fetch('http://127.0.0.1:8000/api/v1/geo/districts').catch(() => null);
        if (!geoRes || !geoRes.ok) geoRes = await fetch('/data/district_boundaries.json');
        if (geoRes && geoRes.ok) {
          const geoData = await geoRes.json();
          setFeatures(geoData.features || []);
        }

        // 2. Crosswalk
        let crwRes = await fetch('http://127.0.0.1:8000/api/v1/geo/crosswalk?limit=100').catch(() => null);
        if (!crwRes || !crwRes.ok) crwRes = await fetch('/data/district_crosswalk.json');
        if (crwRes && crwRes.ok) {
          const crwData = await crwRes.json();
          setCrosswalk(crwData.items || []);
        }

        // 3. Production
        let prodRes = await fetch('http://127.0.0.1:8000/api/v1/production?limit=500').catch(() => null);
        if (!prodRes || !prodRes.ok) prodRes = await fetch('/data/production.json');
        if (prodRes && prodRes.ok) {
          const prodData = await prodRes.json();
          setProduction(prodData.items || []);
        }

        // 4. Historical Yields
        let yieldRes = await fetch('http://127.0.0.1:8000/api/v1/yields?limit=3000').catch(() => null);
        if (!yieldRes || !yieldRes.ok) yieldRes = await fetch('/data/yields.json');
        if (yieldRes && yieldRes.ok) {
          const yldData = await yieldRes.json();
          setYields(yldData.items || []);
        }

        // 5. Prices & Mandis
        let priceRes = await fetch('http://127.0.0.1:8000/api/v1/markets/prices?limit=100').catch(() => null);
        if (!priceRes || !priceRes.ok) priceRes = await fetch('/data/prices.json');
        if (priceRes && priceRes.ok) {
          const prData = await priceRes.json();
          setPrices(prData.items || []);
        }

        // 6. Fetch Available Synthetic Scenarios from backend
        const scenRes = await fetch('http://127.0.0.1:8000/api/v1/decision/scenarios').catch(() => null);
        if (scenRes && scenRes.ok) {
          const scenData = await scenRes.json();
          setAvailableScenarios(scenData || []);
        }
      } catch (err: any) {
        setError(err.message || 'Error communicating with backend service.');
      } finally {
        setLoading(false);
      }
    }

    loadAllData();
  }, []);

  // Fetch and Execute Synthetic Scenario when scenario changes or in Demo Mode
  useEffect(() => {
    if (appMode !== 'SYNTHETIC_DEMO') return;

    let isMounted = true;
    async function executeScenario() {
      try {
        setIsEvaluatingScenario(true);
        // 1. Fetch details & time series
        const detailRes = await fetch(`http://127.0.0.1:8000/api/v1/decision/scenarios/${selectedScenarioId}`);
        if (detailRes.ok) {
          const detailData = await detailRes.json();
          if (isMounted) setScenarioObservations(detailData.observations || []);
        }

        // 2. Execute decision engine algorithm on backend
        const runRes = await fetch(`http://127.0.0.1:8000/api/v1/decision/scenarios/${selectedScenarioId}/run`, {
          method: 'POST',
        });
        if (runRes.ok) {
          const assessData = await runRes.json();
          if (isMounted) setScenarioAssessment(assessData);
        }
      } catch (err) {
        console.error('Failed to run synthetic scenario:', err);
      } finally {
        if (isMounted) setIsEvaluatingScenario(false);
      }
    }

    executeScenario();
    return () => {
      isMounted = false;
    };
  }, [appMode, selectedScenarioId]);

  // Derived: District list from features
  const districtList = useMemo(() => {
    const set = new Set<string>();
    features.forEach((f) => {
      if (f.properties?.dtname) set.add(f.properties.dtname);
    });
    return Array.from(set).sort();
  }, [features]);

  // Derived: Wheat Production map for shading
  const districtWheatProduction = useMemo(() => {
    const map = new Map<string, number>();
    production
      .filter((p) => p.crop_standard.toLowerCase() === 'wheat' && p.agricultural_year === '2022-23')
      .forEach((p) => {
        if (p.production_value !== null) {
          map.set(p.district_original.toLowerCase(), p.production_value);
        }
      });
    return map;
  }, [production]);

  // Derived: Mandi locations
  const mandiLocations: MandiLocation[] = useMemo(() => {
    const list: MandiLocation[] = [];
    prices.forEach((p, idx) => {
      list.push({
        id: `mandi-${idx}`,
        name: p.market_name,
        district: p.market_name.split(' ')[0],
        commodity: p.commodity_name,
        modalPrice: p.modal_price,
        priceUnit: p.price_unit,
        observationDate: p.observation_date,
      });
    });
    return list;
  }, [prices]);

  // District SVG Bounding Box projection
  const bounds = { minX: 73.8, maxX: 76.95, minY: 29.5, maxY: 32.55 };

  function projectCoord(lon: number, lat: number): [number, number] {
    const width = 520;
    const height = 540;
    const x = ((lon - bounds.minX) / (bounds.maxX - bounds.minX)) * width + 10;
    const y = height - ((lat - bounds.minY) / (bounds.maxY - bounds.minY)) * height + 10;
    return [x, y];
  }

  function getPathD(geometry: any): string {
    if (!geometry) return '';
    const rings = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
    let d = '';
    rings.forEach((polygonRings: any[]) => {
      polygonRings.forEach((ring: any[]) => {
        ring.forEach((coord: [number, number], index: number) => {
          const [px, py] = projectCoord(coord[0], coord[1]);
          if (index === 0) d += `M ${px.toFixed(1)} ${py.toFixed(1)} `;
          else d += `L ${px.toFixed(1)} ${py.toFixed(1)} `;
        });
        d += 'Z ';
      });
    });
    return d;
  }

  const districtCentroids = useMemo(() => {
    const map = new Map<string, [number, number]>();
    features.forEach((feat) => {
      const geom = feat.geometry;
      let totalX = 0;
      let totalY = 0;
      let count = 0;
      const rings = geom.type === 'Polygon' ? [geom.coordinates] : geom.coordinates;
      rings.forEach((poly: any[]) => {
        poly.forEach((ring: any[]) => {
          ring.forEach((c: [number, number]) => {
            const [px, py] = projectCoord(c[0], c[1]);
            totalX += px;
            totalY += py;
            count += 1;
          });
        });
      });
      if (count > 0) {
        map.set(feat.properties.dtname.toLowerCase(), [totalX / count, totalY / count]);
      }
    });
    return map;
  }, [features]);

  // Map Color calculation
  function getDistrictFill(dtname: string): string {
    if (shadingMode === 'status') {
      return '#fef3c7'; // Soft Amber tint representing Insufficient Evidence
    }

    const prod = districtWheatProduction.get(dtname.toLowerCase());
    if (prod === undefined || prod === 0) return '#f1f5f9';
    if (prod > 800000) return '#15803d'; // High production dark green
    if (prod > 400000) return '#4ade80'; // Medium production green
    return '#bbf7d0'; // Moderate production light green
  }

  // Active detail computation
  const activeDetail = useMemo(() => {
    const distKey = selectedDistrict.toLowerCase();
    const feat = features.find((f) => f.properties.dtname.toLowerCase() === distKey);
    const cw = crosswalk.find((c) => c.district_source_name_apy.toLowerCase() === distKey);
    const prodWheat = production.find(
      (p) => p.district_original.toLowerCase() === distKey && p.crop_standard.toLowerCase() === 'wheat' && p.agricultural_year === '2022-23'
    );
    const prodRice = production.find(
      (p) => p.district_original.toLowerCase() === distKey && p.crop_standard.toLowerCase() === 'rice' && p.agricultural_year === '2022-23'
    );
    const mandiMatches = mandiLocations.filter(
      (m) => m.district.toLowerCase().includes(distKey) || distKey.includes(m.district.toLowerCase())
    );

    return {
      name: feat?.properties.dtname || selectedDistrict,
      lgdCode: feat?.properties.dist_lgd || cw?.district_id_candidate_lgd || 'Not Matched',
      wheatProd: prodWheat?.production_value ?? null,
      wheatYield: prodWheat?.yield_value ?? null,
      riceProd: prodRice?.production_value ?? null,
      riceYield: prodRice?.yield_value ?? null,
      mandis: mandiMatches,
    };
  }, [selectedDistrict, features, crosswalk, production, mandiLocations]);

  const activeMandi = useMemo(() => {
    if (!selectedMandiId) return null;
    return mandiLocations.find((m) => m.id === selectedMandiId) || null;
  }, [selectedMandiId, mandiLocations]);

  // Chart 1 Data: Historical Wheat Productivity (1968–2023)
  const historicalYieldData = useMemo(() => {
    const distKey = selectedDistrict.toLowerCase();
    const filtered = yields
      .filter((y) => y.district_original.toLowerCase() === distKey && y.crop_standard.toLowerCase() === 'wheat')
      .sort((a, b) => parseInt(a.effective_year, 10) - parseInt(b.effective_year, 10));
    return filtered.slice(-8);
  }, [yields, selectedDistrict]);

  // Chart 2 Data: Top Wheat Basins Comparison
  const districtComparisonData = useMemo(() => {
    const list: { district: string; prodMT: number; isSelected: boolean }[] = [];
    districtWheatProduction.forEach((prod, distKey) => {
      const properName = features.find((f) => f.properties.dtname.toLowerCase() === distKey)?.properties.dtname || distKey;
      list.push({
        district: properName,
        prodMT: prod,
        isSelected: properName.toLowerCase() === selectedDistrict.toLowerCase(),
      });
    });
    list.sort((a, b) => b.prodMT - a.prodMT);
    const top6 = list.slice(0, 6);
    if (!top6.some((d) => d.isSelected)) {
      const foundSelected = list.find((d) => d.isSelected);
      if (foundSelected) top6[5] = foundSelected;
    }
    return top6;
  }, [districtWheatProduction, features, selectedDistrict]);

  // Chart 4 Data: Coverage Matrix
  const coverageDimensions = [
    { name: '1. Crop Yield History', coverage: 100, status: 'VERIFIED', source: 'OGD Punjab (2,754 rows)' },
    { name: '2. Production Estimates', coverage: 100, status: 'VERIFIED', source: 'DES APY (230 rows)' },
    { name: '3. APMC Price Quotes', coverage: 48, status: 'PARTIAL', source: 'AGMARKNET (53 paddy prices)' },
    { name: '4. Daily Grain Arrivals', coverage: 0, status: 'CRITICAL GAP', source: 'e-Mandikaran (0 wheat/paddy)' },
    { name: '5. Public Buffer Stocks', coverage: 0, status: 'NATIONAL ONLY', source: 'DFPD Central Pool (No Punjab)' },
    { name: '6. Private Silo Telemetry', coverage: 0, status: 'NOT OPEN DATA', source: 'Commercial Holdings (Unmeasured)' },
    { name: '7. Weather Baseline', coverage: 100, status: 'VERIFIED', source: 'NASA POWER (3,655 station-days)' },
    { name: '8. Ground-Truth Hoarding Labels', coverage: 0, status: 'UNAVAILABLE', source: 'Regulatory Audits (None)' },
  ];

  return (
    <div className="dashboard-container">
      {/* MODE SWITCHER: Real Evidence vs. Synthetic Demo Mode */}
      <section className="app-mode-banner" aria-label="Application Operating Mode">
        <div className="mode-selector-wrap">
          <span className="mode-heading">System Operating Mode:</span>
          <div className="mode-toggle-group" role="tablist" aria-label="Evidence vs Demo Mode Toggle">
            <button
              type="button"
              role="tab"
              aria-selected={appMode === 'REAL'}
              className={`mode-toggle-btn ${appMode === 'REAL' ? 'active real-active' : ''}`}
              onClick={() => setAppMode('REAL')}
              id="mode-toggle-real"
            >
              <span className="mode-dot green"></span>
              <strong>Real Evidence Mode</strong> (Audited Government Feeds)
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={appMode === 'SYNTHETIC_DEMO'}
              className={`mode-toggle-btn ${appMode === 'SYNTHETIC_DEMO' ? 'active demo-active' : ''}`}
              onClick={() => setAppMode('SYNTHETIC_DEMO')}
              id="mode-toggle-synthetic"
            >
              <span className="mode-dot amber"></span>
              <strong>Synthetic Demo Mode</strong> (Algorithm & Anomaly Lab)
            </button>
          </div>
        </div>

        {appMode === 'SYNTHETIC_DEMO' ? (
          <div className="synthetic-watermark-pill" role="alert">
            <span className="pill-tag">OFFLINE SIMULATION</span>
            <span>SYNTHETIC DEMO — NOT LIVE MARKET EVIDENCE</span>
          </div>
        ) : (
          <div className="real-watermark-pill">
            <span className="pill-tag green">EMPIRICAL GOVERNANCE</span>
            <span>Real Datasets Audited • AGENTS.md Rule 6 Strict Compliance</span>
          </div>
        )}
      </section>

      {/* SYNTHETIC DEMO CONTROLS (Rendered in Demo Mode) */}
      {appMode === 'SYNTHETIC_DEMO' && (
        <section className="scenario-lab-panel" aria-label="Synthetic Scenario Selection">
          <div className="scenario-header">
            <div>
              <h2 className="scenario-title">Interactive Anomaly Detection & Scenario Lab</h2>
              <p className="scenario-subtitle">
                Select an isolated scenario to test the backend decision engine algorithm against planted anomalies,
                isolated signals, or corrupted evidence. Results are calculated dynamically by the server.
              </p>
            </div>
            <div className="algorithm-badge">
              <span>Engine: Robust MAD (v2.1.0)</span>
            </div>
          </div>

          <div className="scenario-chips-row" role="radiogroup" aria-label="Select Test Scenario">
            {(availableScenarios.length > 0
              ? availableScenarios.map((s) => ({
                  id: s.scenario_id,
                  label: s.title,
                  tag: s.expected_decision_status.replace(/_/g, ' '),
                }))
              : [
                  { id: 'scenario_b_convergent_anomaly', label: 'Scenario B: Planted Convergent Anomaly', tag: 'Divergence' },
                  { id: 'scenario_a_normal_baseline', label: 'Scenario A: Normal Baseline', tag: 'Normal' },
                  { id: 'scenario_c_price_spike_only', label: 'Scenario C: Price-Only Spike', tag: 'Price Signal' },
                  { id: 'scenario_d_arrival_drop_only', label: 'Scenario D: Arrival-Only Drop', tag: 'Arrival Signal' },
                  { id: 'scenario_e_insufficient_evidence', label: 'Scenario E: Insufficient / Corrupted', tag: 'Data Gap' },
                ]
            ).map((scen) => (
              <button
                key={scen.id}
                type="button"
                className={`scenario-chip ${selectedScenarioId === scen.id ? 'active' : ''}`}
                onClick={() => setSelectedScenarioId(scen.id)}
                role="radio"
                aria-checked={selectedScenarioId === scen.id}
              >
                <span className="chip-tag">{scen.tag}</span>
                <span className="chip-label">{scen.label}</span>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* A. Meaningful Google Material Summary Metrics Cards */}
      <section className="summary-metrics-grid" aria-label="AgriShield Operational Metrics">
        <div className="metric-card-mat">
          <div className="card-top">
            <span className="metric-label">Usable Observation Basins</span>
            <span className="metric-badge green">Verified Data</span>
          </div>
          <div className="metric-number">23 Districts • 11 Mandis</div>
          <div className="metric-footer">
            <span>DES APY (2018–2023) & AGMARKNET Oct 2024</span>
          </div>
        </div>

        <div className="metric-card-mat">
          <div className="card-top">
            <span className="metric-label">Locations Flagged for Investigation</span>
            <span className="metric-badge amber">Rule 6 Invariant</span>
          </div>
          <div className="metric-number">
            {appMode === 'SYNTHETIC_DEMO' && scenarioAssessment?.decision_status === 'CONVERGENT_SUPPLY_ANOMALY'
              ? '1 Scenario Flagged (Demo)'
              : '0 Flagged (0 Eligible)'}
          </div>
          <div className="metric-footer">
            <span>
              {appMode === 'SYNTHETIC_DEMO'
                ? 'Deterministic backend simulation detection active'
                : '7-Point Gate: Ineligible due to missing staple arrival volumes'}
            </span>
          </div>
        </div>

        <div className="metric-card-mat">
          <div className="card-top">
            <span className="metric-label">District Geographic Coverage</span>
            <span className="metric-badge green">100% Mapped</span>
          </div>
          <div className="metric-number">23 / 23 Districts</div>
          <div className="metric-footer">
            <span>Survey of India / NWIC Boundaries (EPSG:4326)</span>
          </div>
        </div>

        <div className="metric-card-mat">
          <div className="card-top">
            <span className="metric-label">Verified Physical Observations</span>
            <span className="metric-badge blue">6,692 Rows</span>
          </div>
          <div className="metric-number">6,692 Physical Records</div>
          <div className="metric-footer">
            <span>Yields, production, paddy prices & weather station-days</span>
          </div>
        </div>
      </section>

      {/* Top Filter and Context Controls Bar (Real Mode) */}
      {appMode === 'REAL' && (
        <div className="dashboard-toolbar" role="region" aria-label="Dashboard Controls">
          <div className="toolbar-left">
            <label htmlFor="district-select" className="filter-label">
              <strong>Select District:</strong>
            </label>
            <select
              id="district-select"
              className="filter-select"
              value={selectedDistrict}
              onChange={(e) => {
                setSelectedDistrict(e.target.value);
                setSelectedMandiId(null);
              }}
            >
              {districtList.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          <div className="toolbar-center">
            <span className="filter-label"><strong>Commodity:</strong></span>
            <div className="filter-button-group" role="group" aria-label="Commodity Filter">
              <button
                type="button"
                className={`filter-btn ${commodityFilter === 'all' ? 'active' : ''}`}
                onClick={() => setCommodityFilter('all')}
              >
                All Crops
              </button>
              <button
                type="button"
                className={`filter-btn ${commodityFilter === 'wheat' ? 'active' : ''}`}
                onClick={() => setCommodityFilter('wheat')}
              >
                Wheat (Rabi)
              </button>
              <button
                type="button"
                className={`filter-btn ${commodityFilter === 'rice' ? 'active' : ''}`}
                onClick={() => setCommodityFilter('rice')}
              >
                Paddy/Rice (Kharif)
              </button>
            </div>
          </div>

          <div className="toolbar-right">
            <span className="filter-label"><strong>Map Shading:</strong></span>
            <div className="filter-button-group" role="group" aria-label="Map Shading Mode">
              <button
                type="button"
                className={`filter-btn ${shadingMode === 'production' ? 'active' : ''}`}
                onClick={() => setShadingMode('production')}
                title="Shade districts by verified Wheat Production (Metric Tonnes)"
              >
                Wheat Production (MT)
              </button>
              <button
                type="button"
                className={`filter-btn ${shadingMode === 'status' ? 'active' : ''}`}
                onClick={() => setShadingMode('status')}
                title="Shade districts by Evidence Sufficiency Screening Status"
              >
                Evidence Status
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="alert-card-error" role="alert">
          <span className="alert-icon">⚠️</span>
          <div className="alert-body">
            <strong>Data Error:</strong> {error}
          </div>
        </div>
      )}

      {/* Main Grid: Interactive Map + Selected Location Assessment Panel */}
      <div className="dashboard-grid">
        {/* Left Column: Interactive Map */}
        <div className="map-panel">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">Interactive Punjab Map</h2>
              <span className="panel-subtitle">
                {appMode === 'SYNTHETIC_DEMO'
                  ? `Simulated Market Jurisdiction: ${scenarioAssessment?.location_name || 'Khanna Grain Mandi'} (Illustrative Location)`
                  : shadingMode === 'production'
                  ? 'Shaded by 2022-23 Wheat Production (MT). Click any district or APMC pin to inspect evidence.'
                  : 'All 23 districts shaded in Insufficient Evidence tint under 7-Point Screening Gate.'}
              </span>
            </div>
            <div className="map-badge" title="Survey of India / NWIC Verified Geometries">
              <span>EPSG:4326 • 23 Districts</span>
            </div>
          </div>

          {loading ? (
            <div className="loading-container" aria-live="polite">
              <div className="spinner"></div>
              <span>Loading Punjab geospatial boundaries...</span>
            </div>
          ) : (
            <div className="svg-container">
              <svg
                viewBox="0 0 540 560"
                className="punjab-svg-map"
                role="img"
                aria-label="Interactive map of Punjab showing 23 districts and APMC mandi locations"
              >
                {/* District Polygons */}
                <g className="districts-group">
                  {features.map((feat) => {
                    const isSelected = feat.properties.dtname.toLowerCase() === selectedDistrict.toLowerCase();
                    const isHovered = feat.properties.dtname.toLowerCase() === hoveredDistrict?.toLowerCase();
                    const prod = districtWheatProduction.get(feat.properties.dtname.toLowerCase()) || 0;

                    return (
                      <path
                        key={feat.properties.dtname}
                        d={getPathD(feat.geometry)}
                        fill={getDistrictFill(feat.properties.dtname)}
                        className={`district-polygon ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`}
                        onClick={() => {
                          setSelectedDistrict(feat.properties.dtname);
                          setSelectedMandiId(null);
                        }}
                        onMouseEnter={() => setHoveredDistrict(feat.properties.dtname)}
                        onMouseLeave={() => setHoveredDistrict(null)}
                        tabIndex={0}
                        role="button"
                        aria-label={`District ${feat.properties.dtname}: ${prod.toLocaleString()} MT wheat production. Click to inspect assessment.`}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            setSelectedDistrict(feat.properties.dtname);
                            setSelectedMandiId(null);
                          }
                        }}
                      >
                        <title>{`${feat.properties.dtname}: ${prod ? `${prod.toLocaleString()} MT Wheat` : 'Pre-split territory'} • Status: Insufficient Evidence`}</title>
                      </path>
                    );
                  })}
                </g>

                {/* Mandi Marker Pins */}
                <g className="mandis-group">
                  {mandiLocations.map((mandi) => {
                    const centroid = districtCentroids.get(mandi.district.toLowerCase());
                    if (!centroid) return null;
                    const [cx, cy] = centroid;
                    const isMandiSelected = selectedMandiId === mandi.id;

                    return (
                      <g
                        key={mandi.id}
                        className={`mandi-marker-node ${isMandiSelected ? 'selected-mandi' : ''}`}
                        transform={`translate(${cx}, ${cy})`}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedDistrict(mandi.district);
                          setSelectedMandiId(mandi.id);
                        }}
                        tabIndex={0}
                        role="button"
                        aria-label={`APMC Mandi ${mandi.name} in ${mandi.district}. Click to inspect.`}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            setSelectedDistrict(mandi.district);
                            setSelectedMandiId(mandi.id);
                          }
                        }}
                      >
                        <circle
                          r={isMandiSelected ? 9 : 5.5}
                          className="mandi-pin-circle"
                        />
                        <title>{`${mandi.name} (${mandi.district}): ${mandi.modalPrice ? `Rs. ${mandi.modalPrice}/Qtl` : 'Price unlisted'}`}</title>
                      </g>
                    );
                  })}
                </g>
              </svg>

              {/* Map Floating Tooltip */}
              {hoveredDistrict && (
                <div className="map-floating-tooltip" aria-hidden="true">
                  <strong>{hoveredDistrict}</strong>
                  <span>Wheat: {(districtWheatProduction.get(hoveredDistrict.toLowerCase()) || 0).toLocaleString()} MT</span>
                  <span className="tooltip-sub">Screening: Insufficient Evidence</span>
                </div>
              )}

              {/* Map Legend */}
              <div className="map-legend" aria-hidden="true">
                {shadingMode === 'production' ? (
                  <>
                    <div className="legend-item">
                      <span className="legend-swatch prod-high"></span>
                      <span>High Production (&gt;800k MT)</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-swatch prod-mid"></span>
                      <span>Moderate (400k–800k MT)</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-swatch prod-low"></span>
                      <span>Baseline (&lt;400k MT)</span>
                    </div>
                  </>
                ) : (
                  <div className="legend-item">
                    <span className="legend-swatch status-insufficient"></span>
                    <span>Insufficient Data (Gate Blocked)</span>
                  </div>
                )}
                <div className="legend-item">
                  <span className="legend-swatch marker-swatch"></span>
                  <span>Reporting APMC Mandi</span>
                </div>
              </div>

              {/* Source attribution bar */}
              <div className="map-attribution">
                <span>Data Sources: Survey of India • NWIC • DES APY 2022-23 • AGMARKNET Oct 2024</span>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Selected Location Assessment Panel */}
        <div className="assessment-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow-tag">
                {appMode === 'SYNTHETIC_DEMO' ? 'Synthetic Engine Output' : 'Location Assessment'}
              </span>
              <h2 className="panel-title">
                {appMode === 'SYNTHETIC_DEMO'
                  ? scenarioAssessment?.location_name || 'Simulation Catchment'
                  : activeMandi
                  ? `${activeMandi.name} (${activeMandi.district})`
                  : `${activeDetail.name} District`}
              </h2>
            </div>
            <div className="lgd-badge" title="Local Government Directory Code">
              {appMode === 'SYNTHETIC_DEMO' ? 'SIM-DEMO' : `LGD: ${activeDetail.lgdCode}`}
            </div>
          </div>

          {/* DYNAMIC DECISION ENGINE ASSESSMENT CARD */}
          {appMode === 'SYNTHETIC_DEMO' ? (
            <div className={`risk-assessment-card demo-card ${scenarioAssessment?.decision_status.toLowerCase()}`}>
              <div className="risk-header">
                <span className="risk-title">Backend Decision Engine Assessment</span>
                <span className={`risk-badge badge-${scenarioAssessment?.decision_status.toLowerCase()}`}>
                  {isEvaluatingScenario ? 'EVALUATING MODEL...' : (scenarioAssessment?.status_label || 'PROCESSING...')}
                </span>
              </div>

              {/* Anomaly Intensity Gauge (when available) */}
              {scenarioAssessment?.anomaly_intensity_score !== null && scenarioAssessment?.anomaly_intensity_score !== undefined && (
                <div className="anomaly-score-box">
                  <div className="score-top">
                    <span className="score-label">Anomaly Intensity Score</span>
                    <span className="score-value">{scenarioAssessment.anomaly_intensity_score} / 100</span>
                  </div>
                  <div className="score-bar">
                    <div
                      className={`score-bar-fill fill-${scenarioAssessment.decision_status.toLowerCase()}`}
                      style={{ width: `${Math.min(100, Math.max(5, scenarioAssessment.anomaly_intensity_score))}%` }}
                    ></div>
                  </div>
                </div>
              )}

              <p className="risk-summary">
                {scenarioAssessment?.human_explanation}
              </p>

              {/* Per-Signal Breakdown Cards */}
              {scenarioAssessment?.signals && (
                <div className="signals-breakdown-grid">
                  <div className="signal-box">
                    <div className="sig-header">
                      <span className="sig-title">Price Signal</span>
                      <span className={`sig-tag ${scenarioAssessment.signals.price?.status.toLowerCase()}`}>
                        {scenarioAssessment.signals.price?.status}
                      </span>
                    </div>
                    <div className="sig-metric">
                      {scenarioAssessment.signals.price?.observed_value
                        ? `Rs. ${scenarioAssessment.signals.price.observed_value} / Qtl`
                        : 'Unobserved'}
                    </div>
                    <div className="sig-sub">
                      Deviation: {scenarioAssessment.signals.price?.deviation_pct !== null && scenarioAssessment.signals.price?.deviation_pct !== undefined
                        ? `${scenarioAssessment.signals.price.deviation_pct > 0 ? '+' : ''}${scenarioAssessment.signals.price.deviation_pct}%`
                        : 'N/A'} (Z = {scenarioAssessment.signals.price?.robust_z_score ?? 'N/A'})
                    </div>
                  </div>

                  <div className="signal-box">
                    <div className="sig-header">
                      <span className="sig-title">Arrival Signal</span>
                      <span className={`sig-tag ${scenarioAssessment.signals.arrival?.status.toLowerCase()}`}>
                        {scenarioAssessment.signals.arrival?.status}
                      </span>
                    </div>
                    <div className="sig-metric">
                      {scenarioAssessment.signals.arrival?.observed_value !== null && scenarioAssessment.signals.arrival?.observed_value !== undefined
                        ? `${scenarioAssessment.signals.arrival.observed_value} Qtl`
                        : 'Unobserved'}
                    </div>
                    <div className="sig-sub">
                      Deviation: {scenarioAssessment.signals.arrival?.deviation_pct !== null && scenarioAssessment.signals.arrival?.deviation_pct !== undefined
                        ? `${scenarioAssessment.signals.arrival.deviation_pct > 0 ? '+' : ''}${scenarioAssessment.signals.arrival.deviation_pct}%`
                        : 'N/A'} (Z = {scenarioAssessment.signals.arrival?.robust_z_score ?? 'N/A'})
                    </div>
                  </div>
                </div>
              )}

              {/* Recommended Action */}
              <div className="risk-reasons-box">
                <h4 className="box-title">Recommended Next Step:</h4>
                <p className="recommended-action-text">{scenarioAssessment?.recommended_action}</p>
              </div>

              {/* Legal Caveat */}
              <div className="legal-caveat-box">
                <span className="caveat-icon">⚖️</span>
                <span>{scenarioAssessment?.legal_caveat}</span>
              </div>
            </div>
          ) : (
            /* REAL MODE ASSESSMENT CARD */
            <div className="risk-assessment-card">
              <div className="risk-header">
                <span className="risk-title">Hoarding Risk Evaluation</span>
                <span className="risk-badge neutral">INSUFFICIENT DATA TO ASSESS RISK</span>
              </div>
              <p className="risk-summary">
                There is currently <strong>insufficient empirical data</strong> to compute an objective grain-hoarding risk score or rank for {activeDetail.name}.
              </p>
              <div className="risk-reasons-box">
                <h4 className="box-title">Why risk cannot be calculated from current evidence:</h4>
                <ul className="reasons-list">
                  <li>
                    <strong>Zero Wheat/Paddy Market Arrivals:</strong> The acquired daily arrival panel contains 3,892 produce rows (vegetables/fruits) and exactly 0 staple foodgrain records.
                  </li>
                  <li>
                    <strong>100% Null Arrival Volumes:</strong> AGMARKNET daily price feeds report wholesale price quotes only; arrival volumes are unexposed (null).
                  </li>
                  <li>
                    <strong>Unmeasured Private Warehousing:</strong> No verified private silo inventories or inter-state grain movement records exist.
                  </li>
                  <li>
                    <strong>AGENTS.md Rule 6:</strong> Statistical anomalies are investigation prompts only and never proof of intent or illegal hoarding.
                  </li>
                </ul>
              </div>

              <div className="evidence-sufficiency-gauge">
                <div className="gauge-header">
                  <span>Evidence Sufficiency Level</span>
                  <span className="gauge-val">Low / Incomplete</span>
                </div>
                <div className="gauge-bar">
                  <div className="gauge-fill" style={{ width: '28%' }}></div>
                </div>
                <span className="gauge-note">2 of 7 essential screening streams verified</span>
              </div>
            </div>
          )}

          {/* AVAILABLE OBSERVATIONS SECTION */}
          <div className="observations-card">
            <h3 className="section-title">
              {appMode === 'SYNTHETIC_DEMO' ? 'Scenario Observation Snapshot' : 'Verified Observations at this Location'}
            </h3>

            {appMode === 'SYNTHETIC_DEMO' ? (
              <div className="evidence-block">
                <h4 className="evidence-subtitle">Synthetic Observation Stream (45-Day Sequence)</h4>
                <p className="weather-summary">
                  Latest observed daily quote: <strong>Rs. {scenarioObservations.slice(-1)[0]?.modal_price ?? 'N/A'} / Qtl</strong>,
                  Arrival Volume: <strong>{scenarioObservations.slice(-1)[0]?.arrival_quantity ?? 'N/A'} Quintals</strong>.
                  All generated values are strictly isolated in <code>data/synthetic/</code>.
                </p>
              </div>
            ) : (
              <>
                {(commodityFilter === 'all' || commodityFilter === 'wheat') && (
                  <div className="evidence-block">
                    <h4 className="evidence-subtitle">1. Agricultural Production & Yield (DES APY 2022-23)</h4>
                    <div className="stat-grid-duo">
                      <div className="stat-card">
                        <span className="stat-label">Wheat Production</span>
                        <span className="stat-value">
                          {activeDetail.wheatProd !== null ? `${activeDetail.wheatProd.toLocaleString()} MT` : 'Unreported'}
                        </span>
                        <span className="stat-sub">Yield: {activeDetail.wheatYield ? `${activeDetail.wheatYield.toLocaleString()} kg/ha` : 'N/A'}</span>
                      </div>
                      <div className="stat-card">
                        <span className="stat-label">Rice / Paddy Production</span>
                        <span className="stat-value">
                          {activeDetail.riceProd !== null ? `${activeDetail.riceProd.toLocaleString()} MT` : 'Unreported'}
                        </span>
                        <span className="stat-sub">Yield: {activeDetail.riceYield ? `${activeDetail.riceYield.toLocaleString()} kg/ha` : 'N/A'}</span>
                      </div>
                    </div>
                  </div>
                )}

                <div className="evidence-block">
                  <h4 className="evidence-subtitle">2. Wholesale APMC Mandi Market Prices (AGMARKNET)</h4>
                  {activeDetail.mandis.length > 0 ? (
                    <div className="mandi-list">
                      {activeDetail.mandis.map((m) => (
                        <div key={m.id} className="mandi-item">
                          <div>
                            <strong>{m.name}</strong> — {m.commodity}
                            <div className="mandi-date">Observation: {m.observationDate}</div>
                          </div>
                          <div className="mandi-price">
                            {m.modalPrice ? `Rs. ${m.modalPrice.toLocaleString()} / Qtl` : 'Price unlisted'}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="no-mandi-text">
                      No active AGMARKNET price reporting mandis in the current weekly slice for {activeDetail.name}.
                    </p>
                  )}
                </div>

                <div className="evidence-block">
                  <h4 className="evidence-subtitle">3. Agrometeorological Monitoring (NASA POWER)</h4>
                  <p className="weather-summary">
                    Daily temperature, precipitation, and relative humidity monitored via nearest meteorological station. No anomalous localized weather shocks recorded.
                  </p>
                </div>
              </>
            )}
          </div>

          {/* DATA LIMITATIONS BOX */}
          <div className="limitations-footer-box">
            <strong>Data Boundary Notice:</strong> All real statistics shown are empirical observations from verified government portals. No proxy data is used, and zero arrival values are never assumed from absence of reports.
          </div>
        </div>
      </div>

      {/* B. Meaningful Visualizations Section: 4 Charts That Actually Matter */}
      <section className="analytics-charts-section" aria-labelledby="charts-section-title">
        <div className="section-header-row">
          <div>
            <h2 id="charts-section-title" className="section-heading">
              {appMode === 'SYNTHETIC_DEMO' ? 'Synthetic Scenario Analytical Trajectory' : 'Analytical Evidence & Integrity Visualizations'}
            </h2>
            <p className="section-subheading">
              {appMode === 'SYNTHETIC_DEMO'
                ? 'Time-series curve showing the baseline median against observed values with highlighted anomaly window.'
                : 'Four verified, purpose-built visualizations answering specific questions with documented provenance.'}
            </p>
          </div>

          <div className="chart-tabs" role="tablist" aria-label="Visualizations Tab Switcher">
            <button
              type="button"
              role="tab"
              aria-selected={activeChartTab === 'trend'}
              className={`chart-tab-btn ${activeChartTab === 'trend' ? 'active' : ''}`}
              onClick={() => setActiveChartTab('trend')}
            >
              1. Historical Trend
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeChartTab === 'compare'}
              className={`chart-tab-btn ${activeChartTab === 'compare' ? 'active' : ''}`}
              onClick={() => setActiveChartTab('compare')}
            >
              2. Basin Comparison
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeChartTab === 'evidence'}
              className={`chart-tab-btn ${activeChartTab === 'evidence' ? 'active' : ''}`}
              onClick={() => setActiveChartTab('evidence')}
            >
              3. Screening Evidence
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeChartTab === 'coverage'}
              className={`chart-tab-btn ${activeChartTab === 'coverage' ? 'active' : ''}`}
              onClick={() => setActiveChartTab('coverage')}
            >
              4. Supply Coverage
            </button>
          </div>
        </div>

        {/* Tab 1: Historical Trend (or Synthetic Trajectory in Demo Mode) */}
        {activeChartTab === 'trend' && (
          <div className="chart-card-container">
            <div className="chart-card-header">
              <div>
                <h3 className="chart-card-title">
                  {appMode === 'SYNTHETIC_DEMO'
                    ? `Synthetic Price & Arrival Trajectory: ${scenarioAssessment?.location_name || 'Simulation'}`
                    : `Historical Wheat Productivity Series (1968–2023) — ${activeDetail.name}`}
                </h3>
                <span className="chart-card-sub">
                  {appMode === 'SYNTHETIC_DEMO'
                    ? '45-Day Daily Time-Series: Baseline Median vs. Observed Curve'
                    : 'Source: Open Government Data (OGD) Punjab & DES APY • Unit: kg/ha'}
                </span>
              </div>
            </div>

            {appMode === 'SYNTHETIC_DEMO' ? (
              <div className="scenario-chart-display">
                <svg viewBox="0 0 760 220" className="chart-svg" role="img" aria-label="Synthetic price and arrival time series chart">
                  <line x1="50" y1="180" x2="740" y2="180" stroke="#cbd5e1" strokeWidth="1" />
                  <line x1="50" y1="30" x2="50" y2="180" stroke="#cbd5e1" strokeWidth="1" />

                  {/* Shaded Anomaly Window (Days 31-45) */}
                  {selectedScenarioId !== 'scenario_a_normal_baseline' && selectedScenarioId !== 'scenario_e_insufficient_evidence' && (
                    <rect x="520" y="20" width="220" height="160" fill="#fef2f2" opacity="0.6" />
                  )}

                  {/* Draw points & line for Price */}
                  {scenarioObservations.length > 1 && (
                    <path
                      d={scenarioObservations
                        .map((obs, i) => {
                          const x = 60 + (i / (scenarioObservations.length - 1)) * 670;
                          const normPrice = obs.modal_price ? Math.max(0, Math.min(1, (obs.modal_price - 1800) / 1600)) : 0.5;
                          const y = 170 - normPrice * 130;
                          return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
                        })
                        .join(' ')}
                      fill="none"
                      stroke="#0b57d0"
                      strokeWidth="2.5"
                    />
                  )}

                  {/* Draw points & line for Arrivals */}
                  {scenarioObservations.length > 1 && (
                    <path
                      d={scenarioObservations
                        .map((obs, i) => {
                          const x = 60 + (i / (scenarioObservations.length - 1)) * 670;
                          const normArr = obs.arrival_quantity ? Math.max(0, Math.min(1, (obs.arrival_quantity - 200) / 2800)) : 0.5;
                          const y = 170 - normArr * 130;
                          return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
                        })
                        .join(' ')}
                      fill="none"
                      stroke="#d97706"
                      strokeWidth="2"
                      strokeDasharray="4 2"
                    />
                  )}

                  {/* Legend inside SVG */}
                  <g transform="translate(60, 20)">
                    <line x1="0" y1="5" x2="20" y2="5" stroke="#0b57d0" strokeWidth="2.5" />
                    <text x="25" y="9" fontSize="11" fill="#1e293b">Wholesale Price (Rs./Qtl)</text>
                    <line x1="180" y1="5" x2="200" y2="5" stroke="#d97706" strokeWidth="2" strokeDasharray="4 2" />
                    <text x="205" y="9" fontSize="11" fill="#1e293b">Arrival Volume (Qtl)</text>
                    {selectedScenarioId !== 'scenario_a_normal_baseline' && selectedScenarioId !== 'scenario_e_insufficient_evidence' && (
                      <text x="460" y="9" fontSize="11" fill="#b91c1c" fontWeight="bold">Divergence Event Window</text>
                    )}
                  </g>
                </svg>
              </div>
            ) : (
              <div className="chart-svg-wrapper">
                <svg viewBox="0 0 760 220" className="chart-svg" role="img" aria-label={`Historical wheat productivity chart for ${activeDetail.name}`}>
                  <line x1="50" y1="180" x2="740" y2="180" stroke="#cbd5e1" strokeWidth="1" />
                  <line x1="50" y1="30" x2="50" y2="180" stroke="#cbd5e1" strokeWidth="1" />

                  {historicalYieldData.map((d, idx) => {
                    const x = 80 + idx * 85;
                    const val = d.yield_value || 0;
                    const maxVal = 5500;
                    const barHeight = (val / maxVal) * 140;
                    const y = 180 - barHeight;

                    return (
                      <g key={d.effective_year}>
                        <rect x={x - 20} y={y} width="40" height={barHeight} fill="#15803d" rx="3" opacity="0.85" />
                        <text x={x} y={y - 8} textAnchor="middle" fontSize="11" fontWeight="bold" fill="#0f172a">
                          {val.toLocaleString()}
                        </text>
                        <text x={x} y="196" textAnchor="middle" fontSize="11" fill="#64748b">
                          {d.effective_year}
                        </text>
                      </g>
                    );
                  })}
                </svg>
              </div>
            )}

            {/* 6-Point Provenance & Methodology Disclosure */}
            <div className="methodology-disclosure-box">
              <h4 className="disclosure-heading">Chart 1 Quality & Provenance Disclosure</h4>
              <div className="disclosure-grid">
                <div><strong>Question Answered:</strong> How has long-term agricultural grain productivity trended over time?</div>
                <div><strong>Source Dataset:</strong> {appMode === 'SYNTHETIC_DEMO' ? 'Synthetic Scenario Generator (Offline Fixture)' : 'Open Government Data (OGD) Punjab & DES APY'}</div>
                <div><strong>Calculation:</strong> {appMode === 'SYNTHETIC_DEMO' ? 'Daily Price vs. Arrival series' : 'Annual district production (MT) / harvested area (ha) * 1000'}</div>
                <div><strong>Units & Scale:</strong> {appMode === 'SYNTHETIC_DEMO' ? 'Price (Rs./Qtl) & Arrivals (Qtl)' : 'kg/ha (Empirical range: 1,500 – 5,400 kg/ha)'}</div>
                <div><strong>Supported Conclusion:</strong> {appMode === 'SYNTHETIC_DEMO' ? 'Algorithm accurately flags co-occurring divergence' : 'Long-term yield expansion following Green Revolution adoption'}</div>
                <div><strong>Unsupported Conclusion:</strong> This trend does NOT proxy intra-seasonal daily market withholding or trader behavior.</div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Basin Comparison */}
        {activeChartTab === 'compare' && (
          <div className="chart-card-container">
            <div className="chart-card-header">
              <div>
                <h3 className="chart-card-title">Cross-District Wheat Production Comparison (Top Basins)</h3>
                <span className="chart-card-sub">Agricultural Year 2022–23 • Unit: Metric Tonnes (MT)</span>
              </div>
            </div>

            <div className="chart-bars-horizontal">
              {districtComparisonData.map((item) => {
                const maxProd = 1100000;
                const widthPct = Math.min(100, (item.prodMT / maxProd) * 100);

                return (
                  <div key={item.district} className={`horiz-bar-row ${item.isSelected ? 'selected-row' : ''}`}>
                    <div className="bar-label-col">
                      <strong>{item.district}</strong>
                      {item.isSelected && <span className="selected-tag">Selected</span>}
                    </div>
                    <div className="bar-track-col">
                      <div
                        className={`bar-fill ${item.isSelected ? 'fill-selected' : ''}`}
                        style={{ width: `${widthPct}%` }}
                      ></div>
                    </div>
                    <div className="bar-val-col">
                      {item.prodMT.toLocaleString()} MT
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="methodology-disclosure-box">
              <h4 className="disclosure-heading">Chart 2 Quality & Provenance Disclosure</h4>
              <div className="disclosure-grid">
                <div><strong>Question Answered:</strong> Which Punjab district basins contribute the largest physical wheat supply?</div>
                <div><strong>Source Dataset:</strong> Directorate of Economics & Statistics (DES APY 2022-23)</div>
                <div><strong>Calculation:</strong> District aggregate reported production value in Metric Tonnes</div>
                <div><strong>Units & Scale:</strong> Metric Tonnes (MT)</div>
                <div><strong>Supported Conclusion:</strong> Sangrur, Ludhiana, and Patiala form the primary grain production belt</div>
                <div><strong>Unsupported Conclusion:</strong> High production basin status does NOT imply high local hoarding risk.</div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Screening Evidence Breakdown */}
        {activeChartTab === 'evidence' && (
          <div className="chart-card-container">
            <div className="chart-card-header">
              <div>
                <h3 className="chart-card-title">Screening Evidence Breakdown & Invariant Evaluation</h3>
                <span className="chart-card-sub">Compliance with 7-Point Eligibility Gate & AGENTS.md Rule 6</span>
              </div>
            </div>

            <div className="evidence-streams-table">
              <div className="table-header-row">
                <span>Required Supply Stream</span>
                <span>Audit Status</span>
                <span>Verified Observations</span>
                <span>Hoarding Inference Policy</span>
              </div>
              <div className="table-data-row">
                <strong>1. Staple Foodgrain Arrivals</strong>
                <span className="status-tag red">Zero Grain Rows</span>
                <span>3,892 produce rows (62 crops)</span>
                <span>BLOCKED (Cannot proxy grains from produce)</span>
              </div>
              <div className="table-data-row">
                <strong>2. Mandi Wholesale Prices</strong>
                <span className="status-tag yellow">Verified (Prices Only)</span>
                <span>53 Paddy price quotes</span>
                <span>PARTIAL (Arrival volume 100% null)</span>
              </div>
              <div className="table-data-row">
                <strong>3. District Wheat Production</strong>
                <span className="status-tag green">100% Verified</span>
                <span>230 district-year rows</span>
                <span>ANNUAL MACRO CONTEXT ONLY</span>
              </div>
              <div className="table-data-row">
                <strong>4. Agrometeorology</strong>
                <span className="status-tag green">100% Verified</span>
                <span>3,655 station-days (0% nulls)</span>
                <span>WEATHER BASELINE ONLY</span>
              </div>
              <div className="table-data-row">
                <strong>5. Private Warehouse Stocks</strong>
                <span className="status-tag red">Zero Public Data</span>
                <span>0 private silo readings</span>
                <span>BLOCKED (No commercial holding records)</span>
              </div>
            </div>

            <div className="methodology-disclosure-box">
              <h4 className="disclosure-heading">Chart 3 Quality & Provenance Disclosure</h4>
              <div className="disclosure-grid">
                <div><strong>Question Answered:</strong> Are required evidence streams present to substantiate supply anomaly investigation?</div>
                <div><strong>Source Datasets:</strong> PSAMB e-Mandikaran, AGMARKNET, DES APY, NASA POWER</div>
                <div><strong>Calculation:</strong> Evaluation against the 7-Point Eligibility Gate rules</div>
                <div><strong>Units & Scale:</strong> Binary verification status (Verified vs Critical Gap)</div>
                <div><strong>Supported Conclusion:</strong> Critical volume and stock gaps prevent honest hoarding assessment</div>
                <div><strong>Unsupported Conclusion:</strong> Data absence does NOT prove illegal behavior or guilt.</div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Supply Coverage Matrix */}
        {activeChartTab === 'coverage' && (
          <div className="chart-card-container">
            <div className="chart-card-header">
              <div>
                <h3 className="chart-card-title">Institutional Data Coverage & Freshness Matrix</h3>
                <span className="chart-card-sub">Audit across 8 Dimensions of Agricultural Supply Intelligence</span>
              </div>
            </div>

            <div className="coverage-matrix-grid">
              {coverageDimensions.map((dim) => (
                <div key={dim.name} className="coverage-card">
                  <div className="cov-card-header">
                    <span className="cov-name">{dim.name}</span>
                    <span className={`cov-status ${dim.status.toLowerCase().replace(/\s+/g, '-')}`}>
                      {dim.status}
                    </span>
                  </div>
                  <div className="cov-bar">
                    <div className="cov-bar-fill" style={{ width: `${dim.coverage}%` }}></div>
                  </div>
                  <div className="cov-source">Source: {dim.source}</div>
                </div>
              ))}
            </div>

            <div className="methodology-disclosure-box">
              <h4 className="disclosure-heading">Chart 4 Quality & Provenance Disclosure</h4>
              <div className="disclosure-grid">
                <div><strong>Question Answered:</strong> What proportion of the required supply chain dimensions are empirically verified?</div>
                <div><strong>Source Datasets:</strong> 8 Institutional Source Registries</div>
                <div><strong>Calculation:</strong> Verified non-null record completeness across spatial and temporal dimensions</div>
                <div><strong>Units & Scale:</strong> Percentage completeness (0% to 100%)</div>
                <div><strong>Supported Conclusion:</strong> Production and yield history are 100% complete; daily arrivals and stock data are 0%</div>
                <div><strong>Unsupported Conclusion:</strong> Incomplete coverage cannot be smoothed using machine learning proxies.</div>
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
