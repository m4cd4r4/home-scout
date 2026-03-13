"""Launch Gazebo with a house world and spawn the Home Scout robot.

Usage:
    ros2 launch scout_simulation gazebo_house.launch.py
    ros2 launch scout_simulation gazebo_house.launch.py world:=my_house.world
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    description_pkg = get_package_share_directory("scout_description")
    simulation_pkg = get_package_share_directory("scout_simulation")

    xacro_file = os.path.join(description_pkg, "urdf", "scout.urdf.xacro")

    # Launch arguments
    world_arg = DeclareLaunchArgument(
        "world",
        default_value="empty.world",
        description="Gazebo world file to load",
    )
    x_arg = DeclareLaunchArgument("x", default_value="0.0", description="Spawn X position")
    y_arg = DeclareLaunchArgument("y", default_value="0.0", description="Spawn Y position")
    z_arg = DeclareLaunchArgument("z", default_value="0.05", description="Spawn Z position")

    # Process xacro to URDF
    robot_description = Command(["xacro ", xacro_file])

    # Gazebo server and client
    # TODO: Replace with actual gazebo_ros launch include path
    # gazebo = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(
    #             get_package_share_directory("gazebo_ros"),
    #             "launch",
    #             "gazebo.launch.py",
    #         )
    #     ),
    #     launch_arguments={"world": LaunchConfiguration("world")}.items(),
    # )

    # Robot state publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
        output="screen",
    )

    # Spawn the robot in Gazebo
    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-topic", "robot_description",
            "-entity", "home_scout",
            "-x", LaunchConfiguration("x"),
            "-y", LaunchConfiguration("y"),
            "-z", LaunchConfiguration("z"),
        ],
        output="screen",
    )

    # Joint state publisher for non-driven joints
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        output="screen",
    )

    return LaunchDescription([
        world_arg,
        x_arg,
        y_arg,
        z_arg,
        # gazebo,  # TODO: Uncomment when gazebo_ros is available
        robot_state_publisher,
        joint_state_publisher,
        spawn_robot,
    ])
