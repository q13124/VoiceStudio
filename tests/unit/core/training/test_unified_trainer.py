"""
Unit Tests for Unified Trainer
Tests unified training functionality comprehensively.
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

# Import the unified trainer module
try:
    from app.core.training import unified_trainer
    from app.core.training.unified_trainer import (
        UnifiedTrainer,
        create_unified_trainer,
    )
except ImportError as e:
    pytest.skip(f"Could not import unified_trainer: {e}", allow_module_level=True)


class TestUnifiedTrainerImports:
    """Test unified trainer module can be imported."""

    def test_unified_trainer_imports(self):
        """Test unified_trainer can be imported."""
        assert unified_trainer is not None, "Failed to import unified_trainer module"

    def test_unified_trainer_has_classes(self):
        """Test unified_trainer has expected classes."""
        classes = [
            name
            for name in dir(unified_trainer)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "unified_trainer should have classes"

    def test_unified_trainer_class_exists(self):
        """Test UnifiedTrainer class exists."""
        assert hasattr(
            unified_trainer, "UnifiedTrainer"
        ), "UnifiedTrainer class should exist"
        assert isinstance(
            unified_trainer.UnifiedTrainer, type
        ), "UnifiedTrainer should be a class"

    def test_create_unified_trainer_function_exists(self):
        """Test create_unified_trainer function exists."""
        assert hasattr(
            unified_trainer, "create_unified_trainer"
        ), "create_unified_trainer function should exist"
        assert callable(
            unified_trainer.create_unified_trainer
        ), "create_unified_trainer should be callable"


class TestUnifiedTrainerInitialization:
    """Test UnifiedTrainer initialization."""

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_init_default(self, mock_path):
        """Test initialization with default parameters."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
            trainer = UnifiedTrainer()
            assert trainer.engine == "xtts"
            assert trainer.device == "cpu"
            assert trainer.gpu is True
            assert trainer.trainer is None

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_init_custom_engine(self, mock_path):
        """Test initialization with custom engine."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
            trainer = UnifiedTrainer(engine="rvc")
            assert trainer.engine == "rvc"

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_init_custom_output_dir(self, mock_path):
        """Test initialization with custom output directory."""
        mock_path.return_value.mkdir = MagicMock()
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
                trainer = UnifiedTrainer(output_dir=tmpdir)
                assert str(trainer.output_dir) == tmpdir

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_init_cpu_device(self, mock_path):
        """Test initialization with CPU device."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
            trainer = UnifiedTrainer(device="cpu", gpu=False)
            assert trainer.device == "cpu"
            assert trainer.gpu is False

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    def test_init_with_xtts_trainer(self, mock_xtts_trainer, mock_path):
        """Test initialization with XTTS trainer available."""
        mock_path.return_value.mkdir = MagicMock()
        mock_xtts_trainer.return_value = MagicMock()
        trainer = UnifiedTrainer(engine="xtts")
        assert trainer.trainer is not None


