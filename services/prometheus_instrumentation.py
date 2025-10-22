#!/usr/bin/env python3
"""
VoiceStudio Prometheus Instrumentation
Adds Prometheus metrics to FastAPI application
"""

import time
from typing import Dict, Optional
from prometheus_client import (
    Counter, Histogram, Gauge, Info, 
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, REGISTRY
)
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse
import logging

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'voicestudio_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'voicestudio_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

TTS_GENERATION_TIME = Histogram(
    'voicestudio_tts_generation_seconds',
    'TTS generation time in seconds',
    ['engine', 'quality_tier']
)

TTS_REQUESTS = Counter(
    'voicestudio_tts_requests_total',
    'Total number of TTS requests',
    ['engine', 'quality_tier']
)

TTS_ERRORS = Counter(
    'voicestudio_tts_errors_total',
    'Total number of TTS errors',
    ['engine', 'error_type']
)

AUDIO_METRICS_ENABLED = Gauge(
    'voicestudio_audio_metrics_enabled',
    'Whether audio metrics are enabled (1=enabled, 0=disabled)'
)

ACTIVE_CONNECTIONS = Gauge(
    'voicestudio_active_connections',
    'Number of active WebSocket connections'
)

ENGINE_STATUS = Gauge(
    'voicestudio_engine_status',
    'Engine status (1=healthy, 0=unhealthy)',
    ['engine']
)

VOICE_FUSION_OPERATIONS = Counter(
    'voicestudio_voice_fusion_total',
    'Total number of voice fusion operations',
    ['operation_type']
)

VOICE_FUSION_DURATION = Histogram(
    'voicestudio_voice_fusion_duration_seconds',
    'Voice fusion operation duration in seconds',
    ['operation_type']
)

# Application info
APP_INFO = Info(
    'voicestudio_app_info',
    'VoiceStudio application information'
)

class PrometheusInstrumentation:
    """Prometheus instrumentation for VoiceStudio"""
    
    def __init__(self, app_name: str = "VoiceStudio", app_version: str = "1.0.0"):
        self.app_name = app_name
        self.app_version = app_version
        self._setup_app_info()
    
    def _setup_app_info(self):
        """Setup application info metric"""
        APP_INFO.info({
            'name': self.app_name,
            'version': self.app_version,
            'python_version': '3.8+'
        })
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application with Prometheus metrics"""
        
        @app.middleware("http")
        async def prometheus_middleware(request: Request, call_next):
            """Middleware to collect HTTP metrics"""
            start_time = time.time()
            
            # Extract endpoint name (remove query params)
            endpoint = request.url.path
            method = request.method
            
            try:
                response = await call_next(request)
                status_code = str(response.status_code)
                
                # Record metrics
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()
                
                REQUEST_DURATION.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(time.time() - start_time)
                
                return response
                
            except Exception as e:
                # Record error metrics
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code="500"
                ).inc()
                
                REQUEST_DURATION.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(time.time() - start_time)
                
                raise
        
        @app.get("/metrics")
        async def metrics_endpoint():
            """Prometheus metrics endpoint"""
            try:
                metrics_data = generate_latest(REGISTRY)
                return PlainTextResponse(
                    content=metrics_data,
                    media_type=CONTENT_TYPE_LATEST
                )
            except Exception as e:
                logger.error(f"Failed to generate metrics: {e}")
                return PlainTextResponse(
                    content="# Error generating metrics\n",
                    status_code=500
                )
        
        logger.info("Prometheus instrumentation added to FastAPI app")
    
    def record_tts_request(self, engine: str, quality_tier: str, duration: float, success: bool = True):
        """Record TTS request metrics"""
        TTS_REQUESTS.labels(
            engine=engine,
            quality_tier=quality_tier
        ).inc()
        
        TTS_GENERATION_TIME.labels(
            engine=engine,
            quality_tier=quality_tier
        ).observe(duration)
        
        if not success:
            TTS_ERRORS.labels(
                engine=engine,
                error_type="generation_failed"
            ).inc()
    
    def record_tts_error(self, engine: str, error_type: str):
        """Record TTS error metrics"""
        TTS_ERRORS.labels(
            engine=engine,
            error_type=error_type
        ).inc()
    
    def set_audio_metrics_enabled(self, enabled: bool):
        """Set audio metrics enabled status"""
        AUDIO_METRICS_ENABLED.set(1 if enabled else 0)
    
    def set_active_connections(self, count: int):
        """Set active WebSocket connections count"""
        ACTIVE_CONNECTIONS.set(count)
    
    def set_engine_status(self, engine: str, healthy: bool):
        """Set engine health status"""
        ENGINE_STATUS.labels(engine=engine).set(1 if healthy else 0)
    
    def record_voice_fusion(self, operation_type: str, duration: float):
        """Record voice fusion operation metrics"""
        VOICE_FUSION_OPERATIONS.labels(
            operation_type=operation_type
        ).inc()
        
        VOICE_FUSION_DURATION.labels(
            operation_type=operation_type
        ).observe(duration)

# Global instrumentation instance
prometheus_instrumentation = PrometheusInstrumentation()

# Convenience functions
def instrument_app(app, app_name: str = "VoiceStudio", app_version: str = "1.0.0"):
    """Convenience function to instrument FastAPI app"""
    instrumentation = PrometheusInstrumentation(app_name, app_version)
    instrumentation.instrument_fastapi(app)
    return instrumentation

def record_tts_metrics(engine: str, quality_tier: str, duration: float, success: bool = True):
    """Convenience function to record TTS metrics"""
    prometheus_instrumentation.record_tts_request(engine, quality_tier, duration, success)

def record_tts_error(engine: str, error_type: str):
    """Convenience function to record TTS error"""
    prometheus_instrumentation.record_tts_error(engine, error_type)

def set_audio_metrics_status(enabled: bool):
    """Convenience function to set audio metrics status"""
    prometheus_instrumentation.set_audio_metrics_enabled(enabled)

def set_engine_health(engine: str, healthy: bool):
    """Convenience function to set engine health"""
    prometheus_instrumentation.set_engine_status(engine, healthy)

def record_voice_fusion_metrics(operation_type: str, duration: float):
    """Convenience function to record voice fusion metrics"""
    prometheus_instrumentation.record_voice_fusion(operation_type, duration)

# DCGM Exporter integration documentation
DCGM_EXPORTER_DOCS = """
# DCGM Exporter Integration for VoiceStudio

