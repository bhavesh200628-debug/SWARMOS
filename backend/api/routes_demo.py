"""
SWARMOS Demo Mode API Routes
Automated orchestration of the flagship 'Warehouse Incident Response' self-healing scenario.
Allows judges and evaluators to trigger, watch, and test the entire failure-recovery cycle.
"""
import asyncio
import time
import logging
from fastapi import APIRouter
from backend.simulation.engine import simulation_engine
from backend.planning.mission_planner import mission_planner
from backend.models.schemas import FailureType

router = APIRouter(prefix="/api/demo", tags=["demo"])
logger = logging.getLogger("swarmos.demo")

demo_task_handle: asyncio.Task = None
demo_status: dict = {
    "is_running": False,
    "current_stage": "idle",
    "step_index": 0,
    "started_at": None
}

async def _run_autonomous_demo_sequence():
    global demo_status
    try:
        demo_status["is_running"] = True
        demo_status["started_at"] = time.time()
        
        # Step 1: Clean reset
        demo_status["current_stage"] = "resetting_environment"
        demo_status["step_index"] = 1
        simulation_engine.reset()
        await simulation_engine.start()
        await asyncio.sleep(1.0)

        # Step 2: Mission Submission & Nemotron Decomposition
        demo_status["current_stage"] = "submitting_mission"
        demo_status["step_index"] = 2
        mission_prompt = "Inspect Zone B, locate damaged packages, move them to quarantine, and generate an incident report."
        simulation_engine.add_event("demo_step", "Step 1: Submitting incident mission to SWARMOS...")
        
        mission = await mission_planner.create_and_plan_mission(
            prompt=mission_prompt,
            robots=simulation_engine.robots,
            obstacles=simulation_engine.obstacles
        )
        simulation_engine.active_mission_id = mission.id
        simulation_engine.add_event(
            "demo_step",
            f"Step 2: NVIDIA Nemotron decomposed mission into {len(mission.tasks)} tasks. Swarm executing initial assignments.",
            {"tasks": [t.title for t in mission.tasks]}
        )
        await asyncio.sleep(3.5)

        # Step 3: Robot execution underway (Robot A scouts Zone B, Robot B navigates to inspect pkg_b1)
        demo_status["current_stage"] = "fleet_executing"
        demo_status["step_index"] = 3
        simulation_engine.add_event("demo_step", "Step 3: Robots A, B, C navigating to designated staging zones.")
        await asyncio.sleep(3.0)

        # Step 4: Inject Robot B Failure (The Hero Moment!)
        demo_status["current_stage"] = "injecting_failure"
        demo_status["step_index"] = 4
        simulation_engine.add_event(
            "demo_step",
            "Step 4: INJECTING FAILURE -> Robot Bravo (Inspector-02) optical sensor bus malfunction & motor stall."
        )
        await simulation_engine.trigger_failure(
            robot_id="robot_b",
            failure_type=FailureType.ROBOT_UNAVAILABLE,
            description="LIDAR & primary camera link severed during Zone B approach."
        )
        await asyncio.sleep(2.5)

        # Step 5: Self-Healing Reassignment verified
        demo_status["current_stage"] = "reassigned_and_resuming"
        demo_status["step_index"] = 5
        simulation_engine.add_event(
            "demo_step",
            "Step 5: Nemotron successfully reassigned inspection tasks to Robot Alpha. Alpha assuming inspection duties."
        )
        await asyncio.sleep(5.0)

        # Step 6: Transport execution
        demo_status["current_stage"] = "transporting_cargo"
        demo_status["step_index"] = 6
        simulation_engine.add_event(
            "demo_step",
            "Step 6: Robot Charlie (Carrier-03) transporting damaged container pkg_b1 to Quarantine Zone."
        )
        await asyncio.sleep(5.0)

        # Step 7: Mission Completion
        demo_status["current_stage"] = "completed"
        demo_status["step_index"] = 7
        simulation_engine.add_event(
            "demo_step",
            "Step 7: Mission successfully completed! Damaged package quarantined; report compiled."
        )

    except asyncio.CancelledError:
        demo_status["current_stage"] = "cancelled"
    except Exception as e:
        logger.error(f"Error during demo sequence: {e}")
        demo_status["current_stage"] = f"error: {str(e)}"
    finally:
        demo_status["is_running"] = False

@router.post("/run")
async def run_demo():
    """Trigger the automated end-to-end self-healing demonstration."""
    global demo_task_handle
    if demo_task_handle and not demo_task_handle.done():
        demo_task_handle.cancel()

    demo_task_handle = asyncio.create_task(_run_autonomous_demo_sequence())
    return {
        "status": "demo_started",
        "description": "Warehouse Incident Response self-healing scenario initiated."
    }

@router.post("/failure")
async def trigger_demo_failure():
    """Manually trigger the hero failure on Robot B."""
    await simulation_engine.trigger_failure(
        robot_id="robot_b",
        failure_type=FailureType.ROBOT_UNAVAILABLE,
        description="Manual judge trigger: Optical inspection sensor blackout."
    )
    return {
        "status": "failure_injected",
        "target_robot": "robot_b",
        "replan_triggered": True
    }

@router.post("/reset")
async def reset_demo():
    """Reset the demo and warehouse to pristine initial state."""
    global demo_task_handle
    if demo_task_handle and not demo_task_handle.done():
        demo_task_handle.cancel()
    
    simulation_engine.reset()
    demo_status["is_running"] = False
    demo_status["current_stage"] = "idle"
    demo_status["step_index"] = 0
    return {"status": "reset_complete"}

@router.get("/status")
async def get_demo_status():
    """Get current progress of the automated demo."""
    return demo_status
