"""
API Monitor - Proxy wrapper for monitoring backend API calls.

Intercepts all backend API calls during testing, logging request/response
details for debugging and validation purposes.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


class APIMonitor:
    """
    Proxy wrapper for monitoring backend API calls during UI tests.

    Logs all API calls with timing, request/response bodies, and status codes.
    Can be used standalone or integrated with WorkflowTracer.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout: float = 30.0,
        tracer=None
    ):
        """
        Initialize the API monitor.

        Args:
            base_url: Base URL for the backend API.
            timeout: Default request timeout in seconds.
            tracer: Optional WorkflowTracer instance for integrated logging.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.tracer = tracer
        self.call_log: list[dict[str, Any]] = []
        self._session = requests.Session()

    def request(
        self,
        method: str,
        endpoint: str,
        json_data: Any = None,
        data: Any = None,
        files: Any = None,
        params: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs
    ) -> requests.Response:
        """
        Make a request and log details.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (e.g., "/api/health")
            json_data: JSON body to send
            data: Form data to send
            files: Files to upload
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout (defaults to self.timeout)
            **kwargs: Additional arguments passed to requests

        Returns:
            requests.Response object
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.perf_counter()
        timestamp = datetime.now()

        # Merge headers
        request_headers = dict(headers) if headers else {}

        try:
            response = self._session.request(
                method=method.upper(),
                url=url,
                json=json_data,
                data=data,
                files=files,
                params=params,
                headers=request_headers,
                timeout=timeout or self.timeout,
                **kwargs
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Parse response body
            response_body = self._safe_json(response)

            # Log the call
            log_entry = {
                "method": method.upper(),
                "endpoint": endpoint,
                "url": url,
                "status": response.status_code,
                "elapsed_ms": elapsed_ms,
                "timestamp": timestamp.isoformat(),
                "request_body": self._safe_serialize(json_data or data),
                "request_params": params,
                "response_body": response_body,
                "response_headers": dict(response.headers),
                "success": response.status_code < 400,
            }
            self.call_log.append(log_entry)

            # Log to tracer if available
            if self.tracer:
                self.tracer.api_call(method.upper(), endpoint, response, json_data or data)

            return response

        except requests.RequestException as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Log failed call
            log_entry = {
                "method": method.upper(),
                "endpoint": endpoint,
                "url": url,
                "status": None,
                "elapsed_ms": elapsed_ms,
                "timestamp": timestamp.isoformat(),
                "request_body": self._safe_serialize(json_data or data),
                "request_params": params,
                "error": str(e),
                "error_type": type(e).__name__,
                "success": False,
            }
            self.call_log.append(log_entry)

            raise

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a GET request."""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a POST request."""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a PUT request."""
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a PATCH request."""
        return self.request("PATCH", endpoint, **kwargs)

    def health_check(self) -> bool:
        """
        Check if the backend is healthy.

        Returns:
            True if backend responds with 2xx status, False otherwise.
        """
        try:
            response = self.get("/api/health", timeout=5.0)
            return response.status_code < 300
        except Exception:
            return False

    def wait_for_backend(self, timeout: float = 30.0, poll_interval: float = 1.0) -> bool:
        """
        Wait for the backend to become available.

        Args:
            timeout: Maximum time to wait in seconds.
            poll_interval: Time between health checks.

        Returns:
            True if backend became available, False if timeout reached.
        """
        start_time = time.perf_counter()
        while (time.perf_counter() - start_time) < timeout:
            if self.health_check():
                return True
            time.sleep(poll_interval)
        return False

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of all API calls.

        Returns:
            Dictionary with call statistics.
        """
        if not self.call_log:
            return {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "avg_response_time_ms": 0,
            }

        successful = [c for c in self.call_log if c.get("success", False)]
        failed = [c for c in self.call_log if not c.get("success", True)]
        response_times = [c.get("elapsed_ms", 0) for c in self.call_log]

        # Group by endpoint
        by_endpoint: dict[str, list[dict]] = {}
        for call in self.call_log:
            key = f"{call['method']} {call['endpoint']}"
            if key not in by_endpoint:
                by_endpoint[key] = []
            by_endpoint[key].append(call)

        return {
            "total_calls": len(self.call_log),
            "successful_calls": len(successful),
            "failed_calls": len(failed),
            "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "by_endpoint": {
                key: {
                    "count": len(calls),
                    "avg_time_ms": sum(c.get("elapsed_ms", 0) for c in calls) / len(calls),
                    "success_rate": sum(1 for c in calls if c.get("success")) / len(calls),
                }
                for key, calls in by_endpoint.items()
            },
        }

    def export_log(self, output_path: Path) -> Path:
        """
        Export the call log to a JSON file.

        Args:
            output_path: Path to save the log.

        Returns:
            Path to the exported file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            "export_time": datetime.now().isoformat(),
            "base_url": self.base_url,
            "summary": self.get_summary(),
            "calls": self.call_log,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, default=str)

        return output_path

    def clear_log(self):
        """Clear the call log."""
        self.call_log.clear()

    def _safe_json(self, response: requests.Response) -> Any:
        """Safely parse JSON from response."""
        try:
            return response.json()
        except Exception:
            # Return truncated text for non-JSON responses
            text = response.text[:500] if response.text else None
            return text

    def _safe_serialize(self, obj: Any) -> Any:
        """Safely serialize an object to JSON-compatible format."""
        if obj is None:
            return None
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)[:1000]


class APIMonitorFixture:
    """
    Pytest fixture helper for API monitoring.

    Usage in conftest.py:
        @pytest.fixture
        def api_monitor():
            monitor = APIMonitor()
            yield monitor
            monitor.export_log(Path(".buildlogs/validation/api_calls.json"))
    """

    def __init__(self, output_dir: Path = Path(".buildlogs/validation")):
        self.output_dir = output_dir
        self.monitor: APIMonitor | None = None

    def create(self, base_url: str = "http://127.0.0.1:8000", tracer=None) -> APIMonitor:
        """Create a new API monitor."""
        self.monitor = APIMonitor(base_url=base_url, tracer=tracer)
        return self.monitor

    def cleanup(self, test_name: str = "api_calls"):
        """Export log and cleanup after test."""
        if self.monitor:
            self.monitor.export_log(self.output_dir / "api_coverage" / f"{test_name}.json")
            self.monitor = None
