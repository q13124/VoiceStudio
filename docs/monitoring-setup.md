# VoiceStudio Monitoring Setup

This document explains how to set up comprehensive monitoring for VoiceStudio using Prometheus, Grafana, and NVIDIA DCGM Exporter.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VoiceStudio   │    │   Prometheus    │    │     Grafana     │
│      API        │───▶│   (Scraper)     │───▶│  (Dashboard)    │
│   :8000/metrics │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ NVIDIA DCGM     │
                       │   Exporter      │
                       │ :9400/metrics   │
                       └─────────────────┘
```

## Components

### 1. VoiceStudio API Metrics
- **Endpoint**: `/metrics` (when `PROM_ENABLED=true`)
- **Metrics**: HTTP requests, response times, errors, custom business metrics
- **Configuration**: Set via environment variables

### 2. NVIDIA DCGM Exporter
- **Purpose**: Exposes GPU metrics (utilization, memory, temperature, power)
- **Port**: 9400
- **Docker Image**: `nvidia/dcgm-exporter:3.3.8-3.4.0-ubuntu22.04`

### 3. Prometheus
- **Purpose**: Time-series database and metrics scraper
- **Configuration**: `config/prometheus.yml`
- **Scrape Interval**: 15 seconds

### 4. Grafana
- **Purpose**: Metrics visualization and alerting
- **Dashboard**: `config/grafana-dashboard.json`

## Setup Instructions

### Step 1: Enable VoiceStudio Metrics

Set environment variables to enable Prometheus metrics:

```bash
# Windows PowerShell
$env:PROM_ENABLED = "true"
$env:PROM_ENDPOINT = "/metrics"
$env:PROM_INSTRUMENT_APP = "true"
$env:PROM_GROUP_PATHS = "true"

# Linux/macOS
export PROM_ENABLED=true
export PROM_ENDPOINT=/metrics
export PROM_INSTRUMENT_APP=true
export PROM_GROUP_PATHS=true
```

### Step 2: Run NVIDIA DCGM Exporter

```bash
# Start DCGM Exporter (requires Docker with GPU support)
docker run -d --gpus all --restart=always \
  -p 9400:9400 \
  --name dcgm-exporter \
  nvidia/dcgm-exporter:3.3.8-3.4.0-ubuntu22.04
```

### Step 3: Start Prometheus

```bash
# Using Docker
docker run -d --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/config/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:latest

# Or download and run locally
# Download from https://prometheus.io/download/
./prometheus --config.file=config/prometheus.yml
```

### Step 4: Start Grafana

```bash
# Using Docker
docker run -d --name grafana \
  -p 3000:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  grafana/grafana:latest

# Import dashboard: config/grafana-dashboard.json
```

## Configuration Files

### Prometheus Configuration (`config/prometheus.yml`)
- Scrapes VoiceStudio API metrics from `voicestudio.local:8000/metrics`
- Scrapes GPU metrics from DCGM exporter on `gpu-host-1:9400`
- 15-second scrape interval

### Grafana Dashboard (`config/grafana-dashboard.json`)
- API request rate and response time
- GPU utilization, memory usage, temperature, power draw
- Auto-refresh every 30 seconds

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROM_ENABLED` | `false` | Enable Prometheus metrics endpoint |
| `PROM_ENDPOINT` | `/metrics` | Metrics endpoint path |
| `PROM_INSTRUMENT_APP` | `true` | Instrument FastAPI requests |
| `PROM_GROUP_PATHS` | `true` | Group dynamic path parameters |
| `PROM_LATENCY_BUCKETS_MS` | `5,10,25,50,100,250,500,1000,2500,5000,10000` | Histogram buckets |

## Key Metrics

### VoiceStudio API Metrics
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_inprogress` - Current in-flight requests
- `http_exceptions_total` - Total exceptions

### GPU Metrics (DCGM)
- `DCGM_FI_DEV_GPU_UTIL` - GPU utilization percentage
- `DCGM_FI_DEV_FB_USED` - GPU memory used (bytes)
- `DCGM_FI_DEV_FB_TOTAL` - GPU memory total (bytes)
- `DCGM_FI_DEV_GPU_TEMP` - GPU temperature (°C)
- `DCGM_FI_DEV_POWER_USAGE` - GPU power draw (watts)

## Troubleshooting

### Metrics Not Appearing
1. Check `PROM_ENABLED=true` is set
2. Verify `/metrics` endpoint returns data: `curl http://localhost:8000/metrics`
3. Check Prometheus targets: http://localhost:9090/targets

### GPU Metrics Missing
1. Ensure NVIDIA drivers are installed
2. Verify Docker has GPU access: `docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi`
3. Check DCGM exporter logs: `docker logs dcgm-exporter`

### Grafana Dashboard Issues
1. Verify Prometheus is configured as data source
2. Check metric names match exactly (case-sensitive)
3. Ensure time range includes data

## Security Considerations

- Prometheus metrics endpoint is not authenticated by default
- Consider using reverse proxy with authentication for production
- DCGM exporter should only be accessible from Prometheus server
- Use HTTPS in production environments

## Production Deployment

For production deployment, consider:
- Using Kubernetes with proper service discovery
- Setting up alerting rules in Prometheus
- Configuring Grafana alerting channels
- Implementing proper authentication and authorization
- Using persistent storage for Prometheus and Grafana data
