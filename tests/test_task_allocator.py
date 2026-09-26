"""
Unit Tests for SWARMOS Task Allocator
"""
import pytest
from backend.planning.task_allocator import TaskAllocator
from backend.models.schemas import (
    Robot, Task, Position, TaskType, RobotCapability, RobotState
)

def test_allocator_selects_matching_capability():
    allocator = TaskAllocator()
    fleet = {
        "robot_scout": Robot(
            id="robot_scout",
            name="Scout",
            capabilities=[RobotCapability.SCOUT],
            state=RobotState.IDLE,
            battery=95.0,
            position=Position(x=2.0, y=2.0, z=0.0)
        ),
        "robot_carrier": Robot(
            id="robot_carrier",
            name="Carrier",
            capabilities=[RobotCapability.CARRIER],
            state=RobotState.IDLE,
            battery=90.0,
            position=Position(x=2.0, y=2.0, z=0.0)
        )
    }

    # Heavy transport task requires carrier capability
    transport_task = Task(
        id="t_heavy",
        mission_id="m1",
        title="Move pallet",
        task_type=TaskType.TRANSPORT,
        action="transport",
        target_location=Position(x=10.0, y=10.0, z=0.0)
    )

    best_bot, score, reason = allocator.select_best_robot_for_task(transport_task, fleet)
    assert best_bot == "robot_carrier"
    assert score > 0.6

def test_allocator_excludes_low_battery_robot():
    allocator = TaskAllocator()
    fleet = {
        "carrier_low": Robot(
            id="carrier_low",
            name="Carrier Low Battery",
            capabilities=[RobotCapability.CARRIER],
            state=RobotState.IDLE,
            battery=15.0,  # Below threshold
            position=Position(x=2.0, y=2.0, z=0.0)
        )
    }

    transport_task = Task(
        id="t_heavy",
        mission_id="m1",
        title="Move pallet",
        task_type=TaskType.TRANSPORT,
        action="transport"
    )

    best_bot, score, reason = allocator.select_best_robot_for_task(transport_task, fleet)
    assert best_bot is None
