"""Face enrollment node.

Consent-first face enrollment. When a user requests enrollment via the
EnrollFace service, captures multiple face samples from the camera,
generates ArcFace embeddings, encrypts them, and stores locally.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

# TODO: Import when scout_interfaces is built
# from scout_interfaces.srv import EnrollFace
# from scout_interfaces.msg import FaceDetection


class EnrollmentNode(Node):
    def __init__(self) -> None:
        super().__init__("enrollment_node")
        self.declare_parameter("min_samples", 5)
        self.declare_parameter("embedding_model", "mobilefacenet")
        self.declare_parameter("db_path", "/home/scout/data/faces.db")
        self.declare_parameter("encryption_key_path", "/home/scout/keys/face.key")
        self.declare_parameter("camera_topic", "/scout/camera/front/image_raw")

        camera_topic: str = self.get_parameter("camera_topic").value
        self.image_sub = self.create_subscription(
            Image, camera_topic, self.on_image, 10
        )

        # TODO: Create EnrollFace service server
        # self.enroll_srv = self.create_service(
        #     EnrollFace, "/scout/enroll_face", self.handle_enroll
        # )

        self._enrolling: bool = False
        self._enroll_name: str = ""
        self._samples: list[bytes] = []

        self.get_logger().info("Enrollment node ready.")

    def on_image(self, msg: Image) -> None:
        if not self._enrolling:
            return

        # TODO: Detect face in frame using SCRFD
        # TODO: Crop and align face region
        # TODO: Check face quality (blur, lighting, angle)
        # TODO: If quality passes, add to samples list
        # TODO: Log progress: "Captured sample N of min_samples"
        pass

    def handle_enroll(self, request: object, response: object) -> object:
        """Handle EnrollFace service requests."""
        # TODO: Verify request.consent_given is True
        # TODO: Start sample collection (set self._enrolling = True)
        # TODO: Wait for min_samples good captures
        # TODO: Generate ArcFace/MobileFaceNet embedding per sample
        # TODO: Average embeddings for robustness
        # TODO: Encrypt embedding with Fernet (from encryption_key_path)
        # TODO: Store in faces.db with person_name
        # TODO: Set response.success, response.message, response.num_samples
        return response

    def _generate_embedding(self, face_crop: bytes) -> list[float]:
        """Generate a 128-d face embedding from a cropped face image.

        Args:
            face_crop: Raw RGB bytes of the aligned face crop.

        Returns:
            128-dimensional embedding vector.
        """
        # TODO: Preprocess face crop (resize to 112x112, normalize)
        # TODO: Run MobileFaceNet inference on NPU
        # TODO: L2-normalize the output embedding
        return [0.0] * 128


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = EnrollmentNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
