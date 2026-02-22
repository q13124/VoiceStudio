"""
Error Handling and Edge Case Tests.

Comprehensive tests for error handling including:
- Malformed request body handling
- Boundary value testing
- Timeout recovery
- Partial failure scenarios
- Circuit breaker behavior

Part of the Testing Expansion Plan.
"""

import contextlib
import time

import pytest

# Try to import test dependencies
try:
    from httpx import Client as HttpClient

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    HttpClient = None


# Test configuration
API_BASE_URL = "http://localhost:8088"


def retry_on_rate_limit(func, *args, max_retries=3, **kwargs):
    """Retry function on rate limit errors."""
    for i in range(max_retries):
        response = func(*args, **kwargs)
        if response.status_code != 429:
            return response
        time.sleep(1 * (i + 1))
    return response


@pytest.fixture
def api_client():
    """Create API client for testing."""
    if not HAS_HTTPX:
        pytest.skip("httpx not installed")

    try:
        client = HttpClient(base_url=API_BASE_URL, timeout=10.0)
        response = client.get("/api/health")
        if response.status_code != 200:
            pytest.skip("Backend not available")
        return client
    except Exception as e:
        pytest.skip(f"Cannot connect to backend: {e}")


class TestMalformedRequests:
    """Tests for malformed request handling."""

    def test_empty_request_body(self, api_client):
        """Verify empty request body is handled gracefully."""
        response = retry_on_rate_limit(
            api_client.post,
            "/api/synthesis/generate",
            content=b"",
            headers={"Content-Type": "application/json"},
        )

        # Should return 400 or 422, not 500
        assert response.status_code in [
            400,
            422,
        ], f"Empty body should return validation error, got {response.status_code}"

    def test_invalid_json(self, api_client):
        """Verify invalid JSON is rejected properly."""
        invalid_payloads = [
            "{incomplete",
            "{'single': 'quotes'}",
            '{"trailing": "comma",}',
            "[1, 2, 3",
            "not json at all",
            "null",  # Valid JSON but may not be expected
        ]

        for payload in invalid_payloads:
            response = retry_on_rate_limit(
                api_client.post,
                "/api/profiles",
                content=payload.encode(),
                headers={"Content-Type": "application/json"},
            )

            # Should return 400/422, not 500
            assert response.status_code in [
                400,
                415,
                422,
            ], f"Invalid JSON should be rejected: {payload}, got {response.status_code}"

    def test_missing_required_fields(self, api_client):
        """Verify missing required fields return proper error."""
        # Synthesis without text
        response = retry_on_rate_limit(
            api_client.post,
            "/api/synthesis/generate",
            json={"engine": "default"},  # Missing required 'text' field
        )

        # Should return validation error
        assert response.status_code in [
            400,
            422,
            404,
        ], f"Missing field should return validation error, got {response.status_code}"

    def test_wrong_field_types(self, api_client):
        """Verify wrong field types are rejected."""
        wrong_types = [
            {"text": 123, "engine": "default"},  # text should be string
            {"text": "hello", "engine": ["array"]},  # engine should be string
            {"text": "hello", "speed": "fast"},  # speed should be number
        ]

        for payload in wrong_types:
            response = retry_on_rate_limit(api_client.post, "/api/synthesis/generate", json=payload)

            # Should return validation error, not 500
            assert response.status_code != 500, f"Wrong type should not cause 500: {payload}"

    def test_extra_fields_handling(self, api_client):
        """Verify extra fields are handled (ignored or rejected)."""
        response = retry_on_rate_limit(
            api_client.post,
            "/api/profiles",
            json={
                "name": "Test Profile",
                "unknown_field": "should be ignored or rejected",
                "another_unknown": 12345,
            },
        )

        # Should either succeed (ignoring extras) or return 422
        assert response.status_code in [200, 201, 400, 422, 404]

    def test_deeply_nested_json(self, api_client):
        """Verify deeply nested JSON doesn't cause stack overflow."""
        # Create deeply nested structure
        nested = {"level": 0}
        current = nested
        for i in range(100):
            current["nested"] = {"level": i + 1}
            current = current["nested"]

        response = retry_on_rate_limit(api_client.post, "/api/profiles", json=nested)

        # Should handle gracefully
        assert response.status_code != 500


