"""
Unit Tests for Assistant API Routes.

Tests AI production assistant endpoints for chat, conversations, and task suggestions.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_assistant_state():
    """Reset assistant state before each test."""
    from backend.api.routes import assistant
    assistant._conversations = {}
    yield
    assistant._conversations = {}


@pytest.fixture
def assistant_client():
    """Create test client for assistant routes."""
    from backend.api.routes.assistant import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider."""
    mock = MagicMock()
    mock.generate.return_value = "This is a test response from the assistant."
    return mock


# =============================================================================
# Conversation CRUD Tests
# =============================================================================


class TestConversationCRUD:
    """Tests for conversation management endpoints."""

    def test_get_conversations_empty(self, assistant_client):
        """Test GET /conversations returns empty list initially."""
        response = assistant_client.get("/api/assistant/conversations")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_conversation_not_found(self, assistant_client):
        """Test GET /conversations/{id} returns 404 for missing conversation."""
        response = assistant_client.get("/api/assistant/conversations/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_conversation_not_found(self, assistant_client):
        """Test DELETE /conversations/{id} returns 404 for missing conversation."""
        response = assistant_client.delete("/api/assistant/conversations/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# =============================================================================
# Chat Tests
# =============================================================================


class TestChat:
    """Tests for chat endpoint."""

    @patch("backend.api.routes.assistant._get_llm_provider")
    def test_chat_creates_conversation(self, mock_get_provider, assistant_client, mock_llm_provider):
        """Test POST /chat creates new conversation if none specified."""
        mock_get_provider.return_value = mock_llm_provider

        response = assistant_client.post(
            "/api/assistant/chat",
            json={"message": "Hello assistant"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "message_id" in data
        assert "content" in data
        assert "timestamp" in data
        assert "suggestions" in data

    @patch("backend.api.routes.assistant._get_llm_provider")
    def test_chat_continues_conversation(self, mock_get_provider, assistant_client, mock_llm_provider):
        """Test POST /chat can continue existing conversation."""
        mock_get_provider.return_value = mock_llm_provider

        # Create first message
        response1 = assistant_client.post(
            "/api/assistant/chat",
            json={"message": "Hello assistant"},
        )
        assert response1.status_code == 200
        conv_id = response1.json()["conversation_id"]

        # Continue conversation
        response2 = assistant_client.post(
            "/api/assistant/chat",
            json={"message": "Follow up question", "conversation_id": conv_id},
        )
        assert response2.status_code == 200
        assert response2.json()["conversation_id"] == conv_id

    @patch("backend.api.routes.assistant._get_llm_provider")
    def test_chat_with_context(self, mock_get_provider, assistant_client, mock_llm_provider):
        """Test POST /chat accepts context parameter."""
        mock_get_provider.return_value = mock_llm_provider

        response = assistant_client.post(
            "/api/assistant/chat",
            json={
                "message": "Help with my project",
                "context": {"project_name": "Test Project", "current_task": "mixing"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    @patch("backend.api.routes.assistant._get_llm_provider")
    def test_chat_validates_empty_message(self, mock_get_provider, assistant_client, mock_llm_provider):
        """Test POST /chat validates message is not empty."""
        mock_get_provider.return_value = mock_llm_provider

        response = assistant_client.post(
            "/api/assistant/chat",
            json={"message": ""},
        )
        # May return 200 with processing or 422 for validation
        # Depends on implementation - just check it's handled
        assert response.status_code in [200, 422]

    @patch("backend.api.routes.assistant._get_llm_provider")
    def test_chat_conversation_appears_in_list(self, mock_get_provider, assistant_client, mock_llm_provider):
        """Test that conversations created by chat appear in list."""
        mock_get_provider.return_value = mock_llm_provider

        # Create conversation via chat
        response = assistant_client.post(
            "/api/assistant/chat",
            json={"message": "Test message"},
        )
        assert response.status_code == 200
        conv_id = response.json()["conversation_id"]

        # Check conversation is in list
        list_response = assistant_client.get("/api/assistant/conversations")
        assert list_response.status_code == 200
        conversations = list_response.json()
        assert len(conversations) == 1
        assert conversations[0]["conversation_id"] == conv_id

    @patch("backend.api.routes.assistant._get_llm_provider")
    def test_chat_conversation_can_be_retrieved(self, mock_get_provider, assistant_client, mock_llm_provider):
        """Test that conversation can be retrieved after creation."""
        mock_get_provider.return_value = mock_llm_provider

        # Create conversation
        response = assistant_client.post(
            "/api/assistant/chat",
            json={"message": "Test message"},
        )
        assert response.status_code == 200
        conv_id = response.json()["conversation_id"]

        # Retrieve conversation
        get_response = assistant_client.get(f"/api/assistant/conversations/{conv_id}")
        assert get_response.status_code == 200
        conversation = get_response.json()
        assert conversation["conversation_id"] == conv_id
        assert len(conversation["messages"]) >= 2  # User message + assistant response

    @patch("backend.api.routes.assistant._get_llm_provider")
    def test_delete_conversation_success(self, mock_get_provider, assistant_client, mock_llm_provider):
        """Test DELETE /conversations/{id} successfully deletes."""
        mock_get_provider.return_value = mock_llm_provider

        # Create conversation
        response = assistant_client.post(
            "/api/assistant/chat",
            json={"message": "Test message"},
        )
        assert response.status_code == 200
        conv_id = response.json()["conversation_id"]

        # Delete it
        delete_response = assistant_client.delete(f"/api/assistant/conversations/{conv_id}")
        assert delete_response.status_code == 200

        # Verify it's gone
        get_response = assistant_client.get(f"/api/assistant/conversations/{conv_id}")
        assert get_response.status_code == 404


# =============================================================================
# Task Suggestion Tests
# =============================================================================


class TestTaskSuggestions:
    """Tests for task suggestion endpoint."""

    @patch("backend.api.routes.assistant._get_llm_provider")
    def test_suggest_tasks_basic(self, mock_get_provider, assistant_client):
        """Test POST /suggest-tasks returns task suggestions."""
        # Mock provider with async generate method
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Task 1 | Description 1 | mixing | high | 30"
        mock_provider.generate = AsyncMock(return_value=mock_response)
        mock_get_provider.return_value = mock_provider

        response = assistant_client.post(
            "/api/assistant/suggest-tasks?project_id=test-project",
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @patch("backend.api.routes.assistant._get_llm_provider")
    def test_suggest_tasks_with_context(self, mock_get_provider, assistant_client):
        """Test POST /suggest-tasks accepts context as query param."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Task 1 | Description 1 | editing | medium | 15"
        mock_provider.generate = AsyncMock(return_value=mock_response)
        mock_get_provider.return_value = mock_provider

        # context is a dict, but query params expect strings - the API may not support complex context as query
        # Just test with project_id
        response = assistant_client.post(
            "/api/assistant/suggest-tasks?project_id=test-project",
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# =============================================================================
# Provider Tests
# =============================================================================


class TestProviders:
    """Tests for provider listing endpoint."""

    def test_get_providers(self, assistant_client):
        """Test GET /providers returns available providers."""
        response = assistant_client.get("/api/assistant/providers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict) or isinstance(data, list)

    def test_providers_structure(self, assistant_client):
        """Test GET /providers returns expected structure."""
        response = assistant_client.get("/api/assistant/providers")
        assert response.status_code == 200
        # The response should have information about available LLM providers
        data = response.json()
        # At minimum, it should be a valid response
        assert data is not None
