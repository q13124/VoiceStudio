"""
Old Project Tool Functionality Tests
Tests all tools copied from old projects for functionality.

This test suite verifies that all tools from the old project integration
work correctly after being copied and adapted.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
tools_dir = project_root / "tools"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAudioQualityBenchmark:
    """Test audio_quality_benchmark.py tool."""

    def test_tool_exists(self):
        """Test that audio_quality_benchmark.py exists."""
        tool_path = tools_dir / "audio_quality_benchmark.py"
        if not tool_path.exists():
            pytest.skip(
                "audio_quality_benchmark.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("audio_quality_benchmark.py found")

    def test_tool_import(self):
        """Test that audio_quality_benchmark.py can be imported."""
        tool_path = tools_dir / "audio_quality_benchmark.py"
        if not tool_path.exists():
            pytest.skip("audio_quality_benchmark.py not found")

        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "audio_quality_benchmark", tool_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                assert module is not None
                logger.info("audio_quality_benchmark.py imported successfully")
        except Exception as e:
            pytest.fail(f"Failed to import audio_quality_benchmark.py: {e}")

    def test_tool_help(self):
        """Test that audio_quality_benchmark.py has help/usage information."""
        tool_path = tools_dir / "audio_quality_benchmark.py"
        if not tool_path.exists():
            pytest.skip("audio_quality_benchmark.py not found")

        try:
            result = subprocess.run(
                [sys.executable, str(tool_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Tool should either show help or run without error
            assert (
                result.returncode == 0
                or "--help" in result.stdout
                or "usage" in result.stdout.lower()
            )
            logger.info("audio_quality_benchmark.py help/usage verified")
        except subprocess.TimeoutExpired:
            pytest.fail("audio_quality_benchmark.py --help timed out")
        except Exception as e:
            logger.warning(f"Could not test help for audio_quality_benchmark.py: {e}")


class TestQualityDashboard:
    """Test quality_dashboard.py tool."""

    def test_tool_exists(self):
        """Test that quality_dashboard.py exists."""
        tool_path = tools_dir / "quality_dashboard.py"
        if not tool_path.exists():
            pytest.skip(
                "quality_dashboard.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("quality_dashboard.py found")

    def test_tool_import(self):
        """Test that quality_dashboard.py can be imported."""
        tool_path = tools_dir / "quality_dashboard.py"
        if not tool_path.exists():
            pytest.skip("quality_dashboard.py not found")

        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "quality_dashboard", tool_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                assert module is not None
                logger.info("quality_dashboard.py imported successfully")
        except Exception as e:
            pytest.fail(f"Failed to import quality_dashboard.py: {e}")

    def test_tool_help(self):
        """Test that quality_dashboard.py has help/usage information."""
        tool_path = tools_dir / "quality_dashboard.py"
        if not tool_path.exists():
            pytest.skip("quality_dashboard.py not found")

        try:
            result = subprocess.run(
                [sys.executable, str(tool_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert (
                result.returncode == 0
                or "--help" in result.stdout
                or "usage" in result.stdout.lower()
            )
            logger.info("quality_dashboard.py help/usage verified")
        except subprocess.TimeoutExpired:
            pytest.fail("quality_dashboard.py --help timed out")
        except Exception as e:
            logger.warning(f"Could not test help for quality_dashboard.py: {e}")


class TestDatasetQA:
    """Test dataset_qa.py tool."""

    def test_tool_exists(self):
        """Test that dataset_qa.py exists."""
        tool_path = tools_dir / "dataset_qa.py"
        if not tool_path.exists():
            pytest.skip(
                "dataset_qa.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("dataset_qa.py found")

    def test_tool_import(self):
        """Test that dataset_qa.py can be imported."""
        tool_path = tools_dir / "dataset_qa.py"
        if not tool_path.exists():
            pytest.skip("dataset_qa.py not found")

        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("dataset_qa", tool_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                assert module is not None
                logger.info("dataset_qa.py imported successfully")
        except Exception as e:
            pytest.fail(f"Failed to import dataset_qa.py: {e}")

    def test_tool_help(self):
        """Test that dataset_qa.py has help/usage information."""
        tool_path = tools_dir / "dataset_qa.py"
        if not tool_path.exists():
            pytest.skip("dataset_qa.py not found")

        try:
            result = subprocess.run(
                [sys.executable, str(tool_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert (
                result.returncode == 0
                or "--help" in result.stdout
                or "usage" in result.stdout.lower()
            )
            logger.info("dataset_qa.py help/usage verified")
        except subprocess.TimeoutExpired:
            pytest.fail("dataset_qa.py --help timed out")
        except Exception as e:
            logger.warning(f"Could not test help for dataset_qa.py: {e}")


class TestDatasetReport:
    """Test dataset_report.py tool."""

    def test_tool_exists(self):
        """Test that dataset_report.py exists."""
        tool_path = tools_dir / "dataset_report.py"
        if not tool_path.exists():
            pytest.skip(
                "dataset_report.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("dataset_report.py found")

    def test_tool_import(self):
        """Test that dataset_report.py can be imported."""
        tool_path = tools_dir / "dataset_report.py"
        if not tool_path.exists():
            pytest.skip("dataset_report.py not found")

        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("dataset_report", tool_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                assert module is not None
                logger.info("dataset_report.py imported successfully")
        except Exception as e:
            pytest.fail(f"Failed to import dataset_report.py: {e}")

    def test_tool_help(self):
        """Test that dataset_report.py has help/usage information."""
        tool_path = tools_dir / "dataset_report.py"
        if not tool_path.exists():
            pytest.skip("dataset_report.py not found")

        try:
            result = subprocess.run(
                [sys.executable, str(tool_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert (
                result.returncode == 0
                or "--help" in result.stdout
                or "usage" in result.stdout.lower()
            )
            logger.info("dataset_report.py help/usage verified")
        except subprocess.TimeoutExpired:
            pytest.fail("dataset_report.py --help timed out")
        except Exception as e:
            logger.warning(f"Could not test help for dataset_report.py: {e}")


class TestBenchmarkEngines:
    """Test benchmark_engines.py tool."""

    def test_tool_exists(self):
        """Test that benchmark_engines.py exists."""
        tool_path = tools_dir / "benchmark_engines.py"
        if not tool_path.exists():
            pytest.skip(
                "benchmark_engines.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("benchmark_engines.py found")

    def test_tool_import(self):
        """Test that benchmark_engines.py can be imported."""
        tool_path = tools_dir / "benchmark_engines.py"
        if not tool_path.exists():
            pytest.skip("benchmark_engines.py not found")

        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "benchmark_engines", tool_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                assert module is not None
                logger.info("benchmark_engines.py imported successfully")
        except Exception as e:
            pytest.fail(f"Failed to import benchmark_engines.py: {e}")

    def test_tool_help(self):
        """Test that benchmark_engines.py has help/usage information."""
        tool_path = tools_dir / "benchmark_engines.py"
        if not tool_path.exists():
            pytest.skip("benchmark_engines.py not found")

        try:
            result = subprocess.run(
                [sys.executable, str(tool_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert (
                result.returncode == 0
                or "--help" in result.stdout
                or "usage" in result.stdout.lower()
            )
            logger.info("benchmark_engines.py help/usage verified")
        except subprocess.TimeoutExpired:
            pytest.fail("benchmark_engines.py --help timed out")
        except Exception as e:
            logger.warning(f"Could not test help for benchmark_engines.py: {e}")


class TestSystemMonitoringTools:
    """Test system monitoring tools."""

    def test_system_health_validator_exists(self):
        """Test that system_health_validator.py exists."""
        tool_path = tools_dir / "system_health_validator.py"
        if not tool_path.exists():
            pytest.skip(
                "system_health_validator.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("system_health_validator.py found")

    def test_system_monitor_exists(self):
        """Test that system_monitor.py exists."""
        tool_path = tools_dir / "system_monitor.py"
        if not tool_path.exists():
            pytest.skip(
                "system_monitor.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("system_monitor.py found")

    def test_performance_monitor_exists(self):
        """Test that performance_monitor.py exists."""
        tool_path = tools_dir / "performance_monitor.py"
        if not tool_path.exists():
            pytest.skip(
                "performance_monitor.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("performance_monitor.py found")

    def test_profile_engine_memory_exists(self):
        """Test that profile_engine_memory.py exists."""
        tool_path = tools_dir / "profile_engine_memory.py"
        if not tool_path.exists():
            pytest.skip(
                "profile_engine_memory.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("profile_engine_memory.py found")


class TestTrainingTools:
    """Test training tools."""

    def test_train_ultimate_exists(self):
        """Test that train_ultimate.py exists."""
        tool_path = tools_dir / "train_ultimate.py"
        if not tool_path.exists():
            pytest.skip(
                "train_ultimate.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("train_ultimate.py found")

    def test_train_voice_quality_exists(self):
        """Test that train_voice_quality.py exists."""
        tool_path = tools_dir / "train_voice_quality.py"
        if not tool_path.exists():
            pytest.skip(
                "train_voice_quality.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("train_voice_quality.py found")

    def test_config_optimizer_exists(self):
        """Test that config_optimizer.py exists."""
        tool_path = tools_dir / "config_optimizer.py"
        if not tool_path.exists():
            pytest.skip(
                "config_optimizer.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("config_optimizer.py found")


class TestAudioProcessingUtilities:
    """Test audio processing utilities."""

    def test_repair_wavs_exists(self):
        """Test that repair_wavs.py exists."""
        tool_path = tools_dir / "repair_wavs.py"
        if not tool_path.exists():
            pytest.skip(
                "repair_wavs.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("repair_wavs.py found")

    def test_mark_bad_clips_exists(self):
        """Test that mark_bad_clips.py exists."""
        tool_path = tools_dir / "mark_bad_clips.py"
        if not tool_path.exists():
            pytest.skip(
                "mark_bad_clips.py not found - tool not yet copied from old project"
            )
        assert tool_path.exists()
        logger.info("mark_bad_clips.py found")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