class TestUnifiedTrainerPrepareDataset:
    """Test prepare_dataset method."""

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_prepare_dataset_without_trainer(self, mock_path):
        """Test prepare_dataset raises error when trainer not available."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
            trainer = UnifiedTrainer()
            with pytest.raises(RuntimeError, match="Trainer for engine"):
                trainer.prepare_dataset(["audio1.wav"])

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    def test_prepare_dataset_success(self, mock_xtts_trainer, mock_path):
        """Test successful dataset preparation."""
        mock_path.return_value.mkdir = MagicMock()
        mock_trainer = MagicMock()
        mock_trainer.prepare_dataset.return_value = "metadata.json"
        mock_xtts_trainer.return_value = mock_trainer

        trainer = UnifiedTrainer(engine="xtts")
        result = trainer.prepare_dataset(
            ["audio1.wav", "audio2.wav"], transcripts=["text1", "text2"]
        )

        assert result == "metadata.json"
        mock_trainer.prepare_dataset.assert_called_once()

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    def test_prepare_dataset_not_implemented(self, mock_xtts_trainer, mock_path):
        """Test prepare_dataset when method not implemented."""
        mock_path.return_value.mkdir = MagicMock()
        mock_trainer = MagicMock()
        del mock_trainer.prepare_dataset
        mock_xtts_trainer.return_value = mock_trainer

        trainer = UnifiedTrainer(engine="xtts")
        with pytest.raises(NotImplementedError):
            trainer.prepare_dataset(["audio1.wav"])


class TestUnifiedTrainerInitializeModel:
    """Test initialize_model method."""

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_initialize_model_without_trainer(self, mock_path):
        """Test initialize_model raises error when trainer not available."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
            trainer = UnifiedTrainer()
            with pytest.raises(RuntimeError, match="Trainer for engine"):
                trainer.initialize_model()

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    def test_initialize_model_success(self, mock_xtts_trainer, mock_path):
        """Test successful model initialization."""
        mock_path.return_value.mkdir = MagicMock()
        mock_trainer = MagicMock()
        mock_trainer.initialize_model.return_value = True
        mock_xtts_trainer.return_value = mock_trainer

        trainer = UnifiedTrainer(engine="xtts")
        result = trainer.initialize_model()

        assert result is True
        mock_trainer.initialize_model.assert_called_once()

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    def test_initialize_model_not_implemented(self, mock_xtts_trainer, mock_path):
        """Test initialize_model when method not implemented."""
        mock_path.return_value.mkdir = MagicMock()
        mock_trainer = MagicMock()
        del mock_trainer.initialize_model
        mock_xtts_trainer.return_value = mock_trainer

        trainer = UnifiedTrainer(engine="xtts")
        result = trainer.initialize_model()

        assert result is False


class TestUnifiedTrainerTrain:
    """Test train method."""

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @pytest.mark.asyncio
    async def test_train_without_trainer(self, mock_path):
        """Test train raises error when trainer not available."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
            trainer = UnifiedTrainer()
            with tempfile.TemporaryDirectory() as tmpdir:
                metadata_path = Path(tmpdir) / "metadata.json"
                metadata_path.write_text(json.dumps([]))

                with pytest.raises(RuntimeError, match="Trainer for engine"):
                    await trainer.train(str(metadata_path))

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    @pytest.mark.asyncio
    async def test_train_already_training(self, mock_xtts_trainer, mock_path):
        """Test train raises error when already training."""
        mock_path.return_value.mkdir = MagicMock()
        mock_trainer = MagicMock()
        mock_xtts_trainer.return_value = mock_trainer

        trainer = UnifiedTrainer(engine="xtts")
        trainer._is_training = True

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with pytest.raises(RuntimeError, match="Training already in progress"):
                await trainer.train(str(metadata_path))

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    @pytest.mark.asyncio
    async def test_train_success(self, mock_xtts_trainer, mock_path):
        """Test successful training."""
        mock_path.return_value.mkdir = MagicMock()
        mock_trainer = MagicMock()
        mock_trainer.train = AsyncMock(return_value={"final_loss": 0.5})
        mock_xtts_trainer.return_value = mock_trainer

        trainer = UnifiedTrainer(engine="xtts")

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            result = await trainer.train(
                str(metadata_path), epochs=10, batch_size=4, learning_rate=0.001
            )

            assert result["final_loss"] == 0.5
            assert trainer._is_training is False  # Should be reset after training

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    @pytest.mark.asyncio
    async def test_train_not_implemented(self, mock_xtts_trainer, mock_path):
        """Test train when method not implemented."""
        mock_path.return_value.mkdir = MagicMock()
        mock_trainer = MagicMock()
        del mock_trainer.train
        mock_xtts_trainer.return_value = mock_trainer

        trainer = UnifiedTrainer(engine="xtts")

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with pytest.raises(NotImplementedError):
                await trainer.train(str(metadata_path))


class TestUnifiedTrainerCancelTraining:
    """Test cancel_training method."""

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_cancel_training_not_training(self, mock_path):
        """Test cancel_training when not training."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
            trainer = UnifiedTrainer()
            result = trainer.cancel_training()
            assert result is False

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    def test_cancel_training_success(self, mock_xtts_trainer, mock_path):
        """Test successful training cancellation."""
        mock_path.return_value.mkdir = MagicMock()
        mock_trainer = MagicMock()
        mock_trainer.cancel_training.return_value = True
        mock_xtts_trainer.return_value = mock_trainer

        trainer = UnifiedTrainer(engine="xtts")
        trainer._is_training = True

        result = trainer.cancel_training()
        assert result is True
        assert trainer._training_cancelled is True
        mock_trainer.cancel_training.assert_called_once()


