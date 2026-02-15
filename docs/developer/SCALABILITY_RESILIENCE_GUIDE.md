# VoiceStudio Scalability and Resilience Guide

> **Version**: 1.0
> **Last Updated**: 2026-02-14
> **Classification**: Developer Documentation
> **Phase**: Deterministic Sentinel - Phase 6

---

## Overview

This guide documents the scalability and resilience patterns implemented in VoiceStudio, covering circuit breakers, rate limiting, retry logic, timeout management, and horizontal scalability preparation.

---

## 1. Circuit Breaker Pattern

### 1.1 Architecture

VoiceStudio implements the Circuit Breaker pattern (from "Release It!" by Michael Nygard) to prevent cascading failures:

| State | Description | Behavior |
|-------|-------------|----------|
| **CLOSED** | Normal operation | Requests pass through |
| **OPEN** | Circuit tripped | Requests fail fast |
| **HALF_OPEN** | Testing recovery | Limited requests allowed |

### 1.2 Key Components

#### CircuitBreaker (`backend/services/circuit_breaker.py`)

```python
from backend.services.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

# Create circuit breaker
breaker = CircuitBreaker(
    name="xtts_v2",
    config=CircuitBreakerConfig(
        failure_threshold=3,      # Failures before opening
        success_threshold=2,      # Successes to close from half-open
        recovery_timeout=60.0,    # Seconds before trying half-open
        half_open_max_calls=3     # Max concurrent calls in half-open
    )
)

# Use as context manager
async with breaker:
    result = await engine.synthesize(text, voice)

# Or manually
if breaker.allow_request():
    try:
        result = await engine.synthesize(text, voice)
        breaker.record_success()
    except Exception as e:
        breaker.record_failure()
        raise
else:
    raise CircuitBreakerOpenError(breaker.name)
```

### 1.3 Per-Engine Circuit Breakers

```python
from backend.services.circuit_breaker import CircuitBreakerRegistry

# Get or create circuit breaker for engine
breaker = CircuitBreakerRegistry.get("xtts_v2")

# Check all breaker states
statuses = CircuitBreakerRegistry.get_all_statuses()
```

### 1.4 Monitoring

```python
stats = breaker.get_stats()
# Returns: CircuitBreakerStats(
#     name="xtts_v2",
#     state=CircuitState.CLOSED,
#     failure_count=2,
#     success_count=150,
#     last_failure_time=...,
#     total_requests=152,
#     total_failures=5,
#     total_circuit_opens=1
# )
```

---

## 2. Rate Limiting

### 2.1 Architecture

VoiceStudio implements sliding window rate limiting:

| Feature | Description |
|---------|-------------|
| **Algorithm** | Sliding window (more accurate than fixed window) |
| **Granularity** | Per-client, per-endpoint |
| **Burst Support** | Configurable burst allowance |
| **Headers** | Standard rate limit headers in responses |

### 2.2 Key Components

#### SlidingWindowRateLimiter (`backend/api/middleware/rate_limiter.py`)

```python
from backend.api.middleware.rate_limiter import (
    SlidingWindowRateLimiter,
    RateLimitConfig,
    RateLimitMiddleware
)

# Configure rate limiter
config = RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=1000,
    burst_size=10,
    excluded_paths=["/health", "/metrics"],
    path_limits={
        "/api/v1/synthesize": 10,  # Heavy operations
        "/api/v1/clone": 5,        # Very heavy operations
    }
)

# Add middleware to FastAPI
app.add_middleware(RateLimitMiddleware, config=config)
```

### 2.3 Response Headers

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1707897600
Retry-After: 30  (only when rate limited)
```

### 2.4 Custom Key Extraction

```python
def custom_key(request: Request) -> str:
    # Extract API key or user ID
    return request.headers.get("X-API-Key", request.client.host)

config = RateLimitConfig(key_func=custom_key)
```

---

## 3. Retry Logic with Exponential Backoff

### 3.1 Architecture

VoiceStudio implements automatic retry with exponential backoff:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Max Retries | 3 | Maximum retry attempts |
| Base Delay | 1.0s | Initial delay between retries |
| Max Delay | 60.0s | Maximum delay cap |
| Multiplier | 2.0 | Delay multiplier per retry |
| Jitter | 0.1 | Random jitter factor |

### 3.2 Key Components

#### ErrorRecoveryManager (`backend/api/error_recovery.py`)

```python
from backend.api.error_recovery import ErrorRecoveryManager

manager = ErrorRecoveryManager()

# Execute with automatic recovery
result = manager.execute_with_recovery(
    func=lambda: engine.synthesize(text, voice),
    service_name="xtts_v2",
    operation_name="synthesize",
    retry_config=RetryConfig(max_retries=3, base_delay=1.0),
    fallback=lambda: fallback_synthesis(text)
)
```

### 3.3 Decorator Usage

```python
from backend.api.error_recovery import with_recovery

@with_recovery(service_name="whisper", max_retries=3)
async def transcribe_audio(audio_path: str) -> str:
    return await whisper_engine.transcribe(audio_path)
