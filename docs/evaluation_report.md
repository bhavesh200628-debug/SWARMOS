# SWARMOS Empirical Evaluation Report

**Generated Benchmark Evaluation for Nebius x NVIDIA Hackathon 2026**
**Benchmark Execution Profile**: `LOCAL DETERMINISTIC SIMULATION`

> [!IMPORTANT]
> **Performance Transparency**:
> - **Local Simulation Mode**: Measures deterministic local simulation execution loop time (<1ms per cycle).
> - **Live Nebius Inference Mode**: Measures actual network request time and GPU token generation latency (~100–350ms) on Nebius Token Factory clusters.
> - The two execution modes are strictly separated in `evaluation/local_results.json` and `evaluation/live_results.json`.

## Aggregate Metrics

| Metric | Measured Value | Target | Status |
|---|---|---|---|
| **Benchmark Mode** | **LOCAL DETERMINISTIC SIMULATION** | Transparent | VERIFIED |
| **Mission Completion Rate** | **100.0%** | > 95% | PASS |
| **Self-Healing Recovery Rate** | **100.0%** | 100% | PASS |
| **Mean Replanning Latency** | **0.1 ms** | < 500 ms | PASS |
| **Dynamic Task Reassignments** | **6** | >= 4 | PASS |
| **Safety Invariant Violations** | **0** | 0 | PASS |
| **Invalid Schemas / Rejections** | **0** | 0 | PASS |
| **Total Model Invocations** | **10** | N/A | VERIFIED |

## Detailed Scenario Breakdown

| Scenario | Status | Replan Latency | Reassignments | Model Calls |
|---|---|---|---|---|
| Scenario 1: Normal Mission (Baseline) | SUCCESS | 0.0 ms | 0 | 1 |
| Scenario 2: Robot B Failure (Hero Self-Healing) | SUCCESS | 0.1 ms | 1 | 2 |
| Scenario 3: Dynamic Obstacle Incursion | SUCCESS | 0.1 ms | 2 | 2 |
| Scenario 4: Critical Low Battery Recovery | SUCCESS | 0.1 ms | 1 | 2 |
| Scenario 5: Multiple Simultaneous Failures | SUCCESS | 0.1 ms | 2 | 3 |

## Evaluation Methodology
All 5 scenarios are executed deterministically through the exact production reasoning pipeline:
1. Natural language mission prompt submitted.
2. NVIDIA Nemotron decomposes mission into atomic tasks with explicit dependencies.
3. Multi-criteria task allocator checks robot capabilities, battery SOC, and distance.
4. Failure injected during simulated mission execution.
5. Autonomous failure detector classifies anomaly and queries Nemotron for self-healing reassignment.
6. Deterministic Safety Guard verifies coordinate bounds, battery thresholds, collision clearances, and whitelisted action primitives.
7. Reassigned tasks dispatched and executed to completion.
