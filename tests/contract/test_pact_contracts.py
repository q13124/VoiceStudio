"""
Pact-Style Consumer-Driven Contract Tests

Implements consumer-driven contract testing patterns for VoiceStudio.
These tests define the expected interactions from the consumer (frontend)
perspective and verify the provider (backend) fulfills these contracts.

Consumer Contracts:
- Frontend (C# WinUI) expectations of the API
- Engine layer expectations of backend services
- Backend expectations of engine responses

Provider Verification:
- Backend API provides expected responses
- Engine adapters provide expected outputs
"""

import json
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))


pytestmark = pytest.mark.contract


# =============================================================================
# PACT-STYLE CONTRACT DEFINITIONS
# =============================================================================

@dataclass
class Interaction:
    """Defines an expected interaction between consumer and provider."""
    description: str
    request: dict[str, Any]
    expected_response: dict[str, Any]
    provider_state: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Contract:
    """A contract between a consumer and provider."""
    consumer: str
    provider: str
    interactions: list[Interaction] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_interaction(self, interaction: Interaction):
        self.interactions.append(interaction)

    def to_dict(self) -> dict[str, Any]:
        return {
            "consumer": {"name": self.consumer},
            "provider": {"name": self.provider},
            "interactions": [i.to_dict() for i in self.interactions],
            "metadata": self.metadata
        }


class ContractMatcher:
    """Matchers for flexible contract verification."""

    @staticmethod
    def type_match(expected_type: type) -> Callable[[Any], bool]:
        """Match by type."""
        return lambda value: isinstance(value, expected_type)

    @staticmethod
    def regex_match(pattern: str) -> Callable[[Any], bool]:
        """Match by regex pattern."""
        import re
        return lambda value: bool(re.match(pattern, str(value)))

    @staticmethod
    def like(example: Any) -> Callable[[Any], bool]:
        """Match by structure (same type, keys if dict, same length if list)."""
        def matcher(value: Any) -> bool:
            if type(value) != type(example):
                return False
            if isinstance(example, dict):
                return all(k in value for k in example)
            if isinstance(example, list):
                return len(value) >= len(example)
            return True
        return matcher

    @staticmethod
    def each_like(example: Any) -> Callable[[Any], bool]:
        """Match array where each element matches the example."""
        def matcher(value: Any) -> bool:
            if not isinstance(value, list):
                return False
            if len(value) == 0:
                return True
            return all(ContractMatcher.like(example)(item) for item in value)
        return matcher


class ContractVerifier:
    """Verifies a contract against actual responses."""

    def __init__(self, client):
        self.client = client
        self.results: list[dict[str, Any]] = []

    def verify_interaction(self, interaction: Interaction) -> tuple[bool, str]:
        """Verify a single interaction."""
        request = interaction.request
        expected = interaction.expected_response

        method = request.get("method", "GET").lower()
        path = request.get("path", "/")
        body = request.get("body")
        headers = request.get("headers", {})

        try:
            # Make the request
            if method == "get":
                response = self.client.get(path, headers=headers)
            elif method == "post":
                response = self.client.post(path, json=body, headers=headers)
            elif method == "put":
                response = self.client.put(path, json=body, headers=headers)
            elif method == "delete":
                response = self.client.delete(path, headers=headers)
            else:
                return False, f"Unsupported method: {method}"

            # Verify status code
            expected_status = expected.get("status", 200)
            if response.status_code != expected_status:
                return False, f"Status mismatch: expected {expected_status}, got {response.status_code}"

            # Verify response body structure
            if "body" in expected:
                try:
                    actual_body = response.json()
                except Exception:
                    return False, "Could not parse response as JSON"

                match_result = self._match_body(expected["body"], actual_body)
                if not match_result[0]:
                    return match_result

            return True, "OK"

        except Exception as e:
            return False, f"Request failed: {e}"

    def _match_body(self, expected: Any, actual: Any, path: str = "") -> tuple[bool, str]:
        """Recursively match response body against expected structure."""
        if callable(expected):
            # It's a matcher function
            if not expected(actual):
                return False, f"Matcher failed at {path}"
            return True, "OK"

        if isinstance(expected, dict) and isinstance(actual, dict):
            for key, exp_value in expected.items():
                if key not in actual:
                    return False, f"Missing key: {path}.{key}"
                match = self._match_body(exp_value, actual[key], f"{path}.{key}")
                if not match[0]:
                    return match
            return True, "OK"

        if isinstance(expected, list) and isinstance(actual, list):
            if len(actual) < len(expected):
                return False, f"Array too short at {path}"
            for i, exp_item in enumerate(expected):
                if i < len(actual):
                    match = self._match_body(exp_item, actual[i], f"{path}[{i}]")
                    if not match[0]:
                        return match
            return True, "OK"

        if expected != actual:
            return False, f"Value mismatch at {path}: expected {expected}, got {actual}"

        return True, "OK"

    def verify_contract(self, contract: Contract) -> dict[str, Any]:
        """Verify all interactions in a contract."""
        passed = 0
        failed = 0
        failures = []

        for interaction in contract.interactions:
            success, message = self.verify_interaction(interaction)
            if success:
                passed += 1
            else:
                failed += 1
                failures.append({
                    "description": interaction.description,
                    "error": message
                })

        result = {
            "consumer": contract.consumer,
            "provider": contract.provider,
            "passed": passed,
            "failed": failed,
            "failures": failures,
            "timestamp": datetime.now().isoformat()
        }

        self.results.append(result)
        return result


