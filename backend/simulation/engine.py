"""
SWARMOS Simulation Engine
Deterministic, real-time physics and state machine runner for warehouse swarm operations.
"""
import asyncio
import math
import time
import logging
from typing import Dict, Any, List, Optional
from backend.models.schemas import (
    SimulationState, Robot, Package, Obstacle, WarehouseZone,
    RobotState, TaskStatus, FailureType, FailureEvent, Position, PackageState, Mission
)
from backend.simulation.warehouse import (
    create_default_zones, create_default_packages,
    create_default_obstacles, create_default_fleet
)
from backend.planning.mission_planner import mission_planner
from backend.planning.failure_manager import failure_manager

logger = logging.getLogger("swarmos.engine")

class SimulationEngine:
    def __init__(self):
        self.tick_count = 0
        self.is_running = False
        self.speed_multiplier = 1.0
        self.zones: List[WarehouseZone] = create_default_zones()
        self.packages: List[Package] = create_default_packages()
        self.obstacles: List[Obstacle] = create_default_obstacles()
        self.robots: Dict[str, Robot] = create_default_fleet()
        self.active_mission_id: Optional[str] = None
        self.recent_events: List[Dict[str, Any]] = []
        self._loop_task: Optional[asyncio.Task] = None

    def reset(self):
        """Reset simulation to pristine baseline state."""
        self.tick_count = 0
        self.zones = create_default_zones()
        self.packages = create_default_packages()
        self.obstacles = create_default_obstacles()
        self.robots = create_default_fleet()
        self.active_mission_id = None
        self.recent_events = []
        failure_manager.active_failures.clear()
        failure_manager.decision_history.clear()
        mission_planner.active_missions.clear()
        self.add_event("system_reset", "Simulation environment reset to initial state.")
        logger.info("Simulation environment reset.")

    def add_event(self, event_type: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        evt = {
            "timestamp": time.time(),
            "type": event_type,
            "message": message,
            "metadata": metadata or {}
        }
        self.recent_events.append(evt)
        if len(self.recent_events) > 50:
            self.recent_events.pop(0)

    async def start(self):
        if not self.is_running:
            self.is_running = True
            self._loop_task = asyncio.create_task(self._simulation_loop())
            logger.info("Simulation loop started.")

    async def stop(self):
        self.is_running = False
        if self._loop_task:
            self._loop_task.cancel()
            self._loop_task = None
        logger.info("Simulation loop stopped.")

    async def trigger_failure(self, robot_id: str, failure_type: FailureType, description: str):
        """Injects a failure condition and triggers autonomous self-healing."""
        if robot_id not in self.robots:
            return
        
        self.add_event(
            "robot_failure",
            f"ALERT: Robot '{robot_id}' failure: {description}",
            {"robot_id": robot_id, "failure_type": failure_type.value}
        )

        active_tasks = []
        if self.active_mission_id and self.active_mission_id in mission_planner.active_missions:
            active_tasks = mission_planner.active_missions[self.active_mission_id].tasks

        decision = await failure_manager.handle_robot_failure(
            robot_id=robot_id,
            failure_type=failure_type,
            description=description,
            robots=self.robots,
            active_tasks=active_tasks,
            obstacles=self.obstacles
        )

        self.add_event(
            "nemotron_replan",
            f"Nemotron replanned swarm. {decision.get('reasoning')}",
            decision
        )

    def get_state(self) -> SimulationState:
        active_mission = None
        if self.active_mission_id and self.active_mission_id in mission_planner.active_missions:
            active_mission = mission_planner.active_missions[self.active_mission_id]

        return SimulationState(
            timestamp=time.time(),
            tick=self.tick_count,
            robots=list(self.robots.values()),
            packages=self.packages,
            obstacles=self.obstacles,
            zones=self.zones,
            active_mission=active_mission,
            active_failures=list(failure_manager.active_failures.values()),
            recent_decision_events=self.recent_events[-15:],
            simulation_running=self.is_running,
            speed_multiplier=self.speed_multiplier
        )

    async def _simulation_loop(self):
        dt = 0.1  # 10 Hz
        while self.is_running:
            start_tick = time.time()
            self.tick_count += 1

            # 1. Update Mission Progression
            if self.active_mission_id:
                m = mission_planner.update_task_progress(self.active_mission_id, dt * self.speed_multiplier)
                if m:
                    # Sync active task goals to robots
                    for task in m.tasks:
                        if task.status == TaskStatus.IN_PROGRESS and task.assigned_robot_id in self.robots:
                            bot = self.robots[task.assigned_robot_id]
                            if bot.state not in [RobotState.OFFLINE, RobotState.DEGRADED]:
                                bot.current_task_id = task.id
                                if task.action in ["navigate", "transport"] and task.target_location:
                                    bot.target_position = task.target_location
                                    bot.state = RobotState.TRANSPORTING if task.action == "transport" else RobotState.NAVIGATING
                                elif task.action == "inspect":
                                    bot.state = RobotState.INSPECTING

            # 2. Update Kinematics and Movement
            speed = 2.0 * self.speed_multiplier
            for bot in self.robots.values():
                if bot.state == RobotState.OFFLINE:
                    bot.velocity = 0.0
                    continue

                if bot.target_position:
                    dx = bot.target_position.x - bot.position.x
                    dy = bot.target_position.y - bot.position.y
                    dist = math.hypot(dx, dy)

                    if dist > 0.05:
                        bot.heading = math.degrees(math.atan2(dy, dx))
                        step = min(dist, speed * dt)
                        bot.position.x += (dx / dist) * step
                        bot.position.y += (dy / dist) * step
                        bot.velocity = speed
                        bot.battery = max(0.0, bot.battery - (0.04 * step))
                    else:
                        bot.position.x = bot.target_position.x
                        bot.position.y = bot.target_position.y
                        bot.target_position = None
                        bot.velocity = 0.0
                        if bot.state == RobotState.NAVIGATING:
                            bot.state = RobotState.IDLE
                else:
                    bot.velocity = 0.0
                    bot.battery = max(0.0, bot.battery - (0.002 * dt))

            # 3. Synchronize Carried Packages
            # If robot_c is transporting pkg_b1
            carrier = self.robots.get("robot_c")
            pkg_b1 = next((p for p in self.packages if p.id == "pkg_b1"), None)
            if carrier and pkg_b1:
                if carrier.state == RobotState.TRANSPORTING:
                    carrier.carried_package_id = "pkg_b1"
                    pkg_b1.position.x = carrier.position.x + 0.3
                    pkg_b1.position.y = carrier.position.y + 0.3
                    # If arrived at Quarantine zone (x >= 24, y >= 14)
                    if carrier.position.x >= 24.0 and carrier.position.y >= 14.0:
                        pkg_b1.state = PackageState.QUARANTINED
                        carrier.carried_package_id = None
                        if carrier.state != RobotState.OFFLINE:
                            carrier.state = RobotState.IDLE

            elapsed = time.time() - start_tick
            sleep_time = max(0.01, dt - elapsed)
            await asyncio.sleep(sleep_time)

# Global simulation engine singleton
simulation_engine = SimulationEngine()
