"""
Unit Tests for Training Progress Monitor
Tests training progress monitoring functionality comprehensively.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock dependencies before importing
import sys

# Create mock modules for dependencies that might not be available
for module_name in ["torch", "torch.utils.tensorboard", "tensorboard", "wandb"]:
    if module_name not in sys.modules:
        mock_module = MagicMock()
        if module_name == "torch":
            mock_module.__version__ = "2.0.0"  # Required for TTS version check
        elif module_name == "torch.utils.tensorboard" or module_name == "tensorboard":
            mock_module.SummaryWriter = MagicMock()
        elif module_name == "wandb":
            mock_module.init = MagicMock()
        sys.modules[module_name] = mock_module
    elif module_name == "torch":
        # Ensure existing mock has __version__
        if not hasattr(sys.modules[module_name], "__version__") or isinstance(sys.modules[module_name].__version__, MagicMock):
            sys.modules[module_name].__version__ = "2.0.0"

# Import the training progress monitor module
try:
    from app.core.training import training_progress_monitor
    from app.core.training.training_progress_monitor import (
        TrainingProgressMonitor,
        create_training_progress_monitor,
    )
except ImportError as e:
    pytest.skip(f"Could not import training_progress_monitor: {e}", allow_module_level=True)


class TestTrainingProgressMonitorImports:
    """Test training progress monitor module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            training_progress_monitor is not None
        ), "Failed to import training_progress_monitor module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(training_progress_monitor)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"

    def test_training_progress_monitor_class_exists(self):
        """Test TrainingProgressMonitor class exists."""
        assert hasattr(
            training_progress_monitor, "TrainingProgressMonitor"
        ), "TrainingProgressMonitor class should exist"
        assert isinstance(
            training_progress_monitor.TrainingProgressMonitor, type
        ), "TrainingProgressMonitor should be a class"

    def test_create_training_progress_monitor_function_exists(self):
        """Test create_training_progress_monitor function exists."""
        assert hasattr(
            training_progress_monitor, "create_training_progress_monitor"
        ), "create_training_progress_monitor function should exist"
        assert callable(
            training_progress_monitor.create_training_progress_monitor
        ), "create_training_progress_monitor should be callable"


class TestTrainingProgressMonitorInitialization:
    """Test TrainingProgressMonitor initialization."""

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_init_default(self):
        """Test initialization with default parameters."""
        monitor = TrainingProgressMonitor()
        assert monitor.max_history == 1000
        assert monitor.current_status == {}
        assert len(monitor.history) == 0
        assert monitor.metrics_history == {}
        assert len(monitor.callbacks) == 0
        assert monitor.tensorboard_writer is None

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_init_custom_max_history(self):
        """Test initialization with custom max_history."""
        monitor = TrainingProgressMonitor(max_history=500)
        assert monitor.max_history == 500

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_init_disable_tensorboard(self):
        """Test initialization with tensorboard disabled."""
        monitor = TrainingProgressMonitor(enable_tensorboard=False)
        assert monitor.tensorboard_writer is None

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", True)
    @patch("app.core.training.training_progress_monitor.SummaryWriter")
    def test_init_with_tensorboard(self, mock_summary_writer):
        """Test initialization with tensorboard enabled."""
        mock_summary_writer.return_value = MagicMock()
        with tempfile.TemporaryDirectory() as tmpdir:
            monitor = TrainingProgressMonitor(
                log_dir=tmpdir, enable_tensorboard=True
            )
            assert monitor.tensorboard_writer is not None
            mock_summary_writer.assert_called_once()


