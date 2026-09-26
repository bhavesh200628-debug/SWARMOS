"""
Unit Tests for SWARMOS Autonomous Failure Recovery
"""
import pytest
from backend.planning.failure_manager import FailureManager
from backend.models.schemas import (
    Robot, Task, Position, TaskType, TaskStatus, FailureType,
    RobotCapability, RobotState
)

@pytest.mark.asyncio
async def test_failure_manager_reassigns_orphaned_task():
    mgr = FailureManager()
    fleet = {
        "robot_a": Robot(
            id="robot_a",
            name="Alpha",
            capabilities=[RobotCapability.SCOUT, RobotCapability.INSPECTOR],
            state=RobotState.IDLE,
            battery=95.0,
            position=Position(x=12.0, y=5.0, z=0.0)
        ),
        "robot_b": Robot(
            id="robot_b",
            name="Bravo",
            capabilities=[RobotCapability.INSPECTOR],
            state=RobotState.INSPECTING,
            battery=90.0,
            position=Position(x=15.0, y=5.0, z=0.0)
        )
    }

    active_tasks = [
        Task(
            id="task_inspect_zone_b",
            mission_id="m1",
            title="Inspect Zone B",
            task_type=TaskType.INSPECT,
            action="inspect",
            assigned_robot_id="robot_b",
            status=TaskStatus.IN_PROGRESS,
            target_location=Position(x=16.0, y=5.0, z=0.0)
        )
    ]

    # Trigger failure on robot_b
    decision = await mgr.handle_robot_failure(
        robot_id="robot_b",
        failure_type=FailureType.ROBOT_UNAVAILABLE,
        description="Camera feed disconnected",
        robots=fleet,
        active_tasks=active_tasks,
        obstacles=[]
    )

    # Robot B should now be offline
    assert fleet["robot_b"].state == RobotState.OFFLINE
    # Task should be reassigned to robot_a
    assert active_tasks[0].assigned_robot_id == "robot_a"
    assert len(decision["reassignments"]) == 1
    assert decision["reassignments"][0]["to_robot"] == "robot_a"
    assert decision["safety_passed"] is True
