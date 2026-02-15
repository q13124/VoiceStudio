"""
Sentinel Audio Workflow Integration Tests

This module provides pytest integration for the deterministic sentinel
workflow runner, validating the complete VoiceStudio pipeline.

Phase 1 Implementation - Sentinel Infrastructure
Based on: docs/design/DETERMINISTIC_SENTINEL_IMPLEMENTATION_PLAN.md

Usage:
    # Run all sentinel tests
    pytest tests/sentinel/ -v

    # Run only smoke tests
    pytest tests/sentinel/ -v -m smoke

    # Run with backend (requires running server)
    pytest tests/sentinel/ -v -m backend_required

    # Run schema validation only (no backend needed)
    pytest tests/sentinel/test_sentinel_audio_workflow.py::TestSchemaValidation -v
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.proof_runs.sentinel_audio_workflow import (
    CONTRACTS_DIR,
    STEP_TIMEOUTS,
    ReproPacket,
    SchemaValidator,
    SentinelRunner,
    StepResult,
    StepStatus,
)

# Module-level markers
pytestmark = [
    pytest.mark.sentinel,
]


# -----------------------------------------------------------------------------
# Schema Validation Tests (No Backend Required)
# -----------------------------------------------------------------------------

@pytest.mark.smoke
class TestSchemaValidation:
    """Test schema validation without requiring backend."""

    def test_validator_loads_schemas(self):
        """Verify all expected schemas are loaded."""
        validator = SchemaValidator(PROJECT_ROOT / CONTRACTS_DIR)

        expected_schemas = [
            "health_response",
            "upload_response",
            "tts_request",
            "tts_response",
            "job_response",
            "ab_summary_response",
        ]

        for schema_name in expected_schemas:
            assert schema_name in validator._schemas, (
                f"Schema not loaded: {schema_name}"
            )

    def test_health_response_valid(self, sample_health_response: dict):
        """Test valid health response passes validation."""
        validator = SchemaValidator(PROJECT_ROOT / CONTRACTS_DIR)
        is_valid, errors = validator.validate("health_response", sample_health_response)

        assert is_valid, f"Validation failed: {errors}"
        assert len(errors) == 0

    def test_health_response_missing_required(self):
        """Test health response with missing required field fails."""
        validator = SchemaValidator(PROJECT_ROOT / CONTRACTS_DIR)

        invalid_response = {
            "status": "healthy",
            # missing: timestamp, uptime_seconds, version
        }

        is_valid, errors = validator.validate("health_response", invalid_response)

        assert not is_valid
        assert len(errors) > 0

    def test_upload_response_valid(self, sample_upload_response: dict):
        """Test valid upload response passes validation."""
        validator = SchemaValidator(PROJECT_ROOT / CONTRACTS_DIR)
        is_valid, errors = validator.validate("upload_response", sample_upload_response)

        assert is_valid, f"Validation failed: {errors}"

    def test_tts_response_valid(self, sample_tts_response: dict):
        """Test valid TTS response passes validation."""
        validator = SchemaValidator(PROJECT_ROOT / CONTRACTS_DIR)
        is_valid, errors = validator.validate("tts_response", sample_tts_response)

        assert is_valid, f"Validation failed: {errors}"

    def test_tts_response_quality_score_bounds(self):
        """Test quality score must be between 0 and 1."""
        validator = SchemaValidator(PROJECT_ROOT / CONTRACTS_DIR)

        invalid_response = {
            "audio_id": "test",
            "audio_url": "/test",
            "duration": 1.0,
            "quality_score": 1.5,  # Invalid: > 1
        }

        is_valid, errors = validator.validate("tts_response", invalid_response)

        assert not is_valid
        assert any("quality_score" in str(e) for e in errors)


# -----------------------------------------------------------------------------
# Step Result Tests (Unit Tests)
# -----------------------------------------------------------------------------

@pytest.mark.smoke
class TestStepResult:
    """Test StepResult dataclass behavior."""

    def test_step_result_to_dict(self):
        """Test StepResult serialization."""
        result = StepResult(
            step_name="test_step",
            step_index=1,
            status=StepStatus.PASSED,
            started_at="2026-02-12T10:00:00Z",
            completed_at="2026-02-12T10:00:01Z",
            duration_ms=1000.0,
            response={"key": "value"},
        )

        d = result.to_dict()

        assert d["step_name"] == "test_step"
        assert d["step_index"] == 1
        assert d["status"] == "passed"
        assert d["duration_ms"] == 1000.0
        assert d["response_hash"] is not None

    def test_step_result_hash_determinism(self):
        """Test response hash is deterministic."""
        response = {"foo": "bar", "baz": 123}

        result1 = StepResult(
            step_name="test",
            step_index=1,
            status=StepStatus.PASSED,
            started_at="2026-02-12T10:00:00Z",
            response=response,
        )

        result2 = StepResult(
            step_name="test",
            step_index=1,
            status=StepStatus.PASSED,
            started_at="2026-02-12T10:00:00Z",
            response=response,
        )

        # Same response should produce same hash
        assert result1.to_dict()["response_hash"] == result2.to_dict()["response_hash"]


# -----------------------------------------------------------------------------
# Runner Configuration Tests
# -----------------------------------------------------------------------------

@pytest.mark.smoke
class TestRunnerConfiguration:
    """Test SentinelRunner configuration and initialization."""

    def test_runner_generates_unique_run_ids(self):
        """Test that each runner gets a unique run ID."""
        runner1 = SentinelRunner()
        runner2 = SentinelRunner()

        assert runner1.run_id != runner2.run_id

    def test_runner_run_id_format(self):
        """Test run ID follows expected format."""
        runner = SentinelRunner()

        # Format: YYYYMMDD-HHMMSS-{hash}
        parts = runner.run_id.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 8  # YYYYMMDD
        assert len(parts[1]) == 6  # HHMMSS
        assert len(parts[2]) == 8  # hash

    def test_step_timeouts_defined(self):
        """Test all expected step timeouts are defined."""
        expected_steps = [
            "health", "upload", "sync_synth", "async_synth",
            "poll_job", "ab_test", "eval"
        ]

        for step in expected_steps:
            assert step in STEP_TIMEOUTS, f"Missing timeout for step: {step}"
            assert STEP_TIMEOUTS[step] > 0

    def test_runner_custom_api_base(self):
        """Test runner accepts custom API base."""
        custom_base = "http://localhost:9000"
        runner = SentinelRunner(api_base=custom_base)

        assert runner.api_base == custom_base

    def test_runner_strips_trailing_slash(self):
        """Test API base trailing slash is stripped."""
        runner = SentinelRunner(api_base="http://localhost:8000/")

        assert runner.api_base == "http://localhost:8000"


# -----------------------------------------------------------------------------
# Integration Tests (Require Backend)
# -----------------------------------------------------------------------------

@pytest.mark.backend_required
@pytest.mark.slow
class TestSentinelWorkflow:
    """Integration tests requiring a running backend server."""

    @pytest.mark.asyncio
    async def test_health_check_step(
        self,
        sentinel_runner: SentinelRunner,
        backend_available: bool,
    ):
        """Test health check step executes successfully."""
        if not backend_available:
            pytest.skip("Backend not available")

        result = await sentinel_runner._step_health()

        assert result.step_name == "health"
        assert result.step_index == 1
        assert result.status == StepStatus.PASSED
        assert result.response is not None
        assert result.duration_ms is not None
        assert result.duration_ms < STEP_TIMEOUTS["health"] * 1000

    @pytest.mark.asyncio
    async def test_full_workflow_execution(
        self,
        completed_run: ReproPacket,
    ):
        """Test complete workflow execution produces valid repro packet."""
        assert completed_run is not None
        assert completed_run.run_id is not None
        assert completed_run.total_steps == 7
        assert completed_run.overall_status in ["passed", "partial", "failed"]

        # Verify all steps have results
        assert len(completed_run.steps) == 7

        # Verify invariants are computed
        assert "health_check_passed" in completed_run.invariants
        assert "all_schemas_valid" in completed_run.invariants

    @pytest.mark.asyncio
    async def test_artifacts_created(
        self,
        sentinel_runner: SentinelRunner,
        backend_available: bool,
    ):
        """Test that artifacts are created after run."""
        if not backend_available:
            pytest.skip("Backend not available")

        packet = await sentinel_runner.run()

        # Check run directory exists
        assert sentinel_runner.run_dir.exists()

        # Check summary.json exists
        summary_path = sentinel_runner.run_dir / "summary.json"
        assert summary_path.exists()

        # Check steps.jsonl exists
        steps_path = sentinel_runner.run_dir / "steps.jsonl"
        assert steps_path.exists()

        # Verify summary is valid JSON
        with open(summary_path) as f:
            summary = json.load(f)
            assert summary["run_id"] == packet.run_id
            assert "step_counts" in summary

    @pytest.mark.asyncio
    async def test_step_correlation_ids(
        self,
        sentinel_runner: SentinelRunner,
        backend_available: bool,
    ):
        """Test that all steps share the same correlation ID."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Verify correlation ID is set
        assert sentinel_runner._correlation_id is not None

        # Run health check to verify correlation header is sent
        await sentinel_runner._step_health()

        # Correlation ID should be a valid UUID
        import uuid
        try:
            uuid.UUID(sentinel_runner._correlation_id)
        except ValueError:
            pytest.fail("Correlation ID is not a valid UUID")


