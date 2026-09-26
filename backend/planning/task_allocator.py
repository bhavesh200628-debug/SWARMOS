"""
SWARMOS Deterministic Task Allocator
Multi-criteria optimization matching tasks to heterogeneous robots based on:
1. Hard Capability Filters (Scout, Inspector, Carrier)
2. Euclidian Distance & Proximity to Target Location
3. Battery State of Charge (SoC)
4. Current Workload & Availability Status
5. Health Status (Offline / Degraded / Nominal)
"""
import math
import logging
from typing import Dict, List, Optional, Tuple
from backend.models.schemas import Robot, Task, RobotState, Position, RobotCapability

logger = logging.getLogger("swarmos.task_allocator")

CAPABILITY_REQUIREMENTS = {
    "navigate": [RobotCapability.SCOUT, RobotCapability.INSPECTOR, RobotCapability.CARRIER],
    "inspect": [RobotCapability.INSPECTOR, RobotCapability.SCOUT],
    "identify": [RobotCapability.INSPECTOR, RobotCapability.SCOUT],
    "transport": [RobotCapability.CARRIER, RobotCapability.HEAVY_LIFT],
    "verify": [RobotCapability.INSPECTOR, RobotCapability.SCOUT],
    "report_status": [RobotCapability.SCOUT, RobotCapability.INSPECTOR, RobotCapability.CARRIER],
    "return_to_base": [RobotCapability.SCOUT, RobotCapability.INSPECTOR, RobotCapability.CARRIER]
}

class TaskAllocator:
    def __init__(self):
        # Weights for multi-criteria objective function
        self.w_capability = 0.35
        self.w_proximity = 0.30
        self.w_battery = 0.20
        self.w_availability = 0.15

    def select_best_robot_for_task(
        self,
        task: Task,
        robots: Dict[str, Robot],
        exclude_robot_ids: Optional[List[str]] = None
    ) -> Tuple[Optional[str], float, str]:
        """
        Evaluates candidate robots against task requirements and returns:
        (best_robot_id, score, justification)
        """
        exclude_set = set(exclude_robot_ids or [])
        allowed_caps = CAPABILITY_REQUIREMENTS.get(task.action, [RobotCapability.SCOUT])
        
        candidates: List[Tuple[str, float, str]] = []

        for robot_id, robot in robots.items():
            if robot_id in exclude_set:
                continue

            # Hard constraint 1: Operational Status
            if robot.state in [RobotState.OFFLINE, RobotState.DEGRADED]:
                continue

            # Hard constraint 2: Battery threshold
            if robot.battery < 20.0:
                continue

            # Hard constraint 3: Capability matching
            has_matching_cap = any(cap in allowed_caps for cap in robot.capabilities)
            if not has_matching_cap:
                continue

            # Multi-criteria scoring [0.0 - 1.0]
            # 1. Capability affinity (1.0 for exact primary match, 0.7 for secondary)
            cap_score = 1.0 if robot.capabilities[0] in allowed_caps else 0.7

            # 2. Proximity (closer is higher score)
            prox_score = 0.5
            if task.target_location:
                dist = math.hypot(
                    task.target_location.x - robot.position.x,
                    task.target_location.y - robot.position.y
                )
                max_warehouse_diag = math.hypot(30.0, 20.0)
                prox_score = max(0.0, 1.0 - (dist / max_warehouse_diag))

            # 3. Battery score
            battery_score = robot.battery / 100.0

            # 4. Availability / Workload score
            avail_score = 1.0 if robot.state == RobotState.IDLE else 0.4

            total_score = (
                self.w_capability * cap_score +
                self.w_proximity * prox_score +
                self.w_battery * battery_score +
                self.w_availability * avail_score
            )

            reason = (
                f"Cap match ({robot.capabilities[0].value}), "
                f"Proximity score: {prox_score:.2f}, "
                f"Battery: {robot.battery:.0f}%, "
                f"State: {robot.state.value}"
            )
            candidates.append((robot_id, total_score, reason))

        if not candidates:
            return None, 0.0, "No operational robot satisfies the required capabilities and battery constraints."

        # Sort descending by score
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_id, best_score, best_reason = candidates[0]
        return best_id, best_score, best_reason

# Global allocator singleton
task_allocator = TaskAllocator()
