"""
SWARMOS Hardware Abstraction Layer (HAL)
Abstract Base Class defining the unified interface for both simulated AMRs and physical hardware.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.models.schemas import Position, RobotState, Task

class RobotAdapter(ABC):
    def __init__(self, robot_id: str, name: str):
        self.robot_id = robot_id
        self.name = name
        self.is_connected = False

    @abstractmethod
    async def connect(self) -> bool:
        """Establish communication link with robot (simulation bus or physical telemetry channel)"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Gracefully terminate connection"""
        pass

    @abstractmethod
    def get_state(self) -> RobotState:
        """Query current state machine status"""
        pass

    @abstractmethod
    def get_battery(self) -> float:
        """Query battery percentage [0.0 - 100.0]"""
        pass

    @abstractmethod
    def get_position(self) -> Position:
        """Query spatial position in warehouse coordinates"""
        pass

    @abstractmethod
    def get_sensor_data(self) -> Dict[str, Any]:
        """Fetch latest sensor readings (lidar, camera, wheel odometry)"""
        pass

    @abstractmethod
    async def navigate(self, target_pos: Position) -> bool:
        """Issue waypoint navigation command"""
        pass

    @abstractmethod
    async def stop(self) -> bool:
        """Trigger emergency stop / deceleration"""
        pass

    @abstractmethod
    async def execute_task(self, task: Task) -> bool:
        """Execute high-level task primitive"""
        pass

    @abstractmethod
    def report_failure(self, failure_type: str, description: str):
        """Signal an internal subsystem anomaly or stall"""
        pass