## Overview
DCGM Exporter provides GPU metrics for NVIDIA GPUs used in voice cloning operations.

## Installation
```bash
# Download DCGM Exporter
wget https://github.com/NVIDIA/dcgm-exporter/releases/download/v3.1.7-3.1.4/dcgm-exporter-3.1.7-3.1.4.tar.gz
tar -xzf dcgm-exporter-3.1.7-3.1.4.tar.gz

# Install
sudo ./dcgm-exporter-3.1.7-3.1.4/install.sh
```

## Configuration
```yaml
# /etc/dcgm-exporter/dcp-metrics-included.csv
DCGM_FI_DEV_GPU_UTIL,GPU utilization (in %)
DCGM_FI_DEV_MEM_COPY_UTIL,Memory utilization (in %)
DCGM_FI_DEV_GPU_TEMP,GPU temperature (in C)
DCGM_FI_DEV_MEMORY_TEMP,Memory temperature (in C)
DCGM_FI_DEV_POWER_USAGE,Power draw (in W)
DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION,Total energy consumption (in mJ)
DCGM_FI_DEV_SM_CLOCK,SM clock frequency (in MHz)
DCGM_FI_DEV_MEM_CLOCK,Memory clock frequency (in MHz)
DCGM_FI_DEV_MEMORY_USED,Used memory (in MB)
DCGM_FI_DEV_MEMORY_TOTAL,Total memory (in MB)
```

## Service Setup
```bash
# Start DCGM Exporter service
sudo systemctl start dcgm-exporter
sudo systemctl enable dcgm-exporter

# Check status
sudo systemctl status dcgm-exporter
```

## Prometheus Configuration
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'dcgm-exporter'
    static_configs:
      - targets: ['localhost:9400']
    scrape_interval: 15s
```

## Key Metrics for VoiceStudio
- `DCGM_FI_DEV_GPU_UTIL`: GPU utilization during TTS generation
- `DCGM_FI_DEV_MEMORY_USED`: VRAM usage for model loading
- `DCGM_FI_DEV_POWER_USAGE`: Power consumption monitoring
- `DCGM_FI_DEV_GPU_TEMP`: Thermal monitoring

## Integration with VoiceStudio
The DCGM Exporter runs on port 9400 and provides GPU metrics that complement
VoiceStudio's application metrics on port 5090/metrics.

## Monitoring Dashboard
Combine VoiceStudio metrics with GPU metrics in Grafana:
- VoiceStudio TTS generation time vs GPU utilization
- Memory usage patterns during voice cloning
- Power consumption vs audio quality metrics
"""

if __name__ == "__main__":
    print("VoiceStudio Prometheus Instrumentation")
    print("=====================================")
    print("\nAvailable metrics:")
    print("- voicestudio_requests_total")
    print("- voicestudio_request_duration_seconds") 
    print("- voicestudio_tts_generation_seconds")
    print("- voicestudio_tts_requests_total")
    print("- voicestudio_tts_errors_total")
    print("- voicestudio_audio_metrics_enabled")
    print("- voicestudio_active_connections")
    print("- voicestudio_engine_status")
    print("- voicestudio_voice_fusion_total")
    print("- voicestudio_voice_fusion_duration_seconds")
    print("\nDCGM Exporter integration documented above.")