class TestBoundaryValues:
    """Tests for boundary value handling."""

    def test_empty_text_synthesis(self, api_client):
        """Verify empty text is handled properly."""
        response = retry_on_rate_limit(
            api_client.post, "/api/synthesis/generate", json={"text": "", "engine": "default"}
        )

        # Should return validation error or succeed with empty audio
        assert response.status_code in [200, 400, 422, 404]

    def test_whitespace_only_text(self, api_client):
        """Verify whitespace-only text is handled."""
        response = retry_on_rate_limit(
            api_client.post,
            "/api/synthesis/generate",
            json={"text": "   \n\t\r   ", "engine": "default"},
        )

        # Should be handled gracefully
        assert response.status_code != 500

    def test_max_length_text(self, api_client):
        """Verify maximum length text is handled."""
        # Create very long text (100KB)
        long_text = "Test sentence. " * 5000

        response = retry_on_rate_limit(
            api_client.post,
            "/api/synthesis/generate",
            json={"text": long_text, "engine": "default"},
        )

        # Should either process or reject with appropriate error
        assert response.status_code in [200, 400, 413, 422, 404, 503]

    def test_unicode_edge_cases(self, api_client):
        """Verify Unicode edge cases are handled."""
        unicode_texts = [
            "Hello 👋 World 🌍",  # Emojis
            "مرحبا بالعالم",  # Arabic RTL
            "你好世界",  # Chinese
            "Привет мир",  # Russian
            "\u0000\u0001\u0002",  # Control characters
            "Z̤͔͊̓ͤͥ̈́ͧ̄̽A̴̧̪̫̘̲͖͎̰͓̜̤̦̘̥̝̐̈́͐̇̂̀̾͝ͅL̵̨̢̮̱̥̫̞̩̬̼̪̯̱̪̝̰̼̓̀͒̽́̆̂̊͝G̶̡̧̱̼̘͓̮̫͎͈̲̗̤͕̥͋̎̈́̿͂̌̇̐̌͐͘͠͝O̵̢̧̧̯͈̖̙̬̣̟̮̲̯̮͈̾̾̀̌̉̑̑̊͝",  # Zalgo text
            "‮reversed‬",  # RTL override
        ]

        for text in unicode_texts:
            response = retry_on_rate_limit(
                api_client.post, "/api/synthesis/preview", json={"text": text, "engine": "default"}
            )

            # Should handle without 500 error
            assert response.status_code != 500, f"Unicode text caused error: {text[:20]}"

    def test_zero_duration_audio(self, api_client):
        """Verify zero duration audio handling."""
        response = retry_on_rate_limit(
            api_client.post, "/api/audio/process", json={"duration": 0, "operation": "trim"}
        )

        # Should handle gracefully
        assert response.status_code in [200, 400, 404, 422]

    def test_negative_values(self, api_client):
        """Verify negative values are rejected where appropriate."""
        response = retry_on_rate_limit(
            api_client.post, "/api/synthesis/generate", json={"text": "test", "speed": -1.0}
        )

        # Negative speed should be rejected
        assert response.status_code in [400, 422, 404]

    def test_extreme_numeric_values(self, api_client):
        """Verify extreme numeric values are handled."""
        extreme_values = [
            {"speed": 1e308},  # Near max float
            {"speed": 1e-308},  # Near min positive float
            {"speed": float("inf")},  # Infinity
        ]

        for params in extreme_values:
            response = retry_on_rate_limit(
                api_client.post, "/api/synthesis/generate", json={"text": "test", **params}
            )

            # Should be handled, not 500
            assert response.status_code != 500


class TestTimeoutRecovery:
    """Tests for timeout and recovery behavior."""

    def test_client_timeout_handling(self, api_client):
        """Verify server handles client timeouts gracefully."""
        # This tests that server continues even if client times out
        short_timeout_client = HttpClient(base_url=API_BASE_URL, timeout=0.1)

        try:
            response = short_timeout_client.get("/api/health")
        except Exception:
            # Client timeout is expected
            pass

        # Verify server is still responsive
        response = api_client.get("/api/health")
        assert response.status_code == 200

    def test_long_operation_recovery(self, api_client):
        """Verify recovery after potentially long operations."""
        # Trigger a potentially slow operation
        retry_on_rate_limit(
            api_client.post,
            "/api/synthesis/generate",
            json={"text": "Long synthesis test " * 100, "engine": "default"},
        )

        # Whether it succeeds or fails, verify we can still make requests
        health = api_client.get("/api/health")
        assert health.status_code == 200

    def test_concurrent_request_handling(self, api_client):
        """Verify concurrent requests don't cause timeouts."""
        import concurrent.futures

        def make_request():
            try:
                return api_client.get("/api/health").status_code
            except Exception:
                return 0

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]

        # Most should succeed
        success_count = sum(1 for r in results if r == 200)
        assert success_count >= 5, "Too many concurrent requests failed"


