#!/usr/bin/env python3
"""
VoiceStudio GPU Compatibility Test Script

Tests GPU compatibility for VoiceStudio with focus on:
- PyTorch 2.2.2+cu121 compatibility
- CUDA availability and version
- Memory allocation and tensor operations
- Engine inference performance benchmarks

Usage:
    python scripts/test_gpu_compatibility.py
    python scripts/test_gpu_compatibility.py --benchmark
    python scripts/test_gpu_compatibility.py --full-report
"""

import argparse
import json
import logging
import platform
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class GPUInfo:
    """GPU hardware and driver information."""
    name: str = "Unknown"
    driver_version: str = "Unknown"
    cuda_version: str = "Unknown"
    compute_capability: tuple[int, int] = (0, 0)
    memory_total_gb: float = 0.0
    memory_free_gb: float = 0.0
    architecture: str = "Unknown"


@dataclass
class CompatibilityResult:
    """Result of a compatibility check."""
    check_name: str
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark."""
    test_name: str
    duration_ms: float
    memory_used_mb: float
    throughput: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class GPUCompatibilityReport:
    """Complete GPU compatibility report."""
    timestamp: str
    system_info: dict[str, str]
    gpu_info: GPUInfo
    pytorch_info: dict[str, str]
    compatibility_checks: list[CompatibilityResult]
    benchmarks: list[BenchmarkResult]
    overall_status: str
    recommendations: list[str]


def get_system_info() -> dict[str, str]:
    """Gather system information."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": sys.version,
        "architecture": platform.machine(),
        "processor": platform.processor(),
    }


def get_gpu_info() -> GPUInfo:
    """Gather GPU information using PyTorch and nvidia-smi."""
    info = GPUInfo()

    try:
        import torch

        if torch.cuda.is_available():
            info.name = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            info.compute_capability = (props.major, props.minor)
            info.memory_total_gb = props.total_memory / (1024**3)
            info.memory_free_gb = (
                props.total_memory - torch.cuda.memory_allocated(0)
            ) / (1024**3)

            # Determine architecture from compute capability
            cc = props.major * 10 + props.minor
            if cc >= 90:
                info.architecture = "Hopper/Blackwell"
            elif cc >= 89:
                info.architecture = "Ada Lovelace"
            elif cc >= 80:
                info.architecture = "Ampere"
            elif cc >= 75:
                info.architecture = "Turing"
            elif cc >= 70:
                info.architecture = "Volta"
            else:
                info.architecture = f"Compute Capability {props.major}.{props.minor}"

            info.cuda_version = torch.version.cuda or "Unknown"
    except ImportError:
        logger.warning("PyTorch not available")
    except Exception as e:
        logger.warning(f"Error getting GPU info: {e}")

    # Try nvidia-smi for driver version
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            info.driver_version = result.stdout.strip()
    except Exception:
        pass  # ALLOWED: bare except - nvidia-smi may not be available

    return info


def get_pytorch_info() -> dict[str, str]:
    """Get PyTorch version and configuration."""
    info = {
        "version": "Not installed",
        "cuda_available": "False",
        "cuda_version": "N/A",
        "cudnn_version": "N/A",
        "torchaudio_version": "Not installed",
    }

    try:
        import torch
        info["version"] = torch.__version__
        info["cuda_available"] = str(torch.cuda.is_available())
        info["cuda_version"] = torch.version.cuda or "N/A"
        if torch.backends.cudnn.is_available():
            info["cudnn_version"] = str(torch.backends.cudnn.version())
    except ImportError:
        pass  # ALLOWED: bare except - torch optional for compatibility check

    try:
        import torchaudio
        info["torchaudio_version"] = torchaudio.__version__
    except ImportError:
        pass  # ALLOWED: bare except - torchaudio optional for compatibility check

    return info


def check_cuda_availability() -> CompatibilityResult:
    """Check if CUDA is available and functional."""
    try:
        import torch

        if not torch.cuda.is_available():
            return CompatibilityResult(
                check_name="CUDA Availability",
                passed=False,
                message="CUDA is not available. GPU acceleration will not work.",
                details={"torch_cuda_available": False}
            )

        # Try to allocate a tensor on GPU
        device = torch.device("cuda:0")
        test_tensor = torch.zeros(1, device=device)
        del test_tensor
        torch.cuda.empty_cache()

        return CompatibilityResult(
            check_name="CUDA Availability",
            passed=True,
            message="CUDA is available and functional.",
            details={
                "torch_cuda_available": True,
                "device_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
            }
        )
    except Exception as e:
        return CompatibilityResult(
            check_name="CUDA Availability",
            passed=False,
            message=f"CUDA check failed: {e}",
            details={"error": str(e)}
        )


