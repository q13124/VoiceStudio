# Integration Test Suite

Comprehensive integration tests for VoiceStudio Quantum+ backend systems.

## Test Categories

### Engine Workflows
- **test_engine_workflows.py** - Complete engine workflows
  - XTTS complete workflow
  - Engine lifecycle workflow
  - Batch synthesis workflow
  - Error recovery workflow

### API Workflows
- **test_api_workflows.py** - Complete API workflows
  - Profile creation workflow
  - Project workflow
  - Voice synthesis workflow
  - Batch processing workflow
  - Error handling workflow
  - Rate limiting workflow

### Audio Pipelines
- **test_audio_pipelines.py** - Complete audio processing pipelines
  - Preprocessing pipeline
  - Enhancement pipeline
  - Optimized batch pipeline
  - Quality metrics pipeline
  - Effects pipeline
  - Mastering pipeline
  - Complete audio workflow

### System Integration
- **test_system_integration.py** - System-wide integration
  - Database integration
  - Caching integration
  - Monitoring integration
  - Resilience integration
  - Complete system workflow

### Test Data Management
- **test_data_management.py** - Test data fixtures and helpers
  - Test audio generation
  - Test data creation
  - Test data loading/saving
  - Test data cleanup

## Running Tests

### Run All Integration Tests
```bash
pytest tests/integration/ -v
```

### Run Specific Test Category
```bash
pytest tests/integration/test_engine_workflows.py -v
pytest tests/integration/test_api_workflows.py -v
pytest tests/integration/test_audio_pipelines.py -v
pytest tests/integration/test_system_integration.py -v
```

### Run with Coverage
```bash
pytest tests/integration/ --cov=app --cov-report=html
```

## Requirements

- Backend API running on `http://localhost:8000`
- Required dependencies installed
- Test data available (optional)

## Test Data

Test data is managed by `TestDataManager` in `test_data_management.py`.

Test data directory: `tests/test_data/`

## Notes

- Some tests may skip if required modules are not available
- API tests require backend to be running
- Engine tests may require GPU (will fallback to CPU)

---

**Last Updated:** 2025-01-28

