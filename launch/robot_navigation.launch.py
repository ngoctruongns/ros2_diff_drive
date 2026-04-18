import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _nav2_actions(context, robot_share):
    """Evaluated at launch time: selects params file and conditionally adds keepout servers."""
    cfg = context.launch_configurations
    use_keepout = cfg.get("use_keepout_zones", "false").lower() == "true"
    use_sim_time = cfg.get("use_sim_time", "false")
    map_path = cfg.get("map", "")
    keepout_mask = cfg.get("keepout_mask", "")

    # Use user-supplied params file if provided; otherwise auto-select by keepout flag.
    user_params = cfg.get("nav2_params_file", "")
    if user_params:
        nav2_params = user_params
    elif use_keepout:
        nav2_params = os.path.join(robot_share, "config", "nav2_params_robot_keepout.yaml")
    else:
        nav2_params = os.path.join(robot_share, "config", "nav2_params_robot.yaml")

    nav2_bringup = get_package_share_directory("nav2_bringup")
    localization_launch = os.path.join(nav2_bringup, "launch", "localization_launch.py")
    navigation_launch = os.path.join(nav2_bringup, "launch", "navigation_launch.py")

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(localization_launch),
        launch_arguments={
            "map": map_path,
            "use_sim_time": use_sim_time,
            "autostart": "true",
            "params_file": nav2_params,
        }.items(),
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(navigation_launch),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "autostart": "true",
            "params_file": nav2_params,
        }.items(),
    )

    actions = [
        LogInfo(msg=f"[robot_diff_drive] Nav2 params: {nav2_params}"),
        LogInfo(msg="[robot_diff_drive] Starting Nav2 localization (map_server + amcl)..."),
        localization,
        LogInfo(msg="[robot_diff_drive] Starting Nav2 navigation stack..."),
        navigation,
    ]

    if use_keepout:
        sim_time_bool = use_sim_time.lower() == "true"
        keepout_mask_server = Node(
            package="nav2_map_server",
            executable="map_server",
            name="filter_mask_server",
            output="screen",
            parameters=[{
                "yaml_filename": keepout_mask,
                "topic_name": "keepout_filter_mask",
                "frame_id": "map",
                "use_sim_time": sim_time_bool,
            }],
        )
        costmap_filter_info_server = Node(
            package="nav2_map_server",
            executable="costmap_filter_info_server",
            name="costmap_filter_info_server",
            output="screen",
            parameters=[{
                "use_sim_time": sim_time_bool,
                "type": 0,
                "filter_info_topic": "costmap_filter_info",
                "mask_topic": "keepout_filter_mask",
                "base": 0.0,
                "multiplier": 1.0,
            }],
        )
        lifecycle_manager_costmap_filters = Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_costmap_filters",
            output="screen",
            parameters=[{
                "use_sim_time": sim_time_bool,
                "autostart": True,
                "bond_timeout": 0.0,
                "node_names": ["filter_mask_server", "costmap_filter_info_server"],
            }],
        )
        actions = [
            LogInfo(msg="[robot_diff_drive] Starting keepout-zone servers..."),
            keepout_mask_server,
            costmap_filter_info_server,
            lifecycle_manager_costmap_filters,
        ] + actions

    return actions


def generate_launch_description():
    robot_share = get_package_share_directory("robot_diff_drive")
    startup_launch = os.path.join(robot_share, "launch", "robot_pi_startup.launch.py")

    camera_port_arg = DeclareLaunchArgument(
        "camera_port",
        default_value="5000",
        description="UDP port to receive H.264 stream from Raspberry Pi",
    )
    use_joystick_arg = DeclareLaunchArgument(
        "use_joystick",
        default_value="true",
        description="Launch PS3 joystick nodes from robot_pi_startup",
    )
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Use simulation time",
    )
    use_keepout_zones_arg = DeclareLaunchArgument(
        "use_keepout_zones",
        default_value="false",
        description="Enable virtual walls using a keepout mask (needs keepout_mask set)",
    )
    keepout_mask_arg = DeclareLaunchArgument(
        "keepout_mask",
        default_value="",
        description="Absolute path to keepout mask yaml file (required when use_keepout_zones:=true)",
    )
    map_arg = DeclareLaunchArgument(
        "map",
        default_value="",
        description="Absolute path to map yaml file (required for localization)",
    )
    nav2_params_arg = DeclareLaunchArgument(
        "nav2_params_file",
        default_value="",
        description=(
            "Nav2 parameters file. Defaults to nav2_params_robot.yaml or "
            "nav2_params_robot_keepout.yaml depending on use_keepout_zones."
        ),
    )

    robot_startup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(startup_launch),
        launch_arguments={
            "camera_port": LaunchConfiguration("camera_port"),
            "use_joystick": LaunchConfiguration("use_joystick"),
        }.items(),
    )

    return LaunchDescription(
        [
            camera_port_arg,
            use_joystick_arg,
            use_sim_time_arg,
            use_keepout_zones_arg,
            keepout_mask_arg,
            map_arg,
            nav2_params_arg,
            LogInfo(msg="[robot_diff_drive] Starting robot startup stack (bridge + odom + rviz)..."),
            robot_startup,
            OpaqueFunction(function=lambda context: _nav2_actions(context, robot_share)),
        ]
    )
