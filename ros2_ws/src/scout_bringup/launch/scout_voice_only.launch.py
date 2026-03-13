"""Phase 1 launch: Voice interface only (no cameras, no motors)."""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
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
                "personality",
                default_value=os.path.join(config_dir, "personality_default.yaml"),
                description="Path to personality configuration",
            ),
            Node(
                package="scout_voice",
                executable="wake_word_node",
                name="wake_word",
                output="screen",
                parameters=[{"wake_phrase": "hey scout"}],
            ),
            Node(
                package="scout_voice",
                executable="asr_node",
                name="asr",
                output="screen",
                parameters=[{"model": "whisper-small-en", "device": "npu"}],
            ),
            Node(
                package="scout_voice",
                executable="tts_node",
                name="tts",
                output="screen",
                parameters=[{"voice": "en_US-amy-medium", "speed": 1.0}],
            ),
            Node(
                package="scout_voice",
                executable="conversation_node",
                name="conversation",
                output="screen",
                parameters=[
                    LaunchConfiguration("personality"),
                ],
            ),
        ]
    )
