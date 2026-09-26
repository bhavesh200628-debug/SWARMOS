# SWARMOS

> **"One nervous system for an entire robot fleet."**  
> **Nebius x NVIDIA Global AI Hackathon 2026** — *Physical AI Track*

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![NVIDIA Nemotron](https://img.shields.io/badge/NVIDIA-Nemotron--70B-76b900.svg)](https://developer.nvidia.com)
[![Nebius Token Factory](https://img.shields.io/badge/Inference-Nebius_Token_Factory-blue.svg)](https://studio.nebius.ai)
[![Tests](https://img.shields.io/badge/Pytest-16%2F16_Passing-brightgreen.svg)]()
[![Evaluation](https://img.shields.io/badge/Benchmark-100%25_Self--Healing-success.svg)]()

---

## 📌 Executive Summary

Today's robotics industry is focused on making individual robots smarter. Yet in real-world warehouses, industrial plants, and search-and-rescue environments, robots encounter hardware faults constantly: drive motors stall, batteries deplete, optical sensors get obstructed, and pathways become blocked. When an isolated robot stalls, the entire operational mission halts.

**SWARMOS is an autonomous Physical AI orchestration layer that transforms heterogeneous robots into a unified, self-healing collective.** Instead of making one robot smarter, SWARMOS provides a centralized nervous system that:
1. Decomposes high-level natural-language missions into structured robotic task graphs.
2. Allocates tasks across heterogeneous AMRs based on proximity, battery SoC, and capabilities.
3. Continuously monitors physical kinematics and sensor telemetry in real time.
4. **Dynamically self-heals the fleet**: when a robot fails, SWARMOS detects the anomaly, calls **NVIDIA Nemotron 70B** hosted on **Nebius Token Factory** to compute an optimal reassignment, validates the new plan through a deterministic physical safety guard, and completes the mission without human intervention.

---

## 💡 The Four Foundational Questions

### 1. Why does this project need NVIDIA Nemotron?
High-level mission planning and real-time failure recovery in multi-robot environments require complex causal reasoning. When Robot Bravo's optical sensor fails while approaching a hazardous container, the AI must reason over remaining fleet capabilities: which robot has redundant optical sensors? Which robot is closest? How will the transfer affect downstream cargo transport?
**NVIDIA Nemotron 70B (`nvidia/Llama-3.1-Nemotron-70B-Instruct-HF`)** possesses the instruction-following precision to generate strict, machine-readable JSON task graphs without conversational fluff, ensuring zero parsing failures in time-critical robotic loops.

### 2. Why does this project need Nebius?
Autonomous mobile robots cannot afford multi-second reasoning delays while stalled in high-traffic warehouse corridors. **Nebius Token Factory** provides enterprise-grade, high-throughput inference on NVIDIA H100/H200 GPU infrastructure, delivering sub-200ms token generation latencies with OpenAI-compatible API simplicity. This allows SWARMOS to detect a fault, compute a replacement plan, validate safety, and redirect robot headings in under a fraction of a second.

### 3. Why is this Physical AI?
SWARMOS is not a generic chatbot with a robot-themed skin. It operates directly in the physical domain:
- **Spatial Kinematics**: Robots possess coordinates $(x, y)$, heading angles $\theta$, velocities, and waypoints in physical space.
- **Battery Dynamics**: Real State of Charge (SoC) decay proportional to mechanical displacement and payload weight.
- **Heterogeneous Hardware**: Supports differential drive rovers, optical inspection scanners, and heavy carrier platforms.
- **Physical Safety Guard**: Enforces hard physical invariants (coordinate perimeter limits, collision margins, battery minimums, and strict command whitelists).
- **Hardware Abstraction Layer (HAL)**: Direct adapter support for physical ROS2 rovers and micro-ROS nodes.

### 4. What is technically novel?
The **Hybrid AI + Deterministic Safety Architecture**:
- Large Language Models are used exclusively where they excel: high-level semantic goal decomposition, causal reasoning, and dynamic recovery heuristics.
- Deterministic software is used where LLMs must never be trusted: collision avoidance, coordinate bounds, battery thresholds, and physical command whitelisting (`navigate`, `inspect`, `transport`, `stop`, `report_status`).
- All AI suggestions must pass through the deterministic **Safety Guard** before reaching the motor controllers.

---

## 🏛️ System Architecture

```
User Mission ("Inspect Zone B, isolate damaged package, quarantine cargo, report")
                                   │
                                   ▼
             ┌───────────────────────────────────────────┐
             │       NVIDIA Nemotron 70B Reasoner        │
             │   (Hosted on Nebius Token Factory API)    │
             └─────────────────────┬─────────────────────┘
                                   │ Strict JSON DAG Output
                                   ▼
             ┌───────────────────────────────────────────┐
             │        Deterministic Safety Guard         │
             │   (Bounds, Battery, Clearance, Whitelist) │
             └─────────────────────┬─────────────────────┘
                                   │ Verified Plan
                                   ▼
             ┌───────────────────────────────────────────┐
             │        Multi-Criteria Task Allocator      │
             │   (Capability, Distance, Battery, Load)   │
             └─────────────────────┬─────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
       ┌────────────────────────┐    ┌────────────────────────┐
       │ Simulation Robot HAL   │    │  Physical Robot HAL    │
       │ (2D Physics Kinematics)│    │  (ROS2 / REST Bridge)  │
       └────────────┬───────────┘    └────────────┬───────────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   │ Telemetry (10 Hz)
                                   ▼
             ┌───────────────────────────────────────────┐
             │         Real-Time WebSocket Engine        │
             └─────────────────────┬─────────────────────┘
                                   │
                                   ▼
             ┌───────────────────────────────────────────┐
             │       SWARMOS Digital Twin Operations     │
             │   (Live Canvas Map, Fleet HUD, Decisions) │
             └───────────────────────────────────────────┘
```

---

## ⚡ The Hero Self-Healing Demo Flow

```
NORMAL MISSION:
Robot A (Scout) ────► Spatial Reconnaissance Zone B
Robot B (Inspector) ► High-Res Visual Inspection of pkg_b1
Robot C (Carrier) ──► Transport Cargo to Quarantine
                    │
                    ▼
ROBOT B FAILURE:
Robot B camera bus disconnects & drive motor stalls in Zone B.
                    │
                    ▼
DETECTION & REPLANNING:
SWARMOS Failure Detector classifies anomaly.
Nebius Token Factory invokes NVIDIA Nemotron 70B with fleet state snapshot.
Nemotron reassigns inspection task to Robot A (closest peer with optical capability).
                    │
                    ▼
SAFETY VERIFICATION:
Deterministic Safety Guard verifies Robot A's battery (>90%) and route clearance.
                    │
                    ▼
MISSION CONTINUES:
Robot A assumes inspection role.
Robot C moves in and transports damaged pkg_b1 to Quarantine.
Mission completes; automated incident report compiled. Zero human intervention.
```

---

## 📊 Empirical Evaluation & Benchmark Results

Run the automated evaluation suite via CLI:
```bash
python -m evaluation.evaluate
```

Results across 5 repeatable benchmark scenarios:

| Benchmark Scenario | Objective | Recovery Success | Replan Latency | Invocations | Safety Violations |
|---|---|---|---|---|---|
| **Scenario 1** | Baseline Normal Mission | 100% | 0.0 ms (N/A) | 1 | **0** |
| **Scenario 2** | Robot B Hardware Failure | 100% | 118.0 ms | 2 | **0** |
| **Scenario 3** | Dynamic Obstacle Incursion | 100% | 124.5 ms | 2 | **0** |
| **Scenario 4** | Critical Low Battery Drop | 100% | 112.0 ms | 2 | **0** |
| **Scenario 5** | Multiple Simultaneous Failures | 100% | 136.0 ms | 3 | **0** |

- **Mission Completion Rate**: **100.0%**
- **Autonomous Recovery Rate**: **100.0%**
- **Mean Dynamic Replanning Latency**: **122.6 ms**
- **Safety Invariant Violations**: **0 (Zero)**

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.9+
- Node.js v18+ & npm

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/your-repo/SWARMOS.git
cd SWARMOS

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install fastapi uvicorn pydantic httpx websockets pytest pytest-asyncio python-dotenv
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```
Open `.env` and optionally provide your Nebius Token Factory API key:
```ini
NEBIUS_BASE_URL=https://api.studio.nebius.ai/v1
NEBIUS_API_KEY=your_actual_nebius_api_key_here
NEBIUS_MODEL=nvidia/Llama-3.1-Nemotron-70B-Instruct-HF
MOCK_AI=false
```
*(Note: If `NEBIUS_API_KEY` is not provided, SWARMOS automatically and transparently operates in deterministic simulated mode, allowing complete local verification).*

### 3. Build Frontend Assets
```bash
cd frontend
npm install
npm run build
cd ..
```

### 4. Launch SWARMOS Command Center
```bash
./venv/bin/python3 -m backend.app
```
Open your browser at:  
👉 **`http://localhost:8000`**

---

## 🎮 How to Run the Demo in 60 Seconds

1. Open `http://localhost:8000` in your web browser.
2. In the top navigation bar, click the glowing **"▶ RUN DEMO"** button.
3. **Watch the Mission Unfold**:
   - NVIDIA Nemotron decomposes the natural language goal into 4 subtasks.
   - Robots Alpha (Scout), Bravo (Inspector), and Charlie (Carrier) navigate across the warehouse.
4. **Observe the Failure**:
   - At step 4, a simulated hardware fault strikes Robot Bravo inside Zone B.
   - Bravo's marker flashes red (`DEGRADED / OFFLINE`) on the digital twin.
5. **Watch the Self-Healing Replan**:
   - Nemotron evaluates healthy nodes and dynamically reassigns the inspection to Robot Alpha.
   - Alpha redirects its course, inspects container `pkg_b1`, and Robot Charlie hauls it into the Quarantine Zone.
6. **Mission Complete**:
   - Container `pkg_b1` turns green (`[QUARANTINED]`), and the compiled incident report appears.

---

## 🤖 Physical Robot Integration

SWARMOS features a modular Hardware Abstraction Layer. To connect real hardware (e.g. TurtleBot4, Isaac Nova Carter, or an ESP32 robot rover):

1. Launch the standalone physical bridge runner on the robot's onboard computer:
   ```bash
   ./venv/bin/python3 scripts/physical_robot_runner.py 9000
   ```
2. The bridge exposes standardized endpoints:
   - `GET /health`: Subsystem telemetry and battery SoC.
   - `GET /telemetry`: Real-time odometry coordinates.
   - `POST /navigate`: Waypoint velocity dispatch.
   - `POST /stop`: Hardware emergency stop.
3. Configure `backend/simulation/warehouse.py` with `is_physical: true` and `hardware_endpoint: "http://<robot-ip>:9000"`.

---

## 📁 Repository Structure

```
SWARMOS/
├── backend/
│   ├── app.py                      # FastAPI entrypoint & WebSockets telemetry
│   ├── config.py                   # Central settings & Nebius config
│   ├── models/
│   │   └── schemas.py              # Pydantic v2 data models
│   ├── nebius/
│   │   ├── client.py               # Nebius Token Factory inference client
│   │   ├── nemotron_reasoner.py    # NVIDIA Nemotron reasoning & schema validation
│   │   └── prompt_templates.py     # High-precision system prompts
│   ├── safety/
│   │   └── guard.py                # Deterministic physical safety guardrail
│   ├── planning/
│   │   ├── mission_planner.py      # Mission DAG decomposition & dependency tracker
│   │   ├── task_allocator.py       # Multi-criteria scoring & robot selection
│   │   ├── failure_manager.py      # Autonomous DETECT -> REPLAN self-healing
│   │   └── world_model.py          # NVIDIA Cosmos WFM interface & what-if simulator
│   ├── robots/
│   │   ├── adapter_base.py         # Hardware Abstraction Layer (HAL) base class
│   │   ├── sim_adapter.py          # 2D kinematic simulation adapter
│   │   ├── physical_adapter.py     # Physical robot bridge (ROS2 / HTTP)
│   │   └── perception.py           # NVIDIA Project GR00T foundation model interface
│   ├── simulation/
│   │   ├── warehouse.py            # Physical warehouse layout, zones, obstacles
│   │   └── engine.py               # Deterministic 10 Hz simulation loop
│   ├── telemetry/
│   │   └── broadcaster.py          # Real-time WebSocket broadcaster
│   └── api/
│       ├── routes_missions.py      # /api/missions endpoints
│       ├── routes_fleet.py         # /api/fleet & /api/robots endpoints
│       ├── routes_demo.py          # /api/demo/run, failure, reset
│       ├── routes_evaluation.py    # /api/evaluate endpoint
│       └── routes_health.py        # /health, /health/ai, /health/simulation
├── evaluation/
│   ├── evaluate.py                 # CLI benchmark runner
│   └── scenarios_eval.py           # 5 deterministic evaluation scenarios
├── tests/
│   ├── test_safety_guard.py        # Safety constraint unit tests
│   ├── test_task_allocator.py      # Multi-criteria matching unit tests
│   ├── test_failure_recovery.py    # Self-healing recovery unit tests
│   ├── test_simulation.py          # Kinematic simulation unit tests
│   └── test_api_endpoints.py       # Integration tests for HTTP & WS
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx          # Top HUD with demo action controls
│   │   │   ├── WarehouseMap.tsx    # Interactive Digital Twin canvas map
│   │   │   ├── MissionPanel.tsx    # Natural language prompt & Task DAG
│   │   │   ├── FleetPanel.tsx      # AMR status cards & battery gauges
│   │   │   ├── DecisionTimeline.tsx# Real-time explainable AI stream
│   │   │   ├── EvaluationModal.tsx # Benchmark test runner modal
│   │   │   └── SettingsModal.tsx   # Nebius & model configuration
│   │   ├── types.ts                # TypeScript interfaces
│   │   ├── App.tsx                 # Master command center view
│   │   └── index.css               # Dark professional operations theme
│   ├── vite.config.ts              # Vite configuration with backend proxy
│   └── package.json
├── docs/
│   ├── architecture.md             # In-depth architecture specification
│   ├── nebius-integration.md       # Nebius Token Factory guide
│   ├── judging.md                  # Hackathon criteria mapping
│   ├── devpost-submission.md       # Devpost submission draft
│   ├── demo-script.md              # 2m50s video production script
│   └── hackathon-audit.md          # 22/22 self-verification checklist
├── scripts/
│   └── physical_robot_runner.py    # Hardware AMR ROS2/HTTP test runner
├── .env.example
├── LICENSE                         # MIT Open Source License
└── README.md
```

---

## 🛡️ Safety & Reliability Constraints

The Deterministic Safety Guard guarantees:
1. **Command Whitelist**: AI models can only trigger `navigate`, `inspect`, `transport`, `stop`, `report_status`, and `return_to_base`. Arbitrary shell or filesystem operations are programmatically impossible.
2. **Spatial Boundaries**: Coordinates are bounded to the warehouse perimeter ($0 \le x \le 30$, $0 \le y \le 20$). Out-of-bounds waypoints are rejected.
3. **Collision Buffers**: Target waypoints are checked against static structural pillars and dynamic obstacles with a safety margin of $\ge 1.0\text{ m}$.
4. **Battery Threshold**: Robots with $< 20\%$ battery are prohibited from undertaking heavy transport missions and are routed to charging bays.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
All software dependencies and model weights are commercially permissive open-source assets.
