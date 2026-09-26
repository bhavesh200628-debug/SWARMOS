import React, { useState, useEffect } from 'react';
import { X, Cpu, Key, CheckCircle2 } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [aiInfo, setAiInfo] = useState<any>(null);

  useEffect(() => {
    if (isOpen) {
      fetch(`${API_BASE_URL}/health/ai`)
        .then((res) => res.json())
        .then((data) => setAiInfo(data))
        .catch((err) => console.error(err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#090e1a] border border-slate-800 rounded-xl w-full max-w-xl overflow-hidden shadow-2xl flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-[#0b1222]">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-[#76b900]" />
            <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
              SWARMOS Engine & Nebius Configuration
            </h2>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <div className="p-6 space-y-4 text-xs font-mono">
          <div>
            <label className="text-slate-400 block mb-1">NEBIUS TOKEN FACTORY ENDPOINT</label>
            <input
              type="text"
              readOnly
              value={aiInfo?.nebius_endpoint || 'https://api.studio.nebius.ai/v1'}
              className="w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-white focus:outline-none"
            />
          </div>

          <div>
            <label className="text-slate-400 block mb-1">REASONING MODEL</label>
            <input
              type="text"
              readOnly
              value={aiInfo?.target_model || 'nvidia/Llama-3.1-Nemotron-70B-Instruct-HF'}
              className="w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-[#76b900] font-bold focus:outline-none"
            />
            <p className="text-[10px] text-slate-500 mt-1 font-sans">
              Selected NVIDIA open-source reasoning model for mission decomposition and swarm replanning.
            </p>
          </div>

          <div>
            <label className="text-slate-400 block mb-1">NEBIUS API CREDENTIAL STATUS</label>
            <div className="flex items-center space-x-2 bg-slate-900 p-2.5 rounded border border-slate-800">
              <Key className="w-4 h-4 text-slate-400" />
              <span className="text-slate-300">
                {aiInfo?.api_key_configured ? 'Configured via NEBIUS_API_KEY (.env)' : 'Not Set (Operating in Deterministic Simulated Mode)'}
              </span>
            </div>
            <p className="text-[10px] text-slate-500 mt-1 font-sans">
              To activate real-time API calls to Nebius Token Factory, set <code>NEBIUS_API_KEY</code> in <code>.env</code>.
            </p>
          </div>

          <div className="pt-2 border-t border-slate-800">
            <label className="text-slate-400 block mb-1">EXECUTION PROFILE</label>
            <div className="p-3 rounded bg-emerald-950/20 border border-emerald-900/40 text-emerald-400 flex items-center justify-between">
              <span>{aiInfo?.execution_mode || 'DETERMINISTIC_SIMULATED_MODE'}</span>
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-[#0b1222] border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
