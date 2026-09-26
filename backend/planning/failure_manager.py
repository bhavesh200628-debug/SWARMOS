"""
SWARMOS Failure Manager
Detects anomalies, classifies failure modes, queries Nemotron on Nebius for self-healing replans,
enforces safety validation, and dispatches dynamic task reassignments to the fleet.
"""
import time
import logging
from typing import Dict, Any, List, Optional
from backend.models.schemas import (
    FailureType, FailureEvent, RobotState, Robot, Task, TaskStatus,
    AIPlanResponse, SafetyCheckResult
)
from backend.nebius.nemotron_reasoner import nemotron_reasoner
from backend.safety.guard import safety_guard
from backend.planning.task_allocator import task_allocator

logger = logging.getLogger("swarmos.failure_manager")

class FailureManager:
    def __init__(self):
        self.active_failures: Dict[str, FailureEvent] = {}
        self.decision_history: List[Dict[str, Any]] = []

    async def handle_robot_failure(
        self,
        robot_id: str,
        failure_type: FailureType,
        description: str,
        robots: Dict[str, Robot],
        active_tasks: List[Task],
        obstacles: list
    ) -> Dict[str, Any]:
        """
        Full Autonomous Self-Healing Lifecycle:
        DETECT -> CLASSIFY -> REPLAN -> VALIDATE -> EXECUTE
        """
        timestamp = time.time()
        event_id = f"fail_{int(timestamp)}_{robot_id}"
        
        # 1. DETECT & CLASSIFY
        event = FailureEvent(
            id=event_id,
            timestamp=timestamp,
            robot_id=robot_id,
            failure_type=failure_type,
            description=description,
            severity="critical" if failure_type in [FailureType.ROBOT_UNAVAILABLE, FailureType.COMMUNICATION_LOSS] else "warning"
        )
        self.active_failures[event_id] = event
        
        # Mark robot state in fleet
        if robot_id in robots:
            failed_bot = robots[robot_id]
            failed_bot.target_position = None
            failed_bot.velocity = 0.0
            failed_bot.current_task_id = None
            if failure_type == FailureType.LOW_BATTERY:
                failed_bot.state = RobotState.LOW_BATTERY
            elif failure_type == FailureType.OBSTACLE_DETECTED:
                failed_bot.state = RobotState.BLOCKED
            else:
                failed_bot.state = RobotState.OFFLINE
        
        logger.warning(f"🚨 [FAILURE DETECTED] Robot {robot_id}: {failure_type.value} - {description}")

        # Mark all active tasks of failed robot as ORPHANED
        for t in active_tasks:
            if t.assigned_robot_id == robot_id and t.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS, TaskStatus.PENDING]:
                t.status = TaskStatus.ORPHANED
                logger.info(f"⚠️ Task '{t.id}' orphaned due to {robot_id} failure.")

        # 2. REPLAN (Query NVIDIA Nemotron via Nebius)
        orphaned_tasks = [
            t.model_dump() for t in active_tasks
            if t.assigned_robot_id == robot_id and t.status == TaskStatus.ORPHANED
        ]
        
        fleet_dict = {rid: r.model_dump() for rid, r in robots.items()}

        logger.info(f"🧠 Initiating Nemotron replan for {len(orphaned_tasks)} orphaned tasks...")
        ai_plan: AIPlanResponse = await nemotron_reasoner.replan_swarm(
            failed_robot_id=robot_id,
            failure_type=failure_type.value,
            failure_description=description,
            fleet_dict=fleet_dict,
            active_tasks=orphaned_tasks
        )

        # 3. SAFETY VALIDATION
        safety_result: SafetyCheckResult = safety_guard.validate_plan_actions(
            actions=ai_plan.next_actions,
            robots=robots,
            obstacles=obstacles
        )

        reassigned_tasks: List[Dict[str, Any]] = []

        # 4. EXECUTE & COMMIT REASSIGNMENT
        if safety_result.passed or len(safety_result.allowed_actions) > 0:
            for reassignment in ai_plan.reassignments:
                # Find task and update assigned robot
                for t in active_tasks:
                    if t.id == reassignment.task_id:
                        old_robot = t.assigned_robot_id
                        t.assigned_robot_id = reassignment.to_robot
                        t.status = TaskStatus.ASSIGNED
                        t.progress = 0.0
                        # Update replacement robot target in simulation
                        if reassignment.to_robot in robots:
                            rep_bot = robots[reassignment.to_robot]
                            rep_bot.current_task_id = t.id
                            if t.target_location:
                                rep_bot.target_position = t.target_location
                                rep_bot.state = RobotState.NAVIGATING

                        reassigned_tasks.append({
                            "task_id": t.id,
                            "title": t.title,
                            "from_robot": old_robot,
                            "to_robot": reassignment.to_robot,
                            "reason": reassignment.reason
                        })
                        logger.info(f"🔄 Reassigned task '{t.id}' from {old_robot} to {reassignment.to_robot}")

            event.resolved = True
            event.resolved_at = time.time()
            event.mitigation_action = f"Tasks reassigned via Nemotron to: {[r.to_robot for r in ai_plan.reassignments]}"
        else:
            logger.error(f"❌ Safety check failed on Nemotron replan: {safety_result.violations}")
            # Fallback to deterministic allocator
            for task in active_tasks:
                if task.assigned_robot_id == robot_id:
                    alt_robot, score, reason = task_allocator.select_best_robot_for_task(
                        task=task,
                        robots=robots,
                        exclude_robot_ids=[robot_id]
                    )
                    if alt_robot:
                        task.assigned_robot_id = alt_robot
                        reassigned_tasks.append({
                            "task_id": task.id,
                            "title": task.title,
                            "from_robot": robot_id,
                            "to_robot": alt_robot,
                            "reason": f"Deterministic safety fallback: {reason}"
                        })

        decision_log = {
            "timestamp": time.time(),
            "event": "failure_replanned",
            "failed_robot": robot_id,
            "failure_type": failure_type.value,
            "reasoning": ai_plan.reason,
            "confidence": ai_plan.confidence,
            "model": ai_plan.decision_metadata.get("model", "NVIDIA Nemotron"),
            "latency_ms": ai_plan.decision_metadata.get("latency_ms", 120.0),
            "safety_passed": safety_result.passed,
            "reassignments": reassigned_tasks
        }
        self.decision_history.append(decision_log)

        return decision_log

# Global failure manager singleton
failure_manager = FailureManager()
