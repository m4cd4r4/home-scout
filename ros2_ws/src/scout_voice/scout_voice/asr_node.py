"""Automatic Speech Recognition node.

Uses whisper.cpp with Qualcomm NPU acceleration for on-device transcription.
Subscribes to /scout/wake_detected to start recording.
Publishes transcription results via the Transcribe action.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String


class ASRNode(Node):
    def __init__(self) -> None:
        super().__init__("asr_node")
        self.declare_parameter("model", "whisper-small-en")
        self.declare_parameter("device", "npu")
        self.declare_parameter("language", "en")
        self.declare_parameter("max_recording_seconds", 10.0)

        self.wake_sub = self.create_subscription(
            Bool, "/scout/wake_detected", self.on_wake, 10
        )
        self.transcript_pub = self.create_publisher(
            String, "/scout/transcript", 10
        )

        model = self.get_parameter("model").value
        device = self.get_parameter("device").value
        self.get_logger().info(f"ASR node ready. Model: {model}, Device: {device}")

    def on_wake(self, msg: Bool) -> None:
        if not msg.data:
            return
        self.get_logger().info("Wake word detected. Recording...")
        # TODO: Record audio from I2S microphone
        # TODO: Run whisper.cpp inference on NPU
        # TODO: Publish transcript
        transcript = ""  # Placeholder
        out = String()
        out.data = transcript
        self.transcript_pub.publish(out)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = ASRNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
