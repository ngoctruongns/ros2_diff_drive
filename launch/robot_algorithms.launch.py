import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    robot_share = get_package_share_directory("robot_diff_drive")

    slam_config = os.path.join(robot_share, "config", "slam_toolbox.yaml")
    default_nav2_params = PathJoinSubstitution(
        [
            FindPackageShare("nav2_bringup"),
            "params",
            "nav2_params.yaml",
        ]
    )

    use_slam_arg = DeclareLaunchArgument(
        "use_slam",
        default_value="true",
        description="Start SLAM Toolbox for online mapping",
    )
    use_nav2_arg = DeclareLaunchArgument(
        "use_nav2",
        default_value="true",
        description="Start Nav2 stack (planner/controller/BT navigator)",
    )
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Use simulation time",
    )
    nav2_params_arg = DeclareLaunchArgument(
        "nav2_params_file",
        default_value=default_nav2_params,
        description="Nav2 parameters file",
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution(
                    [
                        FindPackageShare("slam_toolbox"),
                        "launch",
                        "online_async_launch.py",
                    ]
                )
            ]
        ),
        condition=IfCondition(LaunchConfiguration("use_slam")),
        launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "slam_params_file": slam_config,
        }.items(),
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution(
                    [
                        FindPackageShare("nav2_bringup"),
                        "launch",
                        "navigation_launch.py",
                    ]
                )
            ]
        ),
        condition=IfCondition(LaunchConfiguration("use_nav2")),
        launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "autostart": "true",
            "params_file": LaunchConfiguration("nav2_params_file"),
        }.items(),
    )

    return LaunchDescription(
        [
            use_slam_arg,
            use_nav2_arg,
            use_sim_time_arg,
            nav2_params_arg,
            LogInfo(msg="[robot_diff_drive] Starting wheel odometry node..."),
            LogInfo(msg="[robot_diff_drive] Starting SLAM Toolbox..."),
            slam_launch,
            LogInfo(msg="[robot_diff_drive] Starting Nav2..."),
            nav2_launch,
        ]
    )
