# Performance Test Suite

Comprehensive performance testing for VoiceStudio including benchmarks, load testing, stress testing, and profiling.

## Test Files

| File | Description |
|------|-------------|
| `test_performance_benchmarks.py` | Performance benchmarks for various operations |
| `test_load_stress.py` | Load and stress testing scenarios |
| `test_profiling.py` | CPU and memory profiling |
| `test_engine_performance.py` | Engine-specific performance tests |
| `test_quality_features_performance.py` | Quality features performance tests |
| `test_api_performance.py` | API endpoint performance tests |
| `test_expanded_performance.py` | Extended performance tests |
| `performance_test_utils.py` | Performance testing utilities and helpers |
| `conftest.py` | Pytest fixtures and report collection |
| `generate_report.py` | Performance report generator (HTML/Markdown/JSON) |

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

## Report Generation

Generate performance reports in HTML, Markdown, or JSON format:

```bash
# Generate HTML report from latest results
python tests/performance/generate_report.py --format html

# Compare against baseline
python tests/performance/generate_report.py --baseline .buildlogs/performance/baselines.json

# Custom output path
python tests/performance/generate_report.py --output report.html --format html

# Markdown format
python tests/performance/generate_report.py --format markdown
```

### Report Features

- Summary statistics (total, passed, failed)
- Regression detection against baseline
- Configurable threshold (default: 20% regression)
- Visual HTML report with tables

## CI Integration

Performance tests run in CI via `.github/workflows/test.yml`:

- **Trigger**: `workflow_dispatch` or release branches
- **Output**: Reports saved as artifacts
- **Duration**: ~30 minutes (excludes slow tests by default)

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
pip install pytest numpy psutil memory-profiler fastapi pytest-html
```

