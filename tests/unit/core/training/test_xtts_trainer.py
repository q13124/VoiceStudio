"""
Unit Tests for XTTS Trainer
Tests XTTS training functionality comprehensively.
"""

import json
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
for module_name in ["torch", "torch.cuda", "TTS", "TTS.api", "TTS.trainer", "TTS.tts.configs.xtts_config", "TTS.tts.models.xtts", "TTS.utils.audio", "TTS.utils.manage", "TTS.datasets", "TTS.utils.generic_utils", "audiomentations", "optuna", "ray", "ray.tune", "hyperopt"]:
    if module_name not in sys.modules:
        mock_module = MagicMock()
        if module_name == "torch":
            mock_module.__version__ = "2.0.0"  # Required for TTS version check
        elif module_name == "torch.cuda":
            mock_module.is_available = lambda: False
        elif module_name == "TTS":
            mock_module.api = MagicMock()
            mock_module.trainer = MagicMock()
            mock_module.tts = MagicMock()
            mock_module.utils = MagicMock()
        elif module_name == "TTS.api":
            mock_module.TTS = MagicMock()
        elif module_name == "TTS.trainer":
            mock_module.Trainer = MagicMock()
            mock_module.TrainerArgs = MagicMock()
        elif module_name == "TTS.tts.configs.xtts_config":
            mock_module.XttsConfig = MagicMock()
        elif module_name == "TTS.tts.models.xtts":
            mock_module.Xtts = MagicMock()
        elif module_name == "TTS.utils.audio":
            mock_module.AudioProcessor = MagicMock()
        elif module_name == "TTS.utils.manage":
            mock_module.ModelManager = MagicMock()
        elif module_name == "TTS.datasets":
            mock_module.load_tts_samples = MagicMock()
        elif module_name == "TTS.utils.generic_utils":
            mock_module.setup_model = MagicMock()
        elif module_name == "audiomentations":
            mock_module.Compose = MagicMock()
            mock_module.AddGaussianNoise = MagicMock()
            mock_module.TimeStretch = MagicMock()
            mock_module.PitchShift = MagicMock()
            mock_module.Shift = MagicMock()
            mock_module.Normalize = MagicMock()
            mock_module.Gain = MagicMock()
        elif module_name == "optuna":
            mock_module.create_study = MagicMock()
        elif module_name == "ray":
            mock_module.tune = MagicMock()
        elif module_name == "ray.tune":
            mock_module.CLIReporter = MagicMock()
        elif module_name == "hyperopt":
            mock_module.fmin = MagicMock()
            mock_module.tpe = MagicMock()
            mock_module.hp = MagicMock()
        sys.modules[module_name] = mock_module

# Ensure torch has __version__ if already in sys.modules
if "torch" in sys.modules:
    if not hasattr(sys.modules["torch"], "__version__") or isinstance(getattr(sys.modules["torch"], "__version__", None), MagicMock):
        sys.modules["torch"].__version__ = "2.0.0"

# Import the XTTS trainer module
try:
    from app.core.training import xtts_trainer
    from app.core.training.xtts_trainer import XTTSTrainer
except ImportError as e:
    pytest.skip(f"Could not import xtts_trainer: {e}", allow_module_level=True)


