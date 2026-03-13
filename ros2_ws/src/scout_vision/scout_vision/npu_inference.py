"""NPU inference utility module.

Provides helpers for running models on the Qualcomm Hexagon NPU via
Qualcomm AI Hub or ONNX Runtime with the QNN execution provider.
This is a library module, not a ROS node.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Detection:
    """A single object detection result."""

    label: str
    confidence: float
    bbox_x: float
    bbox_y: float
    bbox_w: float
    bbox_h: float


@dataclass
class InferenceConfig:
    """Configuration for NPU inference sessions."""

    model_path: Path
    provider: str = "QNNExecutionProvider"
    num_threads: int = 4
    input_width: int = 640
    input_height: int = 480
    labels: list[str] = field(default_factory=list)


class NPUInferenceSession:
    """Manages an ONNX Runtime session with Qualcomm QNN backend."""

    def __init__(self, config: InferenceConfig) -> None:
        self.config = config
        self._session = None
        # TODO: Initialize ONNX Runtime session
        # ort.InferenceSession(
        #     str(config.model_path),
        #     providers=[config.provider],
        # )

    def load_model(self) -> None:
        """Load and warm up the model on NPU."""
        # TODO: Create ONNX Runtime InferenceSession with QNN EP
        # TODO: Run a dummy inference pass to warm up the NPU pipeline
        # TODO: Validate input/output tensor shapes
        pass

    def detect(self, frame_rgb: bytes, width: int, height: int) -> list[Detection]:
        """Run object detection on a single frame.

        Args:
            frame_rgb: Raw RGB bytes of the input frame.
            width: Frame width in pixels.
            height: Frame height in pixels.

        Returns:
            List of Detection results above the confidence threshold.
        """
        # TODO: Preprocess frame (resize, normalize, NHWC->NCHW if needed)
        # TODO: Run self._session.run() on NPU
        # TODO: Post-process outputs (NMS, bbox decoding)
        # TODO: Map class indices to labels
        return []

    def generate_description(self, frame_rgb: bytes, width: int, height: int) -> str:
        """Run VLM inference to describe a scene.

        Used with SmolVLM-256M for open-vocabulary object understanding.

        Args:
            frame_rgb: Raw RGB bytes of the input frame.
            width: Frame width in pixels.
            height: Frame height in pixels.

        Returns:
            Natural language description of the scene.
        """
        # TODO: Preprocess frame for VLM input
        # TODO: Run SmolVLM-256M inference
        # TODO: Decode output tokens to text
        return ""

    def cleanup(self) -> None:
        """Release NPU resources."""
        self._session = None
