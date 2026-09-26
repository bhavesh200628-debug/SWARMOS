"""
SWARMOS Missions API Routes
Handles mission submission, decomposition, task progression tracking, and status retrieval.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.simulation.engine import simulation_engine
from backend.planning.mission_planner import mission_planner
from backend.models.schemas import Mission

router = APIRouter(prefix="/api/missions", tags=["missions"])

class MissionSubmitRequest(BaseModel):
    prompt: str = "Inspect Warehouse Zone B, identify damaged packages, move them to quarantine, and generate an incident report."

@router.post("", response_model=Mission)
async def submit_mission(req: MissionSubmitRequest):
    """Submit a natural language mission for NVIDIA Nemotron decomposition and dispatch."""
    mission = await mission_planner.create_and_plan_mission(
        prompt=req.prompt,
        robots=simulation_engine.robots,
        obstacles=simulation_engine.obstacles
    )
    simulation_engine.active_mission_id = mission.id
    simulation_engine.add_event(
        "mission_submitted",
        f"New mission submitted: '{req.prompt}'",
        {"mission_id": mission.id, "task_count": len(mission.tasks)}
    )
    return mission

@router.get("/{mission_id}", response_model=Mission)
async def get_mission(mission_id: str):
    """Retrieve detailed state and task breakdown for a mission."""
    if mission_id not in mission_planner.active_missions:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission_planner.active_missions[mission_id]

@router.get("", response_model=list)
async def list_missions():
    """List all registered missions."""
    return list(mission_planner.active_missions.values())
