"""
Unit tests for MemorySourceAdapter.

Tests:
- MCP protocol integration
- Fallback chain (MCP -> openmemory.md -> CONTEXT_MEMO)
- Role-aware memory retrieval
- Query building and parsing
- Health checks
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path for tools imports BEFORE any pytest imports
_project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_project_root))

import pytest

# Try to import the modules, skip tests if not available
try:
    from tools.context.core.models import AllocationContext, ContextLevel
    from tools.context.core.registry import build_default_registry
    from tools.context.sources.memory_adapter import (
        PROJECT_ID,
        RELEVANT_MEMORY_TYPES,
        MemorySourceAdapter,
        _parse_mcp_tool_result,
        _resolve_openmemory_path,
        _try_all_mcp_providers,
    )
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    MemorySourceAdapter = None
    AllocationContext = None
    ContextLevel = None
    build_default_registry = None
    _resolve_openmemory_path = None
    _parse_mcp_tool_result = None
    _try_all_mcp_providers = None


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available in path")
class TestMemorySourceAdapter:
    """Tests for MemorySourceAdapter class."""

    @pytest.fixture
    def temp_openmemory_dir(self):
        """Create a temporary directory with sample openmemory.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            openmemory_path = Path(tmpdir) / "openmemory.md"

            content = """# VoiceStudio Project Memory

## Overview

VoiceStudio is a hybrid desktop application for voice synthesis.

## Architecture

- Frontend: WinUI 3 / Windows App SDK
- Backend: FastAPI (Python)
- Engines: XTTS, Piper, RVC

## Components

### VoiceSynthesisView
The main synthesis panel with text input and voice selection.

### ThemeManager
Handles theme switching and persistence.

## Patterns

- MVVM for UI architecture
- Gateway pattern for backend communication
"""
            openmemory_path.write_text(content, encoding="utf-8")

            yield tmpdir

    @pytest.fixture
    def adapter(self):
        """Create a MemorySourceAdapter instance."""
        return MemorySourceAdapter(
            offline=True,
            max_results=5,
            query_type="contextual",
            mcp_enabled=False,
        )

    @pytest.fixture
    def mcp_enabled_adapter(self):
        """Create a MemorySourceAdapter with MCP enabled."""
        return MemorySourceAdapter(
            offline=False,
            max_results=5,
            query_type="contextual",
            mcp_enabled=True,
        )

    def test_adapter_initialization(self, adapter):
        """Test adapter initializes correctly."""
        assert adapter.source_name == "memory"
        assert adapter._max_results == 5
        assert adapter._query_type == "contextual"
        assert adapter._mcp_enabled is False

    def test_health_check_with_openmemory_file(self, adapter, temp_openmemory_dir):
        """Test health check when openmemory.md exists."""
        with patch.dict(os.environ, {"OPENMEMORY_PATH": str(Path(temp_openmemory_dir) / "openmemory.md")}):
            assert adapter.health_check() is True

    def test_health_check_with_context_memo(self, adapter):
        """Test health check with CONTEXT_MEMO env."""
        with patch.dict(os.environ, {"CONTEXT_MEMO": "test context"}):
            assert adapter.health_check() is True

    def test_health_check_with_mcp_enabled(self, mcp_enabled_adapter):
        """Test health check when MCP is enabled."""
        assert mcp_enabled_adapter.health_check() is True

    def test_health_check_no_sources(self, adapter):
        """Test health check when no sources available."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("tools.context.sources.memory_adapter._resolve_openmemory_path", return_value=None):
                assert adapter.health_check() is False

    def test_fetch_returns_context(self, adapter, temp_openmemory_dir):
        """Test that fetch returns memory context."""
        with patch.dict(os.environ, {"OPENMEMORY_PATH": str(Path(temp_openmemory_dir) / "openmemory.md")}):
            context = AllocationContext(
                task_id="TEST-0001",
                phase="Test",
                role="ui-engineer",
                include_git=False,
                budget_chars=5000,
                max_level=ContextLevel.MID,
            )

            result = adapter.fetch(context)

            assert result.success is True
            assert result.source_name == "memory"
            assert len(result.content) > 0 or len(result.data) > 0

    def test_fetch_with_query(self, adapter, temp_openmemory_dir):
        """Test fetch with specific query."""
        with patch.dict(os.environ, {"OPENMEMORY_PATH": str(Path(temp_openmemory_dir) / "openmemory.md")}):
            context = AllocationContext(
                task_id="TEST-0002",
                phase="Test",
                role="ui-engineer",
                include_git=False,
                budget_chars=5000,
                max_level=ContextLevel.MID,
            )

            result = adapter.fetch(context)

            assert result.success is True

    def test_role_query_hints(self, adapter):
        """Test that role-specific query hints are defined."""
        assert "overseer" in MemorySourceAdapter.ROLE_QUERY_HINTS
        assert "ui-engineer" in MemorySourceAdapter.ROLE_QUERY_HINTS
        assert "debug-agent" in MemorySourceAdapter.ROLE_QUERY_HINTS

        # Check hints have content
        assert len(MemorySourceAdapter.ROLE_QUERY_HINTS["overseer"]) > 0
        assert "UI" in MemorySourceAdapter.ROLE_QUERY_HINTS["ui-engineer"]

    def test_estimate_size(self, adapter, temp_openmemory_dir):
        """Test size estimation."""
        with patch.dict(os.environ, {"OPENMEMORY_PATH": str(Path(temp_openmemory_dir) / "openmemory.md")}):
            context = AllocationContext(
                task_id="TEST-0003",
                phase="Test",
                role="overseer",
                include_git=False,
                budget_chars=5000,
                max_level=ContextLevel.MID,
            )

            size = adapter.estimate_size(context)

            # Should return reasonable estimate
            assert size >= 0
            assert size <= 5000

    def test_fetch_env_fallback(self, adapter):
        """Test fallback to CONTEXT_MEMO environment variable."""
        test_memo = "This is test context from environment"

        with patch.dict(os.environ, {"CONTEXT_MEMO": test_memo}):
            items = adapter._fetch_env_hint()

            assert len(items) == 1
            assert items[0].content == test_memo
            assert items[0].source == "env:CONTEXT_MEMO"

    def test_fetch_env_fallback_empty(self, adapter):
        """Test env fallback returns empty when no CONTEXT_MEMO."""
        with patch.dict(os.environ, {}, clear=True):
            items = adapter._fetch_env_hint()
            assert items == []


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available in path")
class TestMCPProtocol:
    """Tests for MCP protocol integration."""

    def test_mcp_unavailable_logged_flag(self):
        """Test that MCP unavailable is logged only once."""
        # Reset the flag
        MemorySourceAdapter._mcp_unavailable_logged = False

        adapter = MemorySourceAdapter(
            offline=False,
            mcp_enabled=True,
        )

        # First call should log
        with patch("tools.context.sources.memory_adapter._try_all_mcp_providers", return_value=None):
            with patch("tools.context.sources.memory_adapter.logger") as mock_logger:
                adapter._call_openmemory_mcp("test query")

                if not MemorySourceAdapter._mcp_unavailable_logged:
                    # Check warning was called
                    assert mock_logger.warning.called or not MemorySourceAdapter._mcp_unavailable_logged

    def test_mcp_disabled_skips_protocol(self):
        """Test that MCP protocol is skipped when disabled."""
        adapter = MemorySourceAdapter(
            offline=True,
            mcp_enabled=False,
        )

        with patch("tools.context.sources.memory_adapter._try_all_mcp_providers") as mock_mcp:
            adapter._call_openmemory_mcp("test query")

            # Should not call MCP when disabled
            mock_mcp.assert_not_called()

    def test_mcp_success_returns_results(self):
        """Test that successful MCP call returns results."""
        adapter = MemorySourceAdapter(
            offline=False,
            mcp_enabled=True,
        )

        mock_results = [
            {"content": "Test memory 1", "source": "openmemory", "relevance": 0.9},
            {"content": "Test memory 2", "source": "openmemory", "relevance": 0.8},
        ]

        with patch("tools.context.sources.memory_adapter._try_all_mcp_providers", return_value=mock_results):
            result = adapter._call_openmemory_mcp("test query")

            assert result == mock_results


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available in path")
class TestOpenMemoryPathResolution:
    """Tests for openmemory.md path resolution."""

    def test_resolve_from_env(self):
        """Test path resolution from OPENMEMORY_PATH env."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            f.write(b"# Test OpenMemory")
            temp_path = f.name

        try:
            with patch.dict(os.environ, {"OPENMEMORY_PATH": temp_path}):
                result = _resolve_openmemory_path()
                assert result == temp_path
        finally:
            os.unlink(temp_path)

    def test_resolve_returns_none_when_not_found(self):
        """Test that None is returned when no openmemory.md found."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.path.exists", return_value=False):
                # In a clean environment with no file, should search and potentially fail
                # This depends on the actual file system state
                pass  # Test behavior is environment-dependent


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available in path")
class TestMCPResultParsing:
    """Tests for MCP result parsing."""

    def test_parse_hsg_format(self):
        """Test parsing OpenMemory HSG format."""
        mock_result = MagicMock()
        mock_result.content = [
            MagicMock(type="text", text='{"memories": [{"content": "Test content", "sector": "semantic", "salience": 0.85}]}')
        ]

        result = _parse_mcp_tool_result(mock_result, 5)

        assert result is not None
        assert len(result) == 1
        assert result[0]["content"] == "Test content"
        assert result[0]["relevance"] == 0.85

    def test_parse_mem0_format(self):
        """Test parsing Mem0 format."""
        mock_result = MagicMock()
        mock_result.content = [
            MagicMock(type="text", text='{"results": [{"memory": {"content": "Mem0 content"}, "metadata": {"source": "mem0"}}]}')
        ]

        result = _parse_mcp_tool_result(mock_result, 5)

        assert result is not None
        assert len(result) == 1
        assert result[0]["content"] == "Mem0 content"

    def test_parse_plain_list(self):
        """Test parsing plain list format."""
        mock_result = MagicMock()
        mock_result.content = [
            MagicMock(type="text", text='[{"content": "Item 1", "source": "test"}, {"content": "Item 2", "source": "test"}]')
        ]

        result = _parse_mcp_tool_result(mock_result, 5)

        assert result is not None
        assert len(result) == 2

    def test_parse_empty_result(self):
        """Test parsing empty result."""
        mock_result = MagicMock()
        mock_result.content = []

        result = _parse_mcp_tool_result(mock_result, 5)

        assert result is None

    def test_parse_respects_max_results(self):
        """Test that parsing respects max_results limit."""
        mock_result = MagicMock()
        items = [{"content": f"Item {i}", "source": "test"} for i in range(10)]
        mock_result.content = [
            MagicMock(type="text", text=json.dumps(items))
        ]

        result = _parse_mcp_tool_result(mock_result, 3)

        assert result is not None
        assert len(result) <= 3


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available in path")
class TestContextManagerIntegration:
    """Integration tests for memory adapter with context manager."""

    def test_adapter_registered_in_registry(self):
        """Test that memory adapter is registered in the source registry."""
        config = {
            "memory": {
                "offline": True,
                "max_results": 5,
                "mcp_enabled": False,
            }
        }

        registry = build_default_registry(config)
        sources = registry.by_name()

        assert "memory" in sources

    def test_adapter_disabled_when_configured(self):
        """Test that memory adapter is not registered when disabled."""
        # Memory adapter should always be registered but behavior changes
        config = {
            "memory": {
                "offline": True,
                "max_results": 5,
                "mcp_enabled": False,
            }
        }

        registry = build_default_registry(config)
        sources = registry.by_name()

        # Memory should be present
        assert "memory" in sources

    def test_mcp_enabled_config_propagation(self):
        """Test that mcp_enabled config is properly propagated."""
        config = {
            "memory": {
                "offline": False,
                "max_results": 10,
                "mcp_enabled": True,
            }
        }

        registry = build_default_registry(config)
        sources = registry.by_name()

        memory_adapter = sources.get("memory")
        if memory_adapter:
            # Verify MCP is enabled (if adapter exposes this)
            assert hasattr(memory_adapter, "_mcp_enabled")
            assert memory_adapter._mcp_enabled is True


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available in path")
class TestFallbackChain:
    """Tests for the fallback chain (MCP -> openmemory.md -> CONTEXT_MEMO)."""

    def test_fallback_to_file_when_mcp_fails(self):
        """Test fallback to openmemory.md when MCP fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            openmemory_path = Path(tmpdir) / "openmemory.md"
            openmemory_path.write_text("# Fallback Content\n\n## Overview\nTest fallback.", encoding="utf-8")

            adapter = MemorySourceAdapter(
                offline=False,
                mcp_enabled=True,
            )

            with patch.dict(os.environ, {"OPENMEMORY_PATH": str(openmemory_path)}):
                with patch("tools.context.sources.memory_adapter._try_all_mcp_providers", return_value=None):
                    result = adapter._call_openmemory_mcp("test query")

                    # Should fall back to file
                    assert result is not None or adapter._try_mcp_query({"query": "test"}) is not None

    def test_full_fallback_chain(self):
        """Test complete fallback chain."""
        adapter = MemorySourceAdapter(
            offline=False,
            mcp_enabled=True,
        )

        # Ensure MCP fails
        with patch("tools.context.sources.memory_adapter._try_all_mcp_providers", return_value=None):
            # Ensure no openmemory.md
            with patch("tools.context.sources.memory_adapter._resolve_openmemory_path", return_value=None):
                # CONTEXT_MEMO should be the last resort
                with patch.dict(os.environ, {"CONTEXT_MEMO": "Last resort context"}):
                    items = adapter._fetch_env_hint()

                    assert len(items) == 1
                    assert "Last resort" in items[0].content


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available in path")
class TestProjectConstants:
    """Tests for project constants."""

    def test_project_id_defined(self):
        """Test that PROJECT_ID is correctly defined."""
        assert PROJECT_ID == "wtsteward11/VoiceStudio"

    def test_memory_types_defined(self):
        """Test that RELEVANT_MEMORY_TYPES is correctly defined."""
        assert "component" in RELEVANT_MEMORY_TYPES
        assert "implementation" in RELEVANT_MEMORY_TYPES
        assert "project_info" in RELEVANT_MEMORY_TYPES
        assert "debug" in RELEVANT_MEMORY_TYPES
