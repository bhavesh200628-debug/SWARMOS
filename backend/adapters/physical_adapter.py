"""
SWARMOS Hardware Abstraction Layer (HAL) - Physical Robot Adapter
Provides bidirectional communication between SWARMOS orchestration layer and physical robots
running ROS2 / micro-ROS or the SWARMOS physical hardware bridge (scripts/physical_robot_runner.py).

Enables drop-in deployment from the digital twin simulation directly to physical AMRs
(e.g., TurtleBot 4, NVIDIA Jetson Orin Nano AMRs, or custom wheeled rovers).
"""
import logging
from typing import Optional, Dict, Any
import httpx
from backend.models.schemas import Position, RobotState

logger = logging.getLogger("swarmos.hal")

class PhysicalRobotAdapter:
    def __init__(self, robot_id: str, endpoint_url: str = "http://127.0.0.1:9000"):
        self.robot_id = robot_id
        self.endpoint_url = endpoint_url
        self.is_connected = False
        self.last_telemetry: Optional[Dict[str, Any]] = None

    async def check_connection(self) -> bool:
        """Verifies physical robot connectivity via HTTP health check."""
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.endpoint_url}/health")
                if res.status_code == 200:
                    self.is_connected = True
                    return True
        except Exception:
            self.is_connected = False
        return False

    async def fetch_telemetry(self) -> Optional[Dict[str, Any]]:
        """Polls physical robot telemetry (pose, battery, sensors)."""
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.endpoint_url}/telemetry")
                if res.status_code == 200:
                    self.last_telemetry = res.json()
                    self.is_connected = True
                    return self.last_telemetry
        except Exception as e:
            logger.warning(f"Failed to fetch physical telemetry for {self.robot_id}: {e}")
            self.is_connected = False
        return None

    async def dispatch_waypoint(self, position: Position) -> bool:
        """Sends motion target to physical robot motor controller."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.post(
                    f"{self.endpoint_url}/navigate",
                    json={"x": position.x, "y": position.y, "z": position.z}
                )
                return res.status_code == 200
        except Exception as e:
            logger.error(f"Failed to dispatch waypoint to physical robot {self.robot_id}: {e}")
            return False

    async def emergency_stop(self) -> bool:
        """Sends immediate physical actuator halt signal."""
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                res = await client.post(f"{self.endpoint_url}/stop")
                return res.status_code == 200
        except Exception as e:
            logger.error(f"Physical emergency stop failed for {self.robot_id}: {e}")
            return False
