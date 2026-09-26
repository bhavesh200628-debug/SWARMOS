"""
SWARMOS Simulation Robot Adapter
Implements the RobotAdapter interface for simulated AMRs operating within the warehouse grid.
"""
import math
import logging
from typing import Dict, Any, Optional
from backend.robots.adapter_base import RobotAdapter
from backend.models.schemas import Position, RobotState, Task

logger = logging.getLogger("swarmos.sim_adapter")

class SimulationRobotAdapter(RobotAdapter):
    def __init__(self, robot_id: str, name: str, initial_pos: Position, battery: float = 100.0):
        super().__init__(robot_id, name)
        self.position = initial_pos
        self.target_position: Optional[Position] = None
        self.battery = battery
        self.state = RobotState.IDLE
        self.speed = 1.8  # meters per second
        self.heading = 0.0
        self.carried_package_id: Optional[str] = None
        self.current_task: Optional[Task] = None
        self.sensor_data: Dict[str, Any] = {
            "lidar_min_dist": 10.0,
            "camera_status": "nominal",
            "odometry_error": 0.01
        }

    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to simulated robot bus: {self.robot_id}")
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    def get_state(self) -> RobotState:
        return self.state

    def get_battery(self) -> float:
        return self.battery

    def get_position(self) -> Position:
        return self.position

    def get_sensor_data(self) -> Dict[str, Any]:
        return self.sensor_data

    async def navigate(self, target_pos: Position) -> bool:
        if self.state in [RobotState.OFFLINE, RobotState.DEGRADED]:
            logger.warning(f"Cannot navigate {self.robot_id}: Robot in {self.state} state.")
            return False
        
        self.target_position = target_pos
        self.state = RobotState.NAVIGATING
        return True

    async def stop(self) -> bool:
        self.target_position = None
        if self.state != RobotState.OFFLINE:
            self.state = RobotState.IDLE
        return True

    async def execute_task(self, task: Task) -> bool:
        self.current_task = task
        if task.action == "navigate":
            if task.target_location:
                return await self.navigate(task.target_location)
        elif task.action == "inspect":
            self.state = RobotState.INSPECTING
            return True
        elif task.action == "transport":
            self.state = RobotState.TRANSPORTING
            if task.target_location:
                return await self.navigate(task.target_location)
            return True
        elif task.action == "stop":
            return await self.stop()
        return True

    def report_failure(self, failure_type: str, description: str):
        self.state = RobotState.OFFLINE
        self.target_position = None
        self.sensor_data["camera_status"] = "offline"
        self.sensor_data["lidar_min_dist"] = 0.0
        logger.warning(f"Simulated robot {self.robot_id} reported failure: {failure_type} ({description})")

    def update_physics_tick(self, dt: float):
        """Simulate kinematic motion, battery consumption, and heading orientation."""
        if self.state == RobotState.OFFLINE:
            return

        if self.target_position:
            dx = self.target_position.x - self.position.x
            dy = self.target_position.y - self.position.y
            dist = math.hypot(dx, dy)

            # Update heading
            if dist > 0.01:
                self.heading = math.degrees(math.atan2(dy, dx))

            step = self.speed * dt
            if dist <= step:
                self.position.x = self.target_position.x
                self.position.y = self.target_position.y
                self.target_position = None
                if self.state == RobotState.NAVIGATING:
                    self.state = RobotState.IDLE
            else:
                self.position.x += (dx / dist) * step
                self.position.y += (dy / dist) * step
                
            # Battery drain proportional to movement
            self.battery = max(0.0, self.battery - (0.05 * step))
        else:
            # Idle idle drain
            self.battery = max(0.0, self.battery - (0.001 * dt))
