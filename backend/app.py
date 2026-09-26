"""
SWARMOS Master FastAPI Application Entrypoint
Integrates REST APIs, real-time WebSockets telemetry, deterministic simulation, and Nebius AI reasoning.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.simulation.engine import simulation_engine
from backend.telemetry.broadcaster import telemetry_broadcaster
from backend.api.routes_missions import router as missions_router
from backend.api.routes_fleet import router as fleet_router
from backend.api.routes_demo import router as demo_router
from backend.api.routes_evaluation import router as eval_router
from backend.api.routes_health import router as health_router

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("swarmos.app")

async def telemetry_loop():
    """Background task continuously broadcasting simulation state to all connected frontends."""
    dt = 1.0 / settings.TELEMETRY_BROADCAST_RATE_HZ
    while True:
        try:
            state = simulation_engine.get_state()
            await telemetry_broadcaster.broadcast_state(state.model_dump())
        except Exception as e:
            logger.error(f"Error in telemetry broadcast loop: {e}")
        await asyncio.sleep(dt)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("==================================================")
    logger.info(f"   Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"   '{settings.TAGLINE}'")
    logger.info("==================================================")
    await simulation_engine.start()
    telemetry_task = asyncio.create_task(telemetry_loop())
    yield
    # Shutdown
    logger.info("Shutting down SWARMOS...")
    telemetry_task.cancel()
    await simulation_engine.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI orchestration layer for heterogeneous physical robot fleets featuring self-healing recovery via NVIDIA Nemotron & Nebius Token Factory.",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(missions_router)
app.include_router(fleet_router)
app.include_router(demo_router)
app.include_router(eval_router)

# Serve compiled frontend assets if available
import os
from fastapi.staticfiles import StaticFiles
frontend_dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="static_assets")
    from fastapi.responses import FileResponse
    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))

@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """Real-time bidirectional WebSocket stream for digital twin telemetry and AI decisions."""
    await telemetry_broadcaster.connect(websocket)
    try:
        while True:
            # Client can send commands or ping
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        telemetry_broadcaster.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        telemetry_broadcaster.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
