"""Base driver node.

Bridge between ROS 2 velocity commands and the STM32H5 motor controller.
Subscribes to /cmd_vel (Twist), sends velocity commands to the MCU over
CAN-FD or SPI, and publishes raw encoder ticks back to ROS.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32MultiArray


class BaseDriverNode(Node):
    def __init__(self) -> None:
        super().__init__("base_driver_node")
        self.declare_parameter("bus_type", "canfd")
        self.declare_parameter("can_interface", "can0")
        self.declare_parameter("spi_device", "/dev/spidev0.0")
        self.declare_parameter("max_linear_speed", 0.3)
        self.declare_parameter("max_angular_speed", 1.0)
        self.declare_parameter("wheel_base", 0.24)
        self.declare_parameter("encoder_ticks_per_rev", 1440)

        self.cmd_vel_sub = self.create_subscription(
            Twist, "/cmd_vel", self.on_cmd_vel, 10
        )
        self.encoder_pub = self.create_publisher(
            Int32MultiArray, "/scout/encoders", 10
        )

        # Read encoder data from MCU at 50 Hz
        self.timer = self.create_timer(0.02, self.read_encoders)

        bus = self.get_parameter("bus_type").value
        self.get_logger().info(f"Base driver ready. Bus: {bus}")

    def on_cmd_vel(self, msg: Twist) -> None:
        linear = msg.linear.x
        angular = msg.angular.z

        # Clamp to safety limits
        max_lin: float = self.get_parameter("max_linear_speed").value
        max_ang: float = self.get_parameter("max_angular_speed").value
        linear = max(-max_lin, min(max_lin, linear))
        angular = max(-max_ang, min(max_ang, angular))

        # TODO: Convert (linear, angular) to left/right wheel velocities
        # TODO: Pack velocity command into CAN-FD frame or SPI packet
        # TODO: Send to STM32H5 MCU
        self.get_logger().debug(
            f"cmd_vel: linear={linear:.2f}, angular={angular:.2f}"
        )

    def read_encoders(self) -> None:
        # TODO: Read encoder ticks from STM32H5 via CAN-FD or SPI
        # TODO: Publish as Int32MultiArray [left_ticks, right_ticks]
        pass


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = BaseDriverNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
