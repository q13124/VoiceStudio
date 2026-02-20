"""
Unit Tests for Auto Trainer
Tests automatic training functionality comprehensively.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock dependencies before importing
import sys

# Create mock modules for dependencies that might not be available
for module_name in ["torch", "torch.cuda"]:
    if module_name not in sys.modules:
        mock_module = MagicMock()
        if module_name == "torch.cuda":
            mock_module.is_available = lambda: False
        sys.modules[module_name] = mock_module

# Import the auto trainer module
try:
    from app.core.training import auto_trainer
    from app.core.training.auto_trainer import AutoTrainer, create_auto_trainer
except ImportError as e:
    pytest.skip(f"Could not import auto_trainer: {e}", allow_module_level=True)


class TestAutoTrainerImports:
    """Test auto trainer module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert auto_trainer is not None, "Failed to import auto_trainer module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(auto_trainer)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"

    def test_auto_trainer_class_exists(self):
        """Test AutoTrainer class exists."""
        assert hasattr(auto_trainer, "AutoTrainer"), "AutoTrainer class should exist"
        assert isinstance(auto_trainer.AutoTrainer, type), "AutoTrainer should be a class"

    def test_create_auto_trainer_function_exists(self):
        """Test create_auto_trainer function exists."""
        assert hasattr(auto_trainer, "create_auto_trainer"), "create_auto_trainer function should exist"
        assert callable(auto_trainer.create_auto_trainer), "create_auto_trainer should be callable"


class TestAutoTrainerInitialization:
    """Test AutoTrainer initialization."""

    @patch("app.core.training.auto_trainer.Path")
    def test_init_default(self, mock_path):
        """Test initialization with default parameters."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()
        assert trainer.engine == "xtts"
        assert trainer.device is None
        assert trainer.gpu is True
        assert trainer.output_dir is not None

    @patch("app.core.training.auto_trainer.Path")
    def test_init_custom_engine(self, mock_path):
        """Test initialization with custom engine."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer(engine="tortoise")
        assert trainer.engine == "tortoise"

    @patch("app.core.training.auto_trainer.Path")
    def test_init_custom_output_dir(self, mock_path):
        """Test initialization with custom output directory."""
        mock_path.return_value.mkdir = MagicMock()
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = AutoTrainer(output_dir=tmpdir)
            assert str(trainer.output_dir) == tmpdir

    @patch("app.core.training.auto_trainer.Path")
    def test_init_cpu_device(self, mock_path):
        """Test initialization with CPU device."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer(device="cpu", gpu=False)
        assert trainer.device == "cpu"
        assert trainer.gpu is False

    @patch("app.core.training.auto_trainer.Path")
    @patch("app.core.training.auto_trainer.HAS_QUALITY_METRICS", True)
    def test_init_with_quality_metrics(self, mock_path):
        """Test initialization with quality metrics available."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.auto_trainer.EnhancedQualityMetrics") as mock_metrics:
            mock_metrics.return_value = MagicMock()
            trainer = AutoTrainer()
            assert trainer.quality_metrics is not None

    @patch("app.core.training.auto_trainer.Path")
    @patch("app.core.training.auto_trainer.HAS_QUALITY_METRICS", False)
    def test_init_without_quality_metrics(self, mock_path):
        """Test initialization without quality metrics."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()
        assert trainer.quality_metrics is None


class TestAutoTrainerParameterGeneration:
    """Test parameter set generation."""

    @patch("app.core.training.auto_trainer.Path")
    def test_generate_parameter_sets(self, mock_path):
        """Test generating parameter sets."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        param_sets = trainer._generate_parameter_sets(3)
        assert len(param_sets) == 3
        for params in param_sets:
            assert "epochs" in params
            assert "batch_size" in params
            assert "learning_rate" in params
            assert params["epochs"] in [50, 100, 150, 200]
            assert params["batch_size"] in [2, 4, 8, 16]
            assert params["learning_rate"] in [0.00001, 0.0001, 0.0005, 0.001]

    @patch("app.core.training.auto_trainer.Path")
    def test_generate_parameter_sets_large_number(self, mock_path):
        """Test generating parameter sets with large number."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        # Should limit to available combinations
        param_sets = trainer._generate_parameter_sets(1000)
        assert len(param_sets) <= 64  # 4 * 4 * 4 = 64 max combinations


class TestAutoTrainerRecommendedParams:
    """Test recommended parameters method."""

    @patch("app.core.training.auto_trainer.Path")
    def test_get_recommended_params_small_dataset(self, mock_path):
        """Test recommended params for small dataset."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        params = trainer.get_recommended_params(
            dataset_size=5,
            audio_duration=10.0,
            quality_target="standard"
        )
        assert "epochs" in params
        assert "batch_size" in params
        assert "learning_rate" in params
        assert "quality_target" in params
        assert params["quality_target"] == "standard"
        assert params["epochs"] >= 100  # More epochs for small datasets

    @patch("app.core.training.auto_trainer.Path")
    def test_get_recommended_params_large_dataset(self, mock_path):
        """Test recommended params for large dataset."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        params = trainer.get_recommended_params(
            dataset_size=100,
            audio_duration=10.0,
            quality_target="standard"
        )
        assert params["epochs"] <= 100  # Fewer epochs for large datasets
        assert params["batch_size"] >= 4  # Larger batch size for large datasets

    @patch("app.core.training.auto_trainer.Path")
    def test_get_recommended_params_fast_quality(self, mock_path):
        """Test recommended params for fast quality target."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        params = trainer.get_recommended_params(
            dataset_size=50,
            audio_duration=10.0,
            quality_target="fast"
        )
        assert params["quality_target"] == "fast"
        assert params["learning_rate"] > 0.0001  # Higher LR for faster training

    @patch("app.core.training.auto_trainer.Path")
    def test_get_recommended_params_high_quality(self, mock_path):
        """Test recommended params for high quality target."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        params = trainer.get_recommended_params(
            dataset_size=50,
            audio_duration=10.0,
            quality_target="high"
        )
        assert params["quality_target"] == "high"
        assert params["epochs"] >= 100  # More epochs for high quality

    @patch("app.core.training.auto_trainer.Path")
    def test_get_recommended_params_ultra_quality(self, mock_path):
        """Test recommended params for ultra quality target."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        params = trainer.get_recommended_params(
            dataset_size=50,
            audio_duration=10.0,
            quality_target="ultra"
        )
        assert params["quality_target"] == "ultra"
        assert params["epochs"] >= 200  # Many epochs for ultra quality
        assert params["learning_rate"] < 0.0001  # Lower LR for better quality


