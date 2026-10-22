import React, { useState, useEffect } from 'react';

interface TelemetryNode {
  id: string;
  name: string;
  type: 'mandi' | 'silo' | 'procurement';
  x: number;
  y: number;
  arrivals: string;
  price: string;
  status: 'normal' | 'divergent';
}

const NODES: TelemetryNode[] = [
  { id: 'LDH', name: 'Ludhiana Central', type: 'silo', x: 230, y: 155, arrivals: '18,450 qtl', price: '₹2,425/qtl', status: 'normal' },
  { id: 'SGR', name: 'Sangrur Grain Terminal', type: 'mandi', x: 260, y: 220, arrivals: '14,200 qtl', price: '₹2,410/qtl', status: 'normal' },
  { id: 'PTA', name: 'Patiala Storage Complex', type: 'silo', x: 340, y: 195, arrivals: '16,800 qtl', price: '₹2,430/qtl', status: 'normal' },
  { id: 'BTI', name: 'Bathinda Supply Hub', type: 'procurement', x: 135, y: 230, arrivals: '22,100 qtl', price: '₹2,415/qtl', status: 'normal' },
  { id: 'ASR', name: 'Amritsar North Mandi', type: 'mandi', x: 165, y: 85, arrivals: '19,300 qtl', price: '₹2,435/qtl', status: 'normal' },
  { id: 'JAL', name: 'Jalandhar Doaba Center', type: 'mandi', x: 205, y: 120, arrivals: '15,600 qtl', price: '₹2,420/qtl', status: 'normal' },
];

