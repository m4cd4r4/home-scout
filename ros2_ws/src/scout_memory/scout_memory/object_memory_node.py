"""Object memory node.

Central memory store for all object sightings. Subscribes to ObjectSighting
messages, persists them in SQLite with FTS5 search, and serves WhereIs
queries from the conversation node.
"""

import sqlite3
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# TODO: Import when scout_interfaces is built
# from scout_interfaces.msg import ObjectSighting
# from scout_interfaces.srv import WhereIs


class ObjectMemoryNode(Node):
    def __init__(self) -> None:
        super().__init__("object_memory_node")
        self.declare_parameter("db_path", "/home/scout/data/memory.db")
        self.declare_parameter("decay_check_interval", 60.0)
        self.declare_parameter("default_ttl_hours", 24.0)

        db_path = Path(self.get_parameter("db_path").value)
        self._db = self._init_db(db_path)

        # TODO: Replace String with ObjectSighting
        self.sighting_sub = self.create_subscription(
            String, "/scout/object_sightings", self.on_sighting, 10
        )

        # TODO: Create WhereIs service server
        # self.where_is_srv = self.create_service(
        #     WhereIs, "/scout/where_is", self.handle_where_is
        # )

        # Periodic confidence decay
        decay_interval: float = self.get_parameter("decay_check_interval").value
        self.decay_timer = self.create_timer(decay_interval, self.run_decay)

        self.get_logger().info(f"Object memory node ready. DB: {db_path}")

    def _init_db(self, db_path: Path) -> sqlite3.Connection:
        """Initialize SQLite database with schema."""
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        schema_sql = Path(__file__).parent.parent / "db" / "schema.sql"
        if schema_sql.exists():
            conn.executescript(schema_sql.read_text())

        return conn

    def on_sighting(self, msg: String) -> None:
        # TODO: Parse ObjectSighting message
        # TODO: Resolve aliases via object_aliases table
        # TODO: Assign room/zone via spatial_index module
        # TODO: Insert into object_sightings table
        # TODO: Update FTS5 index
        self.get_logger().debug("Sighting received.")

    def handle_where_is(self, request: object, response: object) -> object:
        """Handle WhereIs service requests."""
        # TODO: Query object_sightings for most recent match
        # TODO: Apply confidence decay to result
        # TODO: Generate human-readable description
        # TODO: Fill response fields (found, room, zone, description, etc.)
        return response

    def run_decay(self) -> None:
        """Apply time-based confidence decay to stale sightings."""
        # TODO: Call confidence_decay module to update scores
        # TODO: Expire sightings past their TTL
        pass

    def destroy_node(self) -> None:
        if self._db:
            self._db.close()
        super().destroy_node()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = ObjectMemoryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