class TestTrainingProgressMonitorStartMonitoring:
    """Test start_monitoring method."""

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    @patch("app.core.training.training_progress_monitor.HAS_WANDB", False)
    def test_start_monitoring_basic(self):
        """Test basic start_monitoring."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring(
            training_id="test_training_1", total_epochs=100
        )

        status = monitor.get_current_status()
        assert status["training_id"] == "test_training_1"
        assert status["status"] == "running"
        assert status["total_epochs"] == 100
        assert status["current_epoch"] == 0
        assert status["progress"] == 0.0
        assert "started_at" in status

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    @patch("app.core.training.training_progress_monitor.HAS_WANDB", False)
    def test_start_monitoring_with_params(self):
        """Test start_monitoring with initial parameters."""
        monitor = TrainingProgressMonitor()
        initial_params = {"learning_rate": 0.001, "batch_size": 4}
        monitor.start_monitoring(
            training_id="test_training_2",
            total_epochs=50,
            initial_params=initial_params,
        )

        status = monitor.get_current_status()
        assert status["params"] == initial_params

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    @patch("app.core.training.training_progress_monitor.HAS_WANDB", True)
    @patch("app.core.training.training_progress_monitor.wandb")
    def test_start_monitoring_with_wandb(self, mock_wandb):
        """Test start_monitoring with WandB enabled."""
        mock_wandb.init.return_value = MagicMock()
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring(
            training_id="test_training_3",
            total_epochs=100,
            enable_wandb=True,
            wandb_project="test_project",
        )

        assert monitor.enable_wandb is True
        assert monitor.wandb_run is not None
        mock_wandb.init.assert_called_once()


class TestTrainingProgressMonitorUpdateProgress:
    """Test update_progress method."""

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_update_progress_without_monitoring(self):
        """Test update_progress without active monitoring."""
        monitor = TrainingProgressMonitor()
        # Should not raise error, just log warning
        monitor.update_progress(epoch=1, metrics={"loss": 0.5})

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_update_progress_basic(self):
        """Test basic progress update."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        monitor.update_progress(epoch=5, metrics={"loss": 0.5})

        status = monitor.get_current_status()
        assert status["current_epoch"] == 5
        assert status["progress"] == 0.5
        assert status["metrics"]["loss"] == 0.5

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_update_progress_multiple_metrics(self):
        """Test progress update with multiple metrics."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        monitor.update_progress(
            epoch=3, metrics={"loss": 0.5, "accuracy": 0.9, "f1": 0.85}
        )

        metrics = monitor.get_metrics()
        assert metrics["loss"] == 0.5
        assert metrics["accuracy"] == 0.9
        assert metrics["f1"] == 0.85

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_update_progress_history(self):
        """Test that progress updates are added to history."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        monitor.update_progress(epoch=1, metrics={"loss": 0.6})
        monitor.update_progress(epoch=2, metrics={"loss": 0.5})

        history = monitor.get_history()
        assert len(history) == 2
        assert history[0]["epoch"] == 1
        assert history[1]["epoch"] == 2

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_update_progress_metrics_history(self):
        """Test that metrics are tracked in history."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        monitor.update_progress(epoch=1, metrics={"loss": 0.6})
        monitor.update_progress(epoch=2, metrics={"loss": 0.5})

        metrics_history = monitor.get_metrics_history()
        assert "loss" in metrics_history
        assert len(metrics_history["loss"]) == 2
        assert metrics_history["loss"][0] == 0.6
        assert metrics_history["loss"][1] == 0.5

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_update_progress_with_additional_info(self):
        """Test progress update with additional info."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        additional_info = {"step": 100, "batch": 5}
        monitor.update_progress(
            epoch=1, metrics={"loss": 0.5}, additional_info=additional_info
        )

        history = monitor.get_history()
        assert history[0]["additional_info"] == additional_info


class TestTrainingProgressMonitorCompleteTraining:
    """Test complete_training method."""

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_complete_training_success(self):
        """Test completing training successfully."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)
        monitor.complete_training(final_metrics={"loss": 0.3}, success=True)

        status = monitor.get_current_status()
        assert status["status"] == "completed"
        assert status["progress"] == 1.0
        assert status["metrics"]["loss"] == 0.3
        assert "completed_at" in status

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_complete_training_failure(self):
        """Test completing training with failure."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)
        monitor.complete_training(
            success=False, error_message="Training failed"
        )

        status = monitor.get_current_status()
        assert status["status"] == "failed"
        assert status["error"] == "Training failed"

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_complete_training_without_monitoring(self):
        """Test complete_training without active monitoring."""
        monitor = TrainingProgressMonitor()
        # Should not raise error, just log warning
        monitor.complete_training()


class TestTrainingProgressMonitorCancelTraining:
    """Test cancel_training method."""

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_cancel_training(self):
        """Test cancelling training."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)
        monitor.cancel_training(reason="User requested cancellation")

        status = monitor.get_current_status()
        assert status["status"] == "cancelled"
        assert status["cancellation_reason"] == "User requested cancellation"
        assert "cancelled_at" in status

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_cancel_training_without_reason(self):
        """Test cancelling training without reason."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)
        monitor.cancel_training()

        status = monitor.get_current_status()
        assert status["status"] == "cancelled"
        assert "cancellation_reason" not in status


