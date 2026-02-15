"""
API Route Integration Tests.

Tests for the new API routes: diagnostics, errors, slo, tracing.
These tests verify the API endpoints work correctly with mocked services.
"""

import logging
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from .base import IntegrationTestBase, integration

logger = logging.getLogger(__name__)


# =============================================================================
# Diagnostics API Tests
# =============================================================================


class TestDiagnosticsAPI(IntegrationTestBase):
    """Tests for /diagnostics endpoints."""

    @pytest.fixture
    def mock_diagnostics_service(self):
        """Create mock diagnostics service."""
        mock_service = MagicMock()

        # Mock quick status
        mock_service.get_quick_status.return_value = {
            "timestamp": datetime.now().isoformat(),
            "hostname": "test-host",
            "platform": "Windows",
            "python_version": "3.9.13",
            "diagnostics_available": True,
        }

        # Mock diagnostic check
        mock_check = MagicMock()
        mock_check.name = "python_version"
        mock_check.category = "environment"
        mock_check.status = "pass"
        mock_check.message = "Python 3.9.13 detected"
        mock_check.details = {"version": "3.9.13"}
        mock_check.duration_ms = 1.5

        # Mock diagnostic report
        mock_report = MagicMock()
        mock_report.generated_at = datetime.now().isoformat()
        mock_report.hostname = "test-host"
        mock_report.platform = "Windows"
        mock_report.python_version = "3.9.13"
        mock_report.overall_status = "healthy"
        mock_report.checks = [mock_check]
        mock_report.environment = {"VOICESTUDIO_ROOT": "E:/VoiceStudio"}
        mock_report.recommendations = []

        mock_service.run_diagnostics.return_value = mock_report

        # Mock save_report
        mock_service.save_report.return_value = "/tmp/diagnostics_report.json"

        return mock_service

    @pytest.fixture
    def diagnostics_client(self, mock_diagnostics_service):
        """Create test client with mocked diagnostics service."""
        with patch(
            "backend.api.routes.diagnostics.get_diagnostics_service",
            return_value=mock_diagnostics_service,
        ):
            from fastapi import FastAPI

            from backend.api.routes.diagnostics import router

            app = FastAPI()
            app.include_router(router)

            yield TestClient(app)

    @integration
    def test_get_quick_status(self, diagnostics_client):
        """Test GET /diagnostics/status endpoint."""
        response = diagnostics_client.get("/diagnostics/status")

        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "hostname" in data
        assert data["diagnostics_available"] is True

    @integration
    def test_run_diagnostics(self, diagnostics_client):
        """Test GET /diagnostics/run endpoint."""
        response = diagnostics_client.get("/diagnostics/run")

        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        assert "checks" in data
        assert len(data["checks"]) >= 1

    @integration
    def test_run_diagnostics_with_sensitive(self, diagnostics_client, mock_diagnostics_service):
        """Test diagnostics with include_sensitive flag."""
        response = diagnostics_client.get("/diagnostics/run?include_sensitive=true")

        assert response.status_code == 200
        mock_diagnostics_service.run_diagnostics.assert_called_with(True)

    @integration
    def test_get_checks(self, diagnostics_client):
        """Test GET /diagnostics/checks endpoint."""
        response = diagnostics_client.get("/diagnostics/checks")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @integration
    def test_get_checks_with_filter(self, diagnostics_client):
        """Test checks filtering by category."""
        response = diagnostics_client.get("/diagnostics/checks?category=environment")

        assert response.status_code == 200

    @integration
    def test_get_categories(self, diagnostics_client):
        """Test GET /diagnostics/categories endpoint."""
        response = diagnostics_client.get("/diagnostics/categories")

        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "environment" in data["categories"]

    @integration
    def test_save_diagnostic_report(self, diagnostics_client):
        """Test POST /diagnostics/save endpoint."""
        response = diagnostics_client.post("/diagnostics/save")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "filepath" in data

    @integration
    def test_get_recommendations(self, diagnostics_client):
        """Test GET /diagnostics/recommendations endpoint."""
        response = diagnostics_client.get("/diagnostics/recommendations")

        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        assert "recommendations" in data

    @integration
    def test_get_environment_info(self, diagnostics_client):
        """Test GET /diagnostics/environment endpoint."""
        response = diagnostics_client.get("/diagnostics/environment")

        assert response.status_code == 200
        data = response.json()
        assert "environment" in data
        assert "hostname" in data


# =============================================================================
# Error Tracking API Tests
# =============================================================================


