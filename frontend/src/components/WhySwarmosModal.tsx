import React from 'react';
import { X, CheckCircle2, XCircle, Zap, RefreshCw } from 'lucide-react';

interface WhySwarmosModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const WhySwarmosModal: React.FC<WhySwarmosModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#090e1a] border border-slate-800 rounded-xl w-full max-w-4xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-[#0b1222]">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-[#76b900]" />
            <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
              Why SWARMOS? — Fleet-Level Intelligence vs. Single-Robot AI
            </h2>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs">
          {/* Executive Tagline */}
          <div className="bg-[#0c1427] border border-slate-800 p-4 rounded-lg text-center">
            <h3 className="text-base font-bold text-white mb-1">
              "We are not giving robots another brain. We're giving the entire fleet one nervous system."
            </h3>
            <p className="text-slate-400 text-xs">
              Industrial facilities don't need one isolated genius robot. They need a synchronized, self-healing collective workforce.
            </p>
          </div>

          {/* Side by Side Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Traditional Fleet Card */}
            <div className="p-4 rounded-lg bg-red-950/10 border border-red-900/40 flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <XCircle className="w-5 h-5 text-red-400" />
                  <h4 className="text-sm font-bold text-red-300 font-mono">TRADITIONAL FLEET (Siloed AI)</h4>
                </div>
                <div className="space-y-2.5 font-mono text-[11px] text-slate-300">
                  <div className="p-2 rounded bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                    <span>Robot A</span>
                    <span className="text-slate-400">Fixed Task: Scout Zone B</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                    <span>Robot B</span>
                    <span className="text-slate-400">Fixed Task: Visual Inspection</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                    <span>Robot C</span>
                    <span className="text-slate-400">Fixed Task: Transport Cargo</span>
                  </div>
                </div>

                {/* Failure sequence */}
                <div className="mt-4 p-3 rounded bg-red-900/20 border border-red-800/40 text-red-300 text-[11px] space-y-2">
                  <div className="flex items-center space-x-1.5 font-bold">
                    <span>⚠ ANOMALY: Robot B sensor fails / stalls</span>
                  </div>
                  <p className="text-slate-400">
                    Robots A and C have no awareness of Robot B's state. The inspection task remains unfulfilled. Downstream transport halts.
                  </p>
                  <div className="pt-1 font-bold text-red-400 flex items-center space-x-1">
                    <span>❌ RESULT: Mission Interrupted. Facility Line Idle.</span>
                  </div>
                </div>
              </div>
            </div>

            {/* SWARMOS Collective Card */}
            <div className="p-4 rounded-lg bg-emerald-950/15 border border-[#76b900]/40 flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <CheckCircle2 className="w-5 h-5 text-[#76b900]" />
                  <h4 className="text-sm font-bold text-[#76b900] font-mono">SWARMOS (Fleet Nervous System)</h4>
                </div>
                <div className="space-y-2.5 font-mono text-[11px] text-slate-300">
                  <div className="p-2 rounded bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                    <span className="text-emerald-400 font-bold">Fleet Mission</span>
                    <span className="text-slate-300">Global Natural-Language Goal</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                    <span>Dynamic Allocator</span>
                    <span className="text-slate-300">Capability, Battery, Proximity</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                    <span>Safety Guard</span>
                    <span className="text-slate-300">Zero Hallucinations Invariant</span>
                  </div>
                </div>

                {/* Self-Healing sequence */}
                <div className="mt-4 p-3 rounded bg-emerald-900/20 border border-emerald-700/40 text-emerald-300 text-[11px] space-y-2">
                  <div className="flex items-center space-x-1.5 font-bold text-[#76b900]">
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>SELF-HEALING: Robot B fails inside Zone B</span>
                  </div>
                  <p className="text-slate-300">
                    Nemotron on Nebius evaluates remaining fleet, identifies Robot A's camera & proximity, dynamically reassigns inspection in &lt;150ms.
                  </p>
                  <div className="pt-1 font-bold text-[#76b900] flex items-center space-x-1">
                    <span>✓ RESULT: Robot A takes task. Mission completes!</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Key Advantages Grid */}
          <div className="grid grid-cols-3 gap-3 pt-2 font-mono text-[11px]">
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-400 block mb-1">ZERO MISSION HALTS</span>
              <p className="text-slate-300 font-sans text-xs">AMR faults are absorbed dynamically rather than requiring human dispatch.</p>
            </div>
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <span className="text-[#76b900] block mb-1">DETERMINISTIC SAFETY</span>
              <p className="text-slate-300 font-sans text-xs">AI reasons over plans; rigid code guarantees collision and battery boundaries.</p>
            </div>
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <span className="text-blue-400 block mb-1">HETEROGENEOUS FLEET</span>
              <p className="text-slate-300 font-sans text-xs">Mix scouts, vision AMRs, heavy haulers, and rovers in one coordinated team.</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-[#0b1222] border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-[#76b900] hover:bg-[#68a400] text-black font-bold text-xs"
          >
            Got It
          </button>
        </div>
      </div>
    </div>
  );
};
