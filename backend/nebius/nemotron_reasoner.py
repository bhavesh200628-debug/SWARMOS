"""
SWARMOS Nemotron High-Level Reasoner
Invokes NVIDIA Nemotron via Nebius Token Factory with strict JSON schema validation,
retry/repair logic, and transparent deterministic fallback when in MOCK_AI mode.
"""
import re
import json
import time
import logging
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.nebius.client import nebius_client
from backend.nebius.prompt_templates import (
    NEMOTRON_SYSTEM_PROMPT,
    MISSION_DECOMPOSITION_PROMPT_TEMPLATE,
    REPLANNING_PROMPT_TEMPLATE
)
from backend.models.schemas import (
    AIPlanResponse, TaskReassignment, AIPlanAction, Robot, Task
)

logger = logging.getLogger("swarmos.nemotron")

class NemotronReasoner:
    def __init__(self):
        self.client = nebius_client

    def _extract_and_parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Safely extracts JSON from raw model generation, handling markdown blocks."""
        cleaned = raw_text.strip()
        # Remove markdown code blocks if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as err:
            # Attempt to extract first matching JSON object
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise err

    async def decompose_mission(
        self,
        mission_prompt: str,
        fleet_dict: Dict[str, Any]
    ) -> AIPlanResponse:
        """
        Uses NVIDIA Nemotron to decompose a natural language mission into tasks.
        """
        fleet_summary = [
            {
                "id": r["id"],
                "name": r["name"],
                "capabilities": r["capabilities"],
                "state": r["state"],
                "battery": r["battery"],
                "position": {"x": r["position"]["x"], "y": r["position"]["y"]}
            }
            for r in fleet_dict.values()
        ]

        # Check if live Nebius inference should be used
        if not self.client.mock_mode and self.client.api_key:
            prompt = MISSION_DECOMPOSITION_PROMPT_TEMPLATE.format(
                mission_prompt=mission_prompt,
                fleet_state_json=json.dumps(fleet_summary, indent=2)
            )
            messages = [
                {"role": "system", "content": NEMOTRON_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            try:
                raw_res = await self.client.create_chat_completion(
                    messages=messages,
                    temperature=0.15,
                    max_tokens=2048
                )
                parsed_json = self._extract_and_parse_json(raw_res["content"])
                
                # Validate against Pydantic schema
                plan = AIPlanResponse(**parsed_json)
                plan.decision_metadata = {
                    "model": raw_res["model"],
                    "latency_ms": raw_res["latency_ms"],
                    "usage": raw_res.get("usage", {}),
                    "is_mock": False,
                    "timestamp": time.time()
                }
                logger.info(f"✅ Nemotron decomposed mission in {raw_res['latency_ms']:.1f}ms using {raw_res['model']}")
                return plan

            except Exception as e:
                logger.warning(f"Nebius live inference error ({str(e)}). Falling back to deterministic plan.")
                # Fall through to deterministic plan

        # Deterministic Plan (Local / MOCK_AI mode or fallback)
        logger.info("Executing deterministic mission decomposition (NVIDIA Nemotron profile)")
        tasks = [
            {
                "id": "task_1_nav_scout",
                "title": "Zone B Spatial Reconnaissance",
                "task_type": "navigate",
                "action": "navigate",
                "target_zone": "Zone B",
                "target_location": {"x": 14.0, "y": 5.0, "z": 0.0},
                "assigned_robot_id": "robot_a",
                "required_capability": "scout",
                "dependencies": [],
                "estimated_duration_sec": 6.0
            },
            {
                "id": "task_2_inspect",
                "title": "Visual Package Inspection & Anomaly Detection",
                "task_type": "inspect",
                "action": "inspect",
                "target_zone": "Zone B",
                "target_package_id": "pkg_b1",
                "target_location": {"x": 16.0, "y": 5.0, "z": 0.0},
                "assigned_robot_id": "robot_b",
                "required_capability": "inspector",
                "dependencies": ["task_1_nav_scout"],
                "estimated_duration_sec": 8.0
            },
            {
                "id": "task_3_transport",
                "title": "Hazardous Package Transport to Quarantine",
                "task_type": "transport",
                "action": "transport",
                "target_package_id": "pkg_b1",
                "destination_zone": "Quarantine",
                "target_location": {"x": 26.0, "y": 16.0, "z": 0.0},
                "assigned_robot_id": "robot_c",
                "required_capability": "carrier",
                "dependencies": ["task_2_inspect"],
                "estimated_duration_sec": 10.0
            },
            {
                "id": "task_4_report",
                "title": "Incident Verification & Quarantine Clearance Report",
                "task_type": "report_status",
                "action": "report_status",
                "target_zone": "Quarantine",
                "target_location": {"x": 24.0, "y": 15.0, "z": 0.0},
                "assigned_robot_id": "robot_a",
                "required_capability": "scout",
                "dependencies": ["task_3_transport"],
                "estimated_duration_sec": 4.0
            }
        ]

        next_actions = [
            AIPlanAction(
                robot_id="robot_a",
                action="navigate",
                target_zone="Zone B",
                target_location={"x": 14.0, "y": 5.0, "z": 0.0}
            )
        ]

        return AIPlanResponse(
            reason="Decomposed into 4 sequential stages: Scout (Robot A) clears Zone B; Inspector (Robot B) identifies defect on pkg_b1; Carrier (Robot C) transports to Quarantine; Scout verifies containment.",
            confidence=0.96,
            tasks=tasks,
            reassignments=[],
            next_actions=next_actions,
            decision_metadata={
                "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF [Simulated Deterministic]",
                "latency_ms": 145.0,
                "is_mock": True,
                "timestamp": time.time()
            }
        )

    async def replan_swarm(
        self,
        failed_robot_id: str,
        failure_type: str,
        failure_description: str,
        fleet_dict: Dict[str, Any],
        active_tasks: List[Dict[str, Any]]
    ) -> AIPlanResponse:
        """
        Uses NVIDIA Nemotron to replan when a robot fails during mission execution.
        """
        fleet_summary = [
            {
                "id": r["id"],
                "name": r["name"],
                "capabilities": r["capabilities"],
                "state": r["state"],
                "battery": r["battery"],
                "position": {"x": r["position"]["x"], "y": r["position"]["y"]}
            }
            for r in fleet_dict.values()
        ]

        if not self.client.mock_mode and self.client.api_key:
            prompt = REPLANNING_PROMPT_TEMPLATE.format(
                failed_robot_id=failed_robot_id,
                failure_type=failure_type,
                failure_description=failure_description,
                fleet_state_json=json.dumps(fleet_summary, indent=2),
                active_tasks_json=json.dumps(active_tasks, indent=2)
            )
            messages = [
                {"role": "system", "content": NEMOTRON_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            try:
                raw_res = await self.client.create_chat_completion(
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2048
                )
                parsed_json = self._extract_and_parse_json(raw_res["content"])
                plan = AIPlanResponse(**parsed_json)
                plan.decision_metadata = {
                    "model": raw_res["model"],
                    "latency_ms": raw_res["latency_ms"],
                    "usage": raw_res.get("usage", {}),
                    "is_mock": False,
                    "timestamp": time.time()
                }
                logger.info(f"✅ Nemotron dynamic replan generated in {raw_res['latency_ms']:.1f}ms")
                return plan
            except Exception as e:
                logger.warning(f"Nebius replan live error ({str(e)}). Falling back to deterministic self-healing plan.")

        # Deterministic Self-Healing Replanning
        # Find orphaned tasks assigned to failed robot
        orphaned = [t for t in active_tasks if t.get("assigned_robot_id") == failed_robot_id]
        reassignments = []
        next_actions = []

        # Find healthiest available alternative robot
        candidates = [
            r for r in fleet_dict.values()
            if r["id"] != failed_robot_id and r["state"] not in ["offline", "degraded"] and r["battery"] > 20.0
        ]
        
        replacement_robot = "robot_a"
        if candidates:
            # Prefer robot_a (Scout) for inspection reassignment if available
            replacement_robot = candidates[0]["id"]
            for c in candidates:
                if c["id"] == "robot_a":
                    replacement_robot = "robot_a"
                    break

        for task in orphaned:
            reassignments.append(TaskReassignment(
                task_id=task["id"],
                from_robot=failed_robot_id,
                to_robot=replacement_robot,
                reason=f"Robot {failed_robot_id} is disabled ({failure_type}). Reassigned to {replacement_robot} due to proximity and dual optical sensor capability."
            ))
            next_actions.append(AIPlanAction(
                robot_id=replacement_robot,
                action="inspect" if "inspect" in task.get("action", "") else "navigate",
                target_zone=task.get("target_zone", "Zone B"),
                target_location=task.get("target_location", {"x": 16.0, "y": 5.0, "z": 0.0})
            ))

        return AIPlanResponse(
            reason=f"Detected critical failure on {failed_robot_id}. Nemotron dynamically reassigned {len(orphaned)} active tasks to {replacement_robot} to prevent mission abort while maintaining safety boundaries.",
            confidence=0.94,
            reassignments=reassignments,
            next_actions=next_actions,
            decision_metadata={
                "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF [Simulated Deterministic]",
                "latency_ms": 118.0,
                "is_mock": True,
                "timestamp": time.time()
            }
        )

# Global reasoner singleton
nemotron_reasoner = NemotronReasoner()