def check_pytorch_cuda_version() -> CompatibilityResult:
    """Check if PyTorch CUDA version matches expected."""
    expected_cuda = "12.1"
    expected_torch = "2.2.2"

    try:
        import torch

        cuda_version = torch.version.cuda or "Unknown"
        torch_version = torch.__version__

        # Parse versions
        cuda_major_minor = ".".join(cuda_version.split(".")[:2])
        torch_base = torch_version.split("+")[0]

        issues = []
        if cuda_major_minor != expected_cuda:
            issues.append(
                f"CUDA version mismatch: expected {expected_cuda}, got {cuda_major_minor}"
            )
        if not torch_base.startswith(expected_torch):
            issues.append(
                f"PyTorch version mismatch: expected {expected_torch}, got {torch_base}"
            )

        if issues:
            return CompatibilityResult(
                check_name="PyTorch/CUDA Version",
                passed=False,
                message="; ".join(issues),
                details={
                    "expected_cuda": expected_cuda,
                    "actual_cuda": cuda_version,
                    "expected_torch": expected_torch,
                    "actual_torch": torch_version,
                }
            )

        return CompatibilityResult(
            check_name="PyTorch/CUDA Version",
            passed=True,
            message=f"PyTorch {torch_version} with CUDA {cuda_version} matches expected stack.",
            details={
                "cuda_version": cuda_version,
                "torch_version": torch_version,
            }
        )
    except ImportError:
        return CompatibilityResult(
            check_name="PyTorch/CUDA Version",
            passed=False,
            message="PyTorch not installed",
            details={}
        )


def check_compute_capability() -> CompatibilityResult:
    """Check if GPU compute capability is supported."""
    min_cc = (6, 0)  # Minimum for PyTorch 2.x
    recommended_cc = (7, 5)  # Turing and above

    try:
        import torch

        if not torch.cuda.is_available():
            return CompatibilityResult(
                check_name="Compute Capability",
                passed=False,
                message="CUDA not available",
                details={}
            )

        props = torch.cuda.get_device_properties(0)
        cc = (props.major, props.minor)

        if cc < min_cc:
            return CompatibilityResult(
                check_name="Compute Capability",
                passed=False,
                message=f"GPU compute capability {cc[0]}.{cc[1]} is below minimum {min_cc[0]}.{min_cc[1]}",
                details={"compute_capability": f"{cc[0]}.{cc[1]}"}
            )

        if cc >= recommended_cc:
            return CompatibilityResult(
                check_name="Compute Capability",
                passed=True,
                message=f"GPU compute capability {cc[0]}.{cc[1]} is optimal.",
                details={"compute_capability": f"{cc[0]}.{cc[1]}", "optimal": True}
            )

        return CompatibilityResult(
            check_name="Compute Capability",
            passed=True,
            message=f"GPU compute capability {cc[0]}.{cc[1]} is supported but not optimal.",
            details={"compute_capability": f"{cc[0]}.{cc[1]}", "optimal": False}
        )
    except Exception as e:
        return CompatibilityResult(
            check_name="Compute Capability",
            passed=False,
            message=f"Failed to check compute capability: {e}",
            details={"error": str(e)}
        )