class TestAutoTrainerAutoTrain:
    """Test auto_train method."""

    @patch("app.core.training.auto_trainer.Path")
    @patch("app.core.training.auto_trainer.HAS_UNIFIED_TRAINER", False)
    def test_auto_train_without_unified_trainer(self, mock_path):
        """Test auto_train raises error when unified trainer not available."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        with pytest.raises(RuntimeError, match="Unified trainer not available"):
            import asyncio
            asyncio.run(trainer.auto_train("metadata.json"))

    @patch("app.core.training.auto_trainer.Path")
    @patch("app.core.training.auto_trainer.HAS_UNIFIED_TRAINER", True)
    @pytest.mark.asyncio
    async def test_auto_train_without_optimization(self, mock_path):
        """Test auto_train without parameter optimization."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with patch("app.core.training.auto_trainer.UnifiedTrainer") as mock_trainer_class:
                mock_trainer = MagicMock()
                mock_trainer.initialize_model.return_value = True
                mock_trainer.train = AsyncMock(return_value={"final_loss": 0.5})
                mock_trainer.export_model.return_value = str(Path(tmpdir) / "model")
                mock_trainer_class.return_value = mock_trainer

                result = await trainer.auto_train(
                    str(metadata_path),
                    optimize_params=False,
                    max_runs=1
                )

                assert "best_model_path" in result
                assert "best_quality" in result
                assert "best_params" in result
                assert "training_history" in result
                assert result["total_runs"] == 1

    @patch("app.core.training.auto_trainer.Path")
    @patch("app.core.training.auto_trainer.HAS_UNIFIED_TRAINER", True)
    @pytest.mark.asyncio
    async def test_auto_train_with_optimization(self, mock_path):
        """Test auto_train with parameter optimization."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with patch("app.core.training.auto_trainer.UnifiedTrainer") as mock_trainer_class:
                mock_trainer = MagicMock()
                mock_trainer.initialize_model.return_value = True
                mock_trainer.train = AsyncMock(return_value={"final_loss": 0.5})
                mock_trainer.export_model.return_value = str(Path(tmpdir) / "model")
                mock_trainer_class.return_value = mock_trainer

                result = await trainer.auto_train(
                    str(metadata_path),
                    optimize_params=True,
                    max_runs=2
                )

                assert result["total_runs"] == 2
                assert len(result["training_history"]) == 2

    @patch("app.core.training.auto_trainer.Path")
    @patch("app.core.training.auto_trainer.HAS_UNIFIED_TRAINER", True)
    @pytest.mark.asyncio
    async def test_auto_train_with_progress_callback(self, mock_path):
        """Test auto_train with progress callback."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        callback_calls = []

        def progress_callback(update):
            callback_calls.append(update)

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with patch("app.core.training.auto_trainer.UnifiedTrainer") as mock_trainer_class:
                mock_trainer = MagicMock()
                mock_trainer.initialize_model.return_value = True
                mock_trainer.train = AsyncMock(return_value={"final_loss": 0.5})
                mock_trainer.export_model.return_value = str(Path(tmpdir) / "model")
                mock_trainer_class.return_value = mock_trainer

                await trainer.auto_train(
                    str(metadata_path),
                    optimize_params=False,
                    max_runs=1,
                    progress_callback=progress_callback
                )

                assert len(callback_calls) > 0

    @patch("app.core.training.auto_trainer.Path")
    @patch("app.core.training.auto_trainer.HAS_UNIFIED_TRAINER", True)
    @pytest.mark.asyncio
    async def test_auto_train_model_initialization_failure(self, mock_path):
        """Test auto_train handles model initialization failure."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with patch("app.core.training.auto_trainer.UnifiedTrainer") as mock_trainer_class:
                mock_trainer = MagicMock()
                mock_trainer.initialize_model.return_value = False
                mock_trainer_class.return_value = mock_trainer

                result = await trainer.auto_train(
                    str(metadata_path),
                    optimize_params=False,
                    max_runs=1
                )

                assert result["successful_runs"] == 0

    @patch("app.core.training.auto_trainer.Path")
    @patch("app.core.training.auto_trainer.HAS_UNIFIED_TRAINER", True)
    @pytest.mark.asyncio
    async def test_auto_train_training_failure(self, mock_path):
        """Test auto_train handles training failure."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = AutoTrainer()

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with patch("app.core.training.auto_trainer.UnifiedTrainer") as mock_trainer_class:
                mock_trainer = MagicMock()
                mock_trainer.initialize_model.return_value = True
                mock_trainer.train = AsyncMock(side_effect=Exception("Training failed"))
                mock_trainer_class.return_value = mock_trainer

                result = await trainer.auto_train(
                    str(metadata_path),
                    optimize_params=False,
                    max_runs=1
                )

                assert result["successful_runs"] == 0
                assert len(result["training_history"]) == 1
                assert "error" in result["training_history"][0]


class TestCreateAutoTrainer:
    """Test create_auto_trainer factory function."""

    @patch("app.core.training.auto_trainer.Path")
    def test_create_auto_trainer_default(self, mock_path):
        """Test create_auto_trainer with default parameters."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = create_auto_trainer()
        assert isinstance(trainer, AutoTrainer)
        assert trainer.engine == "xtts"

    @patch("app.core.training.auto_trainer.Path")
    def test_create_auto_trainer_custom(self, mock_path):
        """Test create_auto_trainer with custom parameters."""
        mock_path.return_value.mkdir = MagicMock()
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = create_auto_trainer(
                engine="tortoise",
                device="cpu",
                gpu=False,
                output_dir=tmpdir
            )
            assert isinstance(trainer, AutoTrainer)
            assert trainer.engine == "tortoise"
            assert trainer.device == "cpu"
            assert trainer.gpu is False
            assert str(trainer.output_dir) == tmpdir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
