# Service Level Agreements (SLA)

> **GAP-I20 Resolution**: This document defines timing requirements and SLAs for all coordination points.
>
> **Last Updated**: 2026-02-15  
> **Status**: Active  

## Overview

VoiceStudio defines Service Level Agreements (SLAs) for operations to ensure consistent user experience and enable proactive monitoring. All timing thresholds are measured at P95 (95th percentile) unless otherwise noted.

## Endpoint SLAs

### API Response Times

| Endpoint Category | P50 Latency | P95 Latency | Timeout | Retry |
|-------------------|-------------|-------------|---------|-------|
| Health checks | 20ms | 100ms | 500ms | No |
| Metadata queries | 50ms | 200ms | 2s | Yes (2x) |
| Profile list/get | 100ms | 300ms | 3s | Yes (2x) |
| Engine status | 50ms | 150ms | 1s | Yes (3x) |
| Audio upload (< 10MB) | 500ms | 2s | 30s | Yes (2x) |
| Audio download | 200ms | 1s | 30s | Yes (3x) |

### Synthesis Operations

| Operation | P50 Latency | P95 Latency | Timeout | Retry |
|-----------|-------------|-------------|---------|-------|
| Short text (< 100 chars) | 500ms | 2s | 30s | Yes (1x) |
| Medium text (100-500 chars) | 2s | 5s | 60s | Yes (1x) |
| Long text (500-2000 chars) | 5s | 10s | 120s | No |
| Batch synthesis | N/A | N/A | 600s | No |

### Transcription Operations

| Operation | P50 Latency | P95 Latency | Timeout | Retry |
|-----------|-------------|-------------|---------|-------|
| Short audio (< 30s) | 3s | 10s | 60s | Yes (1x) |
| Medium audio (30s-5min) | 30s | 60s | 300s | No |
| Long audio (> 5min) | N/A | N/A | 1800s | No |

### Training Operations

| Operation | P50 Duration | P95 Duration | Timeout | Retry |
|-----------|--------------|--------------|---------|-------|
| Profile training (fine-tune) | 10min | 30min | 3600s | No |
| Voice cloning | 5min | 15min | 1800s | No |
| Quality validation | 30s | 60s | 300s | Yes (1x) |

### File Operations

| Operation | P50 Latency | P95 Latency | Timeout | Retry |
|-----------|-------------|-------------|---------|-------|
| Project save | 100ms | 500ms | 5s | Yes (3x) |
| Project load | 200ms | 1s | 10s | Yes (2x) |
| Export audio | 500ms | 2s | 30s | Yes (2x) |
| Import audio | 300ms | 1s | 30s | Yes (2x) |
| Preferences save | 50ms | 200ms | 2s | Yes (3x) |

## Frontend Coordination Timeouts

### Panel Operations

| Operation | Expected | Warning | Failure | Action on Failure |
|-----------|----------|---------|---------|-------------------|
| Panel load | 100ms | 500ms | 2s | Show skeleton UI |
| Panel activation | 50ms | 200ms | 1s | Log + show error |
| Panel deactivation | 20ms | 100ms | 500ms | Force cleanup |
| Data refresh | 200ms | 1s | 5s | Show stale indicator |

### Command Execution

| Operation | Expected | Warning | Failure | Action on Failure |
|-----------|----------|---------|---------|-------------------|
| Sync command | 50ms | 200ms | 1s | Log + show error |
| Async command start | 10ms | 50ms | 200ms | Log warning |
| Command queue add | 5ms | 20ms | 100ms | Retry once |
| CanExecute evaluation | 1ms | 10ms | 50ms | Cache result |

### Event System

| Operation | Expected | Warning | Failure | Action on Failure |
|-----------|----------|---------|---------|-------------------|
| Event publish | 1ms | 5ms | 20ms | Log warning |
| Event propagation (all handlers) | 10ms | 50ms | 200ms | Log + trace |
| Event handler execution | 5ms | 20ms | 100ms | Log slow handler |
| Throttled event coalesce | 100ms | - | - | Normal behavior |

### Concurrency Operations

| Operation | Expected | Warning | Failure | Action on Failure |
|-----------|----------|---------|---------|-------------------|
| Lock acquisition | 100ms | 500ms | 10s | Deadlock detection |
| Mutex wait | 50ms | 200ms | 5s | Log + timeout |
| Semaphore wait | 50ms | 200ms | 5s | Log + timeout |
| Thread pool queue | 10ms | 50ms | 500ms | Scale pool |

### UI Responsiveness

| Operation | Expected | Warning | Failure | Action on Failure |
|-----------|----------|---------|---------|-------------------|
| UI thread block | 0ms | 16ms | 100ms | Move to background |
| Layout pass | 5ms | 16ms | 50ms | Simplify layout |
| Render frame | 8ms | 16ms | 33ms | Drop frame |
| Input response | 10ms | 50ms | 100ms | Priority dispatch |

## Backend Coordination Timeouts

### Service Communication

