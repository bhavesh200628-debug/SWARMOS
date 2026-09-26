import React from 'react';
import { Play, AlertTriangle, RotateCcw, Cpu, BarChart3, Settings as SettingsIcon, Radio } from 'lucide-react';

interface NavbarProps {
  wsConnected: boolean;
  onRunDemo: () => void;
  onTriggerFailure: () => void;
  onResetDemo: () => void;
  onOpenEval: () => void;
  onOpenSettings: () => void;
  isDemoRunning: boolean;
  aiMode: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  wsConnected,
  onRunDemo,
  onTriggerFailure,
  onResetDemo,
  onOpenEval,
  onOpenSettings,
  isDemoRunning,
  aiMode
}) => {
  return (
    <header className="h-16 border-b border-slate-800 bg-[#070b12] px-6 flex items-center justify-between z-20 select-none">
      {/* Brand & Tagline */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded bg-[#76b900] flex items-center justify-center font-black text-black text-lg tracking-tighter shadow-lg shadow-[#76b900]/20">
            S
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-wider text-white">SWARM<span className="text-[#76b900]">OS</span></span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-500/30 font-mono uppercase tracking-widest">
                v1.0 Physical AI
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono tracking-tight hidden sm:block">
              "One nervous system for an entire robot fleet."
            </p>
          </div>
        </div>

        {/* AI & Stream Status Badges */}
        <div className="hidden lg:flex items-center space-x-3 ml-6 pl-6 border-l border-slate-800 text-xs font-mono">
          <div className="flex items-center space-x-2 px-2.5 py-1 rounded bg-slate-900 border border-slate-700/60">
            <Cpu className="w-3.5 h-3.5 text-[#76b900]" />
            <span className="text-slate-300">Model:</span>
            <span className="text-white font-semibold">NVIDIA Nemotron 70B</span>
            <span className="px-1.5 py-0.2 rounded text-[9px] bg-emerald-900/60 text-emerald-300 border border-emerald-700/40">
              {aiMode === 'live' ? 'NEBIUS LIVE' : 'DETERMINISTIC'}
            </span>
          </div>

          <div className="flex items-center space-x-2 px-2.5 py-1 rounded bg-slate-900 border border-slate-700/60">
            <Radio className={`w-3.5 h-3.5 ${wsConnected ? 'text-emerald-400 animate-pulse' : 'text-amber-500'}`} />
            <span className="text-slate-300">Telemetry:</span>
            <span className={wsConnected ? 'text-emerald-400 font-semibold' : 'text-amber-400'}>
              {wsConnected ? '10 Hz SYNCED' : 'CONNECTING...'}
            </span>
          </div>
        </div>
      </div>

      {/* Global Actions Bar */}
      <div className="flex items-center space-x-2.5">
        <button
          onClick={onRunDemo}
          disabled={isDemoRunning}
          className={`flex items-center space-x-2 px-4 py-2 rounded font-semibold text-xs transition tracking-wide shadow-md ${
            isDemoRunning
              ? 'bg-emerald-900/60 text-emerald-300 border border-emerald-700 cursor-wait animate-pulse'
              : 'bg-[#76b900] hover:bg-[#68a400] text-black shadow-[#76b900]/25 active:scale-95'
          }`}
        >
          <Play className="w-4 h-4 fill-current" />
          <span>{isDemoRunning ? 'DEMO RUNNING...' : 'RUN DEMO'}</span>
        </button>

        <button
          onClick={onTriggerFailure}
          title="Inject a hardware failure on Robot Bravo to trigger autonomous Nemotron self-healing"
          className="flex items-center space-x-2 px-3 py-2 rounded bg-amber-950/60 hover:bg-amber-900/80 text-amber-300 border border-amber-600/40 text-xs font-semibold tracking-wide transition active:scale-95"
        >
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          <span className="hidden sm:inline">TRIGGER FAILURE</span>
        </button>

        <button
          onClick={onResetDemo}
          title="Reset warehouse, fleet, packages, and missions to baseline"
          className="flex items-center space-x-1.5 px-3 py-2 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-medium transition active:scale-95"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">RESET</span>
        </button>

        <button
          onClick={onOpenEval}
          title="Open benchmark evaluation suite"
          className="flex items-center space-x-1.5 px-3 py-2 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-medium transition active:scale-95"
        >
          <BarChart3 className="w-3.5 h-3.5 text-blue-400" />
          <span className="hidden md:inline">EVAL SUITE</span>
        </button>

        <button
          onClick={onOpenSettings}
          title="Configure Nebius Token Factory API keys and models"
          className="p-2 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 transition"
        >
          <SettingsIcon className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
