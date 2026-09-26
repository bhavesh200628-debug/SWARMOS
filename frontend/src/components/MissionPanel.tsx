import React, { useState } from 'react';
import type { Mission } from '../types';
import { Send, Clock, ShieldCheck, FileText } from 'lucide-react';

interface MissionPanelProps {
  activeMission?: Mission | null;
  onSubmitMission: (prompt: string) => void;
  isLoading: boolean;
}

export const MissionPanel: React.FC<MissionPanelProps> = ({
  activeMission,
  onSubmitMission,
  isLoading
}) => {
  const [prompt, setPrompt] = useState(
    'Inspect Warehouse Zone B, identify damaged packages, move them to quarantine, and generate an incident report.'
  );

  const presets = [
    {
      label: 'Warehouse Incident Response (Hero Demo)',
      text: 'Inspect Zone B, locate damaged packages, move them to quarantine, and generate an incident report.'
    },
    {
      label: 'Perimeter Reconnaissance',
      text: 'Perform rapid spatial mapping of Transit Corridor and inspect loading bay perimeter.'
    },
    {
      label: 'Heavy Cargo Staging',
      text: 'Transport pallet pkg_a1 from Zone A to Zone B staging and verify placement.'
    }
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    onSubmitMission(prompt);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-500/40 font-mono">COMPLETED</span>;
      case 'in_progress':
        return <span className="px-2 py-0.5 rounded text-[10px] bg-blue-950 text-blue-400 border border-blue-500/40 font-mono animate-pulse">IN PROGRESS</span>;
      case 'assigned':
        return <span className="px-2 py-0.5 rounded text-[10px] bg-amber-950 text-amber-300 border border-amber-500/40 font-mono">ASSIGNED</span>;
      case 'failed':
        return <span className="px-2 py-0.5 rounded text-[10px] bg-red-950 text-red-400 border border-red-500/40 font-mono">FAILED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 border border-slate-700 font-mono">PENDING</span>;
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#070b14] border border-slate-800 rounded-lg overflow-hidden select-none">
      {/* Panel Header */}
      <div className="px-4 py-3 border-b border-slate-800/80 bg-[#090e1a] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-[#76b900]" />
          <h2 className="text-xs font-bold tracking-wider text-white font-mono uppercase">Mission Command</h2>
        </div>
        {activeMission && (
          <span className="text-[10px] font-mono text-slate-400">
            ID: <strong className="text-white">{activeMission.id}</strong>
          </span>
        )}
      </div>

      {/* Mission Input & Presets */}
      <div className="p-3 border-b border-slate-800/80 bg-[#050811] space-y-2.5">
        <form onSubmit={handleSubmit} className="space-y-2">
          <label className="text-[11px] font-mono text-slate-400 flex items-center justify-between">
            <span>NATURAL LANGUAGE MISSION:</span>
            <span className="text-[10px] text-slate-500">NVIDIA Nemotron Decomposition</span>
          </label>
          <div className="relative">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={2}
              className="w-full bg-[#0a101f] border border-slate-700/80 rounded p-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#76b900] transition font-sans resize-none"
              placeholder="Enter mission objectives for the robot fleet..."
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1 overflow-x-auto py-1 max-w-[70%]">
              {presets.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setPrompt(p.text)}
                  className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-mono truncate max-w-[120px] transition border border-slate-700"
                  title={p.text}
                >
                  {p.label}
                </button>
              ))}
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#76b900] hover:bg-[#68a400] text-black font-semibold text-xs transition active:scale-95 disabled:opacity-50"
            >
              <Send className="w-3 h-3 fill-current" />
              <span>{isLoading ? 'PLANNING...' : 'DISPATCH'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Task DAG & Progression */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400">
          <span>TASK DECOMPOSITION GRAPH</span>
          <span>{activeMission?.tasks.length || 0} SUBTASKS</span>
        </div>

        {(!activeMission || activeMission.tasks.length === 0) ? (
          <div className="h-48 border border-dashed border-slate-800 rounded flex flex-col items-center justify-center text-center p-4 text-slate-500 text-xs font-mono">
            <Clock className="w-6 h-6 mb-2 opacity-40 text-[#76b900]" />
            <p>No active mission dispatch.</p>
            <p className="text-[10px] text-slate-600 mt-1">Submit a mission above or click "RUN DEMO" to initialize.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {activeMission.tasks.map((task, idx) => (
              <div
                key={task.id}
                className={`p-2.5 rounded border transition-all ${
                  task.status === 'in_progress'
                    ? 'bg-slate-900/90 border-[#76b900]/70 shadow-lg shadow-[#76b900]/10'
                    : task.status === 'completed'
                    ? 'bg-[#09111c] border-emerald-900/40 text-slate-300'
                    : 'bg-[#070c17] border-slate-800/80 text-slate-400'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <span className="w-4 h-4 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[10px] font-mono font-bold">
                      {idx + 1}
                    </span>
                    <span className="font-semibold text-xs text-white truncate max-w-[150px]">{task.title}</span>
                  </div>
                  {getStatusBadge(task.status)}
                </div>

                <div className="flex items-center justify-between text-[11px] font-mono mb-2 text-slate-400">
                  <div className="flex items-center space-x-1.5">
                    <span>Robot:</span>
                    <strong className="text-emerald-400">
                      {task.assigned_robot_id ? task.assigned_robot_id.toUpperCase() : 'UNASSIGNED'}
                    </strong>
                  </div>
                  <div>
                    {task.target_zone && <span className="text-amber-300/80">{task.target_zone}</span>}
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${
                      task.status === 'completed' ? 'bg-[#76b900]' : 'bg-blue-500'
                    }`}
                    style={{ width: `${Math.round(task.progress * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Mission Completion Report */}
        {activeMission && activeMission.status === 'completed' && activeMission.report_summary && (
          <div className="p-3 rounded border border-emerald-500/40 bg-emerald-950/20 text-xs space-y-1.5 animate-fadeIn">
            <div className="flex items-center space-x-2 text-emerald-400 font-bold font-mono">
              <ShieldCheck className="w-4 h-4" />
              <span>MISSION REPORT COMPILED</span>
            </div>
            <p className="text-slate-300 text-[11px] leading-relaxed">
              {activeMission.report_summary}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
