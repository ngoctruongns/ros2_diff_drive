# robot_diff_drive

Top-level bringup package for the diff-drive robot. This package is used on the laptop side to:

- start all Pi-related bridge nodes (velocity, LiDAR, camera)
- centralize robot-specific configuration files
- launch basic algorithm stack (wheel odometry, SLAM, Nav2)

## Package Layout

```text
robot_diff_drive/
├── config/
│   ├── robot_pi_startup.yaml
│   ├── odometry.yaml
│   └── slam_toolbox.yaml
├── docs/
│   └── slam_mapping_debug_checklist.md
├── launch/
│   ├── robot_pi_startup.launch.py
│   ├── robot_algorithms.launch.py
│   └── robot_mapping.launch.py
├── CMakeLists.txt
└── package.xml
```

## 1) Pi Bridge Startup

Launch all bridge nodes that connect laptop ROS2 with Raspberry Pi:

```bash
ros2 launch robot_diff_drive robot_pi_startup.launch.py
```

This launch starts:

- `velocity_control/ros2_bridge`
- `ldlidar_ros_bridge/ldlidar_ros_bridge_node`
- `tf2_ros/static_transform_publisher` for LiDAR static TF
- `ros2_pi_camera_bridge/ros2_pi_camera_bridge_node`

### Startup Config

LiDAR static transform is configured in:

- `config/robot_pi_startup.yaml`

Example:

```yaml
robot_pi_startup:
  ros__parameters:
    lidar_tf:
      parent_frame: base_link
      child_frame: lidar_link
      x: 0.0
      y: 0.0
      z: 0.0
      yaw: 0.0
      pitch: 0.0
      roll: 0.0
```

Camera UDP port can still be overridden from CLI:

```bash
ros2 launch robot_diff_drive robot_pi_startup.launch.py camera_port:=5000
```

## 2) Algorithms Startup (Basic)

Launch basic algorithm stack:

```bash
ros2 launch robot_diff_drive robot_algorithms.launch.py
```

By default this launch starts:

- `velocity_control/wheel_odometry_node` (tick -> `/odom`)
- `slam_toolbox` online async mapping
- `nav2_bringup` navigation stack

### Arguments

- `use_slam` (default: `true`)
- `use_nav2` (default: `true`)
- `use_sim_time` (default: `false`)
- `nav2_params_file` (default: Nav2 package params)

Examples:

```bash
# Start only wheel odometry + SLAM
ros2 launch robot_diff_drive robot_algorithms.launch.py use_nav2:=false

# Start only wheel odometry + Nav2
ros2 launch robot_diff_drive robot_algorithms.launch.py use_slam:=false
```

## 3) One-Command Mapping Bringup

Launch bridge + wheel odometry + RViz + SLAM Toolbox in one command:

```bash
ros2 launch robot_diff_drive robot_mapping.launch.py
```

Arguments:

- `camera_port` (default: `5000`)
- `use_sim_time` (default: `false`)
- `slam_params_file` (default: `config/slam_toolbox.yaml`)

Examples:

```bash
# Override camera UDP port
ros2 launch robot_diff_drive robot_mapping.launch.py camera_port:=5600

# Try an alternate SLAM parameter file
ros2 launch robot_diff_drive robot_mapping.launch.py \
  slam_params_file:=/home/tvn/ros2_ws/src/robot_diff_drive/config/slam_toolbox.yaml
```

## Recommended Bringup Order

1. Start Pi bridges:

```bash
ros2 launch robot_diff_drive robot_pi_startup.launch.py
```

1. In a second terminal, start algorithms:

```bash
ros2 launch robot_diff_drive robot_algorithms.launch.py
```

1. Verify critical topics:

```bash
ros2 topic echo /wheel_encoder_ticks
ros2 topic echo /scan
ros2 topic echo /odom
```

## Notes

- Keep robot-specific geometry and TF values in this package `config/` directory.
- Keep reusable protocol/driver/kinematics implementation in feature packages such as `velocity_control`.
- For common mapping failures and fast fixes, use [docs/slam_mapping_debug_checklist.md](docs/slam_mapping_debug_checklist.md).