class TestTrainingProgressMonitorGetters:
    """Test getter methods."""

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_get_current_status(self):
        """Test get_current_status."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        status = monitor.get_current_status()
        assert isinstance(status, dict)
        assert status["training_id"] == "test_training"

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_get_progress(self):
        """Test get_progress."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        assert monitor.get_progress() == 0.0

        monitor.update_progress(epoch=5, metrics={"loss": 0.5})
        assert monitor.get_progress() == 0.5

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_get_metrics(self):
        """Test get_metrics."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        assert monitor.get_metrics() == {}

        monitor.update_progress(epoch=1, metrics={"loss": 0.5, "acc": 0.9})
        metrics = monitor.get_metrics()
        assert metrics["loss"] == 0.5
        assert metrics["acc"] == 0.9

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_get_metrics_history_all(self):
        """Test get_metrics_history for all metrics."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        monitor.update_progress(epoch=1, metrics={"loss": 0.6})
        monitor.update_progress(epoch=2, metrics={"loss": 0.5, "acc": 0.9})

        history = monitor.get_metrics_history()
        assert "loss" in history
        assert "acc" in history
        assert len(history["loss"]) == 2

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_get_metrics_history_specific(self):
        """Test get_metrics_history for specific metric."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        monitor.update_progress(epoch=1, metrics={"loss": 0.6})
        monitor.update_progress(epoch=2, metrics={"loss": 0.5})

        history = monitor.get_metrics_history("loss")
        assert "loss" in history
        assert len(history["loss"]) == 2

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_get_history(self):
        """Test get_history."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        monitor.update_progress(epoch=1, metrics={"loss": 0.6})
        monitor.update_progress(epoch=2, metrics={"loss": 0.5})

        history = monitor.get_history()
        assert len(history) == 2
        assert history[0]["epoch"] == 1
        assert history[1]["epoch"] == 2

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_get_history_with_limit(self):
        """Test get_history with limit."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        for i in range(5):
            monitor.update_progress(epoch=i, metrics={"loss": 0.5})

        history = monitor.get_history(limit=2)
        assert len(history) == 2
        assert history[0]["epoch"] == 3
        assert history[1]["epoch"] == 4


class TestTrainingProgressMonitorCallbacks:
    """Test callback functionality."""

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_register_callback(self):
        """Test registering a callback."""
        monitor = TrainingProgressMonitor()
        callback_calls = []

        def callback(status):
            callback_calls.append(status)

        monitor.register_callback(callback)
        assert len(monitor.callbacks) == 1

        monitor.start_monitoring("test_training", total_epochs=10)
        monitor.update_progress(epoch=1, metrics={"loss": 0.5})

        assert len(callback_calls) == 1

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_unregister_callback(self):
        """Test unregistering a callback."""
        monitor = TrainingProgressMonitor()
        callback_calls = []

        def callback(status):
            callback_calls.append(status)

        monitor.register_callback(callback)
        monitor.unregister_callback(callback)
        assert len(monitor.callbacks) == 0

        monitor.start_monitoring("test_training", total_epochs=10)
        monitor.update_progress(epoch=1, metrics={"loss": 0.5})

        assert len(callback_calls) == 0

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_callback_with_exception(self):
        """Test callback that raises exception doesn't break monitoring."""
        monitor = TrainingProgressMonitor()

        def bad_callback(status):
            raise Exception("Callback error")

        monitor.register_callback(bad_callback)
        monitor.start_monitoring("test_training", total_epochs=10)

        # Should not raise exception
        monitor.update_progress(epoch=1, metrics={"loss": 0.5})


class TestTrainingProgressMonitorSummary:
    """Test get_summary method."""

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_get_summary_without_monitoring(self):
        """Test get_summary without active monitoring."""
        monitor = TrainingProgressMonitor()
        summary = monitor.get_summary()
        assert "message" in summary

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_get_summary_basic(self):
        """Test basic summary."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        summary = monitor.get_summary()
        assert summary["training_id"] == "test_training"
        assert summary["status"] == "running"
        assert summary["total_epochs"] == 10

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_get_summary_with_loss_statistics(self):
        """Test summary with loss statistics."""
        monitor = TrainingProgressMonitor()
        monitor.start_monitoring("test_training", total_epochs=10)

        monitor.update_progress(epoch=1, metrics={"loss": 0.6})
        monitor.update_progress(epoch=2, metrics={"loss": 0.5})
        monitor.update_progress(epoch=3, metrics={"loss": 0.4})

        summary = monitor.get_summary()
        assert "loss_statistics" in summary
        assert summary["loss_statistics"]["current"] == 0.4
        assert summary["loss_statistics"]["min"] == 0.4
        assert summary["loss_statistics"]["max"] == 0.6


class TestTrainingProgressMonitorReset:
    """Test reset method."""

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", True)
    @patch("app.core.training.training_progress_monitor.SummaryWriter")
    def test_reset(self, mock_summary_writer):
        """Test resetting monitor."""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer

        monitor = TrainingProgressMonitor(enable_tensorboard=True)
        monitor.start_monitoring("test_training", total_epochs=10)
        monitor.update_progress(epoch=1, metrics={"loss": 0.5})

        monitor.reset()

        assert monitor.current_status == {}
        assert len(monitor.history) == 0
        assert monitor.metrics_history == {}
        mock_writer.close.assert_called_once()


class TestCreateTrainingProgressMonitor:
    """Test create_training_progress_monitor factory function."""

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_create_training_progress_monitor_default(self):
        """Test create_training_progress_monitor with default parameters."""
        monitor = create_training_progress_monitor()
        assert isinstance(monitor, TrainingProgressMonitor)
        assert monitor.max_history == 1000

    @patch("app.core.training.training_progress_monitor.HAS_TENSORBOARD", False)
    def test_create_training_progress_monitor_custom(self):
        """Test create_training_progress_monitor with custom parameters."""
        monitor = create_training_progress_monitor(
            max_history=500, enable_tensorboard=False
        )
        assert isinstance(monitor, TrainingProgressMonitor)
        assert monitor.max_history == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
