"""
SWARMOS Prompt Templates
High-precision structured prompts designed for NVIDIA Nemotron reasoning on Nebius Token Factory.
"""

NEMOTRON_SYSTEM_PROMPT = """You are NVIDIA Nemotron acting as the centralized high-level reasoning engine for SWARMOS, an AI orchestration layer for heterogeneous robot fleets.

Your role:
1. Decompose complex natural language missions into structured subtasks with explicit dependencies and required capabilities.
2. Dynamically reallocate tasks and self-heal the swarm when robot failures, obstacles, or battery depletion occur.
3. Provide concise, explainable, structured rationale for fleet allocation decisions.
4. Output STRICT, VALID machine-readable JSON matching the requested schema without markdown decorations, conversational filler, or unescaped characters.

Fleet Capabilities:
- "scout": Agile, high-speed spatial exploration, mapping, and hazard discovery.
- "inspector": High-resolution visual inspection, defect detection, and QR/barcode scanning.
- "carrier": High-payload transport, package hauling, and quarantine delivery.

Physical Primitives Allowed:
- "navigate" (requires target_location x, y or target_zone)
- "inspect" (requires target_zone or target_package_id)
- "transport" (requires target_package_id and destination_zone)
- "stop" (emergency halt)
- "report_status" (incident reporting summary)
- "return_to_base" (low battery recovery)
"""

MISSION_DECOMPOSITION_PROMPT_TEMPLATE = """DECOMPOSE THE FOLLOWING WAREHOUSE MISSION:
Mission Prompt: "{mission_prompt}"

Current Fleet State:
{fleet_state_json}

Available Warehouse Zones:
- Zone A: Storage & Intake (x: 2-10, y: 2-8)
- Zone B: High-Density Staging & Inspection (x: 12-22, y: 2-8)
- Quarantine: Hazardous / Damaged Material Hold (x: 24-28, y: 14-18)
- Charging Bay: Power Replenishment (x: 2-6, y: 14-18)
- Transit Corridor: Main thoroughfare (x: 2-28, y: 9-13)

Decompose this mission into a sequence of atomic tasks.
Assign initial robots based on capability matching and proximity.

Output MUST be a single JSON object with this EXACT structure:
{{
  "reason": "Clear 1-2 sentence engineering justification for the plan",
  "confidence": 0.95,
  "tasks": [
    {{
      "id": "task_1",
      "title": "Short descriptive title",
      "task_type": "navigate | inspect | identify | transport | verify | report_status",
      "action": "navigate | inspect | transport | report_status",
      "target_zone": "Zone A | Zone B | Quarantine | Charging Bay",
      "target_package_id": "pkg_1 | null",
      "destination_zone": "Quarantine | null",
      "assigned_robot_id": "robot_a | robot_b | robot_c",
      "required_capability": "scout | inspector | carrier",
      "dependencies": [],
      "estimated_duration_sec": 10.0
    }}
  ],
  "next_actions": [
    {{
      "robot_id": "robot_a",
      "action": "navigate",
      "target_zone": "Zone B"
    }}
  ]
}}
"""

REPLANNING_PROMPT_TEMPLATE = """SELF-HEALING SWARM REPLANNING REQUIRED!

Trigger Event:
Robot '{failed_robot_id}' encountered FAILURE: {failure_type} ({failure_description})

Fleet Status at Failure Point:
{fleet_state_json}

Active Tasks In Progress / Pending:
{active_tasks_json}

Warehouse Constraints:
- Robot '{failed_robot_id}' is OFFLINE / INCAPACITATED and cannot be assigned tasks.
- Only ACTIVE / IDLE robots can assume orphaned tasks.
- Tasks must match robot capabilities or multi-role generalist capabilities.
- Respect existing completed task dependencies.

Produce a dynamic self-healing reassignment plan.
Output MUST be a single JSON object with this EXACT structure:
{{
  "reason": "Concise 1-2 sentence explanation of why the chosen replacement robot was selected (e.g. proximity, capability match, workload)",
  "confidence": 0.92,
  "reassignments": [
    {{
      "task_id": "task_xyz",
      "from_robot": "{failed_robot_id}",
      "to_robot": "replacement_robot_id",
      "reason": "Replacement robot has suitable capability and lowest travel distance."
    }}
  ],
  "next_actions": [
    {{
      "robot_id": "replacement_robot_id",
      "action": "navigate | inspect | transport",
      "target_zone": "Zone B"
    }}
  ]
}}
"""