def check_memory_allocation() -> CompatibilityResult:
    """Test GPU memory allocation."""
    try:
        import torch

        if not torch.cuda.is_available():
            return CompatibilityResult(
                check_name="Memory Allocation",
                passed=False,
                message="CUDA not available",
                details={}
            )

        # Try allocating progressively larger tensors
        test_sizes_mb = [100, 500, 1000, 2000]
        max_allocated = 0

        for size_mb in test_sizes_mb:
            try:
                # Allocate tensor of specified size
                num_elements = (size_mb * 1024 * 1024) // 4  # 4 bytes per float32
                tensor = torch.zeros(num_elements, dtype=torch.float32, device="cuda:0")
                max_allocated = size_mb
                del tensor
                torch.cuda.empty_cache()
            except RuntimeError:
                break

        if max_allocated >= 1000:
            return CompatibilityResult(
                check_name="Memory Allocation",
                passed=True,
                message=f"Successfully allocated up to {max_allocated}MB on GPU.",
                details={"max_allocated_mb": max_allocated}
            )
        elif max_allocated > 0:
            return CompatibilityResult(
                check_name="Memory Allocation",
                passed=True,
                message=f"Limited GPU memory: allocated up to {max_allocated}MB.",
                details={"max_allocated_mb": max_allocated, "warning": "Limited VRAM"}
            )
        else:
            return CompatibilityResult(
                check_name="Memory Allocation",
                passed=False,
                message="Failed to allocate GPU memory.",
                details={}
            )
    except Exception as e:
        return CompatibilityResult(
            check_name="Memory Allocation",
            passed=False,
            message=f"Memory allocation test failed: {e}",
            details={"error": str(e)}
        )


def check_cudnn() -> CompatibilityResult:
    """Check cuDNN availability and version."""
    try:
        import torch

        if not torch.backends.cudnn.is_available():
            return CompatibilityResult(
                check_name="cuDNN",
                passed=False,
                message="cuDNN is not available. Some operations may be slower.",
                details={}
            )

        cudnn_version = torch.backends.cudnn.version()
        return CompatibilityResult(
            check_name="cuDNN",
            passed=True,
            message=f"cuDNN version {cudnn_version} is available.",
            details={"cudnn_version": cudnn_version}
        )
    except Exception as e:
        return CompatibilityResult(
            check_name="cuDNN",
            passed=False,
            message=f"cuDNN check failed: {e}",
            details={"error": str(e)}
        )


def benchmark_tensor_ops() -> BenchmarkResult:
    """Benchmark basic tensor operations."""
    try:
        import torch

        if not torch.cuda.is_available():
            return BenchmarkResult(
                test_name="Tensor Operations",
                duration_ms=0,
                memory_used_mb=0,
                details={"error": "CUDA not available"}
            )

        torch.cuda.synchronize()

        # Create large tensors
        size = (4096, 4096)
        a = torch.randn(size, device="cuda:0")
        b = torch.randn(size, device="cuda:0")

        # Warm up
        _ = torch.matmul(a, b)
        torch.cuda.synchronize()

        # Benchmark
        start = time.perf_counter()
        for _ in range(10):
            c = torch.matmul(a, b)
        torch.cuda.synchronize()
        end = time.perf_counter()

        duration_ms = (end - start) * 1000
        memory_mb = torch.cuda.max_memory_allocated() / (1024**2)

        # Clean up
        del a, b, c
        torch.cuda.empty_cache()

        # Calculate TFLOPS
        flops_per_matmul = 2 * size[0] * size[1] * size[0]
        total_flops = flops_per_matmul * 10
        tflops = total_flops / (duration_ms / 1000) / 1e12

        return BenchmarkResult(
            test_name="Tensor Operations (4096x4096 matmul x10)",
            duration_ms=duration_ms,
            memory_used_mb=memory_mb,
            throughput=tflops,
            details={"matrix_size": size, "iterations": 10, "tflops": round(tflops, 2)}
        )
    except Exception as e:
        return BenchmarkResult(
            test_name="Tensor Operations",
            duration_ms=0,
            memory_used_mb=0,
            details={"error": str(e)}
        )


