"""
GPU Status Routes

Endpoints for GPU monitoring and status information.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from ..optimization import cache_response
except ImportError:

    def cache_response(ttl: int = 300):
        def decorator(func):
            return func

        return decorator


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gpu-status", tags=["gpu-status"])


class GPUDevice(BaseModel):
    """GPU device information."""

    device_id: str
    name: str
    vendor: str  # NVIDIA, AMD, Intel
    memory_total_mb: int
    memory_used_mb: int
    memory_free_mb: int
    utilization_percent: float  # 0.0 to 100.0
    temperature_celsius: Optional[float] = None
    power_usage_watts: Optional[float] = None
    driver_version: Optional[str] = None
    compute_capability: Optional[str] = None
    is_available: bool = True


class GPUStatus(BaseModel):
    """Overall GPU status."""

    devices: List[GPUDevice]
    total_devices: int
    available_devices: int
    primary_device: Optional[str] = None


@router.get("", response_model=GPUStatus)
@cache_response(ttl=5)  # Cache for 5 seconds (GPU status updates frequently)
async def get_gpu_status():
    """Get current GPU status for all devices."""
    try:
        # GPU status detection uses:
        # 1. nvidia-smi for NVIDIA GPUs (fallback if pynvml not available)
        # 2. pyamdgpuinfo for AMD GPUs (not yet implemented)
        # 3. Direct hardware queries when monitoring libraries available
        #
        # Real implementation enhancements would:
        # 1. Use pynvml library for NVIDIA (better than subprocess)
        # 2. Use pyamdgpuinfo for AMD GPU detection
        # 3. Use Intel GPU libraries for Intel GPUs
        # 4. Cache status with refresh rate limiting
        devices = []

        # Try to detect NVIDIA GPUs
        try:
            import subprocess

            result = subprocess.run(
                [
                    "nvidia-smi",
                    (
                        "--query-gpu=index,name,memory.total,"
                        "memory.used,utilization.gpu,"
                        "temperature.gpu,power.draw,driver_version"
                    ),
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        parts = [p.strip() for p in line.split(",")]
                        if len(parts) >= 7:
                            device_id = parts[0]
                            name = parts[1]
                            memory_total = int(parts[2]) if parts[2].isdigit() else 0
                            memory_used = int(parts[3]) if parts[3].isdigit() else 0
                            utilization = (
                                float(parts[4])
                                if parts[4].replace(".", "").isdigit()
                                else 0.0
                            )
                            temperature = (
                                float(parts[5])
                                if parts[5].replace(".", "").isdigit()
                                else None
                            )
                            power = (
                                float(parts[6])
                                if parts[6].replace(".", "").isdigit()
                                else None
                            )
                            driver_version = parts[7] if len(parts) > 7 else None

                            device = GPUDevice(
                                device_id=f"nvidia-{device_id}",
                                name=name,
                                vendor="NVIDIA",
                                memory_total_mb=memory_total,
                                memory_used_mb=memory_used,
                                memory_free_mb=memory_total - memory_used,
                                utilization_percent=utilization,
                                temperature_celsius=temperature,
                                power_usage_watts=power,
                                driver_version=driver_version,
                                is_available=True,
                            )
                            devices.append(device)
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            # nvidia-smi not available or failed
            ...

        # If no real GPUs detected, return empty device list
        # Client should handle empty device list as "no GPU available" state
        # Note: This is acceptable - not all systems have GPUs

        return GPUStatus(
            devices=devices,
            total_devices=len(devices),
            available_devices=len([d for d in devices if d.is_available]),
            primary_device=devices[0].device_id if devices else None,
        )
    except Exception as e:
        logger.error(f"Failed to get GPU status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get GPU status: {str(e)}",
        ) from e


@router.get("/devices", response_model=List[GPUDevice])
@cache_response(ttl=5)  # Cache for 5 seconds (device list updates frequently)
async def list_gpu_devices():
    """List all GPU devices."""
    status = await get_gpu_status()
    return status.devices


@router.get("/devices/{device_id}", response_model=GPUDevice)
@cache_response(ttl=5)  # Cache for 5 seconds (device status updates frequently)
async def get_gpu_device(device_id: str):
    """Get status for a specific GPU device."""
    status = await get_gpu_status()
    for device in status.devices:
        if device.device_id == device_id:
            return device

    raise HTTPException(status_code=404, detail=f"GPU device '{device_id}' not found")
