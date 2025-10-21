#!/usr/bin/env python3

import argparse
import json
import platform
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


def _run_command(command: List[str], timeout_seconds: int = 5) -> Tuple[int, str, str]:
    """
    Execute a command and capture stdout/stderr without raising on failure.
    Returns (returncode, stdout, stderr).
    """
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
            text=True,
        )
        return completed.returncode, completed.stdout.strip(), completed.stderr.strip()
    except Exception as exc:
        return 127, "", f"exception: {exc}"


def _detect_nvidia_smi() -> Optional[str]:
    path = shutil.which("nvidia-smi")
    return path


def _collect_with_nvidia_smi() -> Optional[Dict[str, Any]]:
    nvsmi_path = _detect_nvidia_smi()
    if not nvsmi_path:
        return None

    # Query common fields; nounits to ease parsing
    fields = [
        "index",
        "name",
        "uuid",
        "pci.bus_id",
        "memory.total",
        "memory.used",
        "memory.free",
        "utilization.gpu",
        "utilization.memory",
        "driver_version",
    ]
    query = ",".join(fields)
    code, out, err = _run_command(
        [
            nvsmi_path,
            f"--query-gpu={query}",
            "--format=csv,noheader,nounits",
        ]
    )
    if code != 0 or not out:
        return None

    gpus: List[Dict[str, Any]] = []
    for line in out.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != len(fields):
            # Unexpected format; skip this line safely
            continue
        (
            index,
            name,
            uuid,
            pci_bus_id,
            mem_total,
            mem_used,
            mem_free,
            util_gpu,
            util_mem,
            driver_version,
        ) = parts

        def to_int(value: str) -> Optional[int]:
            try:
                return int(value)
            except Exception:
                return None

        def to_float(value: str) -> Optional[float]:
            try:
                return float(value)
            except Exception:
                return None

        gpu: Dict[str, Any] = {
            "index": to_int(index),
            "name": name,
            "uuid": uuid,
            "vendor": "NVIDIA",
            "pci_bus_id": pci_bus_id,
            "memory_total_mb": to_int(mem_total),
            "memory_used_mb": to_int(mem_used),
            "memory_free_mb": to_int(mem_free),
            "utilization_gpu_pct": to_float(util_gpu),
            "utilization_mem_pct": to_float(util_mem),
            "driver_version": driver_version,
            "source": "nvidia-smi",
        }
        gpus.append(gpu)

    return {"gpus": gpus, "source": "nvidia-smi"}


def _collect_with_nvml() -> Optional[Dict[str, Any]]:
    try:
        import pynvml  # type: ignore
    except Exception:
        return None

    try:
        pynvml.nvmlInit()
    except Exception:
        return None

    gpus: List[Dict[str, Any]] = []
    try:
        count = pynvml.nvmlDeviceGetCount()
        for i in range(count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            try:
                name = name.decode("utf-8")  # type: ignore[attr-defined]
            except Exception:
                pass

            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            util = None
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            except Exception:
                util = None

            pci = None
            try:
                pci = pynvml.nvmlDeviceGetPciInfo(handle)
            except Exception:
                pci = None

            gpu: Dict[str, Any] = {
                "index": i,
                "name": name,
                "uuid": None,
                "vendor": "NVIDIA",
                "pci_bus_id": getattr(pci, "busId", None) if pci else None,
                "memory_total_mb": int(mem.total / (1024 * 1024)) if mem else None,
                "memory_used_mb": int(mem.used / (1024 * 1024)) if mem else None,
                "memory_free_mb": int(mem.free / (1024 * 1024)) if mem else None,
                "utilization_gpu_pct": getattr(util, "gpu", None) if util else None,
                "utilization_mem_pct": getattr(util, "memory", None) if util else None,
                "driver_version": None,
                "source": "pynvml",
            }
            gpus.append(gpu)
    finally:
        try:
            pynvml.nvmlShutdown()
        except Exception:
            pass

    return {"gpus": gpus, "source": "pynvml"}


def _collect_with_torch() -> Optional[Dict[str, Any]]:
    try:
        import torch  # type: ignore
    except Exception:
        return None

    try:
        if not torch.cuda.is_available():
            return None
    except Exception:
        return None

    gpus: List[Dict[str, Any]] = []
    try:
        device_count = torch.cuda.device_count()
        for i in range(device_count):
            name = torch.cuda.get_device_name(i)
            # Use mem_get_info per-device (bytes)
            free_b, total_b = (None, None)
            try:
                with torch.cuda.device(i):
                    free_b, total_b = torch.cuda.mem_get_info()  # type: ignore[assignment]
            except Exception:
                pass
            used_mb = None
            free_mb = int(free_b / (1024 * 1024)) if isinstance(free_b, int) else None
            total_mb = int(total_b / (1024 * 1024)) if isinstance(total_b, int) else None
            if isinstance(total_mb, int) and isinstance(free_mb, int):
                used_mb = total_mb - free_mb

            gpus.append(
                {
                    "index": i,
                    "name": name,
                    "uuid": None,
                    "vendor": "NVIDIA",  # torch.cuda implies CUDA
                    "pci_bus_id": None,
                    "memory_total_mb": total_mb,
                    "memory_used_mb": used_mb,
                    "memory_free_mb": free_mb,
                    "utilization_gpu_pct": None,
                    "utilization_mem_pct": None,
                    "driver_version": None,
                    "source": "torch.cuda",
                }
            )
    except Exception:
        return None

    return {"gpus": gpus, "source": "torch.cuda"}


def collect_vram() -> Dict[str, Any]:
    """
    Collect VRAM telemetry using best-available backend.
    Preference order: nvidia-smi -> NVML -> torch -> none.
    """
    collectors = (
        _collect_with_nvidia_smi,
        _collect_with_nvml,
        _collect_with_torch,
    )

    for collector in collectors:
        result = None
        try:
            result = collector()
        except Exception:
            result = None
        if result and result.get("gpus"):
            return result

    return {"gpus": [], "source": "none"}


def _host_info() -> Dict[str, Any]:
    return {
        "hostname": socket.gethostname(),
        "os": platform.platform(),
        "python_version": sys.version.split(" ")[0],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect GPU VRAM telemetry")
    parser.add_argument(
        "--format",
        choices=["json", "plain"],
        default="json",
        help="Output format",
    )
    args = parser.parse_args()

    payload = collect_vram()
    envelope = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host": _host_info(),
        "gpus": payload.get("gpus", []),
        "source": payload.get("source", "unknown"),
    }

    if args.format == "json":
        print(json.dumps(envelope, ensure_ascii=False))
    else:
        gpus = envelope["gpus"]
        if not gpus:
            print("No GPUs detected.")
        else:
            for gpu in gpus:
                print(
                    f"GPU {gpu.get('index')}: {gpu.get('name')} | "
                    f"Used {gpu.get('memory_used_mb')}MB / {gpu.get('memory_total_mb')}MB"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
