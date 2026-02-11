"""
Integration tests for OpenMemory MCP protocol.

Tests the actual MCP integration when available, with graceful
fallback when MCP servers are not running.

These tests verify:
- MCP client initialization
- Provider discovery and fallback
- Real responses when MCP is available
- Graceful degradation when MCP is unavailable
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch
import tempfile

# Add project root to path for tools imports
_project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_project_root))

import pytest

# Try to import the modules
try:
    from tools.context.sources.memory_adapter import (
        MemorySourceAdapter,
        _try_all_mcp_providers,
        _run_mcp_search,
        _MCP_TOOL_CONFIGS,
        PROJECT_ID,
    )
    from tools.context.core.models import AllocationContext, ContextLevel
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    MemorySourceAdapter = None
    _try_all_mcp_providers = None


def is_npx_available() -> bool:
    """Check if npx is available in PATH."""
    try:
        result = subprocess.run(
            ["npx", "--version"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_mcp_package_available() -> bool:
    """Check if mcp Python package is installed."""
    try:
        import mcp
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available")
class TestMCPAvailability:
    """Tests for MCP availability detection."""
    
    def test_mcp_tool_configs_defined(self):
        """Test that MCP tool configurations are defined."""
        assert "openmemory" in _MCP_TOOL_CONFIGS
        assert "mem0" in _MCP_TOOL_CONFIGS
        
        # Verify config structure
        for provider, config in _MCP_TOOL_CONFIGS.items():
            assert "command" in config
            assert "args" in config
            assert "tool_name" in config
            assert "param_mapping" in config
    
    def test_openmemory_config_structure(self):
        """Test OpenMemory configuration structure."""
        config = _MCP_TOOL_CONFIGS["openmemory"]
        
        assert config["command"] == "npx"
        assert "-y" in config["args"]
        assert "openmemory-mcp" in config["args"]
        assert config["tool_name"] == "openmemory_query"
    
    def test_mem0_config_structure(self):
        """Test Mem0 configuration structure."""
        config = _MCP_TOOL_CONFIGS["mem0"]
        
        assert config["command"] == "npx"
        assert "-y" in config["args"]
        assert "@mem0/mcp" in config["args"]
        assert config["tool_name"] == "search-memory"


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available")
class TestMCPFallbackBehavior:
    """Tests for MCP fallback behavior when servers are unavailable."""
    
    def test_graceful_fallback_when_mcp_unavailable(self):
        """Test that the adapter gracefully falls back when MCP is unavailable."""
        adapter = MemorySourceAdapter(
            offline=False,
            mcp_enabled=True,
            max_results=5,
        )
        
        # Create a temp openmemory.md for fallback
        with tempfile.TemporaryDirectory() as tmpdir:
            openmemory_path = Path(tmpdir) / "openmemory.md"
            openmemory_path.write_text(
                "# VoiceStudio Memory\n\n## Overview\n\nFallback content for testing.",
                encoding="utf-8"
            )
            
            with patch.dict(os.environ, {"OPENMEMORY_PATH": str(openmemory_path)}):
                # Reset the logged flag
                MemorySourceAdapter._mcp_unavailable_logged = False
                
                # Call should not raise, should fall back gracefully
                result = adapter._call_openmemory_mcp("test query")
                
                # Result may be None (no MCP) or list (file fallback)
                # The important thing is no exception was raised
                assert result is None or isinstance(result, list)
    
    def test_fallback_chain_complete(self):
        """Test the complete fallback chain."""
        adapter = MemorySourceAdapter(
            offline=False,
            mcp_enabled=True,
            max_results=5,
        )
        
        # Test with CONTEXT_MEMO as the final fallback
        with patch.dict(os.environ, {"CONTEXT_MEMO": "Final fallback context"}):
            with patch("tools.context.sources.memory_adapter._resolve_openmemory_path", return_value=None):
                # Should use CONTEXT_MEMO fallback
                items = adapter._fetch_env_hint()
                
                assert len(items) == 1
                assert items[0].content == "Final fallback context"


@pytest.mark.skipif(
    not TOOLS_AVAILABLE or not is_npx_available() or not is_mcp_package_available(),
    reason="MCP infrastructure not available"
)
class TestMCPLiveIntegration:
    """
    Live integration tests for MCP when infrastructure is available.
    
    These tests require:
    - npx in PATH
    - mcp Python package installed
    - Network access for MCP server startup
    
    Skip gracefully when requirements are not met.
    """
    
    @pytest.mark.timeout(30)
    def test_try_all_providers_returns_or_none(self):
        """Test that _try_all_mcp_providers returns results or None gracefully."""
        # This test verifies the function handles unavailable servers gracefully
        result = _try_all_mcp_providers(
            query="test query for VoiceStudio architecture",
            max_results=3,
            query_type="contextual",
        )
        
        # Result should be list or None, never raise
        assert result is None or isinstance(result, list)
        
        if result:
            # Verify result structure
            for item in result:
                assert "content" in item
                assert "source" in item or "relevance" in item
    
    @pytest.mark.timeout(30)
    def test_memory_adapter_fetch_with_mcp(self):
        """Test MemorySourceAdapter.fetch with MCP enabled."""
        adapter = MemorySourceAdapter(
            offline=False,
            mcp_enabled=True,
            max_results=5,
        )
        
        # Create fallback file in case MCP is unavailable
        with tempfile.TemporaryDirectory() as tmpdir:
            openmemory_path = Path(tmpdir) / "openmemory.md"
            openmemory_path.write_text(
                "# VoiceStudio\n\n## Overview\n\nTest content.",
                encoding="utf-8"
            )
            
            with patch.dict(os.environ, {"OPENMEMORY_PATH": str(openmemory_path)}):
                context = AllocationContext(
                    task_id="MCP-TEST-001",
                    phase="Integration Test",
                    role="debug-agent",
                    include_git=False,
                    budget_chars=5000,
                    max_level=ContextLevel.MID,
                )
                
                result = adapter.fetch(context)
                
                # Should succeed via MCP or fallback
                assert result.success is True
                assert result.source_name == "memory"


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available")
class TestMCPConfiguration:
    """Tests for MCP configuration from context-sources.json."""
    
    def test_config_file_exists(self):
        """Test that context-sources.json exists."""
        config_path = _project_root / "tools" / "context" / "config" / "context-sources.json"
        assert config_path.exists(), "context-sources.json should exist"
    
    def test_mcp_enabled_in_config(self):
        """Test that MCP is now enabled by default in config."""
        import json
        
        config_path = _project_root / "tools" / "context" / "config" / "context-sources.json"
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        assert "memory" in config
        assert "mcp_enabled" in config["memory"]
        # After Task 2.1, this should be True
        assert config["memory"]["mcp_enabled"] is True
    
    def test_project_id_constant(self):
        """Test that PROJECT_ID matches expected value."""
        assert PROJECT_ID == "wtsteward11/VoiceStudio"


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available")
class TestMCPErrorHandling:
    """Tests for MCP error handling."""
    
    def test_timeout_handling(self):
        """Test that MCP timeout is handled gracefully."""
        # Mock a timeout scenario
        with patch("tools.context.sources.memory_adapter.asyncio.run") as mock_run:
            import asyncio
            mock_run.side_effect = asyncio.TimeoutError("MCP timeout")
            
            result = _run_mcp_search(
                query="test",
                max_results=5,
                query_type="contextual",
                provider="openmemory",
            )
            
            # Should return None on timeout, not raise
            assert result is None
    
    def test_import_error_handling(self):
        """Test handling when mcp package is not installed."""
        with patch.dict(sys.modules, {"mcp": None}):
            with patch("builtins.__import__", side_effect=ImportError("No mcp")):
                # The function should catch ImportError and return None
                # This tests the graceful degradation path
                adapter = MemorySourceAdapter(
                    offline=False,
                    mcp_enabled=True,
                )
                
                # Should not raise during initialization
                assert adapter is not None
    
    def test_network_error_handling(self):
        """Test handling of network errors during MCP communication."""
        with patch("tools.context.sources.memory_adapter.asyncio.run") as mock_run:
            mock_run.side_effect = ConnectionRefusedError("Connection refused")
            
            result = _run_mcp_search(
                query="test",
                max_results=5,
                query_type="contextual",
                provider="openmemory",
            )
            
            # Should return None on connection error
            assert result is None
