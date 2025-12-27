# Quality Features Integration Tests

Integration tests for quality testing and comparison features:
- A/B Testing
- Engine Recommendation
- Quality Benchmarking
- Quality Dashboard

## Running the Tests

### Prerequisites

1. Install test dependencies:
   ```bash
   pip install pytest pytest-cov fastapi testclient
   ```

2. Ensure the backend is accessible (tests use TestClient, so backend doesn't need to be running separately)

### Run All Tests

```bash
# From project root
pytest tests/integration/quality_features/ -v
```

### Run Specific Test File

```bash
# Test A/B Testing
pytest tests/integration/quality_features/test_ab_testing.py -v

# Test Engine Recommendation
pytest tests/integration/quality_features/test_engine_recommendation.py -v

# Test Quality Benchmarking
pytest tests/integration/quality_features/test_quality_benchmarking.py -v

# Test Quality Dashboard
pytest tests/integration/quality_features/test_quality_dashboard.py -v
```

### Run with Coverage

```bash
pytest tests/integration/quality_features/ --cov=backend.api.routes.quality --cov=backend.api.routes.eval_abx --cov-report=html
```

### Run Specific Test

```bash
pytest tests/integration/quality_features/test_ab_testing.py::TestABTesting::test_start_ab_test_success -v
```

## Test Structure

Each test file contains:

1. **Main Test Class**: Tests for happy paths and normal usage
2. **Error Handling Test Class**: Tests for error scenarios and edge cases

## Test Coverage

- ✅ A/B Testing endpoints (start, results)
- ✅ Engine Recommendation endpoint
- ✅ Quality Benchmarking endpoint
- ✅ Quality Dashboard endpoint
- ✅ Error handling scenarios
- ✅ Edge cases
- ✅ Input validation

## Notes

- Some tests may return 503 (Service Unavailable) if quality optimization modules are not available
- Some tests may return 404 if test data (profiles, audio) doesn't exist
- Tests use TestClient which doesn't require a running server
- Tests are designed to be fast and isolated

## Adding New Tests

When adding new tests:

1. Follow the existing test structure
2. Test both happy paths and error cases
3. Use descriptive test names
4. Add docstrings explaining what is being tested
5. Use fixtures from `conftest.py` when possible

