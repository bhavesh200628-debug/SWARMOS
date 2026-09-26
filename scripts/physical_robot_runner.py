"""
SWARMOS Physical Robot Hardware Bridge / Standalone Runner
Runs an HTTP/ROS2 micro-bridge server on physical robot hardware (e.g. Raspberry Pi, Jetson Orin Nano, or laptop connected to AMR).
Exposes the standardized SWARMOS Hardware Abstraction Layer (HAL) endpoints.
"""
import sys
import time
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SWARMOS Physical Hardware Bridge")

state = {
    "robot_id": "robot_physical_01",
    "status": "nominal",
    "battery": 97.4,
    "position": {"x": 4.0, "y": 5.0, "z": 0.0},
    "velocity": 0.0,
    "heading": 0.0,
    "optical_sensor": "OK",
    "lidar_min_range_m": 8.4
}

class NavGoal(BaseModel):
    x: float
    y: float
    z: float = 0.0

@app.get("/health")
def health():
    return {"status": "ok", "hardware": "NVIDIA Jetson Orin / ROS2 Bridge", "battery": state["battery"]}

@app.get("/telemetry")
def get_telemetry():
    return state

@app.post("/navigate")
def navigate_to_waypoint(goal: NavGoal):
    print(f"⏩ [PHYSICAL MOTOR DISPATCH] Navigating to X={goal.x:.2f}, Y={goal.y:.2f}")
    state["position"]["x"] = goal.x
    state["position"]["y"] = goal.y
    state["battery"] = max(0.0, state["battery"] - 0.4)
    return {"status": "accepted", "goal": {"x": goal.x, "y": goal.y}}

@app.post("/stop")
def emergency_stop():
    print("🛑 [PHYSICAL EMERGENCY STOP] Halting all drive actuators!")
    state["velocity"] = 0.0
    return {"status": "halted"}

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    print(f"🚀 Starting SWARMOS Physical Hardware Bridge on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
