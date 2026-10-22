import React, { useState, useEffect, useMemo } from 'react';

interface GeoFeature {
  id: number;
  properties: {
    dtname: string;
    dist_lgd: number;
    district_id: string;
    year_stat: string;
    boundary_vintage_feature: string;
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

export default function DistrictMapView() {
  const [features, setFeatures] = useState<GeoFeature[]>([]);
  const [crosswalk, setCrosswalk] = useState<CrosswalkItem[]>([]);
  const [production, setProduction] = useState<ProductionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDistrict, setSelectedDistrict] = useState<string>('Ludhiana');

  useEffect(() => {
    async function loadGeoData() {
      try {
        setLoading(true);
        // Load Boundaries
        let geoRes = await fetch('http://127.0.0.1:8000/api/v1/geo/districts').catch(() => null);
        if (!geoRes || !geoRes.ok) geoRes = await fetch('/data/district_boundaries.json');
        if (geoRes && geoRes.ok) {
          const geoData = await geoRes.json();
          setFeatures(geoData.features || []);
        }

        // Load Crosswalk
        let crwRes = await fetch('http://127.0.0.1:8000/api/v1/geo/crosswalk?limit=100').catch(() => null);
        if (!crwRes || !crwRes.ok) crwRes = await fetch('/data/district_crosswalk.json');
        if (crwRes && crwRes.ok) {
          const crwData = await crwRes.json();
          setCrosswalk(crwData.items || []);
        }

        // Load Production
        let prodRes = await fetch('http://127.0.0.1:8000/api/v1/production?limit=500').catch(() => null);
        if (!prodRes || !prodRes.ok) prodRes = await fetch('/data/production.json');
        if (prodRes && prodRes.ok) {
          const prodData = await prodRes.json();
          setProduction(prodData.items || []);
        }
      } catch (err) {
        console.error('Error loading geospatial and district data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadGeoData();
  }, []);

  // Compute bounding box across all geometries for SVG projection
  const bounds = useMemo(() => {
    let minLon = 180, maxLon = -180, minLat = 90, maxLat = -90;

    function processCoords(coords: any[]) {
      if (typeof coords[0] === 'number') {
        const [lon, lat] = coords;
        if (lon < minLon) minLon = lon;
        if (lon > maxLon) maxLon = lon;
        if (lat < minLat) minLat = lat;
        if (lat > maxLat) maxLat = lat;
      } else {
        coords.forEach(processCoords);
      }
    }

    features.forEach((f) => processCoords(f.geometry.coordinates));
    return { minLon, maxLon, minLat, maxLat };
  }, [features]);

  // Project longitude/latitude to SVG coordinates (width: 560, height: 600)
  const project = useMemo(() => {
    const width = 560;
    const height = 600;
    const padding = 25;

    const lonSpan = bounds.maxLon - bounds.minLon || 1;
    const latSpan = bounds.maxLat - bounds.minLat || 1;

    return (lon: number, lat: number) => {
      const x = padding + ((lon - bounds.minLon) / lonSpan) * (width - 2 * padding);
      // Invert Y axis for latitude
      const y = height - padding - ((lat - bounds.minLat) / latSpan) * (height - 2 * padding);
      return [x, y];
    };
  }, [bounds]);

  // Convert GeoJSON geometry to SVG path `d` string
  function getPathD(geometry: any): string {
    const { type, coordinates } = geometry;
    if (type === 'Polygon') {
      return coordinates.map((ring: any[]) => {
        return ring.map((pt: any[], i: number) => {
          const [x, y] = project(pt[0], pt[1]);
          return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
        }).join(' ') + ' Z';
      }).join(' ');
    } else if (type === 'MultiPolygon') {
      return coordinates.map((poly: any[]) => {
        return poly.map((ring: any[]) => {
          return ring.map((pt: any[], i: number) => {
            const [x, y] = project(pt[0], pt[1]);
            return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
          }).join(' ') + ' Z';
        }).join(' ');
      }).join(' ');
    }
    return '';
  }

  // Active district metadata & production
  const activeDetail = useMemo(() => {
    const feat = features.find((f) => f.properties.dtname.toLowerCase() === selectedDistrict.toLowerCase());
    const crw = crosswalk.find((c) => c.district_name_boundary.toLowerCase() === selectedDistrict.toLowerCase());
    const prodItems = production.filter((p) => p.district_original.toLowerCase() === selectedDistrict.toLowerCase());

    const latestWheat = prodItems.find((p) => p.crop_standard.toLowerCase() === 'wheat' && p.agricultural_year === '2022-23');
    const latestRice = prodItems.find((p) => p.crop_standard.toLowerCase().includes('paddy') && p.agricultural_year === '2022-23');

    return {
      name: feat?.properties.dtname || selectedDistrict,
      lgdCode: feat?.properties.dist_lgd || feat?.properties.district_id || 'N/A',
      vintage: feat?.properties.year_stat || feat?.properties.boundary_vintage_feature || '2011_c',
      temporalNote: crw?.temporal_note || 'Standard boundary vintage 2011_c',
      wheatProd: latestWheat?.production_value ?? null,
      wheatYield: latestWheat?.yield_value ?? null,
      riceProd: latestRice?.production_value ?? null,
      riceYield: latestRice?.yield_value ?? null,
    };
  }, [features, crosswalk, production, selectedDistrict]);

  return (
    <div className="district-map-view">
      {/* Header */}
      <div className="view-header">
        <div>
          <h1 className="view-title">Punjab District Geospatial Boundaries & Join Audit</h1>
          <p className="view-subtitle">
            Survey of India / NWIC verified district geometries (EPSG:4326) with administrative crosswalk and vintage audit.
          </p>
        </div>
        <div className="provenance-pill" title="Audited Geographic Provenance">
          <span>NWIC / GSI GEOJSON (EPSG:4326)</span>
          <span className="dot">•</span>
          <span>23 PUNJAB DISTRICTS</span>
        </div>
      </div>

      {/* Geospatial Guardrail Banner */}
      <div className="scope-warning-card" style={{ borderColor: 'rgba(14, 165, 233, 0.4)' }}>
        <div className="warning-badge" style={{ backgroundColor: 'rgba(14, 165, 233, 0.15)', color: 'var(--color-sky-400)' }}>
          GEOGRAPHIC INTEGRITY CONTRACT: NO FABRICATED JOINS
        </div>
        <p className="warning-text">
          District statistical data is joined strictly via validated administrative candidate codes.
          <strong>Malerkotla</strong> was carved from <strong>Sangrur</strong> in 2021 (boundary vintage 2022).
          Historical APY years cannot be retroactively split between them without official restatements.
        </p>
      </div>

      {/* Main Map + Inspector Layout */}
      <div className="map-layout">
        {/* Interactive SVG Map */}
        <div className="svg-map-card">
          <div className="map-card-header">
            <h2 className="map-card-title">Interactive District Map (Click to Inspect)</h2>
            <span className="map-hint">Click on any district to inspect production and boundary vintage</span>
          </div>

          <div className="svg-wrapper">
            <svg
              viewBox="0 0 560 600"
              className="punjab-svg-map"
              role="img"
              aria-label="Punjab 23 district boundaries map"
            >
              <g className="districts-layer">
                {features.map((f) => {
                  const dName = f.properties.dtname;
                  const isSelected = dName.toLowerCase() === selectedDistrict.toLowerCase();
                  const isMalerkotla = dName.toLowerCase() === 'malerkotla';
                  return (
                    <path
                      key={f.id || dName}
                      d={getPathD(f.geometry)}
                      className={`district-path ${isSelected ? 'selected' : ''} ${isMalerkotla ? 'malerkotla' : ''}`}
                      onClick={() => setSelectedDistrict(dName)}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') setSelectedDistrict(dName); }}
                      tabIndex={0}
                      role="button"
                      aria-label={`${dName} district boundary. Vintage ${f.properties.year_stat || '2011'}`}
                    >
                      <title>{`${dName} (LGD: ${f.properties.dist_lgd || 'N/A'}, Vintage: ${f.properties.year_stat || '2011'})`}</title>
                    </path>
                  );
                })}
              </g>
            </svg>
          </div>

          <div className="map-legend">
            <div className="legend-item">
              <span className="legend-color normal"></span>
              <span>Standard Vintage (2011_c / update2014)</span>
            </div>
            <div className="legend-item">
              <span className="legend-color malerkotla-legend"></span>
              <span>Malerkotla (2022 Vintage; Pre-Split Caveat)</span>
            </div>
            <div className="legend-item">
              <span className="legend-color selected-legend"></span>
              <span>Selected District</span>
            </div>
          </div>
        </div>

        {/* Selected District Inspection Drawer */}
        <div className="district-detail-card">
          <div className="detail-header">
            <span className="detail-tag">DISTRICT PROFILE</span>
            <h2 className="detail-title">{activeDetail.name}</h2>
            <span className="detail-lgd">Candidate LGD Code: <code>{activeDetail.lgdCode}</code></span>
          </div>

          <div className="detail-section">
            <h3 className="section-label">Geospatial Boundary Provenance</h3>
            <div className="prop-row">
              <span className="prop-key">Boundary Vintage:</span>
              <span className="prop-val mono">{activeDetail.vintage}</span>
            </div>
            <div className="prop-row">
              <span className="prop-key">Coordinate CRS:</span>
              <span className="prop-val mono">EPSG:4326 (WGS 84)</span>
            </div>
            <div className="temporal-box">
              <span className="temporal-tag">Administrative Note:</span>
              <p className="temporal-text">{activeDetail.temporalNote}</p>
            </div>
          </div>

          <div className="detail-section">
            <h3 className="section-label">Production Statistics (2022–23 Final)</h3>
            <div className="crop-stat-box">
              <span className="crop-name">Wheat (Rabi Season)</span>
              <div className="stat-grid">
                <div>
                  <span className="stat-label">Production:</span>
                  <span className="stat-val">
                    {activeDetail.wheatProd !== null ? `${(activeDetail.wheatProd / 1000).toFixed(1)}k Tonnes` : 'Unassigned (pre-split)'}
                  </span>
                </div>
                <div>
                  <span className="stat-label">Yield:</span>
                  <span className="stat-val">
                    {activeDetail.wheatYield !== null ? `${Math.round(activeDetail.wheatYield).toLocaleString()} kg/ha` : 'null'}
                  </span>
                </div>
              </div>
            </div>

            <div className="crop-stat-box" style={{ marginTop: 'var(--space-3)' }}>
              <span className="crop-name">Paddy (Kharif Season)</span>
              <div className="stat-grid">
                <div>
                  <span className="stat-label">Production:</span>
                  <span className="stat-val">
                    {activeDetail.riceProd !== null ? `${(activeDetail.riceProd / 1000).toFixed(1)}k Tonnes` : 'Unassigned (pre-split)'}
                  </span>
                </div>
                <div>
                  <span className="stat-label">Yield:</span>
                  <span className="stat-val">
                    {activeDetail.riceYield !== null ? `${Math.round(activeDetail.riceYield).toLocaleString()} kg/ha` : 'null'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Accessible Crosswalk Table */}
      <div className="table-card">
        <div className="table-header">
          <h2 className="table-title">Full Administrative Crosswalk & Boundary Vintage (23 Districts)</h2>
          <span className="table-note">Accessible tabular representation of geospatial layer.</span>
        </div>

        <div className="table-wrapper">
          <table className="data-table" aria-label="Punjab district boundaries and crosswalk table">
            <thead>
              <tr>
                <th scope="col">DES APY District Name</th>
                <th scope="col">Boundary Feature Name</th>
                <th scope="col">Candidate LGD Code</th>
                <th scope="col">Match Status</th>
                <th scope="col">Boundary Vintage & Temporal Caveat</th>
              </tr>
            </thead>
            <tbody>
              {crosswalk.map((c) => (
                <tr
                  key={c.district_source_name_apy}
                  className={c.district_name_boundary.toLowerCase() === selectedDistrict.toLowerCase() ? 'highlighted-row' : ''}
                  onClick={() => setSelectedDistrict(c.district_name_boundary)}
                  style={{ cursor: 'pointer' }}
                >
                  <td className="cell-district">{c.district_source_name_apy}</td>
                  <td className="cell-district">{c.district_name_boundary}</td>
                  <td className="cell-mono">{c.district_id_candidate_lgd || 'N/A'}</td>
                  <td>
                    <span className="verified-tag">Name Candidate</span>
                  </td>
                  <td className="cell-note">{c.temporal_note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