export const HeroTelemetryVisualizer: React.FC<{ className?: string }> = ({ className = '' }) => {
  const [selectedNode, setSelectedNode] = useState<TelemetryNode>(NODES[0]);
  const [simulationMode, setSimulationMode] = useState<'equilibrium' | 'divergence'>('equilibrium');
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [radarAngle, setRadarAngle] = useState<number>(0);

  useEffect(() => {
    if (isPaused) return;
    const interval = setInterval(() => {
      setRadarAngle((prev) => (prev + 1.5) % 360);
    }, 30);
    return () => clearInterval(interval);
  }, [isPaused]);

  const isDivergent = simulationMode === 'divergence';

  return (
    <div
      className={`hero-telemetry-card ${className}`}
      role="region"
      aria-label="Agricultural Supply Telemetry Hub"
    >
      {/* Top Telemetry Header */}
      <div className="telemetry-header">
        <div className="telemetry-live-badge">
          <span className={`live-pulse-dot ${isDivergent ? 'anomaly' : 'normal'}`} />
          <span className="live-badge-text">
            {isDivergent ? 'SIGNAL DIVERGENCE ACTIVE' : 'NETWORK EQUILIBRIUM'}
          </span>
        </div>

        <div className="telemetry-mode-toggles">
          <button
            type="button"
            className={`telemetry-toggle-btn ${!isDivergent ? 'active' : ''}`}
            onClick={() => setSimulationMode('equilibrium')}
            aria-pressed={!isDivergent}
          >
            Normal Flow
          </button>
          <button
            type="button"
            className={`telemetry-toggle-btn anomaly ${isDivergent ? 'active' : ''}`}
            onClick={() => setSimulationMode('divergence')}
            aria-pressed={isDivergent}
          >
            Simulate Divergence
          </button>
          <button
            type="button"
            className="telemetry-pause-btn"
            onClick={() => setIsPaused(!isPaused)}
            title={isPaused ? 'Resume Pulse Animation' : 'Pause Animation'}
            aria-label={isPaused ? 'Resume Animation' : 'Pause Animation'}
          >
            {isPaused ? '▶' : '⏸'}
          </button>
        </div>
      </div>

      {/* Main Interactive Radar & Flow Canvas */}
      <div className="telemetry-canvas-area">
        <svg
          viewBox="0 0 440 300"
          className="telemetry-svg"
          role="img"
          aria-label="Punjab Foodgrain Transit Flow Radar"
        >
          <defs>
            {/* Grid Pattern */}
            <pattern id="teleGrid" width="24" height="24" patternUnits="userSpaceOnUse">
              <path d="M 24 0 L 0 0 0 24" fill="none" stroke="rgba(203, 213, 225, 0.35)" strokeWidth="0.75" />
            </pattern>

            {/* Linear Gradients for Flow Lines */}
            <linearGradient id="flowNormal" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#059669" stopOpacity="0.3" />
            </linearGradient>

            <linearGradient id="flowAnomaly" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ef4444" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.4" />
            </linearGradient>

            {/* Radar Sweep Gradient */}
            <radialGradient id="radarGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor={isDivergent ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.12)'} />
              <stop offset="100%" stopColor="transparent" />
            </radialGradient>
          </defs>

          {/* Background Grid & Radar Rings */}
          <rect width="100%" height="100%" fill="url(#teleGrid)" rx="12" />
          
          {/* Concentric Radar Distance Rings */}
          <circle cx="220" cy="150" r="130" fill="none" stroke="rgba(203, 213, 225, 0.5)" strokeWidth="1" strokeDasharray="4 4" />
          <circle cx="220" cy="150" r="85" fill="none" stroke="rgba(203, 213, 225, 0.6)" strokeWidth="1" strokeDasharray="3 3" />
          <circle cx="220" cy="150" r="40" fill="url(#radarGlow)" stroke="rgba(203, 213, 225, 0.8)" strokeWidth="1" />

          {/* Radar Sweep Beam */}
          {!isPaused && (
            <line
              x1="220"
              y1="150"
              x2={220 + 130 * Math.cos((radarAngle * Math.PI) / 180)}
              y2={150 + 130 * Math.sin((radarAngle * Math.PI) / 180)}
              stroke={isDivergent ? '#f87171' : '#34d399'}
              strokeWidth="1.5"
              strokeOpacity="0.7"
            />
          )}

          {/* Supply Flow Transit Connectors */}
          <g className="flow-lines">
            {/* Ludhiana Hub Connections */}
            <line x1="230" y1="155" x2="165" y2="85" stroke={isDivergent ? 'url(#flowAnomaly)' : 'url(#flowNormal)'} strokeWidth={isDivergent ? '2.5' : '2'} strokeDasharray={isPaused ? 'none' : '6 4'} className={!isPaused ? 'transit-anim' : ''} />
            <line x1="230" y1="155" x2="205" y2="120" stroke={isDivergent ? 'url(#flowAnomaly)' : 'url(#flowNormal)'} strokeWidth={isDivergent ? '2.5' : '2'} strokeDasharray={isPaused ? 'none' : '6 4'} className={!isPaused ? 'transit-anim' : ''} />
            <line x1="230" y1="155" x2="260" y2="220" stroke={isDivergent ? 'url(#flowAnomaly)' : 'url(#flowNormal)'} strokeWidth={isDivergent ? '2.5' : '2'} strokeDasharray={isPaused ? 'none' : '6 4'} className={!isPaused ? 'transit-anim' : ''} />
            <line x1="230" y1="155" x2="340" y2="195" stroke={isDivergent ? 'url(#flowAnomaly)' : 'url(#flowNormal)'} strokeWidth={isDivergent ? '2.5' : '2'} strokeDasharray={isPaused ? 'none' : '6 4'} className={!isPaused ? 'transit-anim' : ''} />
            <line x1="230" y1="155" x2="135" y2="230" stroke={isDivergent ? 'url(#flowAnomaly)' : 'url(#flowNormal)'} strokeWidth={isDivergent ? '2.5' : '2'} strokeDasharray={isPaused ? 'none' : '6 4'} className={!isPaused ? 'transit-anim' : ''} />
            <line x1="165" y1="85" x2="205" y2="120" stroke="rgba(148, 163, 184, 0.4)" strokeWidth="1.2" strokeDasharray="3 3" />
            <line x1="260" y1="220" x2="340" y2="195" stroke="rgba(148, 163, 184, 0.4)" strokeWidth="1.2" strokeDasharray="3 3" />
            <line x1="135" y1="230" x2="260" y2="220" stroke="rgba(148, 163, 184, 0.4)" strokeWidth="1.2" strokeDasharray="3 3" />
          </g>

          {/* Interactive Geographic Telemetry Nodes */}
          {NODES.map((node) => {
            const isSelected = selectedNode.id === node.id;
            return (
              <g
                key={node.id}
                className="telemetry-node-group"
                onClick={() => setSelectedNode(node)}
                style={{ cursor: 'pointer' }}
              >
                {/* Outer halo */}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={isSelected ? 16 : 11}
                  fill={isDivergent ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)'}
                  stroke={isDivergent ? '#ef4444' : '#10b981'}
                  strokeWidth={isSelected ? 2 : 1}
                  className={!isPaused ? 'node-pulse' : ''}
                />
                {/* Core dot */}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={isSelected ? 6 : 4.5}
                  fill={isDivergent ? '#dc2626' : '#059669'}
                />
                {/* Node Label */}
                <text
                  x={node.x}
                  y={node.y - 12}
                  textAnchor="middle"
                  className="telemetry-node-label"
                  fill="#1e293b"
                  fontSize="10"
                  fontWeight={isSelected ? '700' : '500'}
                >
                  {node.name.split(' ')[0]}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Floating Telemetry HUD Card for Selected Node */}
        <div className="telemetry-hud-card">
          <div className="hud-header">
            <span className="hud-title">{selectedNode.name}</span>
            <span className={`hud-badge ${selectedNode.type}`}>
              {selectedNode.type.toUpperCase()}
            </span>
          </div>

          <div className="hud-metrics">
            <div className="hud-metric-row">
              <span className="hud-metric-label">Wholesale Modal Price:</span>
              <span className={`hud-metric-value ${isDivergent ? 'text-spike' : ''}`}>
                {isDivergent ? '₹3,150 / qtl (+29.8%)' : selectedNode.price}
              </span>
            </div>
            <div className="hud-metric-row">
              <span className="hud-metric-label">Mandi Inflow Volume:</span>
              <span className={`hud-metric-value ${isDivergent ? 'text-drop' : ''}`}>
                {isDivergent ? '6,800 qtl (-63.1%)' : selectedNode.arrivals}
              </span>
            </div>
            <div className="hud-metric-row">
              <span className="hud-metric-label">Statistical Robust Z-Score:</span>
              <span className="hud-metric-value font-mono">
                {isDivergent ? 'Price: +3.82 | Arrival: -4.12' : 'Price: +0.24 | Arrival: -0.18'}
              </span>
            </div>
          </div>

          <div className="hud-footer">
            <span className="hud-footer-text">
              {isDivergent
                ? '⚠️ CONVERGENT ANOMALY: Prompt for Targeted Mandi Field Inspection'
                : '✓ Baseline Normal: All 23 district supply streams within ±2σ bounds'}
            </span>
          </div>
        </div>
      </div>

      {/* Bottom Features Strip */}
      <div className="telemetry-features-strip">
        <div className="telemetry-chip">
          <span className="chip-icon">🏛️</span>
          <span>23 Punjab Districts</span>
        </div>
        <div className="telemetry-chip">
          <span className="chip-icon">⚖️</span>
          <span>Robust MAD Z-Scores</span>
        </div>
        <div className="telemetry-chip">
          <span className="chip-icon">🔒</span>
          <span>Zero Fabricated Intent</span>
        </div>
      </div>
    </div>
  );
};

export default HeroTelemetryVisualizer;