def benchmark_audio_inference() -> BenchmarkResult:
    """Benchmark audio model inference simulation."""
    try:
        import torch
        import torch.nn as nn

        if not torch.cuda.is_available():
            return BenchmarkResult(
                test_name="Audio Inference",
                duration_ms=0,
                memory_used_mb=0,
                details={"error": "CUDA not available"}
            )

        # Simulate audio encoder-decoder
        class SimpleAudioModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Conv1d(1, 64, 7, padding=3),
                    nn.ReLU(),
                    nn.Conv1d(64, 128, 5, padding=2),
                    nn.ReLU(),
                    nn.Conv1d(128, 256, 3, padding=1),
                )
                self.decoder = nn.Sequential(
                    nn.ConvTranspose1d(256, 128, 3, padding=1),
                    nn.ReLU(),
                    nn.ConvTranspose1d(128, 64, 5, padding=2),
                    nn.ReLU(),
                    nn.ConvTranspose1d(64, 1, 7, padding=3),
                )

            def forward(self, x):
                return self.decoder(self.encoder(x))

        model = SimpleAudioModel().cuda().eval()

        # 10 seconds of audio at 22050 Hz
        audio = torch.randn(1, 1, 22050 * 10, device="cuda:0")

        # Warm up
        with torch.no_grad():
            _ = model(audio)
        torch.cuda.synchronize()

        # Benchmark
        start = time.perf_counter()
        with torch.no_grad():
            for _ in range(10):
                _ = model(audio)
        torch.cuda.synchronize()
        end = time.perf_counter()

        duration_ms = (end - start) * 1000
        memory_mb = torch.cuda.max_memory_allocated() / (1024**2)

        # Real-time factor (lower is better, <1.0 means faster than real-time)
        audio_duration_s = 10  # 10 seconds
        processing_time_s = duration_ms / 1000 / 10  # per sample
        rtf = processing_time_s / audio_duration_s

        del model, audio
        torch.cuda.empty_cache()

        return BenchmarkResult(
            test_name="Audio Inference (10s audio x10 iterations)",
            duration_ms=duration_ms,
            memory_used_mb=memory_mb,
            throughput=1.0 / rtf if rtf > 0 else 0,
            details={"real_time_factor": round(rtf, 4), "iterations": 10}
        )
    except Exception as e:
        return BenchmarkResult(
            test_name="Audio Inference",
            duration_ms=0,
            memory_used_mb=0,
            details={"error": str(e)}
        )


def generate_recommendations(
    gpu_info: GPUInfo,
    checks: list[CompatibilityResult],
    benchmarks: list[BenchmarkResult]
) -> list[str]:
    """Generate recommendations based on test results."""
    recommendations = []

    # Check for failed compatibility checks
    failed_checks = [c for c in checks if not c.passed]
    if failed_checks:
        for check in failed_checks:
            if "CUDA" in check.check_name:
                recommendations.append(
                    "Install NVIDIA drivers and CUDA toolkit. "
                    "See: https://developer.nvidia.com/cuda-downloads"
                )
            elif "Version" in check.check_name:
                recommendations.append(
                    "Reinstall PyTorch with correct CUDA version: "
                    "pip install torch==2.2.2+cu121 --index-url https://download.pytorch.org/whl/cu121"
                )

    # Check GPU architecture
    if gpu_info.compute_capability >= (9, 0):
        recommendations.append(
            "Newer GPU detected (Hopper/Blackwell). Consider upgrading to "
            "PyTorch 2.4+ with CUDA 12.4 for optimal performance. "
            "Current stack (2.2.2+cu121) may still work but isn't optimal."
        )

    # Check memory
    if gpu_info.memory_total_gb < 4:
        recommendations.append(
            "Limited GPU memory detected (<4GB). Some models may require CPU fallback. "
            "Consider using smaller model variants or enabling gradient checkpointing."
        )
    elif gpu_info.memory_total_gb < 8:
        recommendations.append(
            "GPU memory is moderate (4-8GB). Larger models like XTTS may require "
            "memory optimization. Enable half-precision (fp16) inference when possible."
        )

    # Check benchmark performance
    for bench in benchmarks:
        if "Tensor" in bench.test_name and bench.throughput > 0 and bench.throughput < 5:
            recommendations.append(
                "GPU compute performance is below expected. Check for thermal throttling "
                "or driver issues. Expected >10 TFLOPS for modern GPUs."
            )
        if "Audio" in bench.test_name and bench.details.get("real_time_factor", 1) > 0.5:
            recommendations.append(
                "Audio inference is not meeting real-time targets. Consider enabling "
                "TorchScript optimization or using smaller model variants."
            )

    if not recommendations:
        recommendations.append("GPU configuration is optimal for VoiceStudio.")

    return recommendations