# =============================================================================
# FRONTEND-BACKEND CONTRACTS
# =============================================================================

def create_frontend_backend_contract() -> Contract:
    """Create contract defining frontend expectations of backend API."""
    contract = Contract(
        consumer="VoiceStudio.App.WinUI",
        provider="VoiceStudio.Backend.API",
        metadata={"pactSpecification": {"version": "2.0.0"}}
    )

    # Health check interaction
    contract.add_interaction(Interaction(
        description="Health check returns status",
        provider_state="Backend is running",
        request={
            "method": "GET",
            "path": "/api/health"
        },
        expected_response={
            "status": 200,
            "body": {
                "status": ContractMatcher.type_match(str)
            }
        }
    ))

    # Profiles list interaction
    contract.add_interaction(Interaction(
        description="List voice profiles",
        provider_state="Backend has profiles",
        request={
            "method": "GET",
            "path": "/api/profiles"
        },
        expected_response={
            "status": 200,
            "body": ContractMatcher.like([])  # Array of profiles
        }
    ))

    # Engines list interaction
    contract.add_interaction(Interaction(
        description="List available engines",
        provider_state="Engines are loaded",
        request={
            "method": "GET",
            "path": "/api/engines"
        },
        expected_response={
            "status": 200,
            "body": ContractMatcher.like([])  # Array of engines
        }
    ))

    # Projects list interaction
    contract.add_interaction(Interaction(
        description="List projects",
        provider_state="Backend has projects",
        request={
            "method": "GET",
            "path": "/api/projects"
        },
        expected_response={
            "status": 200,
            "body": ContractMatcher.like([])  # Array of projects
        }
    ))

    return contract


def create_synthesis_contract() -> Contract:
    """Create contract for synthesis operations."""
    contract = Contract(
        consumer="VoiceStudio.App.WinUI",
        provider="VoiceStudio.Backend.Synthesis",
        metadata={"pactSpecification": {"version": "2.0.0"}}
    )

    # Synthesis request
    contract.add_interaction(Interaction(
        description="Submit synthesis job",
        provider_state="Engine is available",
        request={
            "method": "POST",
            "path": "/api/voice/synthesize",
            "body": {
                "text": "Hello world",
                "engine_id": "xtts"
            }
        },
        expected_response={
            "status": 200,
            "body": {
                "job_id": ContractMatcher.type_match(str)
            }
        }
    ))

    return contract


# =============================================================================
# ENGINE-BACKEND CONTRACTS
# =============================================================================