# -----------------------------------------------------------------------------
# Repro Packet Tests
# -----------------------------------------------------------------------------

@pytest.mark.smoke
class TestReproPacket:
    """Test ReproPacket generation and serialization."""

    def test_repro_packet_to_summary(self):
        """Test ReproPacket summary generation."""
        packet = ReproPacket(
            run_id="test-run-id",
            started_at="2026-02-12T10:00:00Z",
            completed_at="2026-02-12T10:01:00Z",
            duration_ms=60000,
            api_base="http://localhost:8000",
            fixture_hash="abc123",
            overall_status="passed",
            passed_steps=7,
            failed_steps=0,
            skipped_steps=0,
            total_steps=7,
            steps=[],
            invariants={"health_check_passed": True},
            artifacts=[],
        )

        summary = packet.to_summary()

        assert summary["run_id"] == "test-run-id"
        assert summary["overall_status"] == "passed"
        assert summary["step_counts"]["passed"] == 7
        assert summary["step_counts"]["failed"] == 0
        assert summary["invariants"]["health_check_passed"] is True


# -----------------------------------------------------------------------------
# Parameterized Tests
# -----------------------------------------------------------------------------

@pytest.mark.smoke
class TestSchemaValidationParameterized:
    """Parameterized schema validation tests."""

    @pytest.mark.parametrize("schema_name,valid_data", [
        ("health_response", {
            "status": "healthy",
            "timestamp": "2026-02-12T10:00:00Z",
            "uptime_seconds": 0,
            "version": "1.0.0",
        }),
        ("health_response", {
            "status": "degraded",
            "timestamp": "2026-02-12T10:00:00Z",
            "uptime_seconds": 3600,
            "version": "2.0.0-beta",
            "checks": [],
        }),
        ("upload_response", {
            "id": "abc",
            "filename": "test.wav",
            "path": "/path/to/file",
            "size": 1024,
        }),
        ("tts_response", {
            "audio_id": "synth123",
            "audio_url": "/download/synth123",
            "duration": 5.5,
            "quality_score": 0.95,
        }),
    ])
    def test_valid_schema_variations(self, schema_name: str, valid_data: dict):
        """Test various valid schema variations pass validation."""
        validator = SchemaValidator(PROJECT_ROOT / CONTRACTS_DIR)
        is_valid, errors = validator.validate(schema_name, valid_data)

        assert is_valid, f"Schema {schema_name} failed: {errors}"

    @pytest.mark.parametrize("schema_name,invalid_data,expected_error_field", [
        ("health_response", {"status": "invalid_status"}, "status"),
        ("tts_response", {"audio_id": "", "audio_url": "", "duration": -1, "quality_score": 0.5}, "duration"),
        ("job_response", {"id": "x", "name": "y", "type": "invalid", "status": "pending", "progress": 0, "created": "2026-01-01"}, "type"),
    ])
    def test_invalid_schema_variations(
        self,
        schema_name: str,
        invalid_data: dict,
        expected_error_field: str,
    ):
        """Test various invalid schema variations fail validation."""
        validator = SchemaValidator(PROJECT_ROOT / CONTRACTS_DIR)
        is_valid, errors = validator.validate(schema_name, invalid_data)

        # Should fail validation
        assert not is_valid or len(errors) > 0


