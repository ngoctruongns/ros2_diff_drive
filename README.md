# robot_diff_drive

Top-level bringup package for the diff-drive robot. This package is used on the laptop side to:

- start all Pi-related bridge nodes (velocity, LiDAR, camera)
- centralize robot-specific configuration files
- launch practical mapping and navigation flows (SLAM, map save, Nav2)

## Package Layout

```text
robot_diff_drive/
├── config/
│   ├── robot_pi_startup.yaml
│   ├── odometry.yaml
│   ├── slam_toolbox.yaml
│   └── nav2_params_robot.yaml
├── docs/
│   └── slam_mapping_debug_checklist.md
├── launch/
│   ├── robot_pi_startup.launch.py
│   ├── robot_algorithms.launch.py
│   ├── robot_mapping.launch.py
│   └── robot_navigation.launch.py
├── CMakeLists.txt
└── package.xml
```

## Prerequisites

```bash
cd /home/tvn/ros2_ws
source /opt/ros/humble/setup.zsh
source install/setup.zsh
```

Install runtime packages once (if missing):

```bash
sudo apt update
sudo apt install -y ros-humble-joy ros-humble-teleop-twist-joy ros-humble-slam-toolbox ros-humble-navigation2 ros-humble-nav2-bringup
```

## 1) Robot Startup (Pi bridges + RViz + PS3 joystick)

Launch all bridge nodes that connect laptop ROS2 with Raspberry Pi:

```bash
ros2 launch robot_diff_drive robot_pi_startup.launch.py
```

This launch starts:

- `velocity_control/ros2_bridge`
- `velocity_control/wheel_odometry_node`
- `ldlidar_ros_bridge/ldlidar_ros_bridge_node`
- `tf2_ros/static_transform_publisher` for LiDAR static TF
- `ros2_pi_camera_bridge/ros2_pi_camera_bridge_node`
- `joy/joy_node` (PS3 joystick input)
- `teleop_twist_joy/teleop_node` (`/joy` -> `/cmd_vel`)
- `velocity_control/ps3_utils_control` (LED / buzzer button mapping)
- `rviz2`

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

Disable joystick nodes when needed:

```bash
ros2 launch robot_diff_drive robot_pi_startup.launch.py use_joystick:=false
```

## 2) Mapping Workflow (Create Map)

Run mapping in one command (startup + SLAM Toolbox):

```bash
ros2 launch robot_diff_drive robot_mapping.launch.py
```

This is the practical command you can use like TurtleBot3 mapping practice.

Useful arguments:

- `camera_port` (default: `5000`)
- `use_joystick` (default: `true`)
- `use_sim_time` (default: `false`)
- `slam_params_file` (default: `config/slam_toolbox.yaml`)

Examples:

```bash
# Disable joystick in this session
ros2 launch robot_diff_drive robot_mapping.launch.py use_joystick:=false

# Override camera UDP port
ros2 launch robot_diff_drive robot_mapping.launch.py camera_port:=5600
```

## 3) Save Map

After mapping is stable, save map files (`.yaml` + `.pgm`):

```bash
mkdir -p /home/tvn/ros2_ws/src/robot_diff_drive/maps
ros2 run nav2_map_server map_saver_cli -f /home/tvn/ros2_ws/src/robot_diff_drive/maps/my_map
```

Verify output:

```bash
ls -lh /home/tvn/ros2_ws/src/robot_diff_drive/maps
```

## 4) Navigation2 with Saved Map

Run localization + navigation in one command:

```bash
ros2 launch robot_diff_drive robot_navigation.launch.py \
  map:=/home/tvn/ros2_ws/src/robot_diff_drive/maps/my_map.yaml
```

This launch starts:

- robot startup stack (bridge + odometry + LiDAR TF + camera + optional joystick + RViz)
- Nav2 localization (`map_server` + `amcl`)
- Nav2 navigation (`planner_server`, `controller_server`, `bt_navigator`, etc.)

Important arguments:

- `map` (required): absolute path to saved map `.yaml`
- `camera_port` (default: `5000`)
- `use_joystick` (default: `true`)
- `use_sim_time` (default: `false`)
- `nav2_params_file` (default: `config/nav2_params_robot.yaml`)
- `use_keepout_zones` (default: `false`)
- `keepout_mask` (required when `use_keepout_zones:=true`)

### Virtual Wall (Keepout Zones)

You can define forbidden areas (stairs, toilet, restricted zones) with Nav2 keepout filter.

Run navigation with keepout enabled:

```bash
ros2 launch robot_diff_drive robot_navigation.launch.py \
  map:=/home/tvn/ros2_ws/src/robot_diff_drive/maps/my_map.yaml \
  use_keepout_zones:=true \
  keepout_mask:=/home/tvn/ros2_ws/src/robot_diff_drive/maps/my_keepout_mask.yaml
```

How to create `my_keepout_mask.yaml` and mask image:

1. Copy your saved map image (`my_map.pgm`) to a new file `my_keepout_mask.pgm`.
2. Open `my_keepout_mask.pgm` in an image editor and paint forbidden regions as black.
3. Keep allowed regions white.
4. Create a yaml next to the mask image:

```yaml
image: my_keepout_mask.pgm
mode: trinary
resolution: 0.05
origin: [-10.0, -10.0, 0.0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.25
```

Notes:

- `resolution` and `origin` must match your main map yaml.
- Good tools to draw keepout zones: GIMP, Krita, KolourPaint.
- If you want interactive zone drawing later, you can add tools like RViz polygon plugins or custom map editor workflows, but image mask is the most stable and production-friendly with Nav2 Humble.

## 5) How to Practice Like TurtleBot3

Recommended training flow:

1. Build map in your lab area with `robot_mapping.launch.py`.
2. Save map to `robot_diff_drive/maps/`.
3. Relaunch using `robot_navigation.launch.py map:=...`.
4. In RViz2, set `2D Pose Estimate` once to initialize AMCL.
5. Use `2D Nav Goal` to send targets and observe path planning + control.
6. While Nav2 runs, you can still use PS3 teleop for manual recovery/repositioning.

Validation commands during practice:

```bash
ros2 topic list | grep -E '/cmd_vel|/odom|/scan|/map|/amcl_pose|/plan'
ros2 topic hz /scan
ros2 topic hz /odom
```

## 6) Optional: Algorithms Launch (Advanced)

Launch basic algorithm stack:

```bash
ros2 launch robot_diff_drive robot_algorithms.launch.py
```

By default this launch starts:

- `slam_toolbox` online async mapping
- `nav2_bringup` navigation stack

### Arguments

- `use_slam` (default: `true`)
- `use_nav2` (default: `true`)
- `use_sim_time` (default: `false`)
- `nav2_params_file` (default: Nav2 package params)

Examples:

```bash
# Start only SLAM
ros2 launch robot_diff_drive robot_algorithms.launch.py use_nav2:=false

# Start only Nav2 stack
ros2 launch robot_diff_drive robot_algorithms.launch.py use_slam:=false
```

## Notes

- Keep robot-specific geometry and TF values in this package `config/` directory.
- Keep reusable protocol/driver/kinematics implementation in feature packages such as `velocity_control`.
- For common mapping failures and fast fixes, use [docs/slam_mapping_debug_checklist.md](docs/slam_mapping_debug_checklist.md).
