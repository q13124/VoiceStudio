# End-to-End Test Workflows

End-to-end tests for complete user workflows in VoiceStudio Quantum+.

## Overview

These tests verify complete workflows from user interaction to final output, ensuring that all components work together correctly.

## Test Workflows

### A/B Testing Workflow

**File:** `test_ab_testing_workflow.py`

Tests the complete A/B testing workflow:
1. Start A/B test with audio items
2. Retrieve test results
3. Analyze and compare results
4. Error recovery scenarios

**Run:**
```bash
pytest tests/e2e/test_ab_testing_workflow.py -v
```

### Engine Recommendation Workflow

**File:** `test_engine_recommendation_workflow.py`

Tests the complete engine recommendation workflow:
1. Set quality requirements
2. Get engine recommendation
3. Use recommendation for synthesis
4. Test multiple quality tiers
5. Adjust requirements dynamically

**Run:**
```bash
pytest tests/e2e/test_engine_recommendation_workflow.py -v
```

### Quality Benchmarking Workflow

**File:** `test_quality_benchmarking_workflow.py`

Tests the complete quality benchmarking workflow:
1. Set up benchmark parameters
2. Run benchmark across engines
3. Analyze and compare results
4. Identify best engine
5. Test with multiple texts
6. Error recovery

**Run:**
```bash
pytest tests/e2e/test_quality_benchmarking_workflow.py -v
```

## Running All E2E Tests

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Run with coverage
pytest tests/e2e/ --cov=backend.api.routes --cov-report=html

# Run with verbose output
pytest tests/e2e/ -v -s
```

## Test Structure

Each E2E test file contains:

1. **Complete Workflow Test**: Tests the full workflow from start to finish
2. **Multiple Scenario Test**: Tests workflow with variations
3. **Error Recovery Test**: Tests workflow with error handling and recovery

## Prerequisites

- Backend API accessible (tests use TestClient)
- Test data may be required (profiles, audio files)
- Some tests may require engines to be available

## Notes

- E2E tests are slower than unit/integration tests
- Some tests may return 503 if services are not available
- Tests are designed to be independent and can run in any order
- Tests use print statements for workflow visibility (use `-s` flag with pytest)

## Adding New E2E Tests

When adding new E2E tests:

1. Create a new test file: `test_<feature>_workflow.py`
2. Follow the existing test structure
3. Test complete workflows, not just individual steps
4. Include error recovery scenarios
5. Use descriptive test names and docstrings
6. Add print statements for workflow visibility

