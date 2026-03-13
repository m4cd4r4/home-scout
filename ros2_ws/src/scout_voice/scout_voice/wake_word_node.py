"""Wake word detection node.

Listens for "Hey Scout" using openWakeWord or Porcupine.
Publishes to /scout/wake_detected when the wake phrase is heard.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


class WakeWordNode(Node):
    def __init__(self) -> None:
        super().__init__("wake_word_node")
        self.declare_parameter("wake_phrase", "hey scout")
        self.declare_parameter("sensitivity", 0.5)

        self.publisher = self.create_publisher(Bool, "/scout/wake_detected", 10)
        self.timer = self.create_timer(0.1, self.check_audio)
        self.get_logger().info(
            f"Wake word node ready. Listening for: "
            f"{self.get_parameter('wake_phrase').value}"
        )

    def check_audio(self) -> None:
        # TODO: Integrate openWakeWord or Porcupine
        # This stub will be replaced with actual wake word detection
        # when running on VENTUNO Q hardware with I2S microphone
        pass


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = WakeWordNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
