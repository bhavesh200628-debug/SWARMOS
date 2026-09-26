import React from 'react';
import { Activity, ShieldCheck, Cpu, AlertTriangle, ArrowRight } from 'lucide-react';

interface DecisionEvent {
  timestamp: number;
  type: string;
  message: string;
  metadata?: any;
}

interface DecisionTimelineProps {
  events: DecisionEvent[];
}

export const DecisionTimeline: React.FC<DecisionTimelineProps> = ({ events }) => {
  const formatTime = (ts: number) => {
    const d = new Date(ts * 1000);
    return d.toTimeString().split(' ')[0] + '.' + Math.floor(d.getMilliseconds() / 100);
  };

  const getEventBadge = (type: string) => {
    switch (type) {
      case 'robot_failure':
        return (
          <span className="px-1.5 py-0.5 rounded text-[10px] bg-red-950 text-red-400 border border-red-500/50 font-mono font-bold flex items-center space-x-1">
            <AlertTriangle className="w-3 h-3" />
            <span>FAILURE</span>
          </span>
        );
      case 'nemotron_replan':
        return (
          <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950 text-[#76b900] border border-[#76b900]/50 font-mono font-bold flex items-center space-x-1">
            <Cpu className="w-3 h-3" />
            <span>NEMOTRON REPLAN</span>
          </span>
        );
      case 'mission_submitted':
        return (
          <span className="px-1.5 py-0.5 rounded text-[10px] bg-blue-950 text-blue-400 border border-blue-500/50 font-mono font-bold flex items-center space-x-1">
            <Activity className="w-3 h-3" />
            <span>DISPATCH</span>
          </span>
        );
      default:
        return (
          <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700 font-mono">
            {type.toUpperCase()}
          </span>
        );
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#070b14] border border-slate-800 rounded-lg overflow-hidden select-none">
      {/* Header */}
      <div className="px-4 py-2.5 border-b border-slate-800/80 bg-[#090e1a] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-[#76b900]" />
          <h2 className="text-xs font-bold tracking-wider text-white font-mono uppercase">AI Decision & Telemetry Stream</h2>
        </div>
        <div className="flex items-center space-x-3 text-[10px] font-mono text-slate-400">
          <span className="flex items-center space-x-1">
            <ShieldCheck className="w-3 h-3 text-[#76b900]" />
            <span>Deterministic Safety Guard: ENFORCED</span>
          </span>
          <span className="text-slate-600">|</span>
          <span>{events.length} Events Logged</span>
        </div>
      </div>

      {/* Stream List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 font-mono text-xs">
        {events.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-500 text-xs">
            Waiting for fleet activity or mission triggers...
          </div>
        ) : (
          events
            .slice()
            .reverse()
            .map((evt, idx) => (
              <div
                key={idx}
                className="p-2 rounded bg-[#090e1d] border border-slate-800/80 hover:border-slate-700/80 flex flex-col space-y-1 transition"
              >
                <div className="flex items-center justify-between text-[11px]">
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-500">{formatTime(evt.timestamp)}</span>
                    {getEventBadge(evt.type)}
                  </div>
                  {evt.metadata?.latency_ms && (
                    <span className="text-slate-400 text-[10px]">
                      Latency: <strong className="text-white">{evt.metadata.latency_ms.toFixed(1)}ms</strong>
                    </span>
                  )}
                </div>

                <p className="text-slate-200 text-xs font-sans pl-1">{evt.message}</p>

                {/* Structured Replanning Metadata */}
                {evt.type === 'nemotron_replan' && evt.metadata && (
                  <div className="mt-1 p-2 rounded bg-slate-900/90 border border-emerald-900/40 text-[11px] space-y-1">
                    <div className="flex items-center justify-between text-slate-400">
                      <span>Reasoning Model: <strong className="text-[#76b900]">{evt.metadata.model}</strong></span>
                      <span>Confidence: <strong className="text-emerald-400">{(evt.metadata.confidence * 100).toFixed(0)}%</strong></span>
                    </div>

                    {evt.metadata.reassignments && evt.metadata.reassignments.length > 0 && (
                      <div className="mt-1 space-y-1 border-t border-slate-800 pt-1">
                        <span className="text-slate-400 text-[10px] block">DYNAMIC REASSIGNMENT:</span>
                        {evt.metadata.reassignments.map((r: any, rIdx: number) => (
                          <div key={rIdx} className="flex items-center space-x-2 text-slate-300">
                            <span className="text-red-400 font-bold">{r.from_robot?.toUpperCase()}</span>
                            <ArrowRight className="w-3 h-3 text-slate-500" />
                            <span className="text-[#76b900] font-bold">{r.to_robot?.toUpperCase()}</span>
                            <span className="text-slate-400 text-[10px]">({r.title})</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
        )}
      </div>
    </div>
  );
};
