"""
Unit Tests for Parameter Optimizer
Tests hyperparameter optimization functionality comprehensively.
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

# Import the parameter optimizer module
try:
    from app.core.training import parameter_optimizer
    from app.core.training.parameter_optimizer import (
        ParameterOptimizer,
        create_parameter_optimizer,
    )
except ImportError as e:
    pytest.skip(f"Could not import parameter_optimizer: {e}", allow_module_level=True)


class TestParameterOptimizerImports:
    """Test parameter optimizer module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            parameter_optimizer is not None
        ), "Failed to import parameter_optimizer module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(parameter_optimizer)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"

    def test_parameter_optimizer_class_exists(self):
        """Test ParameterOptimizer class exists."""
        assert hasattr(
            parameter_optimizer, "ParameterOptimizer"
        ), "ParameterOptimizer class should exist"
        assert isinstance(
            parameter_optimizer.ParameterOptimizer, type
        ), "ParameterOptimizer should be a class"

    def test_create_parameter_optimizer_function_exists(self):
        """Test create_parameter_optimizer function exists."""
        assert hasattr(
            parameter_optimizer, "create_parameter_optimizer"
        ), "create_parameter_optimizer function should exist"
        assert callable(
            parameter_optimizer.create_parameter_optimizer
        ), "create_parameter_optimizer should be callable"


