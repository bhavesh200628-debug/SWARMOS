"""
Unit Tests for SWARMOS Deterministic Safety Guard
"""
import pytest
from backend.safety.guard import SafetyGuard
from backend.models.schemas import (
    Robot, Obstacle, Position, AIPlanAction, RobotCapability, RobotState
)

@pytest.fixture
def sample_fleet():
    return {
        "robot_a": Robot(
            id="robot_a",
            name="Alpha",
            capabilities=[RobotCapability.SCOUT],
            state=RobotState.IDLE,
            battery=90.0,
            position=Position(x=5.0, y=5.0, z=0.0)
        ),
        "robot_b": Robot(
            id="robot_b",
            name="Bravo",
            capabilities=[RobotCapability.INSPECTOR],
            state=RobotState.OFFLINE,
            battery=80.0,
            position=Position(x=10.0, y=10.0, z=0.0)
        ),
        "robot_c": Robot(
            id="robot_c",
            name="Charlie",
            capabilities=[RobotCapability.CARRIER],
            state=RobotState.IDLE,
            battery=12.0,  # Below 20% limit
            position=Position(x=15.0, y=15.0, z=0.0)
        )
    }

@pytest.fixture
def sample_obstacles():
    return [
        Obstacle(
            id="obs_pillar",
            position=Position(x=10.0, y=10.0, z=0.0),
            radius=1.0,
            is_dynamic=False
        )
    ]

def test_safety_guard_approves_valid_action(sample_fleet, sample_obstacles):
    guard = SafetyGuard()
    actions = [
        AIPlanAction(
            robot_id="robot_a",
            action="navigate",
            target_location=Position(x=6.0, y=6.0, z=0.0)
        )
    ]
    result = guard.validate_plan_actions(actions, sample_fleet, sample_obstacles)
    assert result.passed is True
    assert len(result.allowed_actions) == 1
    assert len(result.violations) == 0

def test_safety_guard_rejects_unwhitelisted_action(sample_fleet, sample_obstacles):
    guard = SafetyGuard()
    actions = [
        AIPlanAction(
            robot_id="robot_a",
            action="execute_shell_rm_rf",  # Malicious/invalid command
            target_location=Position(x=6.0, y=6.0, z=0.0)
        )
    ]
    result = guard.validate_plan_actions(actions, sample_fleet, sample_obstacles)
    assert result.passed is False
    assert any("UNAUTHORIZED_ACTION" in v for v in result.violations)

def test_safety_guard_rejects_offline_robot(sample_fleet, sample_obstacles):
    guard = SafetyGuard()
    actions = [
        AIPlanAction(
            robot_id="robot_b",  # Robot B is OFFLINE
            action="navigate",
            target_location=Position(x=12.0, y=12.0, z=0.0)
        )
    ]
    result = guard.validate_plan_actions(actions, sample_fleet, sample_obstacles)
    assert result.passed is False
    assert any("ROBOT_OFFLINE" in v for v in result.violations)

def test_safety_guard_rejects_critical_low_battery(sample_fleet, sample_obstacles):
    guard = SafetyGuard()
    actions = [
        AIPlanAction(
            robot_id="robot_c",  # Robot C battery is 12% (< 20%)
            action="transport",
            target_location=Position(x=20.0, y=10.0, z=0.0)
        )
    ]
    result = guard.validate_plan_actions(actions, sample_fleet, sample_obstacles)
    assert result.passed is False
    assert any("BATTERY_CRITICAL" in v for v in result.violations)

def test_safety_guard_rejects_out_of_bounds_target(sample_fleet, sample_obstacles):
    guard = SafetyGuard()
    actions = [
        AIPlanAction(
            robot_id="robot_a",
            action="navigate",
            target_location=Position(x=99.0, y=99.0, z=0.0)  # Outside 30x20 perimeter
        )
    ]
    result = guard.validate_plan_actions(actions, sample_fleet, sample_obstacles)
    assert result.passed is False
    assert any("BOUNDARY_VIOLATION" in v for v in result.violations)

def test_safety_guard_rejects_obstacle_collision(sample_fleet, sample_obstacles):
    guard = SafetyGuard()
    actions = [
        AIPlanAction(
            robot_id="robot_a",
            action="navigate",
            target_location=Position(x=10.2, y=10.2, z=0.0)  # Too close to obstacle at (10, 10)
        )
    ]
    result = guard.validate_plan_actions(actions, sample_fleet, sample_obstacles)
    assert result.passed is False
    assert any("COLLISION_HAZARD" in v for v in result.violations)

def test_safety_guard_rejects_capability_mismatch(sample_fleet, sample_obstacles):
    guard = SafetyGuard()
    # Robot A is SCOUT, should not be allowed to execute 'transport'
    actions = [
        AIPlanAction(
            robot_id="robot_a",
            action="transport",
            target_location=Position(x=12.0, y=12.0, z=0.0)
        )
    ]
    result = guard.validate_plan_actions(actions, sample_fleet, sample_obstacles)
    assert result.passed is False
    assert any("CAPABILITY_MISMATCH" in v for v in result.violations)

def test_safety_guard_allows_low_battery_return_to_base(sample_fleet, sample_obstacles):
    guard = SafetyGuard()
    # Robot C has 12% battery (<20%), but return_to_base, stop, and report_status must be allowed
    actions = [
        AIPlanAction(
            robot_id="robot_c",
            action="return_to_base",
            target_location=Position(x=2.0, y=2.0, z=0.0)
        ),
        AIPlanAction(
            robot_id="robot_c",
            action="stop",
            target_location=Position(x=15.0, y=15.0, z=0.0)
        ),
        AIPlanAction(
            robot_id="robot_c",
            action="report_status"
        )
    ]
    result = guard.validate_plan_actions(actions, sample_fleet, sample_obstacles)
    assert result.passed is True
    assert len(result.allowed_actions) == 3

def test_safety_guard_emergency_stop_all(sample_fleet, sample_obstacles):
    guard = SafetyGuard()
    estop_actions = guard.emergency_stop_all(sample_fleet)
    # Robot B is OFFLINE, so estop should target robot_a and robot_c
    target_ids = {a.robot_id for a in estop_actions}
    assert "robot_a" in target_ids
    assert "robot_c" in target_ids
    assert "robot_b" not in target_ids
    assert all(a.action == "stop" for a in estop_actions)

    # Validating the estop actions should pass
    result = guard.validate_plan_actions(estop_actions, sample_fleet, sample_obstacles)
    assert result.passed is True

def test_safety_guard_validate_single_action(sample_fleet, sample_obstacles):
    guard = SafetyGuard()
    robot_a = sample_fleet["robot_a"]
    
    # Valid single action
    ok, err = guard.validate_single_action(robot_a, "navigate", Position(x=5.0, y=5.0, z=0.0), sample_obstacles)
    assert ok is True
    assert err is None

    # Invalid out of bounds
    ok, err = guard.validate_single_action(robot_a, "navigate", Position(x=100.0, y=50.0, z=0.0), sample_obstacles)
    assert ok is False
    assert "out of warehouse bounds" in err

    # Invalid obstacle collision
    ok, err = guard.validate_single_action(robot_a, "navigate", Position(x=10.1, y=10.1, z=0.0), sample_obstacles)
    assert ok is False
    assert "collides with obstacle" in err