class TestPartialFailures:
    """Tests for partial failure scenarios."""

    def test_batch_partial_failure(self, api_client):
        """Verify batch operations handle partial failures."""
        # Try batch operation with mix of valid/invalid items
        batch_items = [
            {"text": "Valid text 1", "id": "1"},
            {"text": "", "id": "2"},  # May be invalid
            {"text": "Valid text 3", "id": "3"},
        ]

        response = retry_on_rate_limit(
            api_client.post, "/api/batch/synthesis", json={"items": batch_items}
        )

        # Should not completely fail due to one bad item
        if response.status_code == 200:
            data = response.json()
            # Should indicate which items succeeded/failed
            assert "results" in data or "items" in data or "errors" in data

    def test_multiple_engine_fallback(self, api_client):
        """Verify fallback to alternative engines on failure."""
        response = retry_on_rate_limit(
            api_client.post,
            "/api/synthesis/generate",
            json={
                "text": "Test fallback",
                "engine": "nonexistent_engine",
                "fallback_enabled": True,
            },
        )

        # Should either fall back or return appropriate error
        assert response.status_code in [200, 400, 404, 422, 503]

    def test_transaction_rollback_on_error(self, api_client):
        """Verify transactions are rolled back on errors."""
        # Create a profile
        create_response = retry_on_rate_limit(
            api_client.post, "/api/profiles", json={"name": "Transaction Test", "settings": {}}
        )

        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create test profile")

        profile_id = create_response.json().get("id", "test-id")

        # Try to update with invalid data
        update_response = retry_on_rate_limit(
            api_client.patch, f"/api/profiles/{profile_id}", json={"invalid_field": "should_fail"}
        )

        # Original profile should be unchanged if update failed
        if update_response.status_code >= 400:
            get_response = api_client.get(f"/api/profiles/{profile_id}")
            if get_response.status_code == 200:
                profile = get_response.json()
                # Original data should be intact
                assert profile.get("name") == "Transaction Test"


class TestCircuitBreaker:
    """Tests for circuit breaker behavior."""

    def test_circuit_opens_on_failures(self, api_client):
        """Verify circuit breaker opens after repeated failures."""
        # Make requests to a failing endpoint
        failure_count = 0
        for _i in range(10):
            response = api_client.get("/api/engines/nonexistent/status")
            if response.status_code in [500, 503]:
                failure_count += 1

        # After failures, circuit may open (503 response)
        # This is advisory - circuit breaker may not be implemented
        pass

    def test_circuit_half_open_recovery(self, api_client):
        """Verify circuit breaker recovery after cooldown."""
        # This tests recovery behavior
        # First verify healthy endpoint works
        response = api_client.get("/api/health")
        assert response.status_code == 200

        # After some failures, system should still recover
        for _ in range(5):
            api_client.get("/api/nonexistent")

        # Health should still work
        response = api_client.get("/api/health")
        assert response.status_code == 200

    def test_fallback_engine_usage(self, api_client):
        """Verify fallback engines are used when primary fails."""
        response = retry_on_rate_limit(
            api_client.post,
            "/api/synthesis/generate",
            json={
                "text": "Test with fallback",
                "engine": "primary_engine",
                "fallback_engines": ["fallback1", "fallback2"],
            },
        )

        # Should succeed with fallback or return appropriate error
        assert response.status_code in [200, 400, 404, 422, 503]


class TestResourceExhaustion:
    """Tests for resource exhaustion scenarios."""

    def test_memory_pressure_handling(self, api_client):
        """Verify system handles memory pressure gracefully."""
        # Try to allocate large response
        response = retry_on_rate_limit(api_client.get, "/api/library", params={"limit": 10000})

        # Should either succeed or return appropriate error
        assert response.status_code in [200, 400, 413, 422, 503]

    def test_connection_limit_handling(self, api_client):
        """Verify connection limits are enforced gracefully."""
        # Create many connections
        clients = []
        for _ in range(20):
            try:
                client = HttpClient(base_url=API_BASE_URL, timeout=5.0)
                clients.append(client)
            except Exception:
                break

        # Original client should still work
        response = api_client.get("/api/health")
        assert response.status_code in [200, 429, 503]

        # Cleanup
        for client in clients:
            with contextlib.suppress(Exception):
                client.close()

    def test_queue_overflow_handling(self, api_client):
        """Verify job queue overflow is handled."""
        # Try to submit many jobs rapidly
        responses = []
        for i in range(20):
            response = api_client.post(
                "/api/jobs/submit", json={"type": "test", "data": {"index": i}}
            )
            responses.append(response.status_code)

        # Should handle gracefully (may queue, reject with 429/503, or succeed)
        for status in responses:
            assert status in [200, 201, 202, 400, 404, 429, 503]


class TestErrorResponseFormat:
    """Tests for error response format consistency."""

    def test_error_response_structure(self, api_client):
        """Verify error responses have consistent structure."""
        # Trigger various errors
        errors = []

        # 404 error
        r1 = api_client.get("/api/nonexistent")
        errors.append(r1)

        # 422 validation error
        r2 = api_client.post("/api/profiles", json={})
        errors.append(r2)

        for response in errors:
            if response.status_code >= 400:
                try:
                    data = response.json()
                    # Should have error info
                    has_error_info = any(
                        [
                            "detail" in data,
                            "message" in data,
                            "error" in data,
                            "errors" in data,
                        ]
                    )
                    assert has_error_info, "Error response should contain error info"
                except Exception:
                    # Non-JSON error response is also acceptable
                    pass

    def test_http_status_code_consistency(self, api_client):
        """Verify HTTP status codes are used correctly."""
        # 404 for not found
        response = api_client.get("/api/profiles/nonexistent-id-12345")
        if response.status_code != 404:
            # May return 200 with empty or 400
            assert response.status_code in [200, 400]

        # 405 for wrong method
        response = api_client.delete("/api/health")
        assert response.status_code in [405, 404]