| Operation | Expected | Warning | Failure | Action on Failure |
|-----------|----------|---------|---------|-------------------|
| Engine spawn | 2s | 5s | 30s | Use fallback |
| Engine health check | 100ms | 500ms | 2s | Mark unhealthy |
| IPC message send | 10ms | 50ms | 500ms | Retry + log |
| IPC message receive | 100ms | 500ms | 5s | Timeout error |

### Database Operations

| Operation | Expected | Warning | Failure | Action on Failure |
|-----------|----------|---------|---------|-------------------|
| Simple query | 10ms | 50ms | 500ms | Log slow query |
| Complex query | 100ms | 500ms | 5s | Optimize query |
| Write operation | 50ms | 200ms | 2s | Retry + log |
| Transaction commit | 20ms | 100ms | 1s | Rollback |

### Circuit Breaker Thresholds

| Metric | Warning | Open Threshold | Recovery Check |
|--------|---------|----------------|----------------|
| Failure rate | > 10% | > 50% (5/10) | Every 30s |
| Latency (P95) | > 2x SLA | > 5x SLA | Every 60s |
| Timeout rate | > 5% | > 20% | Every 30s |
| Error rate | > 5% | > 25% | Every 30s |

## Monitoring Integration

### Metrics to Collect

| Metric | Type | Labels | Aggregation |
|--------|------|--------|-------------|
| `request_duration_seconds` | Histogram | endpoint, method, status | P50, P95, P99 |
| `command_duration_seconds` | Histogram | command_id, status | P50, P95 |
| `event_duration_seconds` | Histogram | event_type | P50, P95 |
| `panel_load_seconds` | Histogram | panel_id | P50, P95 |
| `lock_wait_seconds` | Histogram | lock_name | P50, P95 |
| `circuit_breaker_state` | Gauge | breaker_name, state | Latest |

### Alerting Rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| High Latency | P95 > 2x SLA for 5min | Warning | Investigate |
| Degraded Service | P95 > 5x SLA for 5min | Critical | Page on-call |
| Circuit Open | Any breaker open > 5min | Warning | Investigate |
| High Error Rate | > 5% errors for 5min | Warning | Investigate |
| Very High Error Rate | > 20% errors for 5min | Critical | Page on-call |
| Timeout Spike | > 10% timeouts for 5min | Warning | Scale/investigate |

### Logging Thresholds

Operations exceeding SLA thresholds should log at appropriate levels:

```csharp
// Example: LoggingExtensions.cs
public static void LogWithLatency<T>(
    this ILogger<T> logger, 
    string operation, 
    TimeSpan duration, 
    SlaThresholds thresholds)
{
    var ms = duration.TotalMilliseconds;
    
    if (ms > thresholds.Failure.TotalMilliseconds)
    {
        logger.LogError(
            "[SLA BREACH] {Operation} took {Duration}ms (failure threshold: {Threshold}ms)",
            operation, ms, thresholds.Failure.TotalMilliseconds);
    }
    else if (ms > thresholds.Warning.TotalMilliseconds)
    {
        logger.LogWarning(
            "[SLA WARNING] {Operation} took {Duration}ms (warning threshold: {Threshold}ms)",
            operation, ms, thresholds.Warning.TotalMilliseconds);
    }
    else
    {
        logger.LogDebug("{Operation} completed in {Duration}ms", operation, ms);
    }
}
```

## SLA Configuration

SLA thresholds are configurable via `config/sla.json`:

```json
{
  "endpoints": {
    "health": { "p95_ms": 100, "timeout_ms": 500 },
    "synthesis_short": { "p95_ms": 2000, "timeout_ms": 30000 },
    "synthesis_medium": { "p95_ms": 5000, "timeout_ms": 60000 }
  },
  "coordination": {
    "panel_load": { "expected_ms": 100, "warning_ms": 500, "failure_ms": 2000 },
    "command_execution": { "expected_ms": 50, "warning_ms": 200, "failure_ms": 1000 },
    "event_propagation": { "expected_ms": 10, "warning_ms": 50, "failure_ms": 200 }
  },
  "circuit_breaker": {
    "failure_threshold_percent": 50,
    "recovery_check_seconds": 30
  }
}
```

## Performance Testing

### Baseline Requirements

Regular performance testing should validate:

1. **API Endpoints**: All endpoints meet P95 SLAs under normal load
2. **Stress Testing**: System degrades gracefully under 2x normal load
3. **Spike Testing**: System recovers within 60s after load spike
4. **Soak Testing**: No memory leaks or degradation over 8h run

### Test Scenarios

| Scenario | Load | Duration | Success Criteria |
|----------|------|----------|------------------|
| Baseline | 10 RPS | 30min | All SLAs met |
| Normal | 50 RPS | 1h | P95 < 1.5x SLA |
| Stress | 100 RPS | 30min | P95 < 3x SLA, no errors |
| Spike | 200 RPS burst | 5min | Recovery < 60s |
| Soak | 30 RPS | 8h | Memory stable |

## Related Documents

- [RECOVERY_COORDINATION.md](RECOVERY_COORDINATION.md) - Recovery patterns
- [CONCURRENCY_GUIDE.md](CONCURRENCY_GUIDE.md) - Lock timeouts
- [backend/services/circuit_breaker.py](../../backend/services/circuit_breaker.py) - Circuit breaker implementation