class TestUnifiedTrainerExportModel:
    """Test export_model method."""

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_export_model_without_trainer(self, mock_path):
        """Test export_model raises error when trainer not available."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
            trainer = UnifiedTrainer()
            with pytest.raises(RuntimeError, match="Trainer for engine"):
                trainer.export_model()

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    def test_export_model_success(self, mock_xtts_trainer, mock_path):
        """Test successful model export."""
        mock_path.return_value.mkdir = MagicMock()
        mock_trainer = MagicMock()
        mock_trainer.export_model.return_value = "exported_model_path"
        mock_xtts_trainer.return_value = mock_trainer

        trainer = UnifiedTrainer(engine="xtts")
        result = trainer.export_model(output_path="output", model_name="model")

        assert result == "exported_model_path"
        mock_trainer.export_model.assert_called_once_with("output", "model")

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    def test_export_model_not_implemented(self, mock_xtts_trainer, mock_path):
        """Test export_model when method not implemented."""
        mock_path.return_value.mkdir = MagicMock()
        mock_trainer = MagicMock()
        del mock_trainer.export_model
        mock_xtts_trainer.return_value = mock_trainer

        trainer = UnifiedTrainer(engine="xtts")
        with pytest.raises(NotImplementedError):
            trainer.export_model()


class TestUnifiedTrainerStatus:
    """Test get_training_status and get_supported_engines methods."""

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_get_training_status(self, mock_path):
        """Test get_training_status."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
            trainer = UnifiedTrainer(engine="xtts")
            status = trainer.get_training_status()

            assert status["engine"] == "xtts"
            assert status["is_training"] is False
            assert status["is_cancelled"] is False
            assert status["trainer_available"] is False

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    @patch("app.core.training.unified_trainer.XTTSTrainer")
    def test_get_training_status_with_trainer_status(self, mock_xtts_trainer, mock_path):
        """Test get_training_status with trainer status."""
        mock_path.return_value.mkdir = MagicMock()
        mock_trainer = MagicMock()
        mock_trainer.get_training_status.return_value = {"epoch": 5, "loss": 0.5}
        mock_xtts_trainer.return_value = mock_trainer

        trainer = UnifiedTrainer(engine="xtts")
        status = trainer.get_training_status()

        assert status["trainer_available"] is True
        assert status["epoch"] == 5
        assert status["loss"] == 0.5

    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", True)
    def test_get_supported_engines(self):
        """Test get_supported_engines."""
        trainer = UnifiedTrainer()
        engines = trainer.get_supported_engines()
        assert "xtts" in engines

    @patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False)
    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_get_supported_engines_no_xtts(self, mock_path):
        """Test get_supported_engines when XTTS not available."""
        mock_path.return_value.mkdir = MagicMock()
        trainer = UnifiedTrainer()
        engines = trainer.get_supported_engines()
        assert "xtts" not in engines
        assert len(engines) == 0


class TestCreateUnifiedTrainer:
    """Test create_unified_trainer factory function."""

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_create_unified_trainer_default(self, mock_path):
        """Test create_unified_trainer with default parameters."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
            trainer = create_unified_trainer()
            assert isinstance(trainer, UnifiedTrainer)
            assert trainer.engine == "xtts"

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_create_unified_trainer_custom(self, mock_path):
        """Test create_unified_trainer with custom parameters."""
        mock_path.return_value.mkdir = MagicMock()
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
                trainer = create_unified_trainer(
                    engine="rvc", device="cpu", gpu=False, output_dir=tmpdir
                )
                assert isinstance(trainer, UnifiedTrainer)
                assert trainer.engine == "rvc"
                assert trainer.device == "cpu"
                assert trainer.gpu is False

    @patch("app.core.training.unified_trainer.HAS_TORCH", False)
    @patch("app.core.training.unified_trainer.Path")
    def test_unified_trainer_create_trainer_static(self, mock_path):
        """Test UnifiedTrainer.create_trainer static method."""
        mock_path.return_value.mkdir = MagicMock()
        with patch("app.core.training.unified_trainer.HAS_XTTS_TRAINER", False):
            trainer = UnifiedTrainer.create_trainer(engine="xtts")
            assert isinstance(trainer, UnifiedTrainer)
            assert trainer.engine == "xtts"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
