"""
SWARMOS Fleet API Routes
Handles fleet querying, individual robot telemetry, and failure injection.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from backend.simulation.engine import simulation_engine
from backend.models.schemas import Robot, FailureType

router = APIRouter(prefix="/api", tags=["fleet"])

class RobotFailureRequest(BaseModel):
    failure_type: FailureType = FailureType.ROBOT_UNAVAILABLE
    description: str = "Hardware anomaly detected on drive wheel actuator."

@router.get("/fleet", response_model=List[Robot])
async def get_fleet():
    """Retrieve all robots and their current state, battery, and telemetry."""
    return list(simulation_engine.robots.values())

@router.get("/robots/{robot_id}", response_model=Robot)
async def get_robot(robot_id: str):
    """Retrieve detailed state for a specific robot."""
    if robot_id not in simulation_engine.robots:
        raise HTTPException(status_code=404, detail="Robot not found")
    return simulation_engine.robots[robot_id]

@router.post("/robots/{robot_id}/failure")
async def trigger_robot_failure(robot_id: str, req: RobotFailureRequest):
    """Inject a failure event onto a specific robot to trigger self-healing swarm replanning."""
    if robot_id not in simulation_engine.robots:
        raise HTTPException(status_code=404, detail="Robot not found")
    
    await simulation_engine.trigger_failure(
        robot_id=robot_id,
        failure_type=req.failure_type,
        description=req.description
    )
    return {
        "status": "failure_injected",
        "robot_id": robot_id,
        "failure_type": req.failure_type.value,
        "self_healing_initiated": True
    }
