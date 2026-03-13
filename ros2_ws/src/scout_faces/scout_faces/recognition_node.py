"""Face recognition node.

Subscribes to camera images, runs SCRFD face detection followed by
MobileFaceNet embedding extraction, and matches against enrolled faces.
Publishes FaceDetection messages for each recognized or unknown face.
"""

from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

# TODO: Import when scout_interfaces is built
# from scout_interfaces.msg import FaceDetection


@dataclass
class EnrolledFace:
    """An enrolled face record."""

    person_name: str
    embedding: list[float]


class RecognitionNode(Node):
    def __init__(self) -> None:
        super().__init__("recognition_node")
        self.declare_parameter("detection_model", "scrfd_500m")
        self.declare_parameter("embedding_model", "mobilefacenet")
        self.declare_parameter("match_threshold", 0.6)
        self.declare_parameter("rate_hz", 2.0)
        self.declare_parameter("db_path", "/home/scout/data/faces.db")
        self.declare_parameter("encryption_key_path", "/home/scout/keys/face.key")
        self.declare_parameter("camera_topic", "/scout/camera/front/image_raw")

        camera_topic: str = self.get_parameter("camera_topic").value
        self.image_sub = self.create_subscription(
            Image, camera_topic, self.on_image, 10
        )

        # TODO: Replace String with FaceDetection
        self.face_pub = self.create_publisher(
            String, "/scout/face_detections", 10
        )

        self._enrolled_faces: list[EnrolledFace] = []
        self._last_inference_time: float = 0.0
        self._rate_period: float = 1.0 / self.get_parameter("rate_hz").value

        self._load_enrolled_faces()
        self.get_logger().info(
            f"Recognition node ready. {len(self._enrolled_faces)} faces enrolled."
        )

    def _load_enrolled_faces(self) -> None:
        """Load enrolled face embeddings from encrypted database."""
        # TODO: Open faces.db
        # TODO: Load Fernet key from encryption_key_path
        # TODO: Decrypt stored embeddings
        # TODO: Populate self._enrolled_faces
        pass

    def on_image(self, msg: Image) -> None:
        # Rate-limit inference
        now = self.get_clock().now().nanoseconds / 1e9
        if now - self._last_inference_time < self._rate_period:
            return
        self._last_inference_time = now

        # TODO: Run SCRFD face detection on frame
        # TODO: For each detected face:
        #   - Crop and align the face
        #   - Generate MobileFaceNet embedding
        #   - Compare against enrolled faces (cosine similarity)
        #   - If similarity > match_threshold, identify as enrolled person
        #   - Publish FaceDetection message
        pass

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two embedding vectors.

        Args:
            a: First embedding vector.
            b: Second embedding vector.

        Returns:
            Cosine similarity in range [-1, 1].
        """
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = RecognitionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
