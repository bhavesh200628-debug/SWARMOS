# Hackathon Judging Criteria Alignment

> **NEBIUS x NVIDIA GLOBAL AI HACKATHON 2026**  
> **Track**: Physical AI  
> **Project**: SWARMOS — *"One nervous system for an entire robot fleet."*

---

## Criterion 1: Technological Implementation (25%)

| Hackathon Requirement | SWARMOS Implementation | Code Verification |
|---|---|---|
| **Runtime Nebius Token Factory Usage** | Live OpenAI-compatible integration hitting `https://api.studio.nebius.ai/v1/chat/completions` with token tracking, latency recording, and retry/repair fallback. | [`backend/nebius/client.py`](file:///Users/bhaveshsuthar/Desktop/NVIDIA/backend/nebius/client.py) |
| **NVIDIA Open Model Usage** | Utilizes **NVIDIA Nemotron 70B** (`nvidia/Llama-3.1-Nemotron-70B-Instruct-HF`) for mission decomposition and dynamic replanning. | [`backend/nebius/nemotron_reasoner.py`](file:///Users/bhaveshsuthar/Desktop/NVIDIA/backend/nebius/nemotron_reasoner.py) |
| **Structured Model Output** | Output is strictly machine-readable JSON validated via Pydantic models; zero raw natural language executed directly. | [`backend/models/schemas.py`](file:///Users/bhaveshsuthar/Desktop/NVIDIA/backend/models/schemas.py) |
| **Deterministic Safety Guard** | Hard deterministic software constraints wrapping AI decisions: strict action whitelist (`navigate`, `inspect`, `transport`, `stop`, `report_status`), warehouse spatial bounds (30x20m), battery thresholds (>20%), and obstacle collision buffers. | [`backend/safety/guard.py`](file:///Users/bhaveshsuthar/Desktop/NVIDIA/backend/safety/guard.py) |
| **Heterogeneous Task Allocation** | Multi-criteria objective function balancing capability matching ($w=0.35$), proximity ($w=0.30$), battery State-of-Charge ($w=0.20$), and workload availability ($w=0.15$). | [`backend/planning/task_allocator.py`](file:///Users/bhaveshsuthar/Desktop/NVIDIA/backend/planning/task_allocator.py) |
| **Hardware Abstraction Layer (HAL)** | Clean adapter architecture with `SimulationRobotAdapter` and `PhysicalRobotAdapter` supporting ROS2, Micro-ROS, and HTTP/MQTT telemetry. | [`backend/robots/adapter_base.py`](file:///Users/bhaveshsuthar/Desktop/NVIDIA/backend/robots/adapter_base.py) |
| **NVIDIA Physical AI Alignment** | Implements architecture interfaces for **NVIDIA Cosmos World Foundation Models** (what-if risk simulation) and **NVIDIA GR00T** (perception and low-level action policies). | [`backend/planning/world_model.py`](file:///Users/bhaveshsuthar/Desktop/NVIDIA/backend/planning/world_model.py), [`backend/robots/perception.py`](file:///Users/bhaveshsuthar/Desktop/NVIDIA/backend/robots/perception.py) |
| **Empirical Evaluation Suite** | 5 repeatable benchmark scenarios measuring mission completion (100%), self-healing recovery rate (100%), replan latency (<150ms), and 0 safety invariant violations. | [`evaluation/evaluate.py`](file:///Users/bhaveshsuthar/Desktop/NVIDIA/evaluation/evaluate.py) |

---

## Criterion 2: Design (25%)

- **Command Center Aesthetic**: Built with a dark, high-information-density industrial physical-AI operations design language (`#070b14` canvas, `#76b900` NVIDIA green accents, clean monospace typography).
- **Zero Fake 3D / Zero Fluff**: Focused entirely on operational clarity rather than decorative marketing eye candy.
- **Interactive Digital Twin**: Live SVG/Canvas map updating at 10 Hz over WebSockets displaying robot positions, headings, scanning cones, waypoints, packages, and zones.
- **Explainable Decision Timeline**: Streams structured AI rationale, confidence scores, latency metrics, and robot reassignment diffs (`Robot Bravo → Robot Alpha`) understandable by a judge in under 10 seconds.
- **One-Click Hero Demo Mode**: Includes dedicated "Run Demo", "Trigger Failure", and "Reset" controls providing a repeatable, flawless evaluation experience.

---

## Criterion 3: Potential Impact (25%)

Single-robot intelligence breaks down when individual machines encounter mechanical failures, communication blackouts, or depleted batteries. In industrial settings, a single stalled robot can idle an entire logistics facility or manufacturing line.

### Real-World Deployment Sectors:
1. **Automated Warehousing & Fulfillment**: Enables heterogeneous fleets (forklifts, sorters, AMRs) to self-heal when a carrier robot stalls in high-density corridors.
2. **Advanced Manufacturing**: Continuous assembly line parts delivery where robots dynamically cover for maintenance-flagged peers.
3. **Hazardous Environment Inspection**: Nuclear, offshore oil rig, and chemical plant inspection where robot loss is expected and mission continuity is vital to human safety.
4. **Disaster Response & Search & Rescue**: Autonomous swarm exploration where drone and rover attrition must not abort the search mission.

---

## Criterion 4: Quality of Idea (25%)

### Fleet-Level Nervous System vs. Single-Robot Brain
- **The Prevailing Paradigm**: Most Physical AI projects attempt to make an individual robot smarter by packing vision-language models into single mobile bases.
- **The SWARMOS Paradigm**: Real-world operations do not need one brilliant robot; they need an **intelligent, self-healing collective workforce**.
- **The Hybrid AI + Deterministic Rigor**: Large Language Models like NVIDIA Nemotron provide high-level mission decomposition and creative reassignment heuristics, while deterministic control software enforces rigid safety invariants (collision clearance, coordinate bounds, battery minimums). This prevents hallucinations while preserving flexible autonomous adaptation.
