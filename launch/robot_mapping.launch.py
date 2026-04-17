import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    robot_share = get_package_share_directory("robot_diff_drive")

    startup_launch = os.path.join(robot_share, "launch", "robot_pi_startup.launch.py")
    slam_launch = os.path.join(
        get_package_share_directory("slam_toolbox"),
        "launch",
        "online_async_launch.py",
    )
    slam_params = os.path.join(robot_share, "config", "slam_toolbox.yaml")

    camera_port_arg = DeclareLaunchArgument(
        "camera_port",
        default_value="5000",
        description="UDP port to receive H.264 stream from Raspberry Pi",
    )
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Use simulation time for SLAM Toolbox",
    )
    slam_params_arg = DeclareLaunchArgument(
        "slam_params_file",
        default_value=slam_params,
        description="SLAM Toolbox parameter file",
    )

    robot_startup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(startup_launch),
        launch_arguments={
            "camera_port": LaunchConfiguration("camera_port"),
        }.items(),
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_launch),
        launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "slam_params_file": LaunchConfiguration("slam_params_file"),
        }.items(),
    )

    return LaunchDescription(
        [
            camera_port_arg,
            use_sim_time_arg,
            slam_params_arg,
            LogInfo(msg="[robot_diff_drive] Starting robot startup stack (bridge + odom + rviz)..."),
            robot_startup,
            LogInfo(msg="[robot_diff_drive] Starting SLAM Toolbox mapping..."),
            slam,
        ]
    )