def create_engine_backend_contract() -> Contract:
    """Create contract defining engine expectations of backend services."""
    contract = Contract(
        consumer="VoiceStudio.Engines",
        provider="VoiceStudio.Backend.Services",
        metadata={"pactSpecification": {"version": "2.0.0"}}
    )

    # Engine registration
    contract.add_interaction(Interaction(
        description="Engine registers with service",
        provider_state="Service accepts registrations",
        request={
            "method": "POST",
            "path": "/api/engines/register",
            "body": {
                "engine_id": "test_engine",
                "capabilities": ["synthesis", "transcription"]
            }
        },
        expected_response={
            "status": 200,
            "body": {
                "registered": ContractMatcher.type_match(bool)
            }
        }
    ))

    return contract


# =============================================================================
# CONTRACT TESTS
# =============================================================================

@pytest.mark.contract
class TestFrontendBackendContract:
    """Test frontend-backend contract verification."""

    @pytest.fixture
    def mock_client(self):
        """Create mock client for testing."""
        client = Mock()

        # Mock responses
        client.get.side_effect = lambda path, **kwargs: self._mock_response(path)
        client.post.side_effect = lambda path, **kwargs: self._mock_response(path, "POST")

        return client

    def _mock_response(self, path: str, method: str = "GET"):
        """Generate mock response based on path."""
        response = Mock()

        if "/health" in path:
            response.status_code = 200
            response.json.return_value = {"status": "healthy", "version": "1.0.0"}
        elif "/profiles" in path:
            response.status_code = 200
            response.json.return_value = [
                {"id": "p1", "name": "Profile 1"},
                {"id": "p2", "name": "Profile 2"}
            ]
        elif "/engines" in path:
            response.status_code = 200
            response.json.return_value = [
                {"id": "xtts", "name": "XTTS"},
                {"id": "chatterbox", "name": "Chatterbox"}
            ]
        elif "/projects" in path:
            response.status_code = 200
            response.json.return_value = []
        elif "/synthesize" in path:
            response.status_code = 200
            response.json.return_value = {"job_id": "job-12345"}
        else:
            response.status_code = 404
            response.json.return_value = {"error": "Not found"}

        return response

    def test_frontend_backend_contract(self, mock_client):
        """Test all frontend-backend contract interactions."""
        contract = create_frontend_backend_contract()
        verifier = ContractVerifier(mock_client)

        result = verifier.verify_contract(contract)

        assert result["failed"] == 0, f"Contract failures: {result['failures']}"
        assert result["passed"] >= 4, "Expected at least 4 passing interactions"

    def test_individual_interactions(self, mock_client):
        """Test individual interactions in detail."""
        contract = create_frontend_backend_contract()
        verifier = ContractVerifier(mock_client)

        for interaction in contract.interactions:
            success, message = verifier.verify_interaction(interaction)
            assert success, f"{interaction.description}: {message}"

    def test_contract_serialization(self):
        """Test contract can be serialized to JSON."""
        contract = create_frontend_backend_contract()

        contract_json = json.dumps(contract.to_dict(), indent=2, default=str)
        parsed = json.loads(contract_json)

        assert parsed["consumer"]["name"] == "VoiceStudio.App.WinUI"
        assert parsed["provider"]["name"] == "VoiceStudio.Backend.API"
        assert len(parsed["interactions"]) >= 4


@pytest.mark.contract
class TestSynthesisContract:
    """Test synthesis-specific contracts."""

    @pytest.fixture
    def synthesis_client(self):
        """Create mock synthesis client."""
        client = Mock()

        def handle_post(path, **kwargs):
            response = Mock()
            if "/synthesize" in path:
                body = kwargs.get("json", {})
                if "text" in body:
                    response.status_code = 200
                    response.json.return_value = {
                        "job_id": "synth-job-001",
                        "status": "queued"
                    }
                else:
                    response.status_code = 422
                    response.json.return_value = {
                        "detail": "text is required"
                    }
            else:
                response.status_code = 404
                response.json.return_value = {}
            return response

        client.post.side_effect = handle_post
        return client

    def test_synthesis_contract(self, synthesis_client):
        """Test synthesis contract interactions."""
        contract = create_synthesis_contract()
        verifier = ContractVerifier(synthesis_client)

        result = verifier.verify_contract(contract)

        assert result["failed"] == 0, f"Synthesis contract failures: {result['failures']}"


