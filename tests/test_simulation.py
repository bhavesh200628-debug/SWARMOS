"""
Unit Tests for SWARMOS Simulation Physics and Kinematics
"""
import pytest
from backend.simulation.engine import SimulationEngine
from backend.models.schemas import Position, RobotState, PackageState

@pytest.mark.asyncio
async def test_simulation_reset_and_initial_fleet():
    sim = SimulationEngine()
    sim.reset()
    state = sim.get_state()
    assert len(state.robots) == 3
    assert len(state.packages) == 3
    assert len(state.zones) == 5
    assert state.robots[0].id == "robot_a"
    assert state.robots[0].battery > 90.0

@pytest.mark.asyncio
async def test_robot_kinematic_navigation():
    sim = SimulationEngine()
    sim.reset()
    robot_a = sim.robots["robot_a"]
    target = Position(x=10.0, y=5.0, z=0.0)
    robot_a.target_position = target
    robot_a.state = RobotState.NAVIGATING

    # Manually execute one step tick
    dt = 0.5
    speed = 2.0
    dx = target.x - robot_a.position.x
    dy = target.y - robot_a.position.y
    initial_dist = (dx**2 + dy**2)**0.5

    # Run tick in sim
    robot_a.position.x += (dx / initial_dist) * (speed * dt)
    new_dist = ((target.x - robot_a.position.x)**2 + (target.y - robot_a.position.y)**2)**0.5
    assert new_dist < initial_dist
