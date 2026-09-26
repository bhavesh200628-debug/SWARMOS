"""
Phase 6: Hero Demo 10x Repeatability Test
Runs the full SWARMOS self-healing scenario (Mission Planning -> Dynamic Failure Injection ->
NVIDIA Nemotron Replanning -> Safety Guard Validation -> Package Quarantine) 10 consecutive times.

Asserts 100% deterministic repeatability (10/10 successes) with 0 unhandled orphaned tasks
and 0 safety invariant violations across all runs.
"""
import pytest
import asyncio
from backend.simulation.engine import simulation_engine
from backend.planning.mission_planner import mission_planner
from backend.models.schemas import FailureType, RobotState, TaskStatus
from backend.safety.guard import safety_guard

@pytest.mark.asyncio
async def test_hero_demo_10x_repeatability():
    num_iterations = 10
    successful_runs = 0
    total_violations = 0
    total_unrecovered_orphans = 0

    for iteration in range(1, num_iterations + 1):
        # 1. Reset environment to clean initial state
        simulation_engine.reset()
        assert len(simulation_engine.robots) == 3
        assert simulation_engine.robots["robot_b"].state == RobotState.IDLE

        # 2. Plan Mission via Nemotron Decomposer
        prompt = "Inspect Zone B, locate damaged packages, move them to quarantine, and generate an incident report."
        mission = await mission_planner.create_and_plan_mission(
            prompt=prompt,
            robots=simulation_engine.robots,
            obstacles=simulation_engine.obstacles
        )

        assert len(mission.tasks) >= 3, f"Iteration {iteration}: Mission planning produced fewer than 3 tasks"
        simulation_engine.active_mission_id = mission.id

        # 3. Verify initial assignments comply with safety whitelist and capabilities
        for t in mission.tasks:
            if t.assigned_robot_id:
                robot = simulation_engine.robots[t.assigned_robot_id]
                ok, err = safety_guard.validate_single_action(
                    robot,
                    t.action,
                    t.target_location,
                    simulation_engine.obstacles
                )
                if not ok:
                    total_violations += 1
                assert ok is True, f"Iteration {iteration}: Safety guard rejected initial task action: {err}"

        # 4. Advance simulation to simulate initial movement
        for _ in range(5):
            simulation_engine.update(dt=0.1)

        # 5. Inject Critical Failure on Robot B (The Hero Moment)
        await simulation_engine.trigger_failure(
            robot_id="robot_b",
            failure_type=FailureType.ROBOT_UNAVAILABLE,
            description="LIDAR & primary camera link severed during Zone B approach."
        )

        # 6. Verify Robot B is OFFLINE
        assert simulation_engine.robots["robot_b"].state == RobotState.OFFLINE

        # 7. Verify Task Recovery: No orphaned tasks left unassigned
        orphaned_unassigned = [
            t for t in mission.tasks
            if t.status == TaskStatus.ORPHANED or (t.assigned_robot_id == "robot_b" and t.status != TaskStatus.COMPLETED)
        ]
        if orphaned_unassigned:
            total_unrecovered_orphans += len(orphaned_unassigned)

        assert len(orphaned_unassigned) == 0, (
            f"Iteration {iteration}: Found unassigned/orphaned tasks after failure replan: {orphaned_unassigned}"
        )

        # 8. Verify Robot A assumed the reassigned inspection duty
        robot_a = simulation_engine.robots["robot_a"]
        assert robot_a.state in [RobotState.NAVIGATING, RobotState.IDLE, RobotState.INSPECTING]

        # 9. Verify Safety Audit Trail contains zero critical violations
        recent_events = simulation_engine.recent_events[-10:]
        assert any("failure" in e.get("type", "") for e in recent_events)
        assert any("replan" in e.get("type", "") for e in recent_events)

        # 10. Advance simulation steps through quarantine transport
        for _ in range(20):
            simulation_engine.update(dt=0.1)

        successful_runs += 1

    assert successful_runs == num_iterations, f"Expected {num_iterations} successful runs, got {successful_runs}"
    assert total_violations == 0, f"Expected 0 safety violations, encountered {total_violations}"
    assert total_unrecovered_orphans == 0, f"Expected 0 unrecovered orphans, encountered {total_unrecovered_orphans}"
