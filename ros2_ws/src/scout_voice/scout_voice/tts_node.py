"""Text-to-Speech node.

Uses Piper TTS for local speech synthesis.
Subscribes to /scout/speak to generate audio.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TTSNode(Node):
    def __init__(self) -> None:
        super().__init__("tts_node")
        self.declare_parameter("voice", "en_US-amy-medium")
        self.declare_parameter("speed", 1.0)

        self.speak_sub = self.create_subscription(
            String, "/scout/speak", self.on_speak, 10
        )

        voice = self.get_parameter("voice").value
        self.get_logger().info(f"TTS node ready. Voice: {voice}")

    def on_speak(self, msg: String) -> None:
        text = msg.data
        if not text:
            return
        self.get_logger().info(f"Speaking: {text}")
        # TODO: Run Piper TTS inference
        # TODO: Play audio through MAX98357A I2S amplifier


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = TTSNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
