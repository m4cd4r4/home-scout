"""Camera driver node.

Drives MIPI-CSI cameras on the VENTUNO Q board via V4L2.
Publishes raw image frames to /scout/camera/<name>/image_raw.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class CameraNode(Node):
    def __init__(self) -> None:
        super().__init__("camera_node")
        self.declare_parameter("camera_id", 0)
        self.declare_parameter("name", "front")
        self.declare_parameter("fps", 15)
        self.declare_parameter("width", 640)
        self.declare_parameter("height", 480)

        name = self.get_parameter("name").value
        fps = self.get_parameter("fps").value

        topic = f"/scout/camera/{name}/image_raw"
        self.image_pub = self.create_publisher(Image, topic, 10)

        period = 1.0 / fps
        self.timer = self.create_timer(period, self.capture_frame)

        self.get_logger().info(
            f"Camera node ready. Device: {self.get_parameter('camera_id').value}, "
            f"Topic: {topic}, FPS: {fps}"
        )

    def capture_frame(self) -> None:
        # TODO: Open V4L2 device at /dev/video<camera_id>
        # TODO: Capture frame as raw bytes
        # TODO: Fill sensor_msgs/Image (encoding, step, data)
        # TODO: Publish to /scout/camera/<name>/image_raw
        pass


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = CameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
