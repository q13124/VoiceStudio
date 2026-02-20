"""
ONNX Runtime Wrapper for VoiceStudio
Wrapper for ONNX Runtime inference with engine interface

Compatible with:
- ONNX Runtime 1.16+
- ONNX Runtime GPU 1.16+ (for CUDA support)
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Try to import ONNX Runtime
try:
    import onnxruntime as ort
    HAS_ONNXRUNTIME = True
except ImportError:
    HAS_ONNXRUNTIME = False
    ort = None
    logger.warning(
        "ONNX Runtime not installed. "
        "Install with: pip install onnxruntime"
    )


class ONNXInferenceEngine:
    """
    ONNX Runtime inference engine.

    Provides optimized inference for ONNX models with GPU support.
    """

    def __init__(
        self,
        model_path: str,
        device: str = "cuda",
        providers: list[str] | None = None,
    ):
        """
        Initialize ONNX inference engine.

        Args:
            model_path: Path to ONNX model file
            device: Device to use ('cuda' or 'cpu')
            providers: List of execution providers
                (default: ['CUDAExecutionProvider', 'CPUExecutionProvider'])
        """
        if not HAS_ONNXRUNTIME:
            raise ImportError(
                "ONNX Runtime not installed. "
                "Install with: pip install onnxruntime"
            )

        self.model_path = model_path
        self.device = device

        # Set up execution providers
        if providers is None:
            if device == "cuda":
                providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            else:
                providers = ["CPUExecutionProvider"]

        # Create session options
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = (
            ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        )

        # Create inference session
        try:
            self.session = ort.InferenceSession(
                model_path,
                sess_options=sess_options,
                providers=providers,
            )
            logger.info(
                f"ONNX Runtime session created: {model_path} "
                f"(providers: {self.session.get_providers()})"
            )
        except Exception as e:
            logger.error(f"Failed to create ONNX Runtime session: {e}")
            raise

        # Get input/output metadata
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]

        # Get input shapes
        self.input_shapes = {}
        for inp in self.session.get_inputs():
            shape = []
            for dim in inp.shape:
                if isinstance(dim, (int, str)):
                    shape.append(dim)
                else:
                    shape.append(dim)
            self.input_shapes[inp.name] = shape

    def infer(
        self, inputs: dict[str, np.ndarray]
    ) -> dict[str, np.ndarray]:
        """
        Run inference.

        Args:
            inputs: Dictionary mapping input names to numpy arrays

        Returns:
            Dictionary mapping output names to numpy arrays
        """
        try:
            # Prepare inputs
            ort_inputs = {
                name: inputs[name].astype(np.float32)
                if inputs[name].dtype != np.float32
                else inputs[name]
                for name in self.input_names
                if name in inputs
            }

            # Run inference
            outputs = self.session.run(self.output_names, ort_inputs)

            # Convert to dictionary
            result = dict(zip(self.output_names, outputs))

            return result

        except Exception as e:
            logger.error(f"ONNX inference failed: {e}", exc_info=True)
            raise

    def get_input_info(self) -> dict[str, Any]:
        """
        Get input information.

        Returns:
            Dictionary with input information
        """
        info = {}
        for inp in self.session.get_inputs():
            info[inp.name] = {
                "shape": list(inp.shape),
                "type": inp.type,
            }
        return info

    def get_output_info(self) -> dict[str, Any]:
        """
        Get output information.

        Returns:
            Dictionary with output information
        """
        info = {}
        for out in self.session.get_outputs():
            info[out.name] = {
                "shape": list(out.shape),
                "type": out.type,
            }
        return info

    def get_providers(self) -> list[str]:
        """Get available execution providers."""
        return self.session.get_providers()

    def cleanup(self):
        """Clean up resources."""
        try:
            del self.session
            logger.info("ONNX Runtime session cleaned up")
        except Exception as e:
            logger.warning(f"Error during ONNX cleanup: {e}")


def create_onnx_inference_engine(
    model_path: str,
    device: str = "cuda",
    providers: list[str] | None = None,
) -> ONNXInferenceEngine:
    """Factory function to create an ONNX inference engine."""
    return ONNXInferenceEngine(
        model_path=model_path, device=device, providers=providers
    )

