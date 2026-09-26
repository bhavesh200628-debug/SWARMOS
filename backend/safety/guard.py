"""
SWARMOS Deterministic Safety Guard
Ensures that all AI-generated plans, task allocations, and direct robot actions
strictly comply with physical bounds, collision barriers, battery thresholds,
and an explicit whitelist of permissible robotic primitives.
"""
from typing import List, Dict, Tuple, Optional
import math
from backend.models.schemas import (
    Robot, Obstacle, Position, AIPlanAction, SafetyCheckResult, RobotState
)
from backend.config import settings

class SafetyGuard:
    def __init__(self):
        # Physical warehouse workspace bounds in meters
        self.x_bounds = (0.0, 30.0)
        self.y_bounds = (0.0, 20.0)
        self.min_battery_threshold = settings.MIN_BATTERY_FOR_MISSION
        self.collision_margin = settings.COLLISION_PROXIMITY_LIMIT
        self.allowed_actions = set(settings.ALLOWED_ACTIONS)

    def validate_plan_actions(
        self,
        actions: List[AIPlanAction],
        robots: Dict[str, Robot],
        obstacles: List[Obstacle]
    ) -> SafetyCheckResult:
        violations: List[str] = []
        approved: List[AIPlanAction] = []
        rejected: List[AIPlanAction] = []
        audit_trail: List[str] = []

        for action in actions:
            action_valid = True
            action_desc = f"Action '{action.action}' for robot '{action.robot_id}'"

            # 1. Whitelist Check
            if action.action not in self.allowed_actions:
                violations.append(f"UNAUTHORIZED_ACTION: Action '{action.action}' is not in the allowed safety whitelist: {list(self.allowed_actions)}")
                action_valid = False

            # 2. Robot Existence Check
            if action.robot_id not in robots:
                violations.append(f"UNKNOWN_ROBOT: Target robot '{action.robot_id}' does not exist in fleet registry.")
                action_valid = False
            else:
                robot = robots[action.robot_id]
                # 3. Robot Operational State Check
                if robot.state == RobotState.OFFLINE and action.action != "report_status":
                    violations.append(f"ROBOT_OFFLINE: Robot '{robot.id}' is offline and cannot accept movement commands.")
                    action_valid = False
                
                # 4. Battery Level Check
                if robot.battery < self.min_battery_threshold and action.action not in ["return_to_base", "stop", "report_status"]:
                    violations.append(f"BATTERY_CRITICAL: Robot '{robot.id}' battery at {robot.battery:.1f}% (minimum required: {self.min_battery_threshold}%).")
                    action_valid = False

            # 5. Spatial Boundary Check (if destination given)
            if action.target_location:
                x, y = action.target_location.x, action.target_location.y
                if not (self.x_bounds[0] <= x <= self.x_bounds[1] and self.y_bounds[0] <= y <= self.y_bounds[1]):
                    violations.append(f"BOUNDARY_VIOLATION: Target coordinates ({x:.2f}, {y:.2f}) exceed warehouse perimeter ({self.x_bounds}, {self.y_bounds}).")
                    action_valid = False

                # 6. Obstacle Collision Check
                for obs in obstacles:
                    dist = math.hypot(x - obs.position.x, y - obs.position.y)
                    safe_dist = obs.radius + self.collision_margin
                    if dist < safe_dist:
                        violations.append(f"COLLISION_HAZARD: Target ({x:.2f}, {y:.2f}) is within {dist:.2f}m of obstacle '{obs.id}' (safe margin: {safe_dist:.2f}m).")
                        action_valid = False

            if action_valid:
                approved.append(action)
                audit_trail.append(f"PASSED: {action_desc} approved by SafetyGuard.")
            else:
                rejected.append(action)
                audit_trail.append(f"REJECTED: {action_desc} blocked by SafetyGuard.")

        passed = len(violations) == 0
        return SafetyCheckResult(
            passed=passed,
            violations=violations,
            allowed_actions=approved,
            rejected_actions=rejected,
            safety_audit_trail=audit_trail
        )

    def validate_single_action(
        self,
        robot: Robot,
        action_name: str,
        target_pos: Optional[Position],
        obstacles: List[Obstacle]
    ) -> Tuple[bool, Optional[str]]:
        """Fast check for single robot transition"""
        if action_name not in self.allowed_actions:
            return False, f"Action '{action_name}' not permitted."
        
        if robot.state == RobotState.OFFLINE and action_name != "report_status":
            return False, f"Robot '{robot.id}' is OFFLINE."

        if target_pos:
            if not (self.x_bounds[0] <= target_pos.x <= self.x_bounds[1] and self.y_bounds[0] <= target_pos.y <= self.y_bounds[1]):
                return False, f"Location ({target_pos.x:.1f}, {target_pos.y:.1f}) is out of warehouse bounds."
            
            for obs in obstacles:
                dist = math.hypot(target_pos.x - obs.position.x, target_pos.y - obs.position.y)
                if dist < (obs.radius + self.collision_margin):
                    return False, f"Location collides with obstacle '{obs.id}'."

        return True, None

# Global safety guard singleton
safety_guard = SafetyGuard()
