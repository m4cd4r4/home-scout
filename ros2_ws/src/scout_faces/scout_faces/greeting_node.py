"""Greeting node.

Subscribes to face recognition results and generates personalized
greetings based on who is recognized, time of day, and the robot's
personality configuration.
"""

from datetime import datetime

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# TODO: Import when scout_interfaces is built
# from scout_interfaces.msg import FaceDetection


class GreetingNode(Node):
    def __init__(self) -> None:
        super().__init__("greeting_node")
        self.declare_parameter("personality", "friendly")
        self.declare_parameter("cooldown_seconds", 300.0)
        self.declare_parameter("greet_unknown", False)

        # TODO: Replace String with FaceDetection
        self.face_sub = self.create_subscription(
            String, "/scout/face_detections", self.on_face, 10
        )
        self.speak_pub = self.create_publisher(String, "/scout/speak", 10)

        self._last_greeted: dict[str, float] = {}
        self._cooldown: float = self.get_parameter("cooldown_seconds").value

        self.get_logger().info(
            f"Greeting node ready. Personality: "
            f"{self.get_parameter('personality').value}"
        )

    def on_face(self, msg: String) -> None:
        # TODO: Parse FaceDetection message
        # TODO: Skip if person_name == "unknown" and greet_unknown is False
        # TODO: Skip if person was greeted within cooldown_seconds
        # TODO: Generate greeting and publish to /scout/speak
        pass

    def _generate_greeting(self, person_name: str) -> str:
        """Generate a personalized greeting.

        Args:
            person_name: Name of the recognized person.

        Returns:
            Greeting text to send to TTS.
        """
        hour = datetime.now().hour
        time_greeting = self._time_of_day_greeting(hour)
        personality: str = self.get_parameter("personality").value

        # TODO: Load per-person preferences from config
        # TODO: Vary greetings based on personality parameter
        # TODO: Include context (e.g., "Welcome home" if front door camera)
        return f"{time_greeting}, {person_name}!"

    @staticmethod
    def _time_of_day_greeting(hour: int) -> str:
        """Pick a greeting based on the current hour.

        Args:
            hour: Current hour (0-23).

        Returns:
            Time-appropriate greeting phrase.
        """
        if hour < 12:
            return "Good morning"
        if hour < 17:
            return "Good afternoon"
        return "Good evening"

    def _check_cooldown(self, person_name: str) -> bool:
        """Check if enough time has passed since last greeting.

        Args:
            person_name: Name to check cooldown for.

        Returns:
            True if greeting is allowed (cooldown expired or first time).
        """
        now = self.get_clock().now().nanoseconds / 1e9
        last = self._last_greeted.get(person_name, 0.0)
        if now - last < self._cooldown:
            return False
        self._last_greeted[person_name] = now
        return True


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = GreetingNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
