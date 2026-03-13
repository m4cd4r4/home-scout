"""Patrol manager node.

Reads patrol routes from YAML config files and sends navigation goals
to Nav2 to execute room-by-room patrols. Publishes PatrolStatus messages
and supports the StartPatrol service and Patrol action.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from std_msgs.msg import String

# TODO: Import when scout_interfaces is built
# from scout_interfaces.srv import StartPatrol
# from scout_interfaces.msg import PatrolStatus
# from scout_interfaces.action import Patrol


class PatrolNode(Node):
    def __init__(self) -> None:
        super().__init__("patrol_node")
        self.declare_parameter("config_file", "patrol_routes.yaml")
        self.declare_parameter("default_speed", 0.2)
        self.declare_parameter("detect_objects", True)

        # TODO: Create StartPatrol service server
        # self.start_patrol_srv = self.create_service(
        #     StartPatrol, "/scout/start_patrol", self.handle_start_patrol
        # )

        # TODO: Create Patrol action server
        # self.patrol_action = ActionServer(
        #     self, Patrol, "/scout/patrol", self.execute_patrol
        # )

        # TODO: Replace String with PatrolStatus
        self.status_pub = self.create_publisher(
            String, "/scout/patrol_status", 10
        )

        self._routes: dict[str, list[dict[str, float]]] = {}
        self._is_patrolling: bool = False
        self._current_room: str = ""

        self._load_routes()
        self.get_logger().info("Patrol node ready.")

    def _load_routes(self) -> None:
        config_file: str = self.get_parameter("config_file").value
        # TODO: Load YAML config with room waypoints
        # Expected format:
        # rooms:
        #   kitchen:
        #     waypoints:
        #       - {x: 1.0, y: 2.0, theta: 0.0}
        #       - {x: 1.5, y: 2.5, theta: 1.57}
        #   living_room:
        #     waypoints:
        #       - {x: 3.0, y: 1.0, theta: 0.0}
        self.get_logger().info(f"Loading routes from: {config_file}")

    def handle_start_patrol(self, request: object, response: object) -> object:
        """Handle StartPatrol service requests."""
        # TODO: Validate rooms exist in config
        # TODO: Start patrol sequence
        # TODO: Set response.accepted and response.message
        return response

    async def execute_patrol(self, goal_handle: object) -> object:
        """Execute a Patrol action."""
        # TODO: Iterate through rooms
        # TODO: For each room, send nav2 goals to waypoints
        # TODO: If detect_objects, trigger VLM scan at each waypoint
        # TODO: Publish feedback with current_room and progress
        # TODO: Return result with rooms_visited and objects_found
        pass


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = PatrolNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