```

### 3.4 Retry Categories

| Exception Type | Retryable | Reason |
|----------------|-----------|--------|
| `TimeoutError` | Yes | Transient network issue |
| `ConnectionError` | Yes | Temporary connectivity |
| `HTTPStatus 503` | Yes | Service temporarily unavailable |
| `ValidationError` | No | Client error, won't fix with retry |
| `AuthenticationError` | No | Credentials invalid |

---

## 4. Request Timeout Standardization

### 4.1 Architecture

All timeouts are centralized in `TimeoutConfig` with environment variable overrides:

| Timeout | Default | Environment Variable |
|---------|---------|---------------------|
| Shutdown | 30.0s | `VOICESTUDIO_SHUTDOWN_TIMEOUT` |
| Engine Stop | 10.0s | `VOICESTUDIO_ENGINE_STOP_TIMEOUT` |
| Engine Recovery | 60.0s | `VOICESTUDIO_ENGINE_RECOVERY_TIMEOUT` |
| Health Check | 5.0s | `VOICESTUDIO_HEALTH_CHECK_TIMEOUT` |
| GPU Status | 5.0s | `VOICESTUDIO_GPU_STATUS_TIMEOUT` |
| Database Check | 3.0s | `VOICESTUDIO_DB_CHECK_TIMEOUT` |
| Disk Check | 2.0s | `VOICESTUDIO_DISK_CHECK_TIMEOUT` |
| Memory Check | 2.0s | `VOICESTUDIO_MEMORY_CHECK_TIMEOUT` |
| Engine Check | 10.0s | `VOICESTUDIO_ENGINE_CHECK_TIMEOUT` |

### 4.2 Usage

```python
from backend.settings import config

# Access timeouts
shutdown_timeout = config.timeouts.shutdown
health_timeout = config.timeouts.health_check

# Use in async operations
try:
    async with asyncio.timeout(config.timeouts.engine_check):
        result = await engine.health_check()
except asyncio.TimeoutError:
    logger.warning("Engine health check timed out")
```

### 4.3 Request-Level Timeouts

```python
from backend.api.middleware.tracing import RequestTimeoutMiddleware

app.add_middleware(
    RequestTimeoutMiddleware,
    default_timeout=30.0,
    path_timeouts={
        "/api/v1/synthesize": 120.0,  # Long-running synthesis
        "/api/v1/clone": 300.0,       # Very long cloning
    }
)
```

---

## 5. Horizontal Scalability Preparation

### 5.1 Architecture

VoiceStudio is designed for horizontal scaling with stateless APIs and workload balancing:

| Component | Scalability | Notes |
|-----------|-------------|-------|
| API Servers | Horizontal | Stateless, load-balanced |
| Engine Workers | Horizontal | GPU-bound, workload-balanced |
| Database | Vertical (MVP) | PostgreSQL for production scale |
| Cache | Horizontal | Redis cluster for production |
| Message Queue | Horizontal | Redis/RabbitMQ for production |

### 5.2 Workload Balancer

#### WorkloadBalancer (`backend/services/workload_balancer.py`)

```python
from backend.services.workload_balancer import (
    WorkloadBalancer,
    BalancerConfig,
    WorkloadTask,
    ComputeDevice
)

# Configure balancer
balancer = WorkloadBalancer(
    config=BalancerConfig(
        enable_gpu=True,
        gpu_memory_threshold=0.85,
        gpu_utilization_threshold=0.90,
        prefer_gpu_for_engines=["xtts", "rvc", "whisper"],
        cpu_only_engines=["piper"]
    )
)

# Route task to optimal device
task = WorkloadTask(
    id="synth-123",
    engine_type="xtts",
    estimated_memory_bytes=2 * 1024**3,  # 2GB
    estimated_compute_ms=5000,
    prefer_gpu=True
)

device = await balancer.route_task(task)
# Returns: ComputeDevice.GPU_0 or ComputeDevice.CPU
```

### 5.3 Stateless Design Patterns

```python
# ✅ Stateless: Use request-scoped data
@router.post("/synthesize")
async def synthesize(request: SynthesisRequest):
    # All state from request
    return await engine.synthesize(request.text, request.voice_id)

# ❌ Stateful: Global mutable state
_session_data = {}  # Don't do this

# ✅ External state: Use database/cache
async def get_session(session_id: str):
    return await cache.get(f"session:{session_id}")
```

### 5.4 Production Scaling Checklist

- [ ] Deploy behind load balancer (nginx, HAProxy)
- [ ] Configure Redis for cache and sessions
- [ ] Configure RabbitMQ/Redis for job queue
- [ ] Set up PostgreSQL with read replicas
- [ ] Configure GPU worker pool with NVIDIA Docker
- [ ] Set up health check endpoints for orchestrator
- [ ] Configure auto-scaling rules based on queue depth

---

## Integration Example

### Full Resilience Stack

```python
from backend.services.circuit_breaker import CircuitBreaker
from backend.api.middleware.rate_limiter import SlidingWindowRateLimiter
from backend.api.error_recovery import ErrorRecoveryManager
from backend.settings import config

# Setup
breaker = CircuitBreaker("synthesis", failure_threshold=3)
rate_limiter = SlidingWindowRateLimiter()
recovery = ErrorRecoveryManager()

async def synthesize_with_resilience(text: str, voice_id: str):
    # Check rate limit
    if not await rate_limiter.allow():
        raise RateLimitExceeded()
    
    # Execute with circuit breaker and retry
    async with breaker:
        return await recovery.execute_with_recovery(
            func=lambda: engine.synthesize(text, voice_id),
            service_name="xtts",
            operation_name="synthesize",
            timeout=config.timeouts.engine_check
        )
```

---

## Monitoring Dashboard

Access resilience metrics via:

```
GET /api/health/detailed
GET /api/metrics/circuit-breakers
GET /api/metrics/rate-limits
GET /api/metrics/workload
```

---

## References

- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Rate Limiting Algorithms](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [Exponential Backoff](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [Architecture Overview](ARCHITECTURE.md)
