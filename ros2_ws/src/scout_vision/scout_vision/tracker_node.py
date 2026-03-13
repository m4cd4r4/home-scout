"""Multi-object tracker node.

Subscribes to object detections and maintains persistent object IDs across
frames using a simple IoU-based tracker. Publishes tracked sightings with
stable IDs to help downstream nodes distinguish re-detections from new objects.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TrackedObject:
    """State for a single tracked object."""

    def __init__(self, track_id: int, object_name: str, x: float, y: float) -> None:
        self.track_id = track_id
        self.object_name = object_name
        self.x = x
        self.y = y
        self.frames_since_seen: int = 0
        self.total_sightings: int = 1


class TrackerNode(Node):
    def __init__(self) -> None:
        super().__init__("tracker_node")
        self.declare_parameter("max_lost_frames", 30)
        self.declare_parameter("iou_threshold", 0.3)

        # TODO: Replace String with ObjectSighting once interfaces are built
        self.detection_sub = self.create_subscription(
            String, "/scout/object_sightings", self.on_detection, 10
        )
        self.tracked_pub = self.create_publisher(
            String, "/scout/tracked_objects", 10
        )

        self._tracks: dict[int, TrackedObject] = {}
        self._next_id: int = 0
        self._max_lost: int = self.get_parameter("max_lost_frames").value

        self.get_logger().info(
            f"Tracker node ready. Max lost frames: {self._max_lost}"
        )

    def on_detection(self, msg: String) -> None:
        # TODO: Parse incoming ObjectSighting detections
        # TODO: Match detections to existing tracks (IoU or distance)
        # TODO: Create new tracks for unmatched detections
        # TODO: Increment frames_since_seen for unmatched tracks
        # TODO: Prune tracks exceeding max_lost_frames
        # TODO: Publish tracked sightings with stable track IDs
        pass

    def _assign_id(self) -> int:
        track_id = self._next_id
        self._next_id += 1
        return track_id

    def _prune_lost_tracks(self) -> None:
        lost = [
            tid for tid, t in self._tracks.items()
            if t.frames_since_seen > self._max_lost
        ]
        for tid in lost:
            self.get_logger().debug(f"Pruning lost track {tid}")
            del self._tracks[tid]


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = TrackerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
