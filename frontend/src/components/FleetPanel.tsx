import React from 'react';
import type { Robot } from '../types';
import { Bot, Battery, AlertTriangle, Navigation, Eye, Truck } from 'lucide-react';

interface FleetPanelProps {
  robots: Robot[];
  onTriggerRobotFailure: (robotId: string) => void;
}

export const FleetPanel: React.FC<FleetPanelProps> = ({
  robots,
  onTriggerRobotFailure
}) => {
  const getRoleIcon = (capabilities: string[]) => {
    if (capabilities.includes('carrier')) return <Truck className="w-4 h-4 text-amber-400" />;
    if (capabilities.includes('inspector')) return <Eye className="w-4 h-4 text-purple-400" />;
    return <Navigation className="w-4 h-4 text-[#76b900]" />;
  };

  const getStateBadge = (state: string) => {
    switch (state) {
      case 'idle':
        return <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 font-mono border border-slate-700">IDLE</span>;
      case 'navigating':
        return <span className="px-2 py-0.5 rounded text-[10px] bg-blue-950 text-blue-300 font-mono border border-blue-500/40">NAVIGATING</span>;
      case 'inspecting':
        return <span className="px-2 py-0.5 rounded text-[10px] bg-purple-950 text-purple-300 font-mono border border-purple-500/40 animate-pulse">INSPECTING</span>;
      case 'transporting':
        return <span className="px-2 py-0.5 rounded text-[10px] bg-amber-950 text-amber-300 font-mono border border-amber-500/40">TRANSPORTING</span>;
      case 'offline':
      case 'degraded':
        return <span className="px-2 py-0.5 rounded text-[10px] bg-red-950 text-red-300 font-mono border border-red-500/60 font-bold animate-ping">DEGRADED / OFFLINE</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 font-mono">{state.toUpperCase()}</span>;
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#070b14] border border-slate-800 rounded-lg overflow-hidden select-none">
      {/* Panel Header */}
      <div className="px-4 py-3 border-b border-slate-800/80 bg-[#090e1a] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bot className="w-4 h-4 text-[#76b900]" />
          <h2 className="text-xs font-bold tracking-wider text-white font-mono uppercase">Fleet Status</h2>
        </div>
        <span className="text-[10px] font-mono text-slate-400">
          OPERATIONAL: <strong className="text-emerald-400">{robots.filter(r => r.state !== 'offline').length}</strong>/{robots.length}
        </span>
      </div>

      {/* Robot Cards List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {robots.map((robot) => {
          const isFailed = robot.state === 'offline' || robot.state === 'degraded';
          const batteryColor =
            robot.battery > 50
              ? 'bg-[#76b900]'
              : robot.battery > 20
              ? 'bg-amber-500'
              : 'bg-red-500';

          return (
            <div
              key={robot.id}
              className={`p-3 rounded-lg border transition-all ${
                isFailed
                  ? 'bg-red-950/20 border-red-600/50 shadow-lg shadow-red-950/30'
                  : 'bg-[#080d1b] border-slate-800/80 hover:border-slate-700'
              }`}
            >
              {/* Header: Name + State */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded bg-slate-800 border border-slate-700">
                    {getRoleIcon(robot.capabilities)}
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-white font-mono">{robot.name}</h3>
                    <p className="text-[10px] text-slate-500 font-mono">ID: {robot.id}</p>
                  </div>
                </div>
                {getStateBadge(robot.state)}
              </div>

              {/* Battery & Kinematics */}
              <div className="space-y-1.5 my-2">
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                  <span className="flex items-center space-x-1">
                    <Battery className="w-3 h-3 text-slate-400" />
                    <span>Battery SoC</span>
                  </span>
                  <span className="font-bold text-white">{robot.battery.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${batteryColor}`}
                    style={{ width: `${Math.round(robot.battery)}%` }}
                  />
                </div>
              </div>

              {/* Coordinates & Capabilities */}
              <div className="grid grid-cols-2 gap-2 text-[10px] font-mono bg-slate-900/60 p-2 rounded border border-slate-800/60 mb-2">
                <div>
                  <span className="text-slate-500 block">COORDINATES</span>
                  <span className="text-slate-200">
                    X: {robot.position.x.toFixed(1)}m | Y: {robot.position.y.toFixed(1)}m
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block">HEADING / SPEED</span>
                  <span className="text-slate-200">
                    {robot.heading.toFixed(0)}° / {robot.velocity.toFixed(1)} m/s
                  </span>
                </div>
              </div>

              {/* Carried Cargo Tag */}
              {robot.carried_package_id && (
                <div className="px-2 py-1 rounded bg-amber-950/40 border border-amber-600/40 text-[10px] font-mono text-amber-300 mb-2 flex items-center justify-between">
                  <span>CARGO LOAD:</span>
                  <strong className="text-amber-200">{robot.carried_package_id}</strong>
                </div>
              )}

              {/* Failure Alert Box or Trigger Action */}
              {isFailed ? (
                <div className="px-2 py-1.5 rounded bg-red-900/30 border border-red-500/40 text-[10px] font-mono text-red-300 flex items-center space-x-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
                  <span>SUBSYSTEM FAILURE: Task reassigned to healthy node.</span>
                </div>
              ) : (
                <button
                  onClick={() => onTriggerRobotFailure(robot.id)}
                  className="w-full mt-1 py-1 rounded bg-slate-800/70 hover:bg-red-950 hover:text-red-300 hover:border-red-700/50 border border-slate-700/60 text-[10px] font-mono text-slate-400 transition"
                >
                  Simulate Subsystem Fault
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