class TestErrorsAPI(IntegrationTestBase):
    """Tests for /errors endpoints."""

    @pytest.fixture
    def mock_error_tracker(self):
        """Create mock error tracker."""
        mock_tracker = MagicMock()

        # Create mock enum values
        mock_severity = MagicMock()
        mock_severity.value = "error"

        mock_category = MagicMock()
        mock_category.value = "api"

        # Mock tracked error
        mock_error = MagicMock()
        mock_error.error_id = "err-001"
        mock_error.fingerprint = "abc123"
        mock_error.timestamp = datetime.now().isoformat()
        mock_error.severity = mock_severity
        mock_error.category = mock_category
        mock_error.message = "Test error message"
        mock_error.exception_type = "ValueError"
        mock_error.stacktrace = None
        mock_error.context = None
        mock_error.tags = []
        mock_error.resolved = False

        # Mock aggregate
        mock_aggregate = MagicMock()
        mock_aggregate.fingerprint = "abc123"
        mock_aggregate.first_seen = datetime.now().isoformat()
        mock_aggregate.last_seen = datetime.now().isoformat()
        mock_aggregate.count = 5
        mock_aggregate.severity = mock_severity
        mock_aggregate.category = mock_category
        mock_aggregate.message = "Test error"
        mock_aggregate.exception_type = "ValueError"
        mock_aggregate.affected_endpoints = ["/api/test"]

        # Mock summary
        mock_summary = MagicMock()
        mock_summary.total_errors = 10
        mock_summary.unique_errors = 3
        mock_summary.errors_by_severity = {"error": 8, "warning": 2}
        mock_summary.errors_by_category = {"api": 7, "engine": 3}
        mock_summary.error_rate = 0.05
        mock_summary.top_errors = [mock_aggregate]

        mock_tracker.get_summary.return_value = mock_summary
        mock_tracker.get_errors.return_value = [mock_error]
        mock_tracker.get_aggregates.return_value = [mock_aggregate]
        mock_tracker.resolve_error.return_value = True
        mock_tracker.export_report.return_value = "/tmp/error_report.json"
        mock_tracker.clear_resolved.return_value = 3

        return mock_tracker

    @pytest.fixture
    def errors_client(self, mock_error_tracker):
        """Create test client with mocked error tracker."""
        with patch(
            "backend.api.routes.errors.get_error_tracker",
            return_value=mock_error_tracker,
        ):
            from fastapi import FastAPI

            from backend.api.routes.errors import router

            app = FastAPI()
            app.include_router(router)

            yield TestClient(app)

    @integration
    def test_get_error_summary(self, errors_client):
        """Test GET /errors/summary endpoint."""
        response = errors_client.get("/errors/summary")

        assert response.status_code == 200
        data = response.json()
        assert "total_errors" in data
        assert "unique_errors" in data
        assert "error_rate" in data

    @integration
    def test_get_recent_errors(self, errors_client):
        """Test GET /errors/recent endpoint."""
        response = errors_client.get("/errors/recent")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @integration
    def test_get_recent_errors_with_filter(self, errors_client, mock_error_tracker):
        """Test error filtering by severity."""
        response = errors_client.get("/errors/recent?severity=error&limit=50")

        assert response.status_code == 200

    @integration
    def test_get_error_aggregates(self, errors_client):
        """Test GET /errors/aggregates endpoint."""
        response = errors_client.get("/errors/aggregates")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @integration
    def test_get_error_categories(self, errors_client):
        """Test GET /errors/categories endpoint."""
        response = errors_client.get("/errors/categories")

        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "severities" in data

    @integration
    def test_resolve_error(self, errors_client):
        """Test POST /errors/{error_id}/resolve endpoint."""
        response = errors_client.post(
            "/errors/err-001/resolve",
            json={"resolution_notes": "Fixed in PR #123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @integration
    def test_resolve_error_not_found(self, errors_client, mock_error_tracker):
        """Test resolve for non-existent error."""
        mock_error_tracker.resolve_error.return_value = False

        response = errors_client.post(
            "/errors/nonexistent/resolve",
            json={"resolution_notes": ""},
        )

        assert response.status_code == 404

    @integration
    def test_export_error_report(self, errors_client):
        """Test POST /errors/export endpoint."""
        response = errors_client.post("/errors/export")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "filepath" in data

    @integration
    def test_clear_resolved_errors(self, errors_client):
        """Test DELETE /errors/resolved endpoint."""
        response = errors_client.delete("/errors/resolved")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["removed"] == 3

    @integration
    def test_get_error_rate(self, errors_client):
        """Test GET /errors/rate endpoint."""
        response = errors_client.get("/errors/rate")

        assert response.status_code == 200
        data = response.json()
        assert "error_rate" in data


# =============================================================================
# SLO API Tests
# =============================================================================


class TestSLOAPI(IntegrationTestBase):
    """Tests for /slo endpoints."""

    @pytest.fixture
    def mock_slo_monitor(self):
        """Create mock SLO monitor."""
        mock_monitor = MagicMock()

        # Mock severity enum
        mock_severity = MagicMock()
        mock_severity.value = "warning"

        # Mock SLO status
        mock_status = MagicMock()
        mock_status.slo_id = "api-latency"
        mock_status.slo_name = "API Latency SLO"
        mock_status.target = 99.0
        mock_status.current_value = 98.5
        mock_status.is_met = False
        mock_status.alert_severity = "warning"
        mock_status.window_hours = 24
        mock_status.sample_count = 1000
        mock_status.last_updated = datetime.now().isoformat()
        mock_status.burn_rate = 1.5
        mock_status.error_budget_remaining = 0.5

        # Mock alert
        mock_alert = MagicMock()
        mock_alert.alert_id = "alert-001"
        mock_alert.slo_id = "api-latency"
        mock_alert.slo_name = "API Latency SLO"
        mock_alert.severity = mock_severity
        mock_alert.message = "SLO breach detected"
        mock_alert.current_value = 98.5
        mock_alert.target = 99.0
        mock_alert.timestamp = datetime.now().isoformat()
        mock_alert.acknowledged = False
        mock_alert.acknowledged_by = None
        mock_alert.acknowledged_at = None
        mock_alert.resolved = False
        mock_alert.resolved_at = None

        mock_monitor.get_all_slo_statuses.return_value = [mock_status]
        mock_monitor.get_active_alerts.return_value = [mock_alert]
        mock_monitor.get_overall_health.return_value = "degraded"
        mock_monitor.get_slo_status.return_value = mock_status
        mock_monitor.get_alert_history.return_value = [mock_alert]
        mock_monitor.acknowledge_alert.return_value = True
        mock_monitor.export_status.return_value = "/tmp/slo_status.json"

        return mock_monitor

    @pytest.fixture
    def slo_client(self, mock_slo_monitor):
        """Create test client with mocked SLO monitor."""
        with patch(
            "backend.api.routes.slo.get_slo_monitor",
            return_value=mock_slo_monitor,
        ):
            from fastapi import FastAPI

            from backend.api.routes.slo import router

            app = FastAPI()
            app.include_router(router)

            yield TestClient(app)

    @integration
    def test_get_all_slos(self, slo_client):
        """Test GET /slo endpoint."""
        response = slo_client.get("/slo")

        assert response.status_code == 200
        data = response.json()
        assert "overview" in data
        assert "slos" in data
        assert data["overview"]["total_slos"] >= 1

    @integration
    def test_get_slo_health(self, slo_client):
        """Test GET /slo/health endpoint."""
        response = slo_client.get("/slo/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    @integration
    def test_get_slo_status(self, slo_client):
        """Test GET /slo/{slo_id} endpoint."""
        response = slo_client.get("/slo/api-latency")

        assert response.status_code == 200
        data = response.json()
        assert data["slo_id"] == "api-latency"
        assert "current_value" in data
        assert "target" in data

    @integration
    def test_get_slo_status_not_found(self, slo_client, mock_slo_monitor):
        """Test SLO not found."""
        mock_slo_monitor.get_slo_status.return_value = None

        response = slo_client.get("/slo/nonexistent")

        assert response.status_code == 404

    @integration
    def test_get_active_alerts(self, slo_client):
        """Test GET /slo/alerts/active endpoint."""
        response = slo_client.get("/slo/alerts/active")

        assert response.status_code == 200
        data = response.json()
        assert "active_count" in data
        assert "alerts" in data

    @integration
    def test_get_alert_history(self, slo_client):
        """Test GET /slo/alerts/history endpoint."""
        response = slo_client.get("/slo/alerts/history")

        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data

    @integration
    def test_acknowledge_alert(self, slo_client):
        """Test POST /slo/alerts/{alert_id}/acknowledge endpoint."""
        response = slo_client.post(
            "/slo/alerts/alert-001/acknowledge",
            json={"acknowledged_by": "tester"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @integration
    def test_acknowledge_alert_not_found(self, slo_client, mock_slo_monitor):
        """Test acknowledge for non-existent alert."""
        mock_slo_monitor.acknowledge_alert.return_value = False

        response = slo_client.post(
            "/slo/alerts/nonexistent/acknowledge",
            json={"acknowledged_by": "tester"},
        )

        assert response.status_code == 404

    @integration
    def test_export_slo_status(self, slo_client):
        """Test POST /slo/export endpoint."""
        response = slo_client.post("/slo/export")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @integration
    def test_record_metric(self, slo_client):
        """Test POST /slo/record/{metric_name} endpoint."""
        response = slo_client.post("/slo/record/api_latency_ms?value=150.5")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["metric_name"] == "api_latency_ms"


# =============================================================================
# Tracing API Tests
# =============================================================================


class TestTracingAPI(IntegrationTestBase):
    """Tests for /tracing endpoints."""

    @pytest.fixture
    def mock_span(self):
        """Create a mock span."""
        mock_status = MagicMock()
        mock_status.value = "ok"

        span = MagicMock()
        span.trace_id = "trace-001"
        span.span_id = "span-001"
        span.name = "api.request"
        span.duration_ms = 50.0
        span.status = mock_status
        span.parent_span_id = None
        span.error = None
        return span

    @pytest.fixture
    def mock_trace_exporter(self, mock_span):
        """Create mock trace exporter."""
        mock_exporter = MagicMock()

        mock_exporter.get_traces.return_value = [mock_span]

        # Mock summary
        mock_summary = MagicMock()
        mock_summary.total_traces = 10
        mock_summary.total_spans = 25
        mock_summary.avg_duration_ms = 45.0
        mock_summary.min_duration_ms = 10.0
        mock_summary.max_duration_ms = 200.0
        mock_summary.p50_duration_ms = 40.0
        mock_summary.p95_duration_ms = 150.0
        mock_summary.p99_duration_ms = 190.0
        mock_summary.error_rate = 0.02

        mock_exporter.calculate_summary.return_value = mock_summary
        mock_exporter.group_by_trace.return_value = {"trace-001": [mock_span]}
        mock_exporter.export_to_json.return_value = "/tmp/traces.json"

        return mock_exporter

    @pytest.fixture
    def mock_trace_analyzer(self, mock_span):
        """Create mock trace analyzer."""
        mock_analyzer = MagicMock()

        mock_analyzer.get_operation_stats.return_value = {
            "api.request": {
                "count": 100,
                "avg_ms": 45.0,
                "p50_ms": 40.0,
                "p95_ms": 150.0,
                "error_rate": 0.02,
            }
        }
        mock_analyzer.find_slow_spans.return_value = [mock_span]
        mock_analyzer.find_errors.return_value = []
        mock_analyzer.get_trace_tree.return_value = {
            "span_id": "span-001",
            "name": "api.request",
            "duration_ms": 50.0,
            "status": "ok",
            "children": [],
        }

        return mock_analyzer

    @pytest.fixture
    def tracing_client(self, mock_trace_exporter, mock_trace_analyzer):
        """Create test client with mocked tracing services."""
        with patch(
            "backend.api.routes.tracing.get_trace_exporter",
            return_value=mock_trace_exporter,
        ), patch(
            "backend.api.routes.tracing.get_trace_analyzer",
            return_value=mock_trace_analyzer,
        ):
            from fastapi import FastAPI

            from backend.api.routes.tracing import router

            app = FastAPI()
            app.include_router(router)

            yield TestClient(app)

    @integration
    def test_get_trace_summary(self, tracing_client):
        """Test GET /tracing/summary endpoint."""
        response = tracing_client.get("/tracing/summary")

        assert response.status_code == 200
        data = response.json()
        assert "total_traces" in data
        assert "total_spans" in data
        assert "avg_duration_ms" in data
        assert "error_rate" in data

    @integration
    def test_get_recent_spans(self, tracing_client):
        """Test GET /tracing/recent endpoint."""
        response = tracing_client.get("/tracing/recent")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @integration
    def test_get_recent_spans_with_filter(self, tracing_client):
        """Test spans filtering by operation."""
        response = tracing_client.get("/tracing/recent?operation=api&limit=50")

        assert response.status_code == 200

    @integration
    def test_get_operation_statistics(self, tracing_client):
        """Test GET /tracing/operations endpoint."""
        response = tracing_client.get("/tracing/operations")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "operation" in data[0]
            assert "count" in data[0]

    @integration
    def test_get_slow_spans(self, tracing_client):
        """Test GET /tracing/slow-spans endpoint."""
        response = tracing_client.get("/tracing/slow-spans?threshold_ms=100")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @integration
    def test_get_error_spans(self, tracing_client):
        """Test GET /tracing/errors endpoint."""
        response = tracing_client.get("/tracing/errors")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @integration
    def test_get_trace_tree(self, tracing_client):
        """Test GET /tracing/trace/{trace_id}/tree endpoint."""
        response = tracing_client.get("/tracing/trace/trace-001/tree")

        assert response.status_code == 200
        data = response.json()
        assert "span_id" in data
        assert "name" in data

    @integration
    def test_get_trace_tree_not_found(self, tracing_client, mock_trace_analyzer):
        """Test trace tree not found."""
        mock_trace_analyzer.get_trace_tree.return_value = None

        response = tracing_client.get("/tracing/trace/nonexistent/tree")

        assert response.status_code == 404

    @integration
    def test_export_traces(self, tracing_client):
        """Test POST /tracing/export endpoint."""
        response = tracing_client.post("/tracing/export")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "filepath" in data
        assert "trace_count" in data
