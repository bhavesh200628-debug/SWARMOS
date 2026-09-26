"""
SWARMOS Warehouse Environment Setup
Defines physical layout, zones, static and dynamic obstacles, packages, and initial fleet configuration.
"""
from typing import List, Dict
from backend.models.schemas import (
    WarehouseZone, Package, PackageState, Obstacle, Position,
    Robot, RobotCapability, RobotState
)

def create_default_zones() -> List[WarehouseZone]:
    return [
        WarehouseZone(
            id="zone_a",
            name="Zone A (Intake & Storage)",
            zone_type="storage",
            x_min=2.0, x_max=10.0, y_min=2.0, y_max=8.0,
            color="#3b82f6"  # Blue
        ),
        WarehouseZone(
            id="zone_b",
            name="Zone B (Staging & Inspection)",
            zone_type="inspection",
            x_min=12.0, x_max=22.0, y_min=2.0, y_max=8.0,
            color="#eab308"  # Yellow/Gold
        ),
        WarehouseZone(
            id="quarantine",
            name="Quarantine Zone",
            zone_type="quarantine",
            x_min=24.0, x_max=28.0, y_min=14.0, y_max=18.0,
            color="#ef4444"  # Red
        ),
        WarehouseZone(
            id="charging_bay",
            name="Autonomous Charging Bay",
            zone_type="charging",
            x_min=2.0, x_max=6.0, y_min=14.0, y_max=18.0,
            color="#10b981"  # Emerald
        ),
        WarehouseZone(
            id="transit_corridor",
            name="Central Transit Corridor",
            zone_type="transit",
            x_min=2.0, x_max=28.0, y_min=9.0, y_max=13.0,
            color="#475569"  # Slate
        )
    ]

def create_default_packages() -> List[Package]:
    return [
        Package(
            id="pkg_a1",
            name="Pallet A-04 (Electronics)",
            position=Position(x=5.0, y=4.0, z=0.0),
            state=PackageState.NORMAL,
            weight_kg=12.0,
            zone_id="zone_a"
        ),
        Package(
            id="pkg_b1",
            name="Container B-12 [DAMAGED]",
            position=Position(x=17.0, y=5.0, z=0.0),
            state=PackageState.DAMAGED,
            weight_kg=18.5,
            zone_id="zone_b"
        ),
        Package(
            id="pkg_b2",
            name="Pallet B-07 (Hardware)",
            position=Position(x=20.0, y=6.0, z=0.0),
            state=PackageState.NORMAL,
            weight_kg=9.0,
            zone_id="zone_b"
        )
    ]

def create_default_obstacles() -> List[Obstacle]:
    return [
        Obstacle(
            id="obs_pillar_1",
            position=Position(x=11.0, y=5.0, z=0.0),
            radius=0.7,
            is_dynamic=False,
            description="Structural Support Pillar 1"
        ),
        Obstacle(
            id="obs_pillar_2",
            position=Position(x=11.0, y=11.0, z=0.0),
            radius=0.7,
            is_dynamic=False,
            description="Structural Support Pillar 2"
        ),
        Obstacle(
            id="obs_rack_c",
            position=Position(x=23.0, y=11.0, z=0.0),
            radius=1.0,
            is_dynamic=False,
            description="Heavy Storage Rack Matrix"
        )
    ]

def create_default_fleet() -> Dict[str, Robot]:
    return {
        "robot_a": Robot(
            id="robot_a",
            name="Alpha (Scout-01)",
            robot_type="differential_drive_amr",
            capabilities=[RobotCapability.SCOUT, RobotCapability.INSPECTOR],
            state=RobotState.IDLE,
            battery=98.0,
            position=Position(x=4.0, y=5.0, z=0.0),
            velocity=0.0,
            heading=0.0
        ),
        "robot_b": Robot(
            id="robot_b",
            name="Bravo (Inspector-02)",
            robot_type="vision_inspection_amr",
            capabilities=[RobotCapability.INSPECTOR],
            state=RobotState.IDLE,
            battery=94.0,
            position=Position(x=13.0, y=4.0, z=0.0),
            velocity=0.0,
            heading=90.0
        ),
        "robot_c": Robot(
            id="robot_c",
            name="Charlie (Carrier-03)",
            robot_type="heavy_transport_amr",
            capabilities=[RobotCapability.CARRIER, RobotCapability.HEAVY_LIFT],
            state=RobotState.IDLE,
            battery=91.0,
            position=Position(x=8.0, y=11.0, z=0.0),
            velocity=0.0,
            heading=0.0
        )
    }