def run_compatibility_tests(run_benchmarks: bool = False) -> GPUCompatibilityReport:
    """Run all compatibility tests and generate report."""
    timestamp = datetime.now().isoformat()

    # Gather information
    system_info = get_system_info()
    gpu_info = get_gpu_info()
    pytorch_info = get_pytorch_info()

    # Run compatibility checks
    checks = [
        check_cuda_availability(),
        check_pytorch_cuda_version(),
        check_compute_capability(),
        check_memory_allocation(),
        check_cudnn(),
    ]

    # Run benchmarks if requested
    benchmarks = []
    if run_benchmarks:
        benchmarks = [
            benchmark_tensor_ops(),
            benchmark_audio_inference(),
        ]

    # Determine overall status
    failed_critical = any(
        not c.passed and c.check_name in ["CUDA Availability", "PyTorch/CUDA Version"]
        for c in checks
    )
    if failed_critical:
        overall_status = "FAIL"
    elif any(not c.passed for c in checks):
        overall_status = "PARTIAL"
    else:
        overall_status = "PASS"

    # Generate recommendations
    recommendations = generate_recommendations(gpu_info, checks, benchmarks)

    return GPUCompatibilityReport(
        timestamp=timestamp,
        system_info=system_info,
        gpu_info=gpu_info,
        pytorch_info=pytorch_info,
        compatibility_checks=checks,
        benchmarks=benchmarks,
        overall_status=overall_status,
        recommendations=recommendations,
    )


def print_report(report: GPUCompatibilityReport) -> None:
    """Print report to console."""
    print("\n" + "=" * 60)
    print("VoiceStudio GPU Compatibility Report")
    print("=" * 60)
    print(f"Timestamp: {report.timestamp}")
    print(f"Overall Status: {report.overall_status}")

    print("\n--- System Information ---")
    for key, value in report.system_info.items():
        print(f"  {key}: {value}")

    print("\n--- GPU Information ---")
    print(f"  Name: {report.gpu_info.name}")
    print(f"  Architecture: {report.gpu_info.architecture}")
    print(f"  Compute Capability: {report.gpu_info.compute_capability[0]}.{report.gpu_info.compute_capability[1]}")
    print(f"  Memory: {report.gpu_info.memory_total_gb:.2f} GB total, {report.gpu_info.memory_free_gb:.2f} GB free")
    print(f"  CUDA Version: {report.gpu_info.cuda_version}")
    print(f"  Driver Version: {report.gpu_info.driver_version}")

    print("\n--- PyTorch Information ---")
    for key, value in report.pytorch_info.items():
        print(f"  {key}: {value}")

    print("\n--- Compatibility Checks ---")
    for check in report.compatibility_checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"  [{status}] {check.check_name}: {check.message}")

    if report.benchmarks:
        print("\n--- Benchmarks ---")
        for bench in report.benchmarks:
            print(f"  {bench.test_name}")
            print(f"    Duration: {bench.duration_ms:.2f} ms")
            print(f"    Memory: {bench.memory_used_mb:.2f} MB")
            if bench.throughput > 0:
                print(f"    Throughput: {bench.throughput:.2f}")
            for key, value in bench.details.items():
                if key not in ["error"]:
                    print(f"    {key}: {value}")

    print("\n--- Recommendations ---")
    for rec in report.recommendations:
        print(f"  • {rec}")

    print("\n" + "=" * 60)


def save_report(report: GPUCompatibilityReport, output_path: Path) -> None:
    """Save report to JSON file."""
    # Convert dataclasses to dicts
    report_dict = {
        "timestamp": report.timestamp,
        "system_info": report.system_info,
        "gpu_info": asdict(report.gpu_info),
        "pytorch_info": report.pytorch_info,
        "compatibility_checks": [asdict(c) for c in report.compatibility_checks],
        "benchmarks": [asdict(b) for b in report.benchmarks],
        "overall_status": report.overall_status,
        "recommendations": report.recommendations,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report_dict, f, indent=2)

    logger.info(f"Report saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="VoiceStudio GPU Compatibility Test")
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmarks")
    parser.add_argument("--full-report", action="store_true", help="Run benchmarks and save JSON report")
    parser.add_argument("--output", type=str, default=None, help="Output path for JSON report")
    args = parser.parse_args()

    run_benchmarks = args.benchmark or args.full_report

    logger.info("Starting GPU compatibility tests...")
    report = run_compatibility_tests(run_benchmarks=run_benchmarks)

    print_report(report)

    if args.full_report or args.output:
        output_path = Path(args.output) if args.output else Path(
            "docs/reports/compatibility/GPU_COMPATIBILITY_REPORT.json"
        )
        save_report(report, output_path)

    # Exit with appropriate code
    if report.overall_status == "FAIL":
        sys.exit(1)
    elif report.overall_status == "PARTIAL":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
