# SWARMOS Demo Video Script & Production Plan

**Target Video Duration**: 2 minutes 45 seconds (Strict limit: < 2:50)  
**Music/Audio**: Zero copyrighted music. Clear voiceover audio with subtle mechanical warehouse sound effects.

---

## Shot-by-Shot Timeline

### 0:00 – 0:15 | The Problem Hook
- **Visual**: Cut from footage/renders of individual industrial AMRs operating smoothly to a real robot stalling at a warehouse junction, halting following traffic and sounding error beeps.
- **Voiceover**:
  > *"Today's robots are becoming intelligent individually. But in real-world warehouses and factories, machines break down every single hour: batteries deplete, sensors get blinded, and drive motors stall. When one robot fails, the entire mission fails."*

---

### 0:15 – 0:40 | The SWARMOS Command Center
- **Visual**: Screen capture of the SWARMOS Command Center (`http://localhost:8000`). Show the high-information-density dark UI:
  - Left: Mission DAG breakdown
  - Center: Live digital twin map with animated zones (Zone A, Zone B, Quarantine, Charging) and moving AMRs (Alpha, Bravo, Charlie)
  - Right: Real-time fleet battery SoC, velocity, and coordinate gauges
  - Bottom: AI Decision Timeline
- **Voiceover**:
  > *"Meet SWARMOS: One nervous system for an entire robot fleet. Real-world operations don't need one intelligent robot. They need intelligent, self-healing teams. SWARMOS orchestrates heterogeneous physical robots into a synchronized collective workforce."*

---

### 0:40 – 1:10 | Natural Language Mission Decomposition
- **Visual**: Operator types natural-language prompt in Mission Command:
  `"Inspect Zone B, locate damaged packages, move them to quarantine, and generate an incident report."`
  Click **DISPATCH**.
  Show NVIDIA Nemotron decomposing the goal into 4 structured subtasks with capability requirements and dependencies in under 150ms.
  Show robots begin moving: Alpha (Scout) scans Zone B; Bravo (Inspector) navigates to inspect damaged package `pkg_b1`.
- **Voiceover**:
  > *"The operator simply types what needs to be done. Powered by NVIDIA Nemotron on Nebius Token Factory, SWARMOS decomposes the high-level mission into an explicit dependency graph. Tasks are assigned deterministically to the best-suited robot based on proximity, battery, and capabilities. Alpha scouts Zone B, while Bravo approaches the target container."*

---

### 1:10 – 1:45 | The Hero Moment: Robot Failure & Detection
- **Visual**: In the Command Center, click **TRIGGER FAILURE** (or inject via API).
  Robot Bravo's state immediately turns red (`DEGRADED / OFFLINE`) on the digital twin with a pulsing strobe.
  The bottom timeline logs: `15:42:11 - ALERT: Robot Bravo optical sensor bus severed & drive motor stalled.`
  The active inspection task on `pkg_b1` becomes orphaned.
- **Voiceover**:
  > *"Now, the unexpected happens: Robot Bravo's optical sensor bus malfunctions and its drive motor stalls inside Zone B. In a conventional facility, this stops the line. In SWARMOS, autonomous failure detection kicks in instantaneously."*

---

### 1:45 – 2:10 | Nemotron Self-Healing Replanning
- **Visual**: The UI displays `🧠 REPLANNING SWARM...`
  Within 120ms, NVIDIA Nemotron reasons over remaining healthy nodes:
  `"Reason: Robot Bravo is incapacitated. Robot Alpha is in close proximity with optical scout cameras. Reassigning inspection task to Alpha."`
  Show Deterministic Safety Guard verify the new coordinates (`Safety Check: PASSED`).
  On the map, Robot Alpha changes heading and navigates directly to replace Bravo.
- **Voiceover**:
  > *"SWARMOS immediately packages the fleet state and queries NVIDIA Nemotron via Nebius Token Factory. In under 150 milliseconds, Nemotron analyzes available nodes, recognizes that Alpha possesses redundant camera capabilities and the closest distance, and dynamically reassigns the inspection. Deterministic safety constraints verify the plan, and Alpha takes over without a second wasted."*

---

### 2:10 – 2:30 | Mission Recovery & Completion
- **Visual**: Robot Alpha arrives at `pkg_b1`, confirms damage.
  Robot Charlie (Carrier-03) picks up `pkg_b1` (showing `pkg_b1` attached to Charlie on the digital twin) and transports it across the Transit Corridor into the Quarantine Zone.
  `pkg_b1` changes status to `[SECURE / QUARANTINED]`.
  Mission status updates to `COMPLETED` and an automated incident report card appears.
- **Voiceover**:
  > *"Alpha verifies the defective cargo. Robot Charlie hauls the container into the Quarantine Zone. The mission is completed in full, an audit report is compiled, and zero humans had to enter the hazardous zone."*

---

### 2:30 – 2:45 | The Nebius + NVIDIA Architecture
- **Visual**: Architecture slide showing Nebius Token Factory (`api.studio.nebius.ai/v1`) running NVIDIA Nemotron 70B, passing structured JSON into the Deterministic Safety Guard, connected to the Hardware Abstraction Layer (HAL) for both simulation and physical ROS2 rovers.
  Show benchmark table: 100% mission recovery, 0 safety violations, < 150ms mean replan time.
- **Voiceover**:
  > *"Under the hood, Nebius Token Factory provides the ultra-low-latency GPU inference backbone. NVIDIA Nemotron delivers the deep mission-level reasoning, while our deterministic software guarantees hard physical safety."*

---

### 2:45 – 2:55 | Impact & Closing
- **Visual**: SWARMOS logo with tagline: *"One nervous system for an entire robot fleet."* GitHub repo URL on screen.
- **Voiceover**:
  > *"We are not giving robots another brain. We're giving the entire fleet one nervous system. This is SWARMOS. Thank you."*
