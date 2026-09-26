# Devpost Hackathon Submission Draft

## Project Title
**SWARMOS**

## Tagline
*One nervous system for an entire robot fleet.*

## Primary Hackathon Track
**Physical AI**

---

## 1. Short Description (Pitch)
SWARMOS is an autonomous AI orchestration layer for heterogeneous physical robot fleets. Powered by NVIDIA Nemotron via Nebius Token Factory, SWARMOS decomposes natural language missions into task graphs, monitors physical robot kinematics in real time, and dynamically self-heals the fleet by reassigning missions when individual robots fail.

---

## 2. Long Description & Inspiration
Today's robotics industry is obsessed with making individual robots smarter. Yet in real-world warehouses, construction sites, and disaster zones, individual machines break down constantly: batteries die, drive motors stall, camera lenses get smudged, and corridors get obstructed. When a single robot stalls, the entire operational mission halts.

We asked: **What if, instead of giving each robot an isolated brain, we gave the entire fleet one unified nervous system?**

SWARMOS turns heterogeneous robots (Scouts, Inspectors, Carriers, Manipulators) into a synchronized, self-healing collective workforce. When an AMR fails, SWARMOS detects the anomaly, invokes NVIDIA Nemotron on Nebius Token Factory to reason over the fleet's remaining capabilities, validates the new trajectory against strict deterministic safety guardrails, and dynamically redirects a peer robot to complete the mission.

---

## 3. How SWARMOS Works

1. **Natural Language Mission Input**: The operator issues an objective: *"Inspect Zone B, locate damaged packages, move them to quarantine, and generate an incident report."*
2. **NVIDIA Nemotron 70B Decomposition**: Hosted on Nebius Token Factory, Nemotron transforms this prompt into a Directed Acyclic Graph (DAG) of typed tasks, specifying required capabilities (`scout`, `inspector`, `carrier`) and dependencies.
3. **Deterministic Safety Guard**: Every action primitive is passed through an uncompromising deterministic safety layer ensuring coordinates lie within warehouse bounds, collision margins are respected, and robot batteries exceed safety margins (>20%).
4. **Multi-Criteria Task Allocation**: Tasks are assigned based on a mathematical objective balancing capability affinity, physical proximity, State of Charge, and availability.
5. **Real-Time Digital Twin**: AMRs execute tasks while streaming 10 Hz kinematics (position, heading, battery, cargo load) over WebSockets to a sleek Command Center.
6. **Hero Self-Healing Recovery**: When a robot suffers a sensor failure or hardware stall, SWARMOS triggers autonomous replanning via Nemotron. Orphaned tasks are dynamically reassigned to the closest viable peer without mission failure.

---

## 4. How Nebius and NVIDIA are Used

- **Nebius Token Factory**: Serves as the high-throughput, low-latency inference backbone (`https://api.studio.nebius.ai/v1`). Nebius's GPU infrastructure provides sub-200ms token generation times, enabling real-time robotic re-planning loops.
- **NVIDIA Nemotron 70B (`nvidia/Llama-3.1-Nemotron-70B-Instruct-HF`)**: Provides high-level mission decomposition, zero-shot structured JSON adherence, and explainable failure recovery reasoning.
- **NVIDIA Physical AI Architecture**:
  - Implements an architecture-compliant interface for **NVIDIA Cosmos World Foundation Models** (`backend/planning/world_model.py`) for predictive "what-if" trajectory risk evaluation.
  - Implements an architecture-compliant interface for **NVIDIA Project GR00T** (`backend/robots/perception.py`) for onboard multimodal perception and defect classification.

---

## 5. Technology Stack

- **Backend**: Python 3.9+, FastAPI, Pydantic v2, Uvicorn, WebSockets, HTTPX.
- **Inference**: Nebius Token Factory, NVIDIA Nemotron 70B, OpenAI-compatible SDK.
- **Frontend / Digital Twin**: React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons, SVG Canvas Engine.
- **Hardware Abstraction Layer**: Standardized `RobotAdapter` supporting Simulation Kinematics and Physical Hardware (ROS2, Micro-ROS, HTTP/MQTT).
- **Testing & Benchmarks**: Pytest (16/16 unit/integration tests passing), 5-Scenario Repeatable Evaluation Suite.

---

## 6. Pre-Existing Project Disclosure
**100% New Work**: SWARMOS was architected, implemented, benchmarked, and documented completely from scratch during the hackathon submission window. No pre-existing codebases or boilerplate templates were used.

---

## 7. Known Limitations & Roadmap
- **Current Limitation**: While the Hardware Abstraction Layer is ready for real ROS2 robots, the default hackathon deployment runs a high-fidelity 2D kinematic simulation so judges can evaluate it immediately in browser without requiring access to a physical warehouse.
- **Future Roadmap**: Deep binding to live NVIDIA Isaac Sim and Isaac Lab gym environments; physical testbed deployment on Unitree Go2 and Isaac Nova Carter platforms.
