# SLAM Mapping Debug Checklist (ROS2 + slam_toolbox)

Use this checklist when mapping quality is poor (map distortion, drift, ghost walls, or unstable localization).

## 1) Verify Required Inputs

```bash
ros2 topic list | grep -E "/scan|/odom|/tf"
ros2 topic hz /scan
ros2 topic hz /odom
```

Expected:

- `/scan` is stable (typically 5-15 Hz for low-cost 2D LiDAR).
- `/odom` is stable and monotonic.
- No large timestamp jumps.

## 2) Verify TF Chain

Required chain for mapping:

- `map -> odom` (published by slam_toolbox)
- `odom -> base_link` (published by odometry node)
- `base_link -> lidar_link` (static transform)

Commands:

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo base_link lidar_link
ros2 run tf2_ros tf2_echo map odom
```

If `base_link -> lidar_link` is wrong, update `config/robot_pi_startup.yaml` and relaunch.

## 3) Check LiDAR Mount Parameters

Symptoms of wrong mount:

- map rotates unexpectedly,
- mirrored walls,
- duplicate wall lines.

Check these in `config/robot_pi_startup.yaml`:

- `x`, `y`, `z`
- `yaw`, `pitch`, `roll`
- frame names (`parent_frame`, `child_frame`)

## 4) Check Odometry Quality

If odometry drifts quickly, map will stretch and loop closure will struggle.

Quick checks:

```bash
ros2 topic echo /odom --once
```

Verify:

- `child_frame_id` is `base_link`
- linear/angular velocities are plausible
- pose does not jump when robot is stationary

## 5) Tune slam_toolbox Parameters

Primary file: `config/slam_toolbox.yaml`

Most useful knobs:

- `minimum_travel_distance`, `minimum_travel_heading`
- `minimum_time_interval`
- `scan_buffer_size`
- `loop_search_maximum_distance`
- `link_match_minimum_response_fine`

Guidelines:

- If map is noisy in place: increase `minimum_time_interval`.
- If map updates too slowly: lower `minimum_travel_distance` slightly.
- If false loop closures happen: increase `loop_match_minimum_response_*`.

## 6) Drive Pattern During Mapping

Bad driving causes bad maps even with correct parameters.

Recommended behavior:

- move slowly and steadily,
- avoid fast spins,
- keep clear overlap between passes,
- close loops (return near previous path).

## 7) Save and Validate Map

Save map:

```bash
ros2 run nav2_map_server map_saver_cli -f /home/tvn/ros2_ws/src/robot_diff_drive/maps/test_map
```

Then inspect:

- wall thickness consistency,
- corridor straightness,
- loop closure at start/end area.

## 8) Quick Failure Matrix

- Curved straight walls: bad odom scale or wrong LiDAR yaw.
- Double walls: vibration, timing mismatch, or wrong static TF.
- Global map jumps: unstable loop closure thresholds.
- No map growth: wrong `scan_topic` or missing TF.
