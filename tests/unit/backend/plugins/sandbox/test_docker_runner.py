"""
Unit tests for Docker-based plugin runner.

Tests the DockerRunner, DockerRunnerConfig, and DockerRunnerManager classes.
These tests mock Docker interactions to run without Docker installed.
"""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from backend.plugins.sandbox.docker_runner import (
    DOCKER_AVAILABLE,
    ContainerState,
    DockerRunner,
    DockerRunnerConfig,
    DockerRunnerManager,
    get_docker_manager,
    reset_docker_manager,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_plugin_dir(tmp_path):
    """Create a temporary plugin directory."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    # Create minimal plugin structure
    (plugin_dir / "main.py").write_text('print("Hello from plugin")')
    (plugin_dir / "manifest.json").write_text(json.dumps({
        "id": "test-plugin",
        "name": "Test Plugin",
        "version": "1.0.0",
    }))

    return plugin_dir


@pytest.fixture
def basic_config(temp_plugin_dir):
    """Create a basic runner config."""
    return DockerRunnerConfig(
        plugin_id="test.plugin",
        plugin_path=temp_plugin_dir,
        entry_module="main",
        memory_limit_mb=256,
        cpu_limit=0.5,
    )


@pytest.fixture
def mock_docker_client():
    """Create a mock Docker client."""
    client = MagicMock()
    client.ping.return_value = True

    # Mock images
    client.images.get.return_value = MagicMock()
    client.images.pull.return_value = MagicMock()

    # Mock container
    container = MagicMock()
    container.short_id = "abc123"
    container.status = "running"
    container.start.return_value = None
    container.stop.return_value = None
    container.kill.return_value = None
    container.remove.return_value = None
    container.reload.return_value = None
    container.logs.return_value = "Container logs here"
    container.put_archive.return_value = True
    container.stats.return_value = {
        "memory_stats": {"usage": 100000000, "limit": 256000000},
        "cpu_stats": {"cpu_usage": {"total_usage": 1000}, "system_cpu_usage": 10000, "online_cpus": 4},
        "precpu_stats": {"cpu_usage": {"total_usage": 500}, "system_cpu_usage": 5000},
    }
    container.exec_run.return_value = MagicMock(exit_code=0, output=b'{"result": "ok"}')

    client.containers.create.return_value = container

    return client, container


@pytest.fixture
def runner_with_mocks(basic_config, mock_docker_client):
    """Create a DockerRunner with mocked Docker client."""
    client, container = mock_docker_client
    runner = DockerRunner(basic_config)
    runner._client = client
    runner._container = container
    return runner, client, container


# =============================================================================
# Test DockerRunnerConfig
# =============================================================================


class TestDockerRunnerConfig:
    """Tests for DockerRunnerConfig dataclass."""

    def test_basic_creation(self, temp_plugin_dir):
        """Test creating a basic config."""
        config = DockerRunnerConfig(
            plugin_id="my.plugin",
            plugin_path=temp_plugin_dir,
            entry_module="main",
        )

        assert config.plugin_id == "my.plugin"
        assert config.plugin_path == temp_plugin_dir
        assert config.entry_module == "main"
        assert config.image == "python:3.11-slim"
        assert config.memory_limit_mb == 512
        assert config.cpu_limit == 1.0

    def test_custom_resource_limits(self, temp_plugin_dir):
        """Test config with custom resource limits."""
        config = DockerRunnerConfig(
            plugin_id="my.plugin",
            plugin_path=temp_plugin_dir,
            entry_module="main",
            memory_limit_mb=1024,
            cpu_limit=2.0,
            pids_limit=50,
        )

        assert config.memory_limit_mb == 1024
        assert config.cpu_limit == 2.0
        assert config.pids_limit == 50

    def test_security_defaults(self, temp_plugin_dir):
        """Test security-related defaults."""
        config = DockerRunnerConfig(
            plugin_id="my.plugin",
            plugin_path=temp_plugin_dir,
            entry_module="main",
        )

        assert config.network_mode == "none"  # Isolated
        assert config.read_only_root is True
        assert "ALL" in config.cap_drop
        assert "no-new-privileges:true" in config.security_opt

    def test_empty_plugin_id_raises(self, temp_plugin_dir):
        """Test that empty plugin_id raises ValueError."""
        with pytest.raises(ValueError, match="plugin_id is required"):
            DockerRunnerConfig(
                plugin_id="",
                plugin_path=temp_plugin_dir,
                entry_module="main",
            )

    def test_nonexistent_path_raises(self):
        """Test that non-existent plugin path raises ValueError."""
        with pytest.raises(ValueError, match="plugin_path must exist"):
            DockerRunnerConfig(
                plugin_id="my.plugin",
                plugin_path=Path("/nonexistent/path"),
                entry_module="main",
            )


# =============================================================================
# Test DockerRunner
# =============================================================================


class TestDockerRunner:
    """Tests for DockerRunner class."""

    def test_container_name(self, basic_config):
        """Test container name generation."""
        runner = DockerRunner(basic_config)
        assert runner.container_name == "voicestudio-plugin-test-plugin"

    def test_container_name_sanitization(self, temp_plugin_dir):
        """Test that plugin IDs are sanitized for Docker naming."""
        config = DockerRunnerConfig(
            plugin_id="my_complex.plugin_name",
            plugin_path=temp_plugin_dir,
            entry_module="main",
        )
        runner = DockerRunner(config)

        # Dots and underscores should become hyphens
        assert "." not in runner.container_name
        assert "_" not in runner.container_name

    def test_initial_state(self, basic_config):
        """Test initial runner state."""
        runner = DockerRunner(basic_config)

        assert runner.state == ContainerState.NOT_CREATED
        assert runner.container_id is None
        assert runner.is_running is False

    def test_is_running_states(self, runner_with_mocks):
        """Test is_running property for various states."""
        runner, _, _ = runner_with_mocks

        # States where is_running should be True
        for state in [ContainerState.RUNNING, ContainerState.INITIALIZING, ContainerState.ACTIVE]:
            runner.state = state
            assert runner.is_running is True, f"Expected is_running=True for {state}"

        # States where is_running should be False
        for state in [ContainerState.NOT_CREATED, ContainerState.CREATING, ContainerState.STOPPED]:
            runner.state = state
            assert runner.is_running is False, f"Expected is_running=False for {state}"


class TestDockerRunnerAvailability:
    """Tests for Docker availability checking."""

    def test_docker_available_constant(self):
        """Test that DOCKER_AVAILABLE is a boolean."""
        assert isinstance(DOCKER_AVAILABLE, bool)

    @patch("backend.plugins.sandbox.docker_runner.docker")
    def test_is_available_when_docker_works(self, mock_docker):
        """Test is_available returns True when Docker is working."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_docker.from_env.return_value = mock_client

        with patch("backend.plugins.sandbox.docker_runner.DOCKER_AVAILABLE", True):
            # Need to reimport to get the patched version
            from backend.plugins.sandbox.docker_runner import DockerRunner
            result = DockerRunner.is_available()
            assert result is True

    @patch("backend.plugins.sandbox.docker_runner.DOCKER_AVAILABLE", False)
    def test_is_available_without_package(self):
        """Test is_available returns False when docker package not installed."""
        result = DockerRunner.is_available()
        assert result is False


class TestDockerRunnerLifecycle:
    """Tests for Docker runner lifecycle (start/stop)."""

    @pytest.mark.asyncio
    async def test_start_without_docker_raises(self, basic_config):
        """Test that start raises when Docker is unavailable."""
        runner = DockerRunner(basic_config)

        with patch("backend.plugins.sandbox.docker_runner.DOCKER_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="Docker package not installed"):
                await runner.start()

    @pytest.mark.asyncio
    async def test_start_wrong_state_raises(self, runner_with_mocks):
        """Test that start raises when in wrong state."""
        runner, _, _ = runner_with_mocks
        runner.state = ContainerState.RUNNING

        with pytest.raises(RuntimeError, match="Cannot start in state"):
            await runner.start()

    @pytest.mark.asyncio
    async def test_stop_not_running_noop(self, runner_with_mocks):
        """Test that stop is a no-op when not running."""
        runner, _, container = runner_with_mocks
        runner.state = ContainerState.STOPPED

        await runner.stop()

        # Container methods should not be called
        container.stop.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop_graceful(self, runner_with_mocks):
        """Test graceful shutdown."""
        runner, _, container = runner_with_mocks
        runner.state = ContainerState.ACTIVE

        with patch.object(runner, "_cleanup", new_callable=AsyncMock):
            await runner.stop(force=False)

        container.stop.assert_called_once()
        assert runner.state == ContainerState.STOPPED

    @pytest.mark.asyncio
    async def test_stop_force(self, runner_with_mocks):
        """Test forced shutdown."""
        runner, _, container = runner_with_mocks
        runner.state = ContainerState.ACTIVE

        with patch.object(runner, "_cleanup", new_callable=AsyncMock):
            await runner.stop(force=True)

        container.kill.assert_called_once()


class TestDockerRunnerCapabilities:
    """Tests for plugin capability invocation."""

    @pytest.mark.asyncio
    async def test_invoke_wrong_state_raises(self, runner_with_mocks):
        """Test that invoke raises when not active."""
        runner, _, _ = runner_with_mocks
        runner.state = ContainerState.RUNNING  # Not ACTIVE

        with pytest.raises(RuntimeError, match="Cannot invoke capability in state"):
            await runner.invoke_capability("my_capability", {"param": "value"})


class TestDockerRunnerStats:
    """Tests for container statistics."""

    @pytest.mark.asyncio
    async def test_get_stats(self, runner_with_mocks):
        """Test getting container stats."""
        runner, _, _ = runner_with_mocks
        runner.state = ContainerState.ACTIVE

        stats = await runner.get_stats()

        assert "memory" in stats
        assert "cpu" in stats
        assert stats["memory"]["usage_bytes"] > 0

    @pytest.mark.asyncio
    async def test_get_stats_no_container(self, basic_config):
        """Test get_stats returns empty dict when no container."""
        runner = DockerRunner(basic_config)

        stats = await runner.get_stats()
        assert stats == {}

    @pytest.mark.asyncio
    async def test_get_logs(self, runner_with_mocks):
        """Test getting container logs."""
        runner, _, _ = runner_with_mocks
        runner.state = ContainerState.ACTIVE

        logs = await runner.get_logs(tail=50)

        assert "Container logs" in logs


class TestDockerRunnerCallbacks:
    """Tests for runner callbacks."""

    def test_on_state_change_registration(self, basic_config):
        """Test registering state change callback."""
        runner = DockerRunner(basic_config)
        callback = MagicMock()

        runner.on_state_change(callback)
        runner._set_state(ContainerState.CREATING)

        callback.assert_called_once_with(ContainerState.CREATING)

    def test_on_crash_registration(self, basic_config):
        """Test registering crash callback."""
        runner = DockerRunner(basic_config)
        callback = AsyncMock()

        runner.on_crash(callback)

        # Callback is registered
        assert callback in runner._on_crash


class TestDockerRunnerInternals:
    """Tests for internal helper methods."""

    def test_parse_stats(self, runner_with_mocks):
        """Test stats parsing."""
        runner, _, _ = runner_with_mocks

        raw_stats = {
            "memory_stats": {"usage": 100 * 1024 * 1024, "limit": 512 * 1024 * 1024},
            "cpu_stats": {
                "cpu_usage": {"total_usage": 2000},
                "system_cpu_usage": 20000,
                "online_cpus": 2,
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 1000},
                "system_cpu_usage": 10000,
            },
        }

        parsed = runner._parse_stats(raw_stats)

        assert "memory" in parsed
        assert parsed["memory"]["usage_mb"] == 100
        assert parsed["memory"]["limit_mb"] == 512
        assert "cpu" in parsed

    def test_get_next_request_id(self, runner_with_mocks):
        """Test request ID generation."""
        runner, _, _ = runner_with_mocks

        id1 = runner._get_next_request_id()
        id2 = runner._get_next_request_id()

        assert id1 != id2
        assert "req-" in id1
        assert "req-" in id2


# =============================================================================
# Test DockerRunnerManager
# =============================================================================


class TestDockerRunnerManager:
    """Tests for DockerRunnerManager class."""

    @pytest.fixture(autouse=True)
    def reset_manager(self):
        """Reset global manager before each test."""
        reset_docker_manager()
        yield
        reset_docker_manager()

    def test_get_global_manager(self):
        """Test getting global manager instance."""
        manager1 = get_docker_manager()
        manager2 = get_docker_manager()

        assert manager1 is manager2

    def test_reset_global_manager(self):
        """Test resetting global manager."""
        manager1 = get_docker_manager()
        reset_docker_manager()
        manager2 = get_docker_manager()

        assert manager1 is not manager2

    @patch("backend.plugins.sandbox.docker_runner.DockerRunner.is_available")
    def test_is_docker_available_cached(self, mock_available):
        """Test that Docker availability is cached."""
        mock_available.return_value = True
        manager = DockerRunnerManager()

        result1 = manager.is_docker_available()
        result2 = manager.is_docker_available()

        assert result1 is True
        assert result2 is True
        # Should only check once
        assert mock_available.call_count == 1

    @pytest.mark.asyncio
    @patch("backend.plugins.sandbox.docker_runner.DockerRunner.is_available")
    async def test_create_runner_when_docker_unavailable(self, mock_available, basic_config):
        """Test that create_runner raises when Docker unavailable."""
        mock_available.return_value = False
        manager = DockerRunnerManager()

        with pytest.raises(RuntimeError, match="Docker is not available"):
            await manager.create_runner(basic_config)

    @pytest.mark.asyncio
    @patch("backend.plugins.sandbox.docker_runner.DockerRunner.is_available")
    async def test_create_runner_duplicate_raises(self, mock_available, basic_config):
        """Test that creating duplicate runner raises."""
        mock_available.return_value = True
        manager = DockerRunnerManager()

        await manager.create_runner(basic_config)

        with pytest.raises(ValueError, match="Runner already exists"):
            await manager.create_runner(basic_config)

    @pytest.mark.asyncio
    @patch("backend.plugins.sandbox.docker_runner.DockerRunner.is_available")
    async def test_get_runner(self, mock_available, basic_config):
        """Test getting a runner by plugin ID."""
        mock_available.return_value = True
        manager = DockerRunnerManager()

        runner = await manager.create_runner(basic_config)
        retrieved = manager.get_runner(basic_config.plugin_id)

        assert retrieved is runner

    def test_get_runner_nonexistent(self):
        """Test getting non-existent runner returns None."""
        manager = DockerRunnerManager()

        result = manager.get_runner("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    @patch("backend.plugins.sandbox.docker_runner.DockerRunner.is_available")
    async def test_list_runners(self, mock_available, basic_config, temp_plugin_dir):
        """Test listing all runners."""
        mock_available.return_value = True
        manager = DockerRunnerManager()

        config1 = basic_config
        config2 = DockerRunnerConfig(
            plugin_id="test.plugin2",
            plugin_path=temp_plugin_dir,
            entry_module="main",
        )

        await manager.create_runner(config1)
        await manager.create_runner(config2)

        runners = manager.list_runners()

        assert len(runners) == 2
        assert "test.plugin" in runners
        assert "test.plugin2" in runners

    @pytest.mark.asyncio
    @patch("backend.plugins.sandbox.docker_runner.DockerRunner.is_available")
    async def test_remove_runner(self, mock_available, basic_config):
        """Test removing a runner."""
        mock_available.return_value = True
        manager = DockerRunnerManager()

        await manager.create_runner(basic_config)

        # Mock the runner's remove method
        runner = manager.get_runner(basic_config.plugin_id)
        runner.remove = AsyncMock()

        result = await manager.remove_runner(basic_config.plugin_id)

        assert result is True
        assert manager.get_runner(basic_config.plugin_id) is None

    @pytest.mark.asyncio
    async def test_remove_runner_nonexistent(self):
        """Test removing non-existent runner returns False."""
        manager = DockerRunnerManager()

        result = await manager.remove_runner("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    @patch("backend.plugins.sandbox.docker_runner.DockerRunner.is_available")
    async def test_stop_all(self, mock_available, basic_config, temp_plugin_dir):
        """Test stopping all runners."""
        mock_available.return_value = True
        manager = DockerRunnerManager()

        config1 = basic_config
        config2 = DockerRunnerConfig(
            plugin_id="test.plugin2",
            plugin_path=temp_plugin_dir,
            entry_module="main",
        )

        runner1 = await manager.create_runner(config1)
        runner2 = await manager.create_runner(config2)

        # Mock stop methods
        runner1.stop = AsyncMock()
        runner2.stop = AsyncMock()

        await manager.stop_all()

        runner1.stop.assert_called_once()
        runner2.stop.assert_called_once()

    @pytest.mark.asyncio
    @patch("backend.plugins.sandbox.docker_runner.DockerRunner.is_available")
    async def test_remove_all(self, mock_available, basic_config, temp_plugin_dir):
        """Test removing all runners."""
        mock_available.return_value = True
        manager = DockerRunnerManager()

        config1 = basic_config
        config2 = DockerRunnerConfig(
            plugin_id="test.plugin2",
            plugin_path=temp_plugin_dir,
            entry_module="main",
        )

        runner1 = await manager.create_runner(config1)
        runner2 = await manager.create_runner(config2)

        # Mock remove methods
        runner1.remove = AsyncMock()
        runner2.remove = AsyncMock()

        await manager.remove_all()

        runner1.remove.assert_called_once()
        runner2.remove.assert_called_once()
        assert len(manager.list_runners()) == 0


# =============================================================================
# Test ContainerState enum
# =============================================================================


class TestContainerState:
    """Tests for ContainerState enum."""

    def test_all_states_defined(self):
        """Test that all expected states are defined."""
        expected_states = [
            "NOT_CREATED",
            "CREATING",
            "STARTING",
            "RUNNING",
            "INITIALIZING",
            "ACTIVE",
            "STOPPING",
            "STOPPED",
            "CRASHED",
            "REMOVED",
        ]

        for state_name in expected_states:
            assert hasattr(ContainerState, state_name), f"Missing state: {state_name}"

    def test_state_values_are_strings(self):
        """Test that state values are lowercase strings."""
        for state in ContainerState:
            assert isinstance(state.value, str)
            assert state.value.islower() or state.value == state.value.lower().replace("_", "")
