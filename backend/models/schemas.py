"""
SWARMOS Typed Data Schemas
Pydantic v2 schemas defining robots, missions, tasks, failures, safety constraints, and telemetry.
"""
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
import time

class RobotCapability(str, Enum):
    SCOUT = "scout"
    INSPECTOR = "inspector"
    CARRIER = "carrier"
    MANIPULATOR = "manipulator"
    HEAVY_LIFT = "heavy_lift"

class RobotState(str, Enum):
    IDLE = "idle"
    NAVIGATING = "navigating"
    INSPECTING = "inspecting"
    TRANSPORTING = "transporting"
    DEGRADED = "degraded"
    BLOCKED = "blocked"
    LOW_BATTERY = "low_battery"
    OFFLINE = "offline"
    CHARGING = "charging"

class TaskType(str, Enum):
    NAVIGATE = "navigate"
    INSPECT = "inspect"
    IDENTIFY = "identify"
    TRANSPORT = "transport"
    VERIFY = "verify"
    REPORT = "report_status"
    RETURN_TO_BASE = "return_to_base"

class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Position(BaseModel):
    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    z: float = Field(0.0, description="Z coordinate in meters")

class Robot(BaseModel):
    id: str
    name: str
    robot_type: str = "differential_drive_amr"
    capabilities: List[RobotCapability]
    state: RobotState = RobotState.IDLE
    battery: float = Field(100.0, ge=0.0, le=100.0)
    position: Position
    target_position: Optional[Position] = None
    velocity: float = 0.0  # m/s
    heading: float = 0.0   # degrees (0 = +X axis)
    current_task_id: Optional[str] = None
    carried_package_id: Optional[str] = None
    is_physical: bool = False
    hardware_endpoint: Optional[str] = None

class Task(BaseModel):
    id: str
    mission_id: str
    title: str
    task_type: TaskType
    action: str
    target_location: Optional[Position] = None
    target_zone: Optional[str] = None
    target_package_id: Optional[str] = None
    destination_zone: Optional[str] = None
    assigned_robot_id: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks that must complete first")
    status: TaskStatus = TaskStatus.PENDING
    progress: float = Field(0.0, ge=0.0, le=1.0)
    estimated_duration_sec: float = 10.0
    created_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    error_message: Optional[str] = None

class MissionStatus(str, Enum):
    PENDING_PLANNING = "pending_planning"
    PLANNED = "planned"
    EXECUTING = "executing"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    FAILED = "failed"
    HALTED = "halted"

class FailureType(str, Enum):
    ROBOT_UNAVAILABLE = "robot_unavailable"
    OBSTACLE_DETECTED = "obstacle_detected"
    LOW_BATTERY = "low_battery"
    SENSOR_FAILURE = "sensor_failure"
    COMMUNICATION_LOSS = "communication_loss"

class FailureEvent(BaseModel):
    id: str
    timestamp: float = Field(default_factory=time.time)
    robot_id: str
    failure_type: FailureType
    description: str
    severity: str = "critical"  # "warning", "critical"
    resolved: bool = False
    resolved_at: Optional[float] = None
    mitigation_action: Optional[str] = None

class TaskReassignment(BaseModel):
    task_id: str
    from_robot: Optional[str]
    to_robot: str
    reason: str

class AIPlanAction(BaseModel):
    robot_id: str
    action: str
    target_location: Optional[Position] = None
    target_zone: Optional[str] = None
    package_id: Optional[str] = None
    destination: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)

class AIPlanResponse(BaseModel):
    reason: str = Field(..., description="High-level reasoning explaining the plan or recovery strategy")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    tasks: List[Dict[str, Any]] = Field(default_factory=list, description="List of decomposed tasks")
    reassignments: List[TaskReassignment] = Field(default_factory=list, description="Dynamic task reassignments if replanning")
    next_actions: List[AIPlanAction] = Field(default_factory=list, description="Immediate executable actions")
    decision_metadata: Dict[str, Any] = Field(default_factory=dict)

class Mission(BaseModel):
    id: str
    natural_language_prompt: str
    status: MissionStatus = MissionStatus.PENDING_PLANNING
    tasks: List[Task] = Field(default_factory=list)
    revisions: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    report_summary: Optional[str] = None

class WarehouseZone(BaseModel):
    id: str
    name: str
    zone_type: str  # storage, inspection, quarantine, charging, transit
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    color: str

class PackageState(str, Enum):
    NORMAL = "normal"
    DAMAGED = "damaged"
    QUARANTINED = "quarantined"

class Package(BaseModel):
    id: str
    name: str
    position: Position
    state: PackageState = PackageState.NORMAL
    weight_kg: float = 5.0
    zone_id: str

class Obstacle(BaseModel):
    id: str
    position: Position
    radius: float = 1.0
    is_dynamic: bool = False
    description: str = "Static warehouse pillar"

class SimulationState(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    tick: int = 0
    robots: List[Robot] = Field(default_factory=list)
    packages: List[Package] = Field(default_factory=list)
    obstacles: List[Obstacle] = Field(default_factory=list)
    zones: List[WarehouseZone] = Field(default_factory=list)
    active_mission: Optional[Mission] = None
    active_failures: List[FailureEvent] = Field(default_factory=list)
    recent_decision_events: List[Dict[str, Any]] = Field(default_factory=list)
    simulation_running: bool = True
    speed_multiplier: float = 1.0

class SafetyCheckResult(BaseModel):
    passed: bool
    violations: List[str] = Field(default_factory=list)
    allowed_actions: List[AIPlanAction] = Field(default_factory=list)
    rejected_actions: List[AIPlanAction] = Field(default_factory=list)
    safety_audit_trail: List[str] = Field(default_factory=list)
