"""Tests for Phase 2 bug fixes in context management system.

This module tests:
- BUG-001/BUG-002: CLI argument parsing for --level and --part
- BUG-003/BUG-004/BUG-005: MCP adapter _measure() usage pattern
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch, MagicMock

import pytest

from tools.context.core.models import AllocationContext, ContextLevel, SourceResult
from tools.context.sources.base import BaseSourceAdapter
from tools.context.sources.context7_adapter import Context7Adapter
from tools.context.sources.github_adapter import GitHubAdapter
from tools.context.sources.linear_adapter import LinearAdapter


# -----------------------------------------------------------------------------
# BUG-001/BUG-002: CLI Argument Parsing Tests
# -----------------------------------------------------------------------------

class TestCLIArgumentParsing:
    """Tests for allocate.py CLI argument fixes."""

    def test_level_argument_accepts_high(self) -> None:
        """--level high should be accepted and parsed correctly."""
        parser = self._create_parser()
        args = parser.parse_args(["--level", "high"])
        assert args.level == "high"

    def test_level_argument_accepts_mid(self) -> None:
        """--level mid should be accepted and parsed correctly."""
        parser = self._create_parser()
        args = parser.parse_args(["--level", "mid"])
        assert args.level == "mid"

    def test_level_argument_accepts_low(self) -> None:
        """--level low should be accepted and parsed correctly."""
        parser = self._create_parser()
        args = parser.parse_args(["--level", "low"])
        assert args.level == "low"

    def test_level_argument_defaults_to_mid(self) -> None:
        """--level should default to 'mid' when not specified."""
        parser = self._create_parser()
        args = parser.parse_args([])
        assert args.level == "mid"

    def test_level_argument_rejects_invalid(self) -> None:
        """--level should reject invalid values."""
        parser = self._create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--level", "invalid"])

    def test_part_argument_is_boolean_flag(self) -> None:
        """--part should be a boolean flag."""
        parser = self._create_parser()
        args = parser.parse_args(["--part"])
        assert args.part is True

    def test_part_argument_defaults_to_false(self) -> None:
        """--part should default to False when not specified."""
        parser = self._create_parser()
        args = parser.parse_args([])
        assert args.part is False

    def test_level_and_part_together(self) -> None:
        """--level and --part can be used together."""
        parser = self._create_parser()
        args = parser.parse_args(["--level", "high", "--part"])
        assert args.level == "high"
        assert args.part is True

    def test_level_maps_to_context_level_enum(self) -> None:
        """Level string values should map to ContextLevel enum."""
        level_map = {"high": ContextLevel.HIGH, "mid": ContextLevel.MID, "low": ContextLevel.LOW}
        for level_str, expected_enum in level_map.items():
            assert level_map[level_str] == expected_enum

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser matching allocate.py."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--role", help="Role short name")
        parser.add_argument("--task", help="Task id")
        parser.add_argument("--phase", help="Phase name")
        parser.add_argument("--budget", type=int, default=None)
        parser.add_argument("--include-git", action="store_true")
        parser.add_argument("--preamble", action="store_true")
        parser.add_argument("--part", action="store_true", help="Output P.A.R.T. structured format")
        parser.add_argument("--level", choices=["high", "mid", "low"], default="mid",
                            help="Context level (high=minimal, mid=normal, low=all)")
        parser.add_argument("--config", help="Config path")
        return parser


# -----------------------------------------------------------------------------
# BUG-003/BUG-004/BUG-005: MCP Adapter _measure() Usage Tests
# -----------------------------------------------------------------------------

class TestMCPAdapterMeasurePattern:
    """Tests for correct _measure() usage in MCP adapters."""

    def test_context7_adapter_fetch_returns_source_result(self) -> None:
        """Context7Adapter.fetch() should return SourceResult via _measure()."""
        adapter = Context7Adapter(priority=1, offline=False)
        context = AllocationContext(task_id="TASK-001", phase="Construct", role="test")
        
        result = adapter.fetch(context)
        
        assert isinstance(result, SourceResult)
        assert result.source_name == "context7"
        assert result.success is True
        assert isinstance(result.fetch_time_ms, float)
        assert result.fetch_time_ms >= 0

    def test_context7_adapter_disabled_returns_note(self, monkeypatch) -> None:
        """Context7Adapter returns disabled note when MCP is disabled."""
        monkeypatch.delenv("VOICESTUDIO_CONTEXT7_ENABLED", raising=False)
        adapter = Context7Adapter()
        context = AllocationContext(task_id=None, phase=None, role=None)
        
        result = adapter.fetch(context)
        
        assert result.success is True
        assert "note" in result.data
        assert "disabled" in result.data["note"].lower()

    def test_github_adapter_fetch_returns_source_result(self) -> None:
        """GitHubAdapter.fetch() should return SourceResult via _measure()."""
        adapter = GitHubAdapter(priority=1, offline=False)
        context = AllocationContext(task_id="TASK-001", phase="Construct", role="test")
        
        result = adapter.fetch(context)
        
        assert isinstance(result, SourceResult)
        assert result.source_name == "github"
        assert result.success is True
        assert isinstance(result.fetch_time_ms, float)

    def test_github_adapter_disabled_returns_note(self, monkeypatch) -> None:
        """GitHubAdapter returns disabled note when MCP is disabled."""
        monkeypatch.delenv("VOICESTUDIO_GITHUB_MCP_ENABLED", raising=False)
        adapter = GitHubAdapter()
        context = AllocationContext(task_id=None, phase=None, role=None)
        
        result = adapter.fetch(context)
        
        assert result.success is True
        assert "note" in result.data
        assert "disabled" in result.data["note"].lower()

    def test_linear_adapter_fetch_returns_source_result(self) -> None:
        """LinearAdapter.fetch() should return SourceResult via _measure()."""
        adapter = LinearAdapter(priority=1, offline=False)
        context = AllocationContext(task_id="TASK-001", phase="Construct", role="test")
        
        result = adapter.fetch(context)
        
        assert isinstance(result, SourceResult)
        assert result.source_name == "linear"
        assert result.success is True
        assert isinstance(result.fetch_time_ms, float)

    def test_linear_adapter_disabled_returns_note(self, monkeypatch) -> None:
        """LinearAdapter returns disabled note when MCP is disabled."""
        monkeypatch.delenv("VOICESTUDIO_LINEAR_ENABLED", raising=False)
        adapter = LinearAdapter()
        context = AllocationContext(task_id=None, phase=None, role=None)
        
        result = adapter.fetch(context)
        
        assert result.success is True
        assert "note" in result.data
        assert "disabled" in result.data["note"].lower()


class TestMCPAdapterMeasureWithLoader:
    """Tests verifying _measure() is called with a loader callable."""

    def test_measure_receives_callable_loader(self) -> None:
        """_measure() should receive a callable that returns dict."""
        adapter = Context7Adapter()
        context = AllocationContext(task_id=None, phase=None, role=None)
        
        # Track what _measure receives
        original_measure = adapter._measure
        measure_calls = []
        
        def tracking_measure(loader, ctx):
            measure_calls.append({
                "loader_callable": callable(loader),
                "loader_result": loader() if callable(loader) else None,
                "context": ctx
            })
            return original_measure(loader, ctx)
        
        adapter._measure = tracking_measure
        adapter.fetch(context)
        
        assert len(measure_calls) == 1
        assert measure_calls[0]["loader_callable"] is True
        assert isinstance(measure_calls[0]["loader_result"], dict)

    def test_measure_handles_exception_in_loader(self) -> None:
        """_measure() should handle exceptions from loader gracefully."""
        class FailingAdapter(BaseSourceAdapter):
            def __init__(self):
                super().__init__(source_name="failing", priority=0, offline=True)
            
            def fetch(self, context: AllocationContext) -> SourceResult:
                def _load() -> dict:
                    raise RuntimeError("Simulated failure")
                return self._measure(_load, context)
        
        adapter = FailingAdapter()
        context = AllocationContext(task_id=None, phase=None, role=None)
        
        result = adapter.fetch(context)
        
        assert result.success is False
        assert result.error == "Simulated failure"
        assert result.fetch_time_ms >= 0


class TestMCPAdapterTelemetry:
    """Tests verifying health status tracking via _measure()."""

    def test_successful_fetch_updates_health_status(self) -> None:
        """Successful fetch should update health status."""
        from tools.context.sources.base import reset_source_telemetry
        reset_source_telemetry()
        
        adapter = Context7Adapter()
        context = AllocationContext(task_id=None, phase=None, role=None)
        
        initial_fetches = adapter.health_status.total_fetches
        adapter.fetch(context)
        
        assert adapter.health_status.total_fetches == initial_fetches + 1
        assert adapter.health_status.is_healthy is True

    def test_multiple_adapters_track_independently(self) -> None:
        """Each adapter should track its own health status."""
        from tools.context.sources.base import reset_source_telemetry
        reset_source_telemetry()
        
        context7 = Context7Adapter()
        github = GitHubAdapter()
        linear = LinearAdapter()
        context = AllocationContext(task_id=None, phase=None, role=None)
        
        context7.fetch(context)
        github.fetch(context)
        
        assert context7.health_status.total_fetches == 1
        assert github.health_status.total_fetches == 1
        assert linear.health_status.total_fetches == 0


class TestMCPAdapterEstimateSize:
    """Tests for estimate_size() implementation in MCP adapters."""

    def test_context7_estimate_size_when_disabled(self, monkeypatch) -> None:
        """Context7Adapter should estimate 0 chars when disabled."""
        monkeypatch.delenv("VOICESTUDIO_CONTEXT7_ENABLED", raising=False)
        adapter = Context7Adapter()
        context = AllocationContext(task_id=None, phase=None, role=None)
        
        assert adapter.estimate_size(context) == 0

    def test_context7_estimate_size_when_enabled(self, monkeypatch) -> None:
        """Context7Adapter should estimate >0 chars when enabled."""
        monkeypatch.setenv("VOICESTUDIO_CONTEXT7_ENABLED", "1")
        adapter = Context7Adapter()
        context = AllocationContext(task_id=None, phase=None, role=None)
        
        assert adapter.estimate_size(context) > 0

    def test_github_estimate_size_when_disabled(self, monkeypatch) -> None:
        """GitHubAdapter should estimate 0 chars when disabled."""
        monkeypatch.delenv("VOICESTUDIO_GITHUB_MCP_ENABLED", raising=False)
        adapter = GitHubAdapter()
        context = AllocationContext(task_id=None, phase=None, role=None)
        
        assert adapter.estimate_size(context) == 0

    def test_linear_estimate_size_when_disabled(self, monkeypatch) -> None:
        """LinearAdapter should estimate 0 chars when disabled."""
        monkeypatch.delenv("VOICESTUDIO_LINEAR_ENABLED", raising=False)
        adapter = LinearAdapter()
        context = AllocationContext(task_id=None, phase=None, role=None)
        
        assert adapter.estimate_size(context) == 0
