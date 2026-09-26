export type RobotCapability = 'scout' | 'inspector' | 'carrier' | 'manipulator' | 'heavy_lift';

export type RobotState =
  | 'idle'
  | 'navigating'
  | 'inspecting'
  | 'transporting'
  | 'degraded'
  | 'blocked'
  | 'low_battery'
  | 'offline'
  | 'charging';

export interface Position {
  x: number;
  y: number;
  z?: number;
}

export interface Robot {
  id: string;
  name: string;
  robot_type: string;
  capabilities: RobotCapability[];
  state: RobotState;
  battery: number;
  position: Position;
  target_position?: Position | null;
  velocity: number;
  heading: number;
  current_task_id?: string | null;
  carried_package_id?: string | null;
  is_physical?: boolean;
}

export type TaskType =
  | 'navigate'
  | 'inspect'
  | 'identify'
  | 'transport'
  | 'verify'
  | 'report_status'
  | 'return_to_base';

export type TaskStatus = 'pending' | 'assigned' | 'in_progress' | 'completed' | 'failed' | 'cancelled';

export interface Task {
  id: string;
  mission_id: string;
  title: string;
  task_type: TaskType;
  action: string;
  target_location?: Position | null;
  target_zone?: string | null;
  target_package_id?: string | null;
  destination_zone?: string | null;
  assigned_robot_id?: string | null;
  dependencies: string[];
  status: TaskStatus;
  progress: number;
  estimated_duration_sec: number;
  completed_at?: number | null;
  error_message?: string | null;
}

export interface Mission {
  id: string;
  natural_language_prompt: string;
  status: 'pending_planning' | 'planned' | 'executing' | 'replanning' | 'completed' | 'failed' | 'halted';
  tasks: Task[];
  revisions: Array<{
    revision: number;
    timestamp: number;
    reason: string;
    model: string;
    confidence: number;
    latency_ms: number;
  }>;
  completed_at?: number | null;
  report_summary?: string | null;
}

export interface WarehouseZone {
  id: string;
  name: string;
  zone_type: string;
  x_min: number;
  x_max: number;
  y_min: number;
  y_max: number;
  color: string;
}

export interface Package {
  id: string;
  name: string;
  position: Position;
  state: 'normal' | 'damaged' | 'quarantined';
  weight_kg: number;
  zone_id: string;
}

export interface Obstacle {
  id: string;
  position: Position;
  radius: number;
  is_dynamic: boolean;
  description: string;
}

export interface FailureEvent {
  id: string;
  timestamp: number;
  robot_id: string;
  failure_type: string;
  description: string;
  severity: string;
  resolved: boolean;
  resolved_at?: number | null;
  mitigation_action?: string | null;
}

export interface SimulationState {
  timestamp: number;
  tick: number;
  robots: Robot[];
  packages: Package[];
  obstacles: Obstacle[];
  zones: WarehouseZone[];
  active_mission?: Mission | null;
  active_failures: FailureEvent[];
  recent_decision_events: Array<{
    timestamp: number;
    type: string;
    message: string;
    metadata?: any;
  }>;
  simulation_running: boolean;
  speed_multiplier: number;
}
