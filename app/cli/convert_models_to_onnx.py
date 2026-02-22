"""
CLI script to convert PyTorch models to ONNX format.

Usage:
    python -m app.cli.convert_models_to_onnx --model <model_path> --output <output_path>
    python -m app.cli.convert_models_to_onnx --batch --models-dir <dir>
"""

import argparse
import logging
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.engines.onnx_converter import (
    convert_pytorch_to_onnx,
    get_onnx_model_info,
    optimize_onnx_model,
    quantize_onnx_model,
    validate_onnx_model,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_single_model(
    model_path: str,
    output_path: str,
    input_shape: tuple,
    optimize: bool = True,
    quantize: bool = False,
    device: str = "cpu",
):
    """Convert a single model to ONNX."""
    logger.info(f"Converting model: {model_path}")

    # Convert to ONNX
    success = convert_pytorch_to_onnx(
        model=None,  # Would need actual model instance
        input_shape=input_shape,
        output_path=output_path,
        device=device,
    )

    if not success:
        logger.error("Conversion failed")
        return False

    # Optimize if requested
    if optimize:
        optimized_path = output_path.replace(".onnx", "_optimized.onnx")
        success = optimize_onnx_model(output_path, optimized_path)
        if success:
            output_path = optimized_path

    # Quantize if requested
    if quantize:
        quantized_path = output_path.replace(".onnx", "_quantized.onnx")
        success = quantize_onnx_model(output_path, quantized_path)
        if success:
            output_path = quantized_path

    # Validate
    if validate_onnx_model(output_path):
        logger.info(f"Model successfully converted: {output_path}")

        # Print model info
        info = get_onnx_model_info(output_path)
        if info:
            logger.info(f"Model info: {info}")

        return True

    return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Convert PyTorch models to ONNX format")
    parser.add_argument("--model", type=str, help="Path to PyTorch model file")
    parser.add_argument("--output", type=str, help="Path to output ONNX model")
    parser.add_argument(
        "--input-shape",
        type=str,
        default="1,3,224,224",
        help="Input shape (comma-separated, e.g., '1,3,224,224')",
    )
    parser.add_argument("--optimize", action="store_true", help="Optimize ONNX model")
    parser.add_argument("--quantize", action="store_true", help="Quantize ONNX model")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or cuda)")
    parser.add_argument("--batch", action="store_true", help="Batch convert models")
    parser.add_argument("--models-dir", type=str, help="Directory containing models")

    args = parser.parse_args()

    if args.batch:
        # Batch conversion
        if not args.models_dir:
            logger.error("--models-dir required for batch conversion")
            return

        models_dir = Path(args.models_dir)
        if not models_dir.exists():
            logger.error(f"Models directory not found: {models_dir}")
            return

        # Find all .pth files
        model_files = list(models_dir.rglob("*.pth"))
        logger.info(f"Found {len(model_files)} models to convert")

        for model_file in model_files:
            output_file = model_file.with_suffix(".onnx")
            input_shape = tuple(map(int, args.input_shape.split(",")))

            convert_single_model(
                str(model_file),
                str(output_file),
                input_shape,
                args.optimize,
                args.quantize,
                args.device,
            )

    else:
        # Single model conversion
        if not args.model or not args.output:
            logger.error("--model and --output required for single conversion")
            return

        input_shape = tuple(map(int, args.input_shape.split(",")))

        convert_single_model(
            args.model,
            args.output,
            input_shape,
            args.optimize,
            args.quantize,
            args.device,
        )


if __name__ == "__main__":
    main()
