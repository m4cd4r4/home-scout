"""SLAM wrapper node.

Configures and launches RTAB-Map for simultaneous localization and mapping.
Bridges the LiDAR, camera, and odometry topics to RTAB-Map's expected inputs
and exposes map save/load services.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SLAMNode(Node):
    def __init__(self) -> None:
        super().__init__("slam_node")
        self.declare_parameter("mode", "mapping")
        self.declare_parameter("map_path", "/home/scout/maps/home.db")
        self.declare_parameter("lidar_topic", "/scout/lidar/scan")
        self.declare_parameter("odom_topic", "/odom")
        self.declare_parameter("camera_topic", "/scout/camera/front/image_raw")
        self.declare_parameter("use_icp", True)
        self.declare_parameter("loop_closure_enabled", True)

        self.status_pub = self.create_publisher(
            String, "/scout/slam_status", 10
        )

        mode = self.get_parameter("mode").value
        map_path = self.get_parameter("map_path").value
        self.get_logger().info(f"SLAM node ready. Mode: {mode}, Map: {map_path}")

        # TODO: Configure RTAB-Map parameters based on declared params
        # TODO: In "mapping" mode, start building a new map
        # TODO: In "localization" mode, load existing map and localize only
        # TODO: Subscribe to lidar, odom, and camera topics
        # TODO: Expose /scout/slam/save_map service
        # TODO: Expose /scout/slam/reset service

    def save_map(self) -> bool:
        """Save the current map to disk."""
        map_path: str = self.get_parameter("map_path").value
        # TODO: Call RTAB-Map's map save functionality
        self.get_logger().info(f"Saving map to: {map_path}")
        return True

    def reset_map(self) -> None:
        """Reset the current map and start fresh."""
        # TODO: Call RTAB-Map's reset functionality
        self.get_logger().info("Map reset requested.")


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = SLAMNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