class TestXTTSTrainerImports:
    """Test XTTS trainer module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert xtts_trainer is not None, "Failed to import xtts_trainer module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(xtts_trainer)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"

    def test_xtts_trainer_class_exists(self):
        """Test XTTSTrainer class exists."""
        assert hasattr(xtts_trainer, "XTTSTrainer"), "XTTSTrainer class should exist"
        assert isinstance(xtts_trainer.XTTSTrainer, type), "XTTSTrainer should be a class"


class TestXTTSTrainerInitialization:
    """Test XTTSTrainer initialization."""

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_init_default(self, mock_torch):
        """Test initialization with default parameters."""
        mock_torch.cuda.is_available.return_value = False
        with patch("app.core.training.xtts_trainer.Path") as mock_path:
            mock_path.return_value.mkdir = MagicMock()
            trainer = XTTSTrainer()
            assert trainer.base_model == "tts_models/multilingual/multi-dataset/xtts_v2"
            assert trainer.device == "cpu"
            assert trainer.model is None
            assert trainer.config is None
            assert trainer._is_training is False
            assert trainer._training_cancelled is False

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_init_custom_output_dir(self, mock_torch):
        """Test initialization with custom output directory."""
        mock_torch.cuda.is_available.return_value = False
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = XTTSTrainer(output_dir=tmpdir)
            assert str(trainer.output_dir) == tmpdir

    @patch("app.core.training.xtts_trainer.HAS_TTS", False)
    def test_init_without_tts(self):
        """Test initialization fails when TTS is not available."""
        with pytest.raises(ImportError, match="Coqui TTS not installed"):
            XTTSTrainer()


class TestXTTSTrainerAugmentationPipeline:
    """Test augmentation pipeline creation."""

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    @patch("app.core.training.xtts_trainer.HAS_AUDIOMENTATIONS", True)
    def test_create_augmentation_pipeline_with_audiomentations(self, mock_torch):
        """Test creating augmentation pipeline when audiomentations is available."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        # Mock all audiomentations components including Normalize and Gain
        with patch("app.core.training.xtts_trainer.Compose") as mock_compose, \
             patch("app.core.training.xtts_trainer.AddGaussianNoise") as mock_noise, \
             patch("app.core.training.xtts_trainer.TimeStretch") as mock_stretch, \
             patch("app.core.training.xtts_trainer.PitchShift") as mock_pitch, \
             patch("app.core.training.xtts_trainer.Shift") as mock_shift, \
             patch("app.core.training.xtts_trainer.Normalize") as mock_normalize, \
             patch("app.core.training.xtts_trainer.Gain") as mock_gain:
            # Set up all mocks to return MagicMock instances
            mock_noise.return_value = MagicMock()
            mock_stretch.return_value = MagicMock()
            mock_pitch.return_value = MagicMock()
            mock_shift.return_value = MagicMock()
            mock_normalize.return_value = MagicMock()
            mock_gain.return_value = MagicMock()
            mock_compose.return_value = MagicMock()
            
            pipeline = trainer.create_augmentation_pipeline()
            assert pipeline is not None
            mock_compose.assert_called_once()

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    @patch("app.core.training.xtts_trainer.HAS_AUDIOMENTATIONS", False)
    def test_create_augmentation_pipeline_without_audiomentations(self, mock_torch):
        """Test creating augmentation pipeline when audiomentations is not available."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()
        pipeline = trainer.create_augmentation_pipeline()
        assert pipeline is None

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    @patch("app.core.training.xtts_trainer.HAS_AUDIOMENTATIONS", True)
    def test_create_augmentation_pipeline_custom_options(self, mock_torch):
        """Test creating augmentation pipeline with custom options."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        # Mock all audiomentations components including Normalize and Gain
        with patch("app.core.training.xtts_trainer.Compose") as mock_compose, \
             patch("app.core.training.xtts_trainer.AddGaussianNoise") as mock_noise, \
             patch("app.core.training.xtts_trainer.TimeStretch") as mock_stretch, \
             patch("app.core.training.xtts_trainer.PitchShift") as mock_pitch, \
             patch("app.core.training.xtts_trainer.Shift") as mock_shift, \
             patch("app.core.training.xtts_trainer.Normalize") as mock_normalize, \
             patch("app.core.training.xtts_trainer.Gain") as mock_gain:
            mock_noise.return_value = MagicMock()
            mock_stretch.return_value = MagicMock()
            mock_pitch.return_value = MagicMock()
            mock_shift.return_value = MagicMock()
            mock_normalize.return_value = MagicMock()
            mock_gain.return_value = MagicMock()
            mock_compose.return_value = MagicMock()
            
            pipeline = trainer.create_augmentation_pipeline(
                sample_rate=44100,
                enable_noise=False,
                enable_time_stretch=False,
                enable_pitch_shift=False,
                enable_shift=False
            )
            assert pipeline is not None


class TestXTTSTrainerDatasetPreparation:
    """Test dataset preparation."""

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_prepare_dataset_no_files(self, mock_torch):
        """Test prepare_dataset raises error with no files."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        with pytest.raises(ValueError, match="No audio files provided"):
            trainer.prepare_dataset([])

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_prepare_dataset_invalid_files(self, mock_torch):
        """Test prepare_dataset raises error with invalid files."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        with pytest.raises(ValueError, match="No valid audio files found"):
            trainer.prepare_dataset(["nonexistent_file.wav"])

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_prepare_dataset_valid_files(self, mock_torch):
        """Test prepare_dataset with valid files."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test audio files
            audio_file1 = Path(tmpdir) / "test1.wav"
            audio_file2 = Path(tmpdir) / "test2.wav"
            audio_file1.touch()
            audio_file2.touch()

            metadata_path = trainer.prepare_dataset(
                [str(audio_file1), str(audio_file2)],
                transcripts=["Test transcript 1", "Test transcript 2"]
            )

            assert Path(metadata_path).exists()
            with open(metadata_path) as f:
                metadata = json.load(f)
                assert len(metadata) == 2
                assert metadata[0]["audio_file"] == str(audio_file1.absolute())
                assert metadata[0]["text"] == "Test transcript 1"
                assert metadata[1]["text"] == "Test transcript 2"

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_prepare_dataset_without_transcripts(self, mock_torch):
        """Test prepare_dataset without transcripts."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        with tempfile.TemporaryDirectory() as tmpdir:
            audio_file = Path(tmpdir) / "test_audio.wav"
            audio_file.touch()

            metadata_path = trainer.prepare_dataset([str(audio_file)])

            assert Path(metadata_path).exists()
            with open(metadata_path) as f:
                metadata = json.load(f)
                assert len(metadata) == 1
                assert metadata[0]["text"] != ""  # Should extract from filename


