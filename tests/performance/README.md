# Performance Test Suite

Comprehensive performance testing for VoiceStudio including benchmarks, load testing, stress testing, and profiling.

## Test Files

- `test_performance_benchmarks.py` - Performance benchmarks for various operations
- `test_load_stress.py` - Load and stress testing scenarios
- `test_profiling.py` - CPU and memory profiling
- `test_engine_performance.py` - Engine-specific performance tests
- `test_quality_features_performance.py` - Quality features performance tests
- `test_api_performance.py` - API endpoint performance tests ✅ **NEW**
- `performance_test_utils.py` - Performance testing utilities and helpers ✅ **NEW**

## Running Tests

### Run all performance tests:
```bash
pytest tests/performance/ -v
```

### Run specific test categories:
```bash
# Benchmarks only
pytest tests/performance/test_performance_benchmarks.py -v

# Load testing only
pytest tests/performance/test_load_stress.py -v

# Profiling only
pytest tests/performance/test_profiling.py -v
```

### Run with markers:
```bash
# Slow tests (stress tests)
pytest tests/performance/ -v -m slow
```

## Performance Baselines

Performance baselines are documented in test results. Key metrics:

- **Audio Processing**: < 0.1s for normalization, < 0.2s for resampling
- **Quality Metrics**: < 2.0s for full metrics, < 0.5s for MOS score
- **Memory Usage**: < 100MB for typical operations
- **Concurrent Requests**: > 10 requests/second

## Performance Test Utilities

The performance test suite includes utilities in `performance_test_utils.py`:

- **PerformanceTimer**: Context manager for timing operations
- **PerformanceBenchmark**: Benchmark utility with statistics (min, max, avg, median, P95, P99)
- **PerformanceMetrics**: Data class for performance metrics
- **LoadTester**: Load testing utility for concurrent requests

### Example Usage

```python
from tests.performance.performance_test_utils import PerformanceBenchmark

benchmark = PerformanceBenchmark("my_operation")
metrics = benchmark.run(my_function, iterations=10)
benchmark.assert_performance(metrics, max_avg_time=1.0)
```

## Dependencies

Required packages:
- `pytest`
- `numpy`
- `psutil`
- `cProfile` (built-in)
- `memory_profiler` (optional)
- `fastapi` (for API performance tests)

Install with:
```bash
pip install pytest numpy psutil memory-profiler fastapi
```

