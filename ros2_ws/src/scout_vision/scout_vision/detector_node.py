"""Object detector node.

Subscribes to camera images, runs SmolVLM-256M on the Qualcomm Hexagon NPU,
and publishes ObjectSighting messages for each detected object.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Header

# TODO: Import when scout_interfaces is built
# from scout_interfaces.msg import ObjectSighting


class DetectorNode(Node):
    def __init__(self) -> None:
        super().__init__("detector_node")
        self.declare_parameter("model", "smolvlm-256m")
        self.declare_parameter("confidence_threshold", 0.4)
        self.declare_parameter("rate_hz", 2.0)
        self.declare_parameter("camera_topic", "/scout/camera/front/image_raw")

        camera_topic: str = self.get_parameter("camera_topic").value
        self.image_sub = self.create_subscription(
            Image, camera_topic, self.on_image, 10
        )

        # TODO: Replace String with ObjectSighting once interfaces are built
        from std_msgs.msg import String

        self.sighting_pub = self.create_publisher(
            String, "/scout/object_sightings", 10
        )

        self._last_inference_time = 0.0
        self._rate_period = 1.0 / self.get_parameter("rate_hz").value

        model = self.get_parameter("model").value
        threshold = self.get_parameter("confidence_threshold").value
        self.get_logger().info(
            f"Detector node ready. Model: {model}, "
            f"Threshold: {threshold}, Camera: {camera_topic}"
        )

    def on_image(self, msg: Image) -> None:
        # Rate-limit inference to rate_hz
        now = self.get_clock().now().nanoseconds / 1e9
        if now - self._last_inference_time < self._rate_period:
            return
        self._last_inference_time = now

        # TODO: Convert sensor_msgs/Image to numpy array
        # TODO: Run NPU inference via npu_inference module
        # TODO: Filter detections below confidence_threshold
        # TODO: Publish ObjectSighting for each detection
        self.get_logger().debug("Frame received, inference pending.")


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = DetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
