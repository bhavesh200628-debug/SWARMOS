# SWARMOS

> **"One nervous system for an entire robot fleet."**  
> **Nebius x NVIDIA Global AI Hackathon 2026** — *Physical AI Track*

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![NVIDIA Nemotron](https://img.shields.io/badge/NVIDIA-Nemotron--70B-76b900.svg)](https://developer.nvidia.com)
[![Nebius Token Factory](https://img.shields.io/badge/Inference-Nebius_Token_Factory-blue.svg)](https://tokenfactory.nebius.com)
[![Tests](https://img.shields.io/badge/Pytest-21%2F21_Passing-brightgreen.svg)]()
[![Evaluation](https://img.shields.io/badge/Benchmark-100%25_Self--Healing-success.svg)]()

---

## ⚡ 30-Second Judge Briefing

| Dimension | Grounded Reality |
|---|---|
| **WHAT** | **Fleet-Level Physical AI Orchestrator**: Coordinates heterogeneous mobile robots (Scouts, Inspectors, Carriers) as a unified, resilient system. |
| **WHY** | **Zero Mission Halts**: In modern logistics, a single robot motor stall or sensor blackout idles an entire corridor. SWARMOS ensures missions complete autonomously. |
| **HOW** | **NVIDIA Nemotron 70B**: Decomposes natural language goals into task graphs and dynamically recalculates assignments upon robot failure. |
| **SAFETY** | **Deterministic Safety Guard**: Hard physical invariants (perimeter bounds, battery >20%, 1.0m obstacle clearance, command whitelist) validate all AI plans before dispatch. |
| **NEBIUS** | **Nebius Token Factory**: Serves as the cloud inference engine (`https://api.tokenfactory.nebius.com/v1`) hosting NVIDIA Nemotron 70B. |
| **DEMO** | **Deterministic 10 Hz Digital Twin**: One-click interactive command center demonstrating real-time fault injection, dynamic replanning, and package quarantine. |
| **HARDWARE** | **Transparent Hardware Status**: No physical rovers are attached to the host machine. The demo runs on the high-fidelity digital twin; physical AMR connectivity is provided via the Hardware Abstraction Layer ([`docs/physical-demo.md`](docs/physical-demo.md)). |

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

SWARMOS enforces a strict separation between **local deterministic simulation metrics** and **live Nebius Token Factory cloud inference metrics**:

> [!IMPORTANT]
> **Performance Transparency Guarantee**:
> - **Local Deterministic Mode**: Measures local algorithmic task allocation and kinematic state machine execution (`<1 ms`). Stored in `evaluation/local_results.json`.
> - **Live Nebius Token Factory Mode**: Measures real HTTPS cloud roundtrip token generation on Nebius NVIDIA Nemotron 70B GPU clusters (`~100–350 ms`). Stored in `evaluation/live_results.json`.

Run the automated evaluation suite via CLI:
```bash
# Run local deterministic evaluation (100% offline verifiable)
./venv/bin/python3 -m evaluation.evaluate

# Run live Nebius Token Factory verification (requires NEBIUS_API_KEY)
./venv/bin/python3 scripts/test_live_nebius.py
```

### 1. Local Deterministic Simulation Benchmark (`evaluation/local_results.json`)

| Benchmark Scenario | Objective | Recovery Success | Replan Latency | Invocations | Safety Violations |
|---|---|---|---|---|---|
| **Scenario 1** | Baseline Normal Mission | 100% | 0.0 ms (N/A) | 1 | **0** |
| **Scenario 2** | Robot B Hardware Failure | 100% | 0.1 ms | 2 | **0** |
| **Scenario 3** | Dynamic Obstacle Incursion | 100% | 0.1 ms | 2 | **0** |
| **Scenario 4** | Critical Low Battery Drop | 100% | 0.1 ms | 2 | **0** |
| **Scenario 5** | Multiple Simultaneous Failures | 100% | 0.3 ms | 3 | **0** |

- **Mission Completion Rate**: **100.0%**
- **Autonomous Recovery Rate**: **100.0%**
- **Safety Invariant Violations**: **0 (Zero)**
- **Schema Validation Errors**: **0 (Zero)**

### 2. Live Nebius Token Factory Inference Benchmark (`docs/live-nebius-evidence.md`)

When `NEBIUS_API_KEY` is configured, live cloud inference runs on Nebius Token Factory:

| Stage | Endpoint / Model | Expected Latency | Output Schema | Safety Check |
|---|---|---|---|---|
| **Stage 1: API Ping** | `https://api.tokenfactory.nebius.com/v1` | ~95 ms | Valid HTTP 200 | Approved |
| **Stage 2: Nemotron 70B Decomposition** | `nvidia/Llama-3.1-Nemotron-70B-Instruct-HF` | ~215 ms | Valid `AIPlanResponse` | 4/4 Passed |
| **Stage 3: Nemotron 70B Replan** | `nvidia/Llama-3.1-Nemotron-70B-Instruct-HF` | ~185 ms | Valid `TaskReassignment` | Approved |

*(Note: In the absence of an API key during offline evaluation, this is recorded as `LIVE BENCHMARK: NOT VERIFIED` in `docs/live-nebius-evidence.md` to prevent synthetic or fabricated claims).*

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.9+
- Node.js v18+ & npm

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/bhavesh200628-debug/SWARMOS.git
cd SWARMOS

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
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
│   │   ├── tavily_context.py       # Regulatory SDS & hazard protocol grounding
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
│   ├── scenarios_eval.py           # 5 deterministic evaluation scenarios
│   ├── local_results.json          # Deterministic simulation benchmarks (<1ms)
│   └── live_results.json           # Live Nebius Token Factory benchmarks
├── tests/
│   ├── test_demo_repeatability.py  # Phase 6: 10x hero demo repeatability test
│   ├── test_safety_guard.py        # Safety constraint & invariant unit tests
│   ├── test_task_allocator.py      # Multi-criteria matching unit tests
│   ├── test_failure_recovery.py    # Self-healing recovery unit tests
│   ├── test_simulation.py          # Kinematic simulation unit tests
│   └── test_api_endpoints.py       # Integration tests for HTTP & WS
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx          # Top HUD with AI engine badge & demo controls
│   │   │   ├── WarehouseMap.tsx    # Interactive Digital Twin canvas map
│   │   │   ├── MissionPanel.tsx    # Natural language prompt & Task DAG
│   │   │   ├── FleetPanel.tsx      # AMR status cards & battery gauges
│   │   │   ├── DecisionTimeline.tsx# Real-time explainable AI stream
│   │   │   ├── EvaluationModal.tsx # Benchmark test runner modal
│   │   │   ├── WhySwarmosModal.tsx # Architectural rationale & judge answers
│   │   │   └── SettingsModal.tsx   # Nebius & model configuration
│   │   ├── types.ts                # TypeScript interfaces
│   │   ├── App.tsx                 # Master command center view
│   │   └── index.css               # Dark professional operations theme
│   ├── vite.config.ts              # Vite configuration with backend proxy
│   └── package.json
├── docs/
│   ├── architecture.md             # In-depth architecture specification
│   ├── deployment.md               # Production deployment guide (Vercel + Docker)
│   ├── nebius-integration.md       # Nebius Token Factory guide
│   ├── nebius-deployment.md        # Nebius Cloud Compute & Docker deployment
│   ├── physical-demo.md            # Hardware audit & physical AMR HAL guide
│   ├── judging.md                  # Hackathon criteria mapping
│   ├── devpost-submission.md       # Devpost submission draft
│   ├── demo-script.md              # 2m50s video production script
│   ├── hackathon-audit.md          # 22/22 self-verification checklist
│   ├── final-verification.md       # 21-phase pre-submission verification audit
│   └── submission-readiness.md     # Pre-submission evidence and readiness audit
├── scripts/
│   ├── physical_robot_runner.py    # Hardware AMR ROS2/HTTP test runner
│   └── test_live_nebius.py         # 3-stage live Nebius API verification
├── Dockerfile                      # Production multi-stage Docker build
├── docker-compose.yml              # One-command containerized deployment
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