class TestXTTSTrainerModelInitialization:
    """Test model initialization."""

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_initialize_model_success(self, mock_torch):
        """Test successful model initialization."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        with patch("app.core.training.xtts_trainer.TTS") as mock_tts, \
             patch("app.core.training.xtts_trainer.XttsConfig") as mock_config, \
             patch("app.core.training.xtts_trainer.Xtts") as mock_xtts, \
             patch("app.core.training.xtts_trainer.Path") as mock_path:

            mock_tts_instance = MagicMock()
            mock_tts_instance.model_path = "/path/to/model"
            mock_tts_instance.to = MagicMock()
            mock_tts.return_value = mock_tts_instance

            mock_config_instance = MagicMock()
            mock_config.return_value = mock_config_instance

            mock_xtts_instance = MagicMock()
            mock_xtts_instance.load_checkpoint = MagicMock()
            mock_xtts_instance.to = MagicMock()
            mock_xtts.init_from_config.return_value = mock_xtts_instance

            mock_path.return_value.exists.return_value = False

            result = trainer.initialize_model()
            assert result is True
            assert trainer.model is not None
            assert trainer.config is not None

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_initialize_model_failure(self, mock_torch):
        """Test model initialization failure."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        with patch("app.core.training.xtts_trainer.TTS") as mock_tts:
            mock_tts.side_effect = Exception("Model loading failed")

            result = trainer.initialize_model()
            assert result is False


class TestXTTSTrainerTraining:
    """Test training functionality."""

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    @pytest.mark.asyncio
    async def test_train_without_model(self, mock_torch):
        """Test train raises error when model not initialized."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with pytest.raises(RuntimeError, match="Model not initialized"):
                await trainer.train(str(metadata_path))

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    @pytest.mark.asyncio
    async def test_train_already_training(self, mock_torch):
        """Test train raises error when already training."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()
        trainer.model = MagicMock()
        trainer._is_training = True

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with pytest.raises(RuntimeError, match="Training already in progress"):
                await trainer.train(str(metadata_path))

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_cancel_training(self, mock_torch):
        """Test cancel training."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()
        trainer._is_training = True

        trainer.cancel_training()
        assert trainer._training_cancelled is True

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_is_training(self, mock_torch):
        """Test is_training method."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        assert trainer.is_training() is False
        trainer._is_training = True
        assert trainer.is_training() is True


class TestXTTSTrainerExport:
    """Test model export functionality."""

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_export_model_success(self, mock_torch):
        """Test successful model export."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = Path(tmpdir) / "checkpoint"
            checkpoint_dir.mkdir()
            (checkpoint_dir / "model.pth").touch()
            (checkpoint_dir / "config.json").touch()

            output_path = trainer.export_model(str(checkpoint_dir))
            assert Path(output_path).exists()

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_export_model_checkpoint_not_found(self, mock_torch):
        """Test export raises error when checkpoint not found."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        with pytest.raises(FileNotFoundError, match="Checkpoint not found"):
            trainer.export_model("nonexistent_checkpoint")


class TestXTTSTrainerHyperparameterOptimization:
    """Test hyperparameter optimization."""

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    @patch("app.core.training.xtts_trainer.HAS_OPTUNA", True)
    def test_optimize_hyperparameters_optuna(self, mock_torch):
        """Test hyperparameter optimization with optuna."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        with patch("app.core.training.xtts_trainer.optuna") as mock_optuna:
            mock_study = MagicMock()
            mock_study.best_params = {"learning_rate": 0.001, "batch_size": 8}
            mock_study.best_value = 0.95
            mock_optuna.create_study.return_value = mock_study

            result = trainer.optimize_hyperparameters(method="optuna", n_trials=10)
            assert "best_params" in result
            assert "best_value" in result

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    @patch("app.core.training.xtts_trainer.HAS_OPTUNA", False)
    def test_optimize_hyperparameters_optuna_not_available(self, mock_torch):
        """Test hyperparameter optimization when optuna not available."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        # Source raises ValueError when method not available
        with pytest.raises(ValueError, match="not available"):
            trainer.optimize_hyperparameters(method="optuna", n_trials=10)

    @patch("app.core.training.xtts_trainer.HAS_TTS", True)
    @patch("app.core.training.xtts_trainer.torch")
    def test_optimize_hyperparameters_invalid_method(self, mock_torch):
        """Test hyperparameter optimization with invalid method."""
        mock_torch.cuda.is_available.return_value = False
        trainer = XTTSTrainer()

        # Source raises ValueError for invalid/unavailable methods
        with pytest.raises(ValueError, match="not available"):
            trainer.optimize_hyperparameters(method="invalid_method", n_trials=10)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
