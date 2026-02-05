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

        # Try to detect AMD GPUs
        try:
            # Method 1: Try pyamdgpuinfo library (preferred)
            try:
                import pyamdgpuinfo
                
                amd_count = pyamdgpuinfo.detect_gpus()
                for i in range(amd_count):
                    gpu = pyamdgpuinfo.get_gpu(i)
                    device = GPUDevice(
                        device_id=f"amd-{i}",
                        name=gpu.name if hasattr(gpu, 'name') else f"AMD GPU {i}",
                        vendor="AMD",
                        memory_total_mb=int(gpu.memory_info['vram_size'] / (1024 * 1024)) if hasattr(gpu, 'memory_info') else 0,
                        memory_used_mb=int(gpu.memory_info.get('vram_usage', 0) / (1024 * 1024)) if hasattr(gpu, 'memory_info') else 0,
                        memory_free_mb=0,  # Will be calculated
                        utilization_percent=gpu.gpu_load * 100 if hasattr(gpu, 'gpu_load') else 0.0,
                        temperature_celsius=gpu.temperature if hasattr(gpu, 'temperature') else None,
                        power_usage_watts=gpu.power if hasattr(gpu, 'power') else None,
                        driver_version=None,
                        is_available=True,
                    )
                    device.memory_free_mb = device.memory_total_mb - device.memory_used_mb
                    devices.append(device)
                logger.debug(f"Detected {amd_count} AMD GPU(s) via pyamdgpuinfo")
            except ImportError:
                # pyamdgpuinfo not installed, try fallback methods
                
                # Method 2: Try rocm-smi for AMD ROCm GPUs (Linux)
                try:
                    import subprocess
                    import platform
                    
                    if platform.system() == "Linux":
                        result = subprocess.run(
                            ["rocm-smi", "--showid", "--showname", "--showmeminfo", "vram"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if result.returncode == 0:
                            # Parse rocm-smi output (format varies by version)
                            lines = result.stdout.strip().split("\n")
                            gpu_idx = 0
                            for line in lines:
                                if "GPU" in line and ":" in line:
                                    parts = line.split(":")
                                    if len(parts) >= 2:
                                        device = GPUDevice(
                                            device_id=f"amd-{gpu_idx}",
                                            name=parts[1].strip() if len(parts) > 1 else f"AMD ROCm GPU {gpu_idx}",
                                            vendor="AMD",
                                            memory_total_mb=0,
                                            memory_used_mb=0,
                                            memory_free_mb=0,
                                            utilization_percent=0.0,
                                            temperature_celsius=None,
                                            power_usage_watts=None,
                                            driver_version=None,
                                            is_available=True,
                                        )
                                        devices.append(device)
                                        gpu_idx += 1
                            logger.debug(f"Detected {gpu_idx} AMD GPU(s) via rocm-smi")
                except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
                    pass
                
                # Method 3: Try WMI for Windows AMD GPUs
                try:
                    import platform
                    
                    if platform.system() == "Windows":
                        import subprocess
                        
                        # Use WMIC to query AMD GPUs
                        result = subprocess.run(
                            ["wmic", "path", "win32_VideoController", "get", "Name,AdapterRAM,DriverVersion", "/format:csv"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if result.returncode == 0:
                            lines = result.stdout.strip().split("\n")
                            gpu_idx = len([d for d in devices if d.vendor == "AMD"])  # Continue from existing AMD count
                            for line in lines:
                                if line.strip() and "AMD" in line.upper() and "Node" not in line:
                                    parts = [p.strip() for p in line.split(",")]
                                    if len(parts) >= 3:
                                        # CSV format: Node,AdapterRAM,DriverVersion,Name
                                        name = parts[-1] if parts[-1] else f"AMD GPU {gpu_idx}"
                                        adapter_ram = int(parts[1]) // (1024 * 1024) if parts[1].isdigit() else 0
                                        driver_version = parts[2] if len(parts) > 2 else None
                                        
                                        # Skip if already detected
                                        if not any(d.name == name and d.vendor == "AMD" for d in devices):
                                            device = GPUDevice(
                                                device_id=f"amd-{gpu_idx}",
                                                name=name,
                                                vendor="AMD",
                                                memory_total_mb=adapter_ram,
                                                memory_used_mb=0,
                                                memory_free_mb=adapter_ram,
                                                utilization_percent=0.0,
                                                temperature_celsius=None,
                                                power_usage_watts=None,
                                                driver_version=driver_version,
                                                is_available=True,
                                            )
                                            devices.append(device)
                                            gpu_idx += 1
                            if gpu_idx > 0:
                                logger.debug(f"Detected AMD GPU(s) via WMI")
                except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
                    pass
        except Exception as e:
            logger.debug(f"AMD GPU detection failed: {e}")

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
