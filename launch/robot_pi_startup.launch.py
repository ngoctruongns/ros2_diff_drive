"""
robot_pi_startup.launch.py
--------------------------
Starts all bridge nodes that relay data between the Raspberry Pi and ROS2
running on the laptop:

  1. velocity_control bridge  — motor commands / encoder feedback (via FastDDS)
  2. LiDAR bridge             — LD-Radar point cloud (via FastDDS)
     + static TF              — base_link → ldlidar_frame
  3. Pi camera bridge         — H.264 video stream (via UDP)

Launch arguments
----------------
  Velocity-control bridge
    (no run-time args — wheel geometry is read from the package params file)

  LiDAR bridge
        static TF is loaded from config/robot_pi_startup.yaml

  Camera bridge
    camera_port : UDP port on which the H.264 stream arrives (default: 5000)
"""

import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    robot_config = get_package_share_directory("robot_diff_drive")

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
    lidar_tf = startup_params.get("lidar_tf", {})
    lidar_topic_name = startup_params.get("lidar_topic_name", "ldlidar_scan")

    # ── Camera argument ───────────────────────────────────────────────────────
    camera_port_arg = DeclareLaunchArgument(
        "camera_port",
        default_value="5000",
        description="UDP port to receive the raw H.264 stream from Raspberry Pi",
    )

    # =========================================================================
    # 1. Velocity-control bridge
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
    # 2a. LiDAR bridge
    #     Receives raw LiDAR data from Pi via FastDDS → publishes /scan
    # =========================================================================
    ldlidar_bridge_node = Node(
        package="ldlidar_ros_bridge",
        executable="ldlidar_ros_bridge_node",
        name="ldlidar_bridge",
        output="screen",
        parameters=[{"lidar_topic_name": lidar_topic_name}],
    )

    # 2b. Static transform: base_link → ldlidar_frame from config/robot_pi_startup.yaml
    ldlidar_tf_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="ldlidar_static_tf",
        arguments=[
            str(lidar_tf.get("x", 0.0)),
            str(lidar_tf.get("y", 0.0)),
            str(lidar_tf.get("z", 0.0)),
            str(lidar_tf.get("yaw", 0.0)),
            str(lidar_tf.get("pitch", 0.0)),
            str(lidar_tf.get("roll", 0.0)),
            str(lidar_tf.get("parent_frame", "base_link")),
            str(lidar_tf.get("child_frame", "lidar_link")),
        ],
        output="screen",
    )

    # =========================================================================
    # 3. Pi camera bridge
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
    # 4. RViz2
    #    Visualises sensor data from all Pi bridge nodes
    # =========================================================================
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
    )

    return LaunchDescription(
        [
            # Arguments
            camera_port_arg,
            # Nodes
            LogInfo(msg="[robot_diff_drive] Starting velocity-control bridge..."),
            velocity_bridge_node,
            odom_node,
            LogInfo(msg="[robot_diff_drive] Starting LiDAR bridge..."),
            ldlidar_bridge_node,
            ldlidar_tf_node,
            LogInfo(msg="[robot_diff_drive] Starting Pi camera bridge..."),
            camera_bridge_node,
            LogInfo(msg="[robot_diff_drive] Starting RViz2..."),
            rviz_node,
        ]
    )