class TestParameterOptimizerInitialization:
    """Test ParameterOptimizer initialization."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        optimizer = ParameterOptimizer()
        assert optimizer.optimization_strategy == "grid_search"
        assert optimizer.max_iterations == 10
        assert optimizer.optimization_history == []

    def test_init_custom_strategy(self):
        """Test initialization with custom strategy."""
        optimizer = ParameterOptimizer(optimization_strategy="random_search")
        assert optimizer.optimization_strategy == "random_search"

    def test_init_custom_max_iterations(self):
        """Test initialization with custom max_iterations."""
        optimizer = ParameterOptimizer(max_iterations=20)
        assert optimizer.max_iterations == 20

    def test_init_invalid_strategy(self):
        """Test initialization with invalid strategy defaults to grid_search."""
        optimizer = ParameterOptimizer(optimization_strategy="invalid_strategy")
        assert optimizer.optimization_strategy == "grid_search"

    def test_init_bayesian_strategy(self):
        """Test initialization with bayesian strategy."""
        optimizer = ParameterOptimizer(optimization_strategy="bayesian")
        assert optimizer.optimization_strategy == "bayesian"


class TestParameterOptimizerGridSearch:
    """Test grid search parameter generation."""

    def test_generate_grid_search_simple(self):
        """Test generating grid search parameters."""
        optimizer = ParameterOptimizer(optimization_strategy="grid_search")
        parameter_space = {
            "epochs": [50, 100],
            "batch_size": [2, 4],
        }

        param_sets = optimizer._generate_grid_search(parameter_space)
        assert len(param_sets) == 4  # 2 * 2 = 4 combinations
        assert {"epochs": 50, "batch_size": 2} in param_sets
        assert {"epochs": 50, "batch_size": 4} in param_sets
        assert {"epochs": 100, "batch_size": 2} in param_sets
        assert {"epochs": 100, "batch_size": 4} in param_sets

    def test_generate_grid_search_three_params(self):
        """Test generating grid search with three parameters."""
        optimizer = ParameterOptimizer(optimization_strategy="grid_search")
        parameter_space = {
            "epochs": [50, 100],
            "batch_size": [2, 4],
            "learning_rate": [0.0001, 0.001],
        }

        param_sets = optimizer._generate_grid_search(parameter_space)
        assert len(param_sets) == 8  # 2 * 2 * 2 = 8 combinations

    def test_generate_grid_search_single_value(self):
        """Test generating grid search with single value per parameter."""
        optimizer = ParameterOptimizer(optimization_strategy="grid_search")
        parameter_space = {
            "epochs": [100],
            "batch_size": [4],
        }

        param_sets = optimizer._generate_grid_search(parameter_space)
        assert len(param_sets) == 1
        assert param_sets[0] == {"epochs": 100, "batch_size": 4}


class TestParameterOptimizerRandomSearch:
    """Test random search parameter generation."""

    def test_generate_random_search(self):
        """Test generating random search parameters."""
        optimizer = ParameterOptimizer(optimization_strategy="random_search")
        parameter_space = {
            "epochs": [50, 100, 150],
            "batch_size": [2, 4, 8],
        }

        param_sets = optimizer._generate_random_search(parameter_space, num_samples=5)
        assert len(param_sets) == 5

        for param_set in param_sets:
            assert "epochs" in param_set
            assert "batch_size" in param_set
            assert param_set["epochs"] in [50, 100, 150]
            assert param_set["batch_size"] in [2, 4, 8]

    def test_generate_random_search_single_sample(self):
        """Test generating single random sample."""
        optimizer = ParameterOptimizer(optimization_strategy="random_search")
        parameter_space = {
            "epochs": [100],
            "batch_size": [4],
        }

        param_sets = optimizer._generate_random_search(parameter_space, num_samples=1)
        assert len(param_sets) == 1
        assert param_sets[0]["epochs"] == 100
        assert param_sets[0]["batch_size"] == 4


class TestParameterOptimizerBayesianSearch:
    """Test Bayesian search parameter generation."""

    def test_generate_bayesian_search(self):
        """Test generating Bayesian search parameters."""
        optimizer = ParameterOptimizer(optimization_strategy="bayesian")
        parameter_space = {
            "epochs": [50, 100, 150],
            "batch_size": [2, 4, 8],
        }

        param_sets = optimizer._generate_bayesian_search(parameter_space, num_samples=3)
        assert len(param_sets) == 3

        for param_set in param_sets:
            assert "epochs" in param_set
            assert "batch_size" in param_set


class TestParameterOptimizerRecommendedSpace:
    """Test get_recommended_space method."""

    def test_get_recommended_space_small_dataset(self):
        """Test recommended space for small dataset."""
        optimizer = ParameterOptimizer()
        space = optimizer.get_recommended_space(dataset_size=5, quality_target="standard")

        assert "epochs" in space
        assert "batch_size" in space
        assert "learning_rate" in space
        assert 200 in space["epochs"]  # More epochs for small datasets
        assert 2 in space["batch_size"]

    def test_get_recommended_space_large_dataset(self):
        """Test recommended space for large dataset."""
        optimizer = ParameterOptimizer()
        space = optimizer.get_recommended_space(dataset_size=100, quality_target="standard")

        assert 50 in space["epochs"]  # Fewer epochs for large datasets
        assert 16 in space["batch_size"]  # Larger batch size

    def test_get_recommended_space_fast_quality(self):
        """Test recommended space for fast quality target."""
        optimizer = ParameterOptimizer()
        space = optimizer.get_recommended_space(dataset_size=50, quality_target="fast")

        assert 0.002 in space["learning_rate"]  # Higher LR for faster training

    def test_get_recommended_space_high_quality(self):
        """Test recommended space for high quality target."""
        optimizer = ParameterOptimizer()
        space = optimizer.get_recommended_space(dataset_size=50, quality_target="high")

        assert 0.00005 in space["learning_rate"]  # Lower LR for better quality

    def test_get_recommended_space_ultra_quality(self):
        """Test recommended space for ultra quality target."""
        optimizer = ParameterOptimizer()
        space = optimizer.get_recommended_space(dataset_size=50, quality_target="ultra")

        assert 0.00001 in space["learning_rate"]  # Very low LR for maximum quality


class TestParameterOptimizerOptimizeParameters:
    """Test optimize_parameters method."""

    @patch("app.core.training.parameter_optimizer.HAS_UNIFIED_TRAINER", False)
    def test_optimize_parameters_without_unified_trainer(self):
        """Test optimize_parameters raises error when unified trainer not available."""
        optimizer = ParameterOptimizer()
        parameter_space = {"epochs": [50], "batch_size": [4]}

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with pytest.raises(RuntimeError, match="Unified trainer not available"):
                optimizer.optimize_parameters(
                    str(metadata_path), parameter_space=parameter_space
                )

    @patch("app.core.training.parameter_optimizer.HAS_UNIFIED_TRAINER", True)
    def test_optimize_parameters_grid_search(self):
        """Test optimize_parameters with grid search."""
        optimizer = ParameterOptimizer(
            optimization_strategy="grid_search", max_iterations=2
        )
        parameter_space = {"epochs": [50, 100], "batch_size": [4]}

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with patch("app.core.training.parameter_optimizer.UnifiedTrainer") as mock_trainer_class:
                mock_trainer = MagicMock()
                mock_trainer.initialize_model.return_value = True
                mock_trainer.train = AsyncMock(return_value={"final_loss": 0.5})
                mock_trainer_class.return_value = mock_trainer

                result = optimizer.optimize_parameters(
                    str(metadata_path), parameter_space=parameter_space
                )

                assert "best_params" in result
                assert "best_quality" in result
                assert "optimization_history" in result
                assert result["strategy"] == "grid_search"

    @patch("app.core.training.parameter_optimizer.HAS_UNIFIED_TRAINER", True)
    def test_optimize_parameters_random_search(self):
        """Test optimize_parameters with random search."""
        optimizer = ParameterOptimizer(
            optimization_strategy="random_search", max_iterations=3
        )
        parameter_space = {"epochs": [50, 100], "batch_size": [4, 8]}

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with patch("app.core.training.parameter_optimizer.UnifiedTrainer") as mock_trainer_class:
                mock_trainer = MagicMock()
                mock_trainer.initialize_model.return_value = True
                mock_trainer.train = AsyncMock(return_value={"final_loss": 0.5})
                mock_trainer_class.return_value = mock_trainer

                result = optimizer.optimize_parameters(
                    str(metadata_path), parameter_space=parameter_space
                )

                assert result["strategy"] == "random_search"
                assert result["total_iterations"] == 3

    @patch("app.core.training.parameter_optimizer.HAS_UNIFIED_TRAINER", True)
    def test_optimize_parameters_with_progress_callback(self):
        """Test optimize_parameters with progress callback."""
        optimizer = ParameterOptimizer(max_iterations=2)
        parameter_space = {"epochs": [50], "batch_size": [4]}

        callback_calls = []

        def progress_callback(update):
            callback_calls.append(update)

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with patch("app.core.training.parameter_optimizer.UnifiedTrainer") as mock_trainer_class:
                mock_trainer = MagicMock()
                mock_trainer.initialize_model.return_value = True
                mock_trainer.train = AsyncMock(return_value={"final_loss": 0.5})
                mock_trainer_class.return_value = mock_trainer

                optimizer.optimize_parameters(
                    str(metadata_path),
                    parameter_space=parameter_space,
                    progress_callback=progress_callback,
                )

                assert len(callback_calls) > 0

    @patch("app.core.training.parameter_optimizer.HAS_UNIFIED_TRAINER", True)
    def test_optimize_parameters_model_initialization_failure(self):
        """Test optimize_parameters handles model initialization failure."""
        optimizer = ParameterOptimizer(max_iterations=2)
        parameter_space = {"epochs": [50], "batch_size": [4]}

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps([]))

            with patch("app.core.training.parameter_optimizer.UnifiedTrainer") as mock_trainer_class:
                mock_trainer = MagicMock()
                mock_trainer.initialize_model.return_value = False
                mock_trainer_class.return_value = mock_trainer

                result = optimizer.optimize_parameters(
                    str(metadata_path), parameter_space=parameter_space
                )

                assert result["best_params"] is None


class TestParameterOptimizerSummary:
    """Test get_optimization_summary method."""

    def test_get_optimization_summary_empty(self):
        """Test summary with no optimization history."""
        optimizer = ParameterOptimizer()
        summary = optimizer.get_optimization_summary()
        assert "message" in summary

    def test_get_optimization_summary_with_history(self):
        """Test summary with optimization history."""
        optimizer = ParameterOptimizer()
        optimizer.optimization_history = [
            {
                "iteration": 1,
                "params": {"epochs": 50},
                "quality_score": 0.8,
                "loss": 0.2,
            },
            {
                "iteration": 2,
                "params": {"epochs": 100},
                "quality_score": 0.9,
                "loss": 0.1,
            },
        ]

        summary = optimizer.get_optimization_summary()
        assert summary["total_iterations"] == 2
        assert summary["successful_iterations"] == 2
        assert summary["best_quality"] == 0.9
        assert summary["best_loss"] == 0.1
        assert summary["strategy"] == "grid_search"

    def test_get_optimization_summary_with_failures(self):
        """Test summary with failed iterations."""
        optimizer = ParameterOptimizer()
        optimizer.optimization_history = [
            {
                "iteration": 1,
                "params": {"epochs": 50},
                "quality_score": 0.8,
                "loss": 0.2,
            },
            {"iteration": 2, "params": {"epochs": 100}, "error": "Training failed"},
        ]

        summary = optimizer.get_optimization_summary()
        assert summary["total_iterations"] == 2
        assert summary["successful_iterations"] == 1
        assert summary["failed_iterations"] == 1


class TestCreateParameterOptimizer:
    """Test create_parameter_optimizer factory function."""

    def test_create_parameter_optimizer_default(self):
        """Test create_parameter_optimizer with default parameters."""
        optimizer = create_parameter_optimizer()
        assert isinstance(optimizer, ParameterOptimizer)
        assert optimizer.optimization_strategy == "grid_search"
        assert optimizer.max_iterations == 10

    def test_create_parameter_optimizer_custom(self):
        """Test create_parameter_optimizer with custom parameters."""
        optimizer = create_parameter_optimizer(
            optimization_strategy="random_search", max_iterations=20
        )
        assert isinstance(optimizer, ParameterOptimizer)
        assert optimizer.optimization_strategy == "random_search"
        assert optimizer.max_iterations == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
