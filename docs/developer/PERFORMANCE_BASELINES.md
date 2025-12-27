# VoiceStudio Quantum+ Performance Baselines

Performance baselines and benchmarks for quality testing and comparison features.

## Overview

This document establishes performance baselines for quality features to ensure acceptable response times and resource usage.

## Performance Baselines

### A/B Testing

#### Start A/B Test (`POST /api/eval/abx/start`)

- **Baseline:** < 500ms average response time
- **Target:** < 200ms average response time
- **Max Acceptable:** 1000ms
- **Concurrent Load:** 10 requests with 5 workers should complete in < 2s

#### Get Results (`GET /api/eval/abx/results`)

- **Baseline:** < 100ms average response time
- **Target:** < 50ms average response time
- **Max Acceptable:** 200ms

### Engine Recommendation

#### Get Recommendation (`GET /api/quality/engine-recommendation`)

- **Baseline:** < 200ms average response time
- **Target:** < 100ms average response time
- **Max Acceptable:** 500ms
- **Concurrent Load:** 20 requests with 10 workers should complete in < 1s
- **Performance by Tier:**
  - Fast: < 150ms
  - Standard: < 200ms
  - High: < 250ms
  - Ultra: < 300ms

### Quality Benchmarking

#### Run Benchmark (`POST /api/quality/benchmark`)

**Note:** Benchmarking is inherently slower as it performs actual synthesis.

- **Single Engine Baseline:** < 30s
- **Multiple Engines (3):** < 120s
- **Per Engine Average:** < 40s per engine
- **Max Acceptable:** 180s for 3 engines

**Performance Factors:**
- Engine initialization time
- Synthesis time per engine
- Quality metric calculation time
- Number of engines tested

### Quality Dashboard

#### Get Dashboard (`GET /api/quality/dashboard`)

- **Baseline:** < 300ms average response time
- **Target:** < 150ms average response time
- **Max Acceptable:** 1000ms
- **Concurrent Load:** 10 requests with 5 workers should complete in < 2s
- **Performance by Time Range:**
  - 7 days: < 200ms
  - 30 days: < 300ms
  - 90 days: < 400ms

## Performance Testing

### Running Performance Tests

```bash
# Run all performance tests
pytest tests/performance/ -v

# Run specific test
pytest tests/performance/test_quality_features_performance.py::TestABTestingPerformance::test_ab_test_start_performance -v

# Run with timing output
pytest tests/performance/ -v -s
```

### Performance Test Structure

Performance tests measure:
- **Response Time:** Time from request to response
- **Throughput:** Requests per second
- **Concurrent Load:** Performance under concurrent requests
- **Resource Usage:** CPU and memory usage (if available)

### Interpreting Results

**Good Performance:**
- Response times meet or exceed baselines
- No significant degradation under load
- Consistent performance across multiple runs

**Performance Issues:**
- Response times exceed baselines by > 50%
- Significant degradation under concurrent load
- High variance in response times

## Optimization Recommendations

### A/B Testing

- Cache evaluation results when possible
- Use async processing for long evaluations
- Batch multiple evaluations when appropriate

### Engine Recommendation

- Cache recommendation results for common requirements
- Pre-compute recommendations for standard tiers
- Use efficient algorithm for engine matching

### Quality Benchmarking

- Run benchmarks asynchronously
- Provide progress updates via WebSocket
- Cache benchmark results for identical inputs
- Allow cancellation of long-running benchmarks

### Quality Dashboard

- Cache dashboard data with appropriate TTL
- Use database indexes for efficient queries
- Aggregate data incrementally
- Limit time range queries to reasonable ranges

## Monitoring

### Key Metrics to Monitor

1. **Response Time Percentiles:**
   - P50 (median)
   - P95
   - P99

2. **Error Rates:**
   - 4xx errors
   - 5xx errors
   - Timeout rates

3. **Throughput:**
   - Requests per second
   - Successful requests per second

4. **Resource Usage:**
   - CPU usage
   - Memory usage
   - Database query time

### Performance Alerts

Set up alerts for:
- Response time > 2x baseline
- Error rate > 1%
- Throughput < 50% of expected
- Resource usage > 80%

## Performance Improvement History

### Version 1.0.0

- Initial performance baselines established
- A/B Testing: < 500ms
- Engine Recommendation: < 200ms
- Quality Benchmarking: < 120s (3 engines)
- Quality Dashboard: < 300ms

---

**Last Updated:** 2025-01-27  
**Version:** 1.0.0

