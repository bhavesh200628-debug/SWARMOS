import React, { useState, useEffect, useRef } from 'react';
import type { SimulationState } from './types';
import { Navbar } from './components/Navbar';
import { WarehouseMap } from './components/WarehouseMap';
import { MissionPanel } from './components/MissionPanel';
import { FleetPanel } from './components/FleetPanel';
import { DecisionTimeline } from './components/DecisionTimeline';
import { EvaluationModal } from './components/EvaluationModal';
import { SettingsModal } from './components/SettingsModal';

export const App: React.FC = () => {
  const [wsConnected, setWsConnected] = useState(false);
  const [simState, setSimState] = useState<SimulationState>({
    timestamp: Date.now() / 1000,
    tick: 0,
    robots: [],
    packages: [],
    obstacles: [],
    zones: [],
    active_mission: null,
    active_failures: [],
    recent_decision_events: [],
    simulation_running: true,
    speed_multiplier: 1.0,
  });
  const [isDemoRunning, setIsDemoRunning] = useState(false);
  const [isMissionLoading, setIsMissionLoading] = useState(false);
  const [evalModalOpen, setEvalModalOpen] = useState(false);
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [aiMode, setAiMode] = useState<'live' | 'mock'>('mock');

  const wsRef = useRef<WebSocket | null>(null);

  // Fetch initial state & AI health
  const fetchState = async () => {
    try {
      const res = await fetch('/health/ai');
      if (res.ok) {
        const data = await res.json();
        setAiMode(data.is_mock ? 'mock' : 'live');
      }
    } catch (e) {
      console.warn('Backend not yet reachable', e);
    }
  };

  useEffect(() => {
    fetchState();
  }, []);

  // WebSocket Telemetry Connection
  useEffect(() => {
    let reconnectTimer: any = null;

    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.port === '5173' ? 'localhost:8000' : window.location.host;
      const wsUrl = `${protocol}//${host}/ws/telemetry`;

      console.log('Connecting to SWARMOS Telemetry:', wsUrl);
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('Connected to SWARMOS Telemetry stream');
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'telemetry_update' && payload.data) {
            setSimState(payload.data);
          }
        } catch (err) {
          console.error('Error parsing telemetry message:', err);
        }
      };

      ws.onclose = () => {
        console.log('SWARMOS Telemetry disconnected. Retrying...');
        setWsConnected(false);
        reconnectTimer = setTimeout(connectWebSocket, 2000);
      };

      ws.onerror = (err) => {
        console.warn('WebSocket error, falling back to reconnect', err);
        ws.close();
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimer) clearTimeout(reconnectTimer);
    };
  }, []);

  // Actions
  const handleRunDemo = async () => {
    setIsDemoRunning(true);
    try {
      await fetch('/api/demo/run', { method: 'POST' });
    } catch (err) {
      console.error('Demo run trigger failed', err);
    } finally {
      setTimeout(() => setIsDemoRunning(false), 24000);
    }
  };

  const handleTriggerFailure = async () => {
    try {
      await fetch('/api/demo/failure', { method: 'POST' });
    } catch (err) {
      console.error('Failure trigger failed', err);
    }
  };

  const handleTriggerRobotFailure = async (robotId: string) => {
    try {
      await fetch(`/api/robots/${robotId}/failure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          failure_type: 'robot_unavailable',
          description: 'Drive system stall / Sensor telemetry blackout',
        }),
      });
    } catch (err) {
      console.error('Individual robot failure trigger failed', err);
    }
  };

  const handleResetDemo = async () => {
    setIsDemoRunning(false);
    try {
      await fetch('/api/demo/reset', { method: 'POST' });
    } catch (err) {
      console.error('Reset trigger failed', err);
    }
  };

  const handleSubmitMission = async (prompt: string) => {
    setIsMissionLoading(true);
    try {
      await fetch('/api/missions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
    } catch (err) {
      console.error('Mission submit failed', err);
    } finally {
      setIsMissionLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#070b14] text-slate-100 overflow-hidden font-sans">
      {/* Top Navbar */}
      <Navbar
        wsConnected={wsConnected}
        onRunDemo={handleRunDemo}
        onTriggerFailure={handleTriggerFailure}
        onResetDemo={handleResetDemo}
        onOpenEval={() => setEvalModalOpen(true)}
        onOpenSettings={() => setSettingsModalOpen(true)}
        isDemoRunning={isDemoRunning}
        aiMode={aiMode}
      />

      {/* Main Grid Workspace */}
      <div className="flex-1 flex flex-col p-3 gap-3 min-h-0">
        {/* Upper Command View: Left Mission DAG, Center Digital Twin Map, Right Fleet */}
        <div className="flex-1 flex gap-3 min-h-0">
          {/* Left Panel: Mission Input & Task DAG */}
          <div className="w-80 xl:w-96 flex-shrink-0 h-full">
            <MissionPanel
              activeMission={simState.active_mission}
              onSubmitMission={handleSubmitMission}
              isLoading={isMissionLoading}
            />
          </div>

          {/* Center Panel: Real-Time Warehouse Map / Digital Twin */}
          <div className="flex-1 h-full min-w-0">
            <WarehouseMap
              robots={simState.robots}
              packages={simState.packages}
              obstacles={simState.obstacles}
              zones={simState.zones}
            />
          </div>

          {/* Right Panel: Fleet Status Cards */}
          <div className="w-80 xl:w-96 flex-shrink-0 h-full">
            <FleetPanel
              robots={simState.robots}
              onTriggerRobotFailure={handleTriggerRobotFailure}
            />
          </div>
        </div>

        {/* Lower View: AI Decision & Telemetry Event Stream */}
        <div className="h-56 xl:h-64 flex-shrink-0">
          <DecisionTimeline events={simState.recent_decision_events} />
        </div>
      </div>

      {/* Modals */}
      <EvaluationModal isOpen={evalModalOpen} onClose={() => setEvalModalOpen(false)} />
      <SettingsModal isOpen={settingsModalOpen} onClose={() => setSettingsModalOpen(false)} />
    </div>
  );
};

export default App;
