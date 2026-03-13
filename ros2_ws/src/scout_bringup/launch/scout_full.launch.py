"""Full system launch: all subsystems active."""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    config_dir = os.path.join(
        get_package_share_directory("scout_bringup"), "config"
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "sim", default_value="false", description="Run in simulation mode"
            ),
            # Voice subsystem
            Node(
                package="scout_voice",
                executable="wake_word_node",
                name="wake_word",
                output="screen",
            ),
            Node(
                package="scout_voice",
                executable="asr_node",
                name="asr",
                output="screen",
            ),
            Node(
                package="scout_voice",
                executable="tts_node",
                name="tts",
                output="screen",
            ),
            Node(
                package="scout_voice",
                executable="conversation_node",
                name="conversation",
                output="screen",
            ),
            # Vision subsystem
            Node(
                package="scout_vision",
                executable="camera_node",
                name="camera_front",
                output="screen",
                parameters=[{"camera_id": 0, "name": "front"}],
            ),
            Node(
                package="scout_vision",
                executable="detector_node",
                name="detector",
                output="screen",
            ),
            # Navigation subsystem
            Node(
                package="scout_nav",
                executable="base_driver_node",
                name="base_driver",
                output="screen",
            ),
            Node(
                package="scout_nav",
                executable="patrol_node",
                name="patrol",
                output="screen",
            ),
            # Memory subsystem
            Node(
                package="scout_memory",
                executable="object_memory_node",
                name="object_memory",
                output="screen",
                parameters=[
                    {"db_path": "/home/scout/data/scout_memory.db"},
                ],
            ),
            # Face recognition subsystem
            Node(
                package="scout_faces",
                executable="recognition_node",
                name="face_recognition",
                output="screen",
            ),
            Node(
                package="scout_faces",
                executable="greeting_node",
                name="greeting",
                output="screen",
            ),
        ]
    )
