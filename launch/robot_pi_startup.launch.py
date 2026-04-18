"""
robot_pi_startup.launch.py
--------------------------
Starts all bridge nodes that relay data between the Raspberry Pi and ROS2
running on the laptop:

  1. robot_state_publisher    — publishes /robot_description + all static TFs from URDF
  2. velocity_control bridge  — motor commands / encoder feedback (via FastDDS)
  3. LiDAR bridge             — LD-Radar point cloud (via FastDDS)
  4. Pi camera bridge         — H.264 video stream (via UDP)

Launch arguments
----------------
  Velocity-control bridge
    (no run-time args — wheel geometry is read from the package params file)

  Camera bridge
    camera_port : UDP port on which the H.264 stream arrives (default: 5000)

  Joystick (PS3)
    use_joystick : launch joy + teleop_twist_joy + ps3_utils_control (default: true)
"""

import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    robot_config = get_package_share_directory("robot_diff_drive")

    # Load URDF for robot_state_publisher
    urdf_file = os.path.join(robot_config, "urdf", "robot.urdf")
    with open(urdf_file, "r", encoding="utf-8") as f:
        robot_description = f.read()

    source_rviz_config = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "rviz",
            "robot_pi_startup.rviz",
        )
    )
    installed_rviz_config = os.path.join(
        robot_config,
        "rviz",
        "robot_pi_startup.rviz",
    )
    rviz_config = (
        source_rviz_config if os.path.exists(source_rviz_config) else installed_rviz_config
    )

    startup_config_file = os.path.join(robot_config, "config", "robot_pi_startup.yaml")

    with open(startup_config_file, "r", encoding="utf-8") as f:
        startup_config = yaml.safe_load(f) or {}

    startup_params = startup_config.get("robot_pi_startup", {}).get(
        "ros__parameters", {}
    )
    lidar_topic_name = startup_params.get("lidar_topic_name", "ldlidar_scan")

    # ── Camera argument ──────────────────────────────────────────────────────────────
    camera_port_arg = DeclareLaunchArgument(
        "camera_port",
        default_value="5000",
        description="UDP port to receive the raw H.264 stream from Raspberry Pi",
    )

    # ── Joystick argument ─────────────────────────────────────────────────────
    use_joystick_arg = DeclareLaunchArgument(
        "use_joystick",
        default_value="true",
        description="Launch PS3 joystick nodes (joy, teleop_twist_joy, ps3_utils_control)",
    )

    # =========================================================================
    # 1. Robot state publisher
    #    Publishes /robot_description and all static TFs defined in the URDF
    #    (including base_footprint → base_link and base_link → lidar_link).
    #    Replaces the old static_transform_publisher.
    # =========================================================================
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description}],
    )

    # =========================================================================
    # 2. Velocity-control bridge
    #    Receives encoder ticks from STM32 → publishes /odom (or tick topics)
    #    Subscribes /cmd_vel → forwards motor commands to STM32 via FastDDS
    # =========================================================================
    velocity_params = os.path.join(robot_config, "config", "ros2_bridge_params.yaml")

    velocity_bridge_node = Node(
        package="velocity_control",
        executable="ros2_bridge",
        name="velocity_bridge",
        output="screen",
        parameters=[velocity_params],
    )

    odom_config = os.path.join(robot_config, "config", "odometry.yaml")

    odom_node = Node(
        package="velocity_control",
        executable="wheel_odometry_node",
        name="wheel_odometry",
        output="screen",
        parameters=[odom_config],
    )

    # =========================================================================
    # 3. LiDAR bridge
    #     Receives raw LiDAR data from Pi via FastDDS → publishes /scan
    #     TF base_link → lidar_link is now handled by robot_state_publisher.
    # =========================================================================
    ldlidar_bridge_node = Node(
        package="ldlidar_ros_bridge",
        executable="ldlidar_ros_bridge_node",
        name="ldlidar_bridge",
        output="screen",
        parameters=[{"lidar_topic_name": lidar_topic_name}],
    )

    # =========================================================================
    # 4. Pi camera bridge
    #    Receives UDP H.264 stream from Pi → publishes /image_raw/compressed
    # =========================================================================
    camera_bridge_node = Node(
        package="ros2_pi_camera_bridge",
        executable="ros2_pi_camera_bridge_node",
        name="camera_bridge",
        output="screen",
        parameters=[{"port": LaunchConfiguration("camera_port")}],
    )

    # =========================================================================
    # 5. RViz2
    #    Visualises sensor data from all Pi bridge nodes
    # =========================================================================
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
    )

    # =========================================================================
    # 6. PS3 joystick control
    #    joy_node        — reads raw joystick events
    #    teleop_node     — converts joystick axes to /cmd_vel (hold L1 to move)
    #    ps3_utils_node  — maps buttons to LED / buzzer commands
    # =========================================================================
    velocity_config = get_package_share_directory("velocity_control")
    ps3_teleop_config = os.path.join(velocity_config, "joy_stick", "ps3_teleop.yaml")
    ps3_utils_config = os.path.join(velocity_config, "joy_stick", "ps3_utils_control.yaml")

    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        output="screen",
        condition=IfCondition(LaunchConfiguration("use_joystick")),
        parameters=[{
            "dev": "/dev/input/js0",
            "deadzone": 0.1,
            "autorepeat_rate": 20.0,
        }],
    )

    teleop_node = Node(
        package="teleop_twist_joy",
        executable="teleop_node",
        name="teleop_twist_joy_node",
        output="screen",
        condition=IfCondition(LaunchConfiguration("use_joystick")),
        parameters=[ps3_teleop_config],
        remappings=[("cmd_vel", "/cmd_vel")],
    )

    ps3_utils_node = Node(
        package="velocity_control",
        executable="ps3_utils_control",
        name="ps3_utils_control_node",
        output="screen",
        condition=IfCondition(LaunchConfiguration("use_joystick")),
        parameters=[ps3_utils_config],
    )

    return LaunchDescription(
        [
            # Arguments
            camera_port_arg,
            use_joystick_arg,
            # Nodes
            LogInfo(msg="[robot_diff_drive] Starting robot state publisher (URDF model)..."),
            robot_state_publisher_node,
            LogInfo(msg="[robot_diff_drive] Starting velocity-control bridge..."),
            velocity_bridge_node,
            odom_node,
            LogInfo(msg="[robot_diff_drive] Starting LiDAR bridge..."),
            ldlidar_bridge_node,
            LogInfo(msg="[robot_diff_drive] Starting Pi camera bridge..."),
            camera_bridge_node,
            LogInfo(msg="[robot_diff_drive] Starting RViz2..."),
            rviz_node,
            LogInfo(msg="[robot_diff_drive] Starting PS3 joystick control..."),
            joy_node,
            teleop_node,
            ps3_utils_node,
        ]
    )