@pytest.mark.contract
class TestContractMatchers:
    """Test contract matchers work correctly."""

    def test_type_match(self):
        """Test type matching."""
        matcher = ContractMatcher.type_match(str)
        assert matcher("hello")
        assert not matcher(123)

    def test_like_matcher(self):
        """Test structure matching."""
        matcher = ContractMatcher.like({"id": "", "name": ""})
        assert matcher({"id": "1", "name": "Test", "extra": "field"})
        assert not matcher({"id": "1"})  # Missing name

    def test_each_like_matcher(self):
        """Test array matching."""
        matcher = ContractMatcher.each_like({"id": ""})
        assert matcher([{"id": "1"}, {"id": "2", "name": "Extra"}])
        assert matcher([])  # Empty arrays are valid
        assert not matcher("not an array")

    def test_regex_match(self):
        """Test regex matching."""
        matcher = ContractMatcher.regex_match(r"^[a-z]+-\d+$")
        assert matcher("job-123")
        assert not matcher("JOB-123")


@pytest.mark.contract
class TestContractPublishing:
    """Test contract publishing and storage."""

    def test_contract_to_pact_format(self):
        """Test contract exports to Pact-compatible format."""
        contract = create_frontend_backend_contract()
        pact_format = contract.to_dict()

        # Verify Pact format structure
        assert "consumer" in pact_format
        assert "provider" in pact_format
        assert "interactions" in pact_format
        assert pact_format["consumer"]["name"] == "VoiceStudio.App.WinUI"

    def test_save_contract(self, tmp_path):
        """Test contract can be saved to file."""
        contract = create_frontend_backend_contract()

        contract_file = tmp_path / "pact-frontend-backend.json"

        # Save contract (without matchers for JSON serialization)
        contract_data = {
            "consumer": {"name": contract.consumer},
            "provider": {"name": contract.provider},
            "interactions": [
                {
                    "description": i.description,
                    "request": i.request,
                    "provider_state": i.provider_state
                }
                for i in contract.interactions
            ]
        }

        with open(contract_file, 'w') as f:
            json.dump(contract_data, f, indent=2)

        assert contract_file.exists()

        # Reload and verify
        with open(contract_file) as f:
            loaded = json.load(f)

        assert loaded["consumer"]["name"] == "VoiceStudio.App.WinUI"
        assert len(loaded["interactions"]) >= 4


@pytest.mark.contract
class TestProviderStateSetup:
    """Test provider state setup for contract testing."""

    @pytest.fixture
    def provider_states(self):
        """Define provider state setup functions."""
        return {
            "Backend is running": lambda: {"status": "running"},
            "Backend has profiles": lambda: {"profiles": [{"id": "p1"}]},
            "Engines are loaded": lambda: {"engines": [{"id": "xtts"}]},
            "Backend has projects": lambda: {"projects": []},
            "Engine is available": lambda: {"engine_status": "ready"},
            "Service accepts registrations": lambda: {"accepts": True},
        }

    def test_provider_states_defined(self, provider_states):
        """Test all contract provider states are defined."""
        contracts = [
            create_frontend_backend_contract(),
            create_synthesis_contract(),
            create_engine_backend_contract(),
        ]

        missing_states = []
        for contract in contracts:
            for interaction in contract.interactions:
                if interaction.provider_state and interaction.provider_state not in provider_states:
                    missing_states.append(interaction.provider_state)

        assert not missing_states, f"Missing provider states: {missing_states}"

    def test_provider_state_execution(self, provider_states):
        """Test provider states can be executed."""
        for state_name, setup_fn in provider_states.items():
            result = setup_fn()
            assert isinstance(result, dict), f"State {state_name} should return dict"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "contract"])
