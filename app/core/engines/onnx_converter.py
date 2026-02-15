"""
ONNX Model Converter for VoiceStudio
Convert PyTorch models to ONNX format for optimized inference

Compatible with:
- PyTorch 2.0+
- ONNX 1.15+
- ONNX Runtime 1.16+
"""

from __future__ import annotations

import logging
import os
from typing import Any

import torch

logger = logging.getLogger(__name__)

# Try to import ONNX
try:
    import onnx
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False
    onnx = None
    ort = None
    logger.warning(
        "ONNX not installed. Install with: pip install onnx onnxruntime"
    )


def convert_pytorch_to_onnx(
    model: torch.nn.Module,
    input_shape: tuple[int, ...],
    output_path: str,
    opset_version: int = 17,
    dynamic_axes: dict[str, Any] | None = None,
    device: str = "cpu",
) -> bool:
    """
    Convert PyTorch model to ONNX format.

    Args:
        model: PyTorch model to convert
        input_shape: Input tensor shape (e.g., (1, 3, 224, 224))
        output_path: Path to save ONNX model
        opset_version: ONNX opset version (default 17)
        dynamic_axes: Dictionary for dynamic axes
            Example: {"input": {0: "batch_size"}, "output": {0: "batch_size"}}
        device: Device to use for conversion ('cpu' or 'cuda')

    Returns:
        True if conversion successful, False otherwise
    """
    if not HAS_ONNX:
        logger.error("ONNX not available. Install with: pip install onnx")
        return False

    try:
        # Set model to evaluation mode
        model.eval()

        # Create dummy input
        dummy_input = torch.randn(input_shape).to(device)
        model = model.to(device)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        # Export to ONNX
        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=opset_version,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes=dynamic_axes,
            verbose=False,
        )

        logger.info(f"Model converted to ONNX: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to convert model to ONNX: {e}", exc_info=True)
        return False


def optimize_onnx_model(
    input_path: str,
    output_path: str,
    optimization_level: str = "all",
) -> bool:
    """
    Optimize ONNX model.

    Args:
        input_path: Path to input ONNX model
        output_path: Path to save optimized model
        optimization_level: Optimization level
            - "basic": Basic optimizations
            - "extended": Extended optimizations
            - "all": All optimizations (default)

    Returns:
        True if optimization successful, False otherwise
    """
    if not HAS_ONNX:
        logger.error("ONNX not available")
        return False

    try:
        # Load model
        model = onnx.load(input_path)

        # Optimize model
        if optimization_level == "all":
            # Use ONNX Runtime optimizations
            try:
                from onnxruntime.transformers import optimizer

                optimized_model = optimizer.optimize_model(
                    input_path,
                    model_type="bert",  # Generic optimization
                    num_heads=0,
                    hidden_size=0,
                )
                optimized_model.save_model_to_file(output_path)
                logger.info(f"Model optimized: {output_path}")
                return True
            except ImportError:
                logger.warning(
                    "ONNX Runtime transformers not available. "
                    "Using basic optimization."
                )
                # Fallback to basic optimization
                optimized_model = onnx.optimizer.optimize(model)
                onnx.save(optimized_model, output_path)
                logger.info(f"Model optimized (basic): {output_path}")
                return True
        else:
            # Basic optimization
            optimized_model = onnx.optimizer.optimize(model)
            onnx.save(optimized_model, output_path)
            logger.info(f"Model optimized: {output_path}")
            return True

    except Exception as e:
        logger.error(f"Failed to optimize ONNX model: {e}", exc_info=True)
        return False


def validate_onnx_model(model_path: str) -> bool:
    """
    Validate ONNX model.

    Args:
        model_path: Path to ONNX model

    Returns:
        True if model is valid, False otherwise
    """
    if not HAS_ONNX:
        logger.error("ONNX not available")
        return False

    try:
        model = onnx.load(model_path)
        onnx.checker.check_model(model)
        logger.info(f"ONNX model is valid: {model_path}")
        return True
    except Exception as e:
        logger.error(f"ONNX model validation failed: {e}")
        return False


def get_onnx_model_info(model_path: str) -> dict[str, Any] | None:
    """
    Get information about ONNX model.

    Args:
        model_path: Path to ONNX model

    Returns:
        Dictionary with model information or None if failed
    """
    if not HAS_ONNX:
        return None

    try:
        model = onnx.load(model_path)

        info = {
            "ir_version": model.ir_version,
            "opset_import": [
                {"domain": op.domain, "version": op.version}
                for op in model.opset_import
            ],
            "producer_name": model.producer_name,
            "producer_version": model.producer_version,
            "inputs": [
                {
                    "name": inp.name,
                    "type": str(inp.type),
                    "shape": [
                        dim.dim_value if dim.dim_value > 0 else "dynamic"
                        for dim in inp.type.tensor_type.shape.dim
                    ],
                }
                for inp in model.graph.input
            ],
            "outputs": [
                {
                    "name": out.name,
                    "type": str(out.type),
                    "shape": [
                        dim.dim_value if dim.dim_value > 0 else "dynamic"
                        for dim in out.type.tensor_type.shape.dim
                    ],
                }
                for out in model.graph.output
            ],
        }

        return info

    except Exception as e:
        logger.error(f"Failed to get ONNX model info: {e}")
        return None


def quantize_onnx_model(
    input_path: str,
    output_path: str,
    quantization_type: str = "int8",
) -> bool:
    """
    Quantize ONNX model.

    Args:
        input_path: Path to input ONNX model
        output_path: Path to save quantized model
        quantization_type: Type of quantization ('int8', 'uint8', 'float16')

    Returns:
        True if quantization successful, False otherwise
    """
    if not HAS_ONNX or ort is None:
        logger.error("ONNX Runtime not available for quantization")
        return False

    try:
        from onnxruntime.quantization import QuantType, quantize_dynamic

        # Map quantization type
        quant_type_map = {
            "int8": QuantType.QUInt8,
            "uint8": QuantType.QUInt8,
            "float16": QuantType.QFloat16,
        }

        quant_type = quant_type_map.get(quantization_type.lower(), QuantType.QUInt8)

        # Quantize model
        quantize_dynamic(
            input_path,
            output_path,
            weight_type=quant_type,
        )

        logger.info(f"Model quantized: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to quantize ONNX model: {e}", exc_info=True)
        return False

