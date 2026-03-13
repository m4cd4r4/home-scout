"""Odometry node.

Computes robot odometry by fusing wheel encoder ticks with IMU data.
Publishes nav_msgs/Odometry to /odom and broadcasts the odom -> base_link
TF transform.
"""

import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import Int32MultiArray

# TODO: from tf2_ros import TransformBroadcaster


class OdometryNode(Node):
    def __init__(self) -> None:
        super().__init__("odometry_node")
        self.declare_parameter("wheel_radius", 0.033)
        self.declare_parameter("wheel_base", 0.24)
        self.declare_parameter("ticks_per_rev", 1440)
        self.declare_parameter("publish_tf", True)

        self.encoder_sub = self.create_subscription(
            Int32MultiArray, "/scout/encoders", self.on_encoders, 10
        )
        self.odom_pub = self.create_publisher(Odometry, "/odom", 10)

        # TODO: self.tf_broadcaster = TransformBroadcaster(self)

        # Odometry state
        self._x: float = 0.0
        self._y: float = 0.0
        self._theta: float = 0.0
        self._prev_left: int | None = None
        self._prev_right: int | None = None

        self.get_logger().info("Odometry node ready.")

    def on_encoders(self, msg: Int32MultiArray) -> None:
        if len(msg.data) < 2:
            return

        left_ticks = msg.data[0]
        right_ticks = msg.data[1]

        if self._prev_left is None:
            self._prev_left = left_ticks
            self._prev_right = right_ticks
            return

        # Compute deltas
        dl = left_ticks - self._prev_left
        dr = right_ticks - self._prev_right
        self._prev_left = left_ticks
        self._prev_right = right_ticks

        # TODO: Convert tick deltas to distance using wheel_radius and ticks_per_rev
        # TODO: Compute differential drive kinematics (dx, dy, dtheta)
        # TODO: Update self._x, self._y, self._theta
        # TODO: Fill and publish Odometry message
        # TODO: Broadcast odom -> base_link transform
        _ = dl, dr  # Suppress unused warnings until implemented

    def _ticks_to_meters(self, ticks: int) -> float:
        radius: float = self.get_parameter("wheel_radius").value
        tpr: int = self.get_parameter("ticks_per_rev").value
        return (ticks / tpr) * 2.0 * math.pi * radius


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = OdometryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
