import React, { useState } from 'react';
import type { Robot, Package, Obstacle, WarehouseZone } from '../types';

interface WarehouseMapProps {
  robots: Robot[];
  packages: Package[];
  obstacles: Obstacle[];
  zones: WarehouseZone[];
  onSelectRobot?: (robot: Robot) => void;
}

export const WarehouseMap: React.FC<WarehouseMapProps> = ({
  robots,
  packages,
  obstacles,
  zones,
  onSelectRobot
}) => {
  const [selectedEntity, setSelectedEntity] = useState<any>(null);

  // Warehouse physical dimension in meters
  const WORLD_WIDTH = 30.0;
  const WORLD_HEIGHT = 20.0;

  // Transform world meters to SVG canvas coordinates (viewBox 0 0 1000 666)
  const scaleX = (x: number) => (x / WORLD_WIDTH) * 1000;
  const scaleY = (y: number) => (y / WORLD_HEIGHT) * 666;

  const getRobotColor = (robot: Robot) => {
    if (robot.state === 'offline' || robot.state === 'degraded') return '#ef4444'; // Red
    if (robot.state === 'inspecting') return '#a855f7'; // Purple
    if (robot.state === 'transporting') return '#f59e0b'; // Amber
    if (robot.state === 'navigating') return '#3b82f6'; // Blue
    return '#76b900'; // NVIDIA Green
  };

  return (
    <div className="relative w-full h-full bg-[#080d1a] border border-slate-800 rounded-lg overflow-hidden flex flex-col shadow-inner select-none">
      {/* Top Map HUD overlay */}
      <div className="absolute top-3 left-4 z-10 flex items-center space-x-3 pointer-events-none">
        <div className="bg-slate-900/90 border border-slate-700/70 backdrop-blur-md px-3 py-1.5 rounded flex items-center space-x-2 text-xs font-mono text-slate-300">
          <span className="w-2 h-2 rounded-full bg-[#76b900] animate-pulse" />
          <span className="font-bold text-white tracking-wider">WAREHOUSE DIGITAL TWIN</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-400">Scale: 1m = 33.3px (30m x 20m)</span>
        </div>
      </div>

      {/* SVG Canvas Map */}
      <div className="relative flex-1 w-full h-full flex items-center justify-center p-2">
        <svg
          viewBox="0 0 1000 666"
          className="w-full h-full max-h-[620px] rounded border border-slate-800/80 bg-[#050914] shadow-2xl"
        >
          <defs>
            {/* Grid Pattern */}
            <pattern id="grid" width="33.33" height="33.3" patternUnits="userSpaceOnUse">
              <path d="M 33.33 0 L 0 0 0 33.3" fill="none" stroke="#1e293b" strokeWidth="0.7" strokeOpacity="0.4" />
            </pattern>
            {/* Warning Hatch Pattern for Obstacles */}
            <pattern id="hatch" width="8" height="8" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
              <line x1="0" y1="0" x2="0" y2="8" stroke="#ef4444" strokeWidth="2" strokeOpacity="0.4" />
            </pattern>
            {/* Scanner Pulse Filter */}
            <radialGradient id="scannerGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#a855f7" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#a855f7" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Background Grid */}
          <rect width="1000" height="666" fill="url(#grid)" />

          {/* Zones */}
          {zones.map((zone) => {
            const x = scaleX(zone.x_min);
            const y = scaleY(zone.y_min);
            const width = scaleX(zone.x_max - zone.x_min);
            const height = scaleY(zone.y_max - zone.y_min);

            return (
              <g key={zone.id} className="cursor-pointer" onClick={() => setSelectedEntity(zone)}>
                <rect
                  x={x}
                  y={y}
                  width={width}
                  height={height}
                  fill={zone.color}
                  fillOpacity={zone.id === 'quarantine' ? '0.12' : '0.06'}
                  stroke={zone.color}
                  strokeWidth="1.5"
                  strokeDasharray={zone.id === 'transit_corridor' ? '6,4' : 'none'}
                  rx="6"
                />
                <text
                  x={x + 12}
                  y={y + 22}
                  fill={zone.color}
                  fontSize="12"
                  fontFamily="monospace"
                  fontWeight="bold"
                  letterSpacing="1"
                >
                  {zone.name.toUpperCase()}
                </text>
              </g>
            );
          })}

          {/* Obstacles */}
          {obstacles.map((obs) => {
            const cx = scaleX(obs.position.x);
            const cy = scaleY(obs.position.y);
            const r = (obs.radius / WORLD_WIDTH) * 1000;

            return (
              <g key={obs.id} className="cursor-pointer" onClick={() => setSelectedEntity(obs)}>
                <circle cx={cx} cy={cy} r={r} fill="#1e293b" stroke="#475569" strokeWidth="2" />
                <circle cx={cx} cy={cy} r={r} fill="url(#hatch)" />
                <text
                  x={cx}
                  y={cy + 3}
                  textAnchor="middle"
                  fill="#94a3b8"
                  fontSize="9"
                  fontFamily="monospace"
                >
                  {obs.id.replace('obs_', '').toUpperCase()}
                </text>
              </g>
            );
          })}

          {/* Packages */}
          {packages.map((pkg) => {
            const px = scaleX(pkg.position.x);
            const py = scaleY(pkg.position.y);
            const isDamaged = pkg.state === 'damaged';
            const isQuarantined = pkg.state === 'quarantined';

            return (
              <g
                key={pkg.id}
                className="cursor-pointer transition-transform duration-300"
                onClick={() => setSelectedEntity(pkg)}
              >
                {/* Pulsing beacon if damaged */}
                {isDamaged && (
                  <circle cx={px} cy={py} r="18" fill="none" stroke="#ef4444" strokeWidth="1.5" strokeOpacity="0.8">
                    <animate attributeName="r" values="10;24;10" dur="1.8s" repeatCount="indefinite" />
                    <animate attributeName="stroke-opacity" values="0.9;0.1;0.9" dur="1.8s" repeatCount="indefinite" />
                  </circle>
                )}

                <rect
                  x={px - 10}
                  y={py - 10}
                  width="20"
                  height="20"
                  rx="3"
                  fill={isQuarantined ? '#10b981' : isDamaged ? '#ef4444' : '#3b82f6'}
                  stroke="#ffffff"
                  strokeWidth="1.2"
                />

                <text
                  x={px}
                  y={py + 3}
                  textAnchor="middle"
                  fill="#ffffff"
                  fontSize="8"
                  fontWeight="bold"
                  fontFamily="sans-serif"
                >
                  {isDamaged ? '!' : 'P'}
                </text>

                <text
                  x={px}
                  y={py + 22}
                  textAnchor="middle"
                  fill={isDamaged ? '#f87171' : '#94a3b8'}
                  fontSize="9"
                  fontFamily="monospace"
                  fontWeight="bold"
                >
                  {pkg.id} {isDamaged ? '[DAMAGED]' : isQuarantined ? '[SECURE]' : ''}
                </text>
              </g>
            );
          })}

          {/* Robot Paths / Waypoint Trajectories */}
          {robots.map((robot) => {
            if (!robot.target_position) return null;
            const rx = scaleX(robot.position.x);
            const ry = scaleY(robot.position.y);
            const tx = scaleX(robot.target_position.x);
            const ty = scaleY(robot.target_position.y);
            const color = getRobotColor(robot);

            return (
              <g key={`path-${robot.id}`}>
                <line
                  x1={rx}
                  y1={ry}
                  x2={tx}
                  y2={ty}
                  stroke={color}
                  strokeWidth="1.8"
                  strokeDasharray="5,5"
                  strokeOpacity="0.7"
                />
                <circle cx={tx} cy={ty} r="4" fill="none" stroke={color} strokeWidth="1.5" />
              </g>
            );
          })}

          {/* Robots */}
          {robots.map((robot) => {
            const rx = scaleX(robot.position.x);
            const ry = scaleY(robot.position.y);
            const color = getRobotColor(robot);
            const isFailed = robot.state === 'offline' || robot.state === 'degraded';
            const isInspecting = robot.state === 'inspecting';

            return (
              <g
                key={robot.id}
                className="cursor-pointer"
                onClick={() => {
                  setSelectedEntity(robot);
                  onSelectRobot?.(robot);
                }}
              >
                {/* Inspection Scanner Cone */}
                {isInspecting && (
                  <circle cx={rx} cy={ry} r="35" fill="url(#scannerGlow)">
                    <animate attributeName="r" values="25;45;25" dur="1.5s" repeatCount="indefinite" />
                  </circle>
                )}

                {/* Failure Halo strobe */}
                {isFailed && (
                  <circle cx={rx} cy={ry} r="26" fill="none" stroke="#ef4444" strokeWidth="2.5">
                    <animate attributeName="r" values="18;34;18" dur="1s" repeatCount="indefinite" />
                    <animate attributeName="stroke-opacity" values="1;0.2;1" dur="1s" repeatCount="indefinite" />
                  </circle>
                )}

                {/* Robot Main Body */}
                <circle
                  cx={rx}
                  cy={ry}
                  r="15"
                  fill="#0b1329"
                  stroke={color}
                  strokeWidth="2.5"
                  className="transition-colors duration-300"
                />

                {/* Heading Direction Arrow */}
                <g transform={`rotate(${robot.heading}, ${rx}, ${ry})`}>
                  <polygon
                    points={`${rx + 16},${ry} ${rx + 9},${ry - 5} ${rx + 9},${ry + 5}`}
                    fill={color}
                  />
                </g>

                {/* Inner Icon / Status */}
                {isFailed ? (
                  <text x={rx} y={ry + 4} textAnchor="middle" fill="#ef4444" fontSize="12" fontWeight="bold">
                    ✕
                  </text>
                ) : (
                  <circle cx={rx} cy={ry} r="4" fill={color} />
                )}

                {/* Robot Label & State Pill */}
                <g transform={`translate(${rx}, ${ry - 22})`}>
                  <rect
                    x="-42"
                    y="-12"
                    width="84"
                    height="18"
                    rx="3"
                    fill="#030712"
                    fillOpacity="0.9"
                    stroke={color}
                    strokeWidth="1"
                  />
                  <text
                    x="0"
                    y="0"
                    textAnchor="middle"
                    fill="#f8fafc"
                    fontSize="9"
                    fontFamily="monospace"
                    fontWeight="bold"
                  >
                    {robot.id.toUpperCase()} ({robot.battery.toFixed(0)}%)
                  </text>
                </g>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Bottom Map Legend */}
      <div className="h-10 bg-[#060a14] border-t border-slate-800/80 px-4 flex items-center justify-between text-[11px] font-mono text-slate-400">
        <div className="flex items-center space-x-4">
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#76b900]" />
            <span>Active / Scout</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
            <span>Navigating</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
            <span>Inspecting</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
            <span>Transporting</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
            <span className="text-red-400 font-bold">Offline / Failed</span>
          </span>
        </div>
        <div>
          {selectedEntity && (
            <span className="text-slate-300">
              Selected: <strong className="text-white">{selectedEntity.name || selectedEntity.id}</strong>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
