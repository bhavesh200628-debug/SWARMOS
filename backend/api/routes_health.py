"""
SWARMOS Observability & Health Check Routes
Endpoints reporting system status, Nebius Token Factory connection, model health, and simulation metrics.
"""
from fastapi import APIRouter
from backend.config import settings
from backend.simulation.engine import simulation_engine
from backend.nebius.client import nebius_client
import time

router = APIRouter(tags=["health"])

server_start_time = time.time()

@router.get("/health")
@router.get("/api/health")
async def health_check():
    """General system health and service metadata."""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "uptime_sec": round(time.time() - server_start_time, 1)
    }

@router.get("/health/ai")
async def health_ai():
    """Nebius Token Factory & NVIDIA Nemotron connectivity status."""
    is_live = not nebius_client.mock_mode and bool(nebius_client.api_key)
    return {
        "status": "operational",
        "provider": "Nebius Token Factory",
        "model": settings.NEBIUS_MODEL,
        "mode": "LIVE NEBIUS — NVIDIA NEMOTRON" if is_live else "LOCAL SIMULATION",
        "configured": bool(settings.NEBIUS_API_KEY),
        "last_success": nebius_client.last_success,
        "last_latency": nebius_client.last_latency,
        "nebius_endpoint": settings.NEBIUS_BASE_URL,
        "target_model": settings.NEBIUS_MODEL,
        "fallback_model": settings.NEBIUS_FALLBACK_MODEL,
        "execution_mode": "LIVE_NEBIUS_TOKEN_FACTORY" if is_live else "DETERMINISTIC_SIMULATED_MODE",
        "api_key_configured": bool(settings.NEBIUS_API_KEY),
        "is_mock": not is_live
    }

@router.get("/health/simulation")
async def health_simulation():
    """Simulation engine tick rates and robot status."""
    return {
        "status": "running" if simulation_engine.is_running else "paused",
        "tick_count": simulation_engine.tick_count,
        "active_robots": len(simulation_engine.robots),
        "active_packages": len(simulation_engine.packages),
        "speed_multiplier": simulation_engine.speed_multiplier,
        "active_mission": simulation_engine.active_mission_id
    }