# -----------------------------------------------------------------------------
# Mocked Unit Tests (No Backend Required)
# -----------------------------------------------------------------------------

@pytest.mark.smoke
class TestMockedWorkflowSteps:
    """Unit tests with mocked HTTP responses - no backend required."""

    @pytest.fixture
    def mock_response_factory(self):
        """Create mock response objects."""
        def _create_response(status_code: int, json_data: dict):
            response = MagicMock()
            response.status_code = status_code
            response.json.return_value = json_data
            response.text = json.dumps(json_data)
            return response
        return _create_response

    @pytest.mark.asyncio
    async def test_health_step_success_mocked(self, mock_response_factory, tmp_path: Path):
        """Test health step with mocked successful response."""
        mock_response = mock_response_factory(200, {
            "status": "healthy",
            "timestamp": "2026-02-12T10:00:00Z",
            "uptime_seconds": 3600,
            "version": "1.0.0",
        })

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            runner = SentinelRunner(
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            async with runner:
                result = await runner._step_health()

            assert result.status == StepStatus.PASSED
            assert result.step_name == "health"
            assert result.response["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_step_timeout_mocked(self, tmp_path: Path):
        """Test health step handles timeout correctly."""
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Request timed out")

            runner = SentinelRunner(
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            async with runner:
                result = await runner._step_health()

            assert result.status == StepStatus.FAILED
            assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_upload_step_success_mocked(self, mock_response_factory, tmp_path: Path):
        """Test upload step with mocked successful response."""
        # Create a test fixture file
        fixture_path = tmp_path / "test.wav"
        fixture_path.write_bytes(b"RIFF" + b"\x00" * 100)

        mock_response = mock_response_factory(201, {
            "id": "upload_123",
            "filename": "test.wav",
            "path": "/data/audio/upload_123.wav",
            "size": 104,
        })

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            runner = SentinelRunner(
                fixture_path=fixture_path,
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            async with runner:
                result = await runner._step_upload()

            assert result.status == StepStatus.PASSED
            assert runner._upload_id == "upload_123"

    @pytest.mark.asyncio
    async def test_upload_step_missing_fixture(self, tmp_path: Path):
        """Test upload step skips when fixture is missing."""
        runner = SentinelRunner(
            fixture_path=tmp_path / "nonexistent.wav",
            artifacts_dir=tmp_path / "artifacts",
            enable_circuit_breaker=False,
        )
        async with runner:
            result = await runner._step_upload()

        assert result.status == StepStatus.SKIPPED
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_sync_synth_step_success_mocked(self, mock_response_factory, tmp_path: Path):
        """Test sync synthesis step with mocked response."""
        mock_response = mock_response_factory(200, {
            "audio_id": "synth_456",
            "audio_url": "/api/audio/synth_456/download",
            "duration": 2.5,
            "quality_score": 0.85,
        })

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            runner = SentinelRunner(
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            runner._upload_id = "upload_123"  # Simulate previous step

            async with runner:
                result = await runner._step_sync_synth()

            assert result.status == StepStatus.PASSED
            assert runner._sync_audio_id == "synth_456"

    @pytest.mark.asyncio
    async def test_sync_synth_skipped_without_upload(self, tmp_path: Path):
        """Test sync synthesis skips when no upload ID."""
        runner = SentinelRunner(
            artifacts_dir=tmp_path / "artifacts",
            enable_circuit_breaker=False,
        )
        async with runner:
            result = await runner._step_sync_synth()

        assert result.status == StepStatus.SKIPPED
        assert "upload ID" in result.error

    @pytest.mark.asyncio
    async def test_async_synth_step_success_mocked(self, mock_response_factory, tmp_path: Path):
        """Test async synthesis job creation with mocked response."""
        mock_response = mock_response_factory(201, {
            "id": "job_789",
            "name": "sentinel_batch_test",
            "status": "pending",
        })

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            runner = SentinelRunner(
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            async with runner:
                result = await runner._step_async_synth()

            assert result.status == StepStatus.PASSED
            assert runner._async_job_id == "job_789"

    @pytest.mark.asyncio
    async def test_poll_job_success_mocked(self, mock_response_factory, tmp_path: Path):
        """Test job polling with mocked completion response."""
        mock_response = mock_response_factory(200, {
            "id": "job_789",
            "status": "completed",
            "result_id": "result_abc",
        })

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            runner = SentinelRunner(
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            runner._async_job_id = "job_789"

            async with runner:
                result = await runner._step_poll_job()

            assert result.status == StepStatus.PASSED
            assert runner._async_audio_id == "result_abc"

    @pytest.mark.asyncio
    async def test_ab_test_step_success_mocked(self, mock_response_factory, tmp_path: Path):
        """Test A/B test step with mocked response."""
        mock_response = mock_response_factory(200, {
            "test_id": "ab_test_123",
            "sample_a": {
                "sample_label": "A",
                "audio_id": "a_audio",
                "audio_url": "/audio/a",
                "engine": "piper",
                "duration": 2.0,
            },
            "sample_b": {
                "sample_label": "B",
                "audio_id": "b_audio",
                "audio_url": "/audio/b",
                "engine": "xtts_v2",
                "duration": 2.1,
            },
        })

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            runner = SentinelRunner(
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            async with runner:
                result = await runner._step_ab_test()

            assert result.status == StepStatus.PASSED
            assert runner._ab_test_id == "ab_test_123"

    @pytest.mark.asyncio
    async def test_eval_step_success_mocked(self, mock_response_factory, tmp_path: Path):
        """Test evaluation step with mocked response."""
        mock_response = mock_response_factory(200, {
            "audio_id": "synth_456",
            "analysis": {
                "quality_score": 0.9,
                "mos_estimate": 4.2,
            },
        })

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            runner = SentinelRunner(
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            runner._sync_audio_id = "synth_456"

            async with runner:
                result = await runner._step_eval()

            assert result.status == StepStatus.PASSED


# -----------------------------------------------------------------------------
# Error Scenario Tests
# -----------------------------------------------------------------------------

@pytest.mark.smoke
class TestErrorScenarios:
    """Test error handling for various HTTP error scenarios."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code,expected_status", [
        (400, StepStatus.FAILED),
        (401, StepStatus.FAILED),
        (403, StepStatus.FAILED),
        (404, StepStatus.FAILED),
        (500, StepStatus.FAILED),
        (502, StepStatus.FAILED),
        (503, StepStatus.FAILED),
    ])
    async def test_error_status_codes(
        self,
        status_code: int,
        expected_status: StepStatus,
        tmp_path: Path,
    ):
        """Test handling of various HTTP error codes."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"error": f"Error {status_code}"}
        mock_response.text = f"Error {status_code}"

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            runner = SentinelRunner(
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            async with runner:
                result = await runner._step_health()

            assert result.status == expected_status

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_class,exception_message", [
        (httpx.ConnectError, "Connection refused"),
        (httpx.ConnectTimeout, "Connection timed out"),
        (httpx.TimeoutException, "Request timed out"),
        (httpx.NetworkError, "Network unreachable"),
    ])
    async def test_network_failures(
        self,
        exception_class: type,
        exception_message: str,
        tmp_path: Path,
    ):
        """Test handling of various network-level failures."""
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = exception_class(exception_message)

            runner = SentinelRunner(
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            async with runner:
                result = await runner._step_health()

            assert result.status == StepStatus.FAILED
            assert result.error is not None

    @pytest.mark.asyncio
    async def test_malformed_json_response(self, tmp_path: Path):
        """Test handling of malformed JSON response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Not valid JSON {"

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            runner = SentinelRunner(
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            async with runner:
                result = await runner._step_health()

            # Should still process but may fail schema validation
            assert result.response is not None
            assert "raw_text" in result.response

    @pytest.mark.asyncio
    async def test_schema_validation_failure(self, tmp_path: Path):
        """Test handling of schema validation failure."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "invalid_status_value",  # Invalid enum value
            "timestamp": "not-a-timestamp",
        }
        mock_response.text = "{}"

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            runner = SentinelRunner(
                artifacts_dir=tmp_path / "artifacts",
                enable_circuit_breaker=False,
            )
            async with runner:
                result = await runner._step_health()

            assert result.status == StepStatus.FAILED
            assert len(result.validation_errors) > 0


# -----------------------------------------------------------------------------
# Circuit Breaker Tests
# -----------------------------------------------------------------------------

@pytest.mark.smoke
class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self, tmp_path: Path):
        """Test circuit breaker opens after threshold failures."""
        from scripts.proof_runs.sentinel_audio_workflow import SimpleCircuitBreaker

        breaker = SimpleCircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0,
        )

        # Record failures
        for _ in range(3):
            breaker.record_failure()

        assert breaker.state == "open"
        assert not breaker.allow_request()

    @pytest.mark.asyncio
    async def test_circuit_breaker_recovers(self, tmp_path: Path):
        """Test circuit breaker recovers after timeout."""
        import time

        from scripts.proof_runs.sentinel_audio_workflow import SimpleCircuitBreaker

        breaker = SimpleCircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,  # Very short for testing
        )

        # Trip the breaker
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == "open"

        # Wait for recovery timeout
        time.sleep(0.15)

        # Should allow request (half-open)
        assert breaker.allow_request()
        assert breaker.state == "half_open"

    @pytest.mark.asyncio
    async def test_circuit_breaker_closes_after_success(self, tmp_path: Path):
        """Test circuit breaker closes after successful requests."""
        import time

        from scripts.proof_runs.sentinel_audio_workflow import SimpleCircuitBreaker

        breaker = SimpleCircuitBreaker(
            failure_threshold=2,
            success_threshold=2,
            recovery_timeout=0.1,
        )

        # Trip the breaker
        breaker.record_failure()
        breaker.record_failure()

        # Wait and allow recovery
        time.sleep(0.15)
        breaker.allow_request()  # Transitions to half-open

        # Record successes
        breaker.record_success()
        breaker.record_success()

        assert breaker.state == "closed"
