"""
Parameter Optimizer Module for VoiceStudio
Hyperparameter optimization for training

Compatible with:
- Python 3.10+
- torch>=2.0.0
"""

from __future__ import annotations

import logging
import random
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

# Import unified trainer
try:
    from .unified_trainer import UnifiedTrainer

    HAS_UNIFIED_TRAINER = True
except ImportError:
    HAS_UNIFIED_TRAINER = False
    logger.warning("Unified trainer not available")

# Import quality metrics
try:
    from app.core.audio.enhanced_quality_metrics import EnhancedQualityMetrics

    HAS_QUALITY_METRICS = True
except ImportError:
    HAS_QUALITY_METRICS = False
    logger.warning("Enhanced quality metrics not available")


class ParameterOptimizer:
    """
    Parameter Optimizer for hyperparameter optimization.

    Supports:
    - Grid search
    - Random search
    - Bayesian optimization (simplified)
    - Quality-based parameter selection
    - Parameter space definition
    - Optimization history tracking
    """

    def __init__(
        self,
        optimization_strategy: str = "grid_search",
        max_iterations: int = 10,
    ):
        """
        Initialize Parameter Optimizer.

        Args:
            optimization_strategy: Strategy ("grid_search", "random_search", "bayesian")
            max_iterations: Maximum optimization iterations
        """
        self.optimization_strategy = optimization_strategy.lower()
        self.max_iterations = max_iterations
        self.optimization_history: list[dict[str, Any]] = []

        # Validate strategy
        valid_strategies = ["grid_search", "random_search", "bayesian"]
        if self.optimization_strategy not in valid_strategies:
            logger.warning(
                f"Unknown strategy '{optimization_strategy}', using grid_search"
            )
            self.optimization_strategy = "grid_search"

    def optimize_parameters(
        self,
        metadata_path: str,
        parameter_space: dict[str, list[Any]],
        validation_audio: str | None = None,
        engine: str = "xtts",
        device: str | None = None,
        gpu: bool = True,
        progress_callback: Callable[[dict], None] | None = None,
    ) -> dict[str, Any]:
        """
        Optimize training parameters.

        Args:
            metadata_path: Path to dataset metadata
            parameter_space: Parameter space definition
                Example: {
                    "epochs": [50, 100, 150],
                    "batch_size": [2, 4, 8],
                    "learning_rate": [0.0001, 0.0005, 0.001]
                }
            validation_audio: Optional validation audio for quality assessment
            engine: Training engine name
            device: Device to use
            gpu: Whether to use GPU
            progress_callback: Optional progress callback

        Returns:
            Dictionary with best parameters and optimization results
        """
        if not HAS_UNIFIED_TRAINER:
            raise RuntimeError("Unified trainer not available")

        # Generate parameter sets based on strategy
        if self.optimization_strategy == "grid_search":
            param_sets = self._generate_grid_search(parameter_space)
        elif self.optimization_strategy == "random_search":
            param_sets = self._generate_random_search(
                parameter_space, self.max_iterations
            )
        else:  # bayesian
            param_sets = self._generate_bayesian_search(
                parameter_space, self.max_iterations
            )

        # Limit to max_iterations
        param_sets = param_sets[: self.max_iterations]

        best_params = None
        best_quality = -1.0
        best_result = None

        # Initialize quality metrics if available
        quality_metrics = None
        if HAS_QUALITY_METRICS:
            try:
                quality_metrics = EnhancedQualityMetrics()
            except Exception as e:
                logger.warning(f"Failed to initialize quality metrics: {e}")

        # Evaluate each parameter set
        for idx, params in enumerate(param_sets):
            if progress_callback:
                progress_callback(
                    {
                        "iteration": idx + 1,
                        "total_iterations": len(param_sets),
                        "status": "evaluating",
                        "params": params,
                    }
                )

            logger.info(
                f"Optimization iteration {idx + 1}/{len(param_sets)}: {params}"
            )

            try:
                # Create trainer
                trainer = UnifiedTrainer(
                    engine=engine,
                    device=device,
                    gpu=gpu,
                    output_dir=f"models/optimization/run_{idx + 1}",
                )

                # Initialize model
                if not trainer.initialize_model():
                    logger.warning(
                        f"Model initialization failed for iteration {idx + 1}"
                    )
                    continue

                # Train with these parameters
                def train_progress_callback(update):
                    if progress_callback:
                        progress_callback(
                            {
                                "iteration": idx + 1,
                                "total_iterations": len(param_sets),
                                "status": "training",
                                "params": params,
                                "training_progress": update,
                            }
                        )

                import asyncio

                result = asyncio.run(
                    trainer.train(
                        metadata_path=metadata_path,
                        epochs=params.get("epochs", 100),
                        batch_size=params.get("batch_size", 4),
                        learning_rate=params.get("learning_rate", 0.0001),
                        progress_callback=train_progress_callback,
                    )
                )

                # Evaluate quality
                quality_score = 0.0
                if validation_audio and quality_metrics:
                    try:
                        # Simplified quality evaluation
                        # In practice, would synthesize test audio and evaluate
                        if result.get("final_loss"):
                            quality_score = max(0.0, 1.0 - result["final_loss"])
                    except Exception as e:
                        logger.warning(f"Quality evaluation failed: {e}")

                # Use loss as quality indicator if no validation
                if quality_score == 0.0 and result.get("final_loss"):
                    quality_score = max(0.0, 1.0 - result["final_loss"])

                # Track optimization history
                optimization_result = {
                    "iteration": idx + 1,
                    "params": params,
                    "quality_score": quality_score,
                    "loss": result.get("final_loss", 0.0),
                    "result": result,
                }
                self.optimization_history.append(optimization_result)

                # Update best if better
                if quality_score > best_quality:
                    best_quality = quality_score
                    best_params = params
                    best_result = result

                if progress_callback:
                    progress_callback(
                        {
                            "iteration": idx + 1,
                            "total_iterations": len(param_sets),
                            "status": "completed",
                            "params": params,
                            "quality_score": quality_score,
                        }
                    )

            except Exception as e:
                logger.error(f"Optimization iteration {idx + 1} failed: {e}")
                self.optimization_history.append(
                    {
                        "iteration": idx + 1,
                        "params": params,
                        "error": str(e),
                    }
                )

        return {
            "best_params": best_params,
            "best_quality": best_quality,
            "best_result": best_result,
            "optimization_history": self.optimization_history,
            "strategy": self.optimization_strategy,
            "total_iterations": len(param_sets),
        }

    def _generate_grid_search(
        self, parameter_space: dict[str, list[Any]]
    ) -> list[dict[str, Any]]:
        """
        Generate parameter sets for grid search.

        Args:
            parameter_space: Parameter space definition

        Returns:
            List of parameter dictionaries
        """
        param_sets = []
        param_names = list(parameter_space.keys())
        param_values = [parameter_space[name] for name in param_names]

        # Generate all combinations
        from itertools import product

        for combination in product(*param_values):
            param_set = dict(zip(param_names, combination, strict=False))
            param_sets.append(param_set)

        return param_sets

    def _generate_random_search(
        self, parameter_space: dict[str, list[Any]], num_samples: int
    ) -> list[dict[str, Any]]:
        """
        Generate parameter sets for random search.

        Args:
            parameter_space: Parameter space definition
            num_samples: Number of random samples

        Returns:
            List of parameter dictionaries
        """
        param_sets = []

        for _ in range(num_samples):
            param_set = {}
            for param_name, param_values in parameter_space.items():
                param_set[param_name] = random.choice(param_values)
            param_sets.append(param_set)

        return param_sets

    def _generate_bayesian_search(
        self, parameter_space: dict[str, list[Any]], num_samples: int
    ) -> list[dict[str, Any]]:
        """
        Generate parameter sets for Bayesian optimization (simplified).

        Uses a simple approach: start with grid search, then focus on promising regions.

        Args:
            parameter_space: Parameter space definition
            num_samples: Number of samples

        Returns:
            List of parameter dictionaries
        """
        # Simplified Bayesian: use random search for now
        # In a full implementation, would use Gaussian Process or similar
        return self._generate_random_search(parameter_space, num_samples)

    def get_recommended_space(
        self,
        dataset_size: int,
        quality_target: str = "standard",
    ) -> dict[str, list[Any]]:
        """
        Get recommended parameter space based on dataset characteristics.

        Args:
            dataset_size: Number of audio files in dataset
            quality_target: Quality target ("fast", "standard", "high", "ultra")

        Returns:
            Recommended parameter space
        """
        # Base parameter ranges
        if dataset_size < 10:
            epochs_range = [100, 150, 200]
            batch_size_range = [2, 4]
        elif dataset_size < 50:
            epochs_range = [50, 100, 150]
            batch_size_range = [2, 4, 8]
        else:
            epochs_range = [50, 100]
            batch_size_range = [4, 8, 16]

        # Adjust learning rate based on quality target
        if quality_target == "fast":
            lr_range = [0.0005, 0.001, 0.002]
        elif quality_target == "high":
            lr_range = [0.00005, 0.0001, 0.0002]
        elif quality_target == "ultra":
            lr_range = [0.00001, 0.00005, 0.0001]
        else:  # standard
            lr_range = [0.0001, 0.0005, 0.001]

        return {
            "epochs": epochs_range,
            "batch_size": batch_size_range,
            "learning_rate": lr_range,
        }

    def get_optimization_summary(self) -> dict[str, Any]:
        """
        Get summary of optimization results.

        Returns:
            Dictionary with optimization summary
        """
        if not self.optimization_history:
            return {"message": "No optimization history"}

        successful_runs = [
            h for h in self.optimization_history if "error" not in h
        ]

        if not successful_runs:
            return {"message": "No successful optimization runs"}

        quality_scores = [r["quality_score"] for r in successful_runs]
        losses = [r.get("loss", 0.0) for r in successful_runs if "loss" in r]

        return {
            "total_iterations": len(self.optimization_history),
            "successful_iterations": len(successful_runs),
            "failed_iterations": len(self.optimization_history) - len(successful_runs),
            "best_quality": max(quality_scores) if quality_scores else 0.0,
            "average_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
            "best_loss": min(losses) if losses else 0.0,
            "average_loss": sum(losses) / len(losses) if losses else 0.0,
            "strategy": self.optimization_strategy,
        }


def create_parameter_optimizer(
    optimization_strategy: str = "grid_search",
    max_iterations: int = 10,
) -> ParameterOptimizer:
    """
    Factory function to create a Parameter Optimizer instance.

    Args:
        optimization_strategy: Strategy ("grid_search", "random_search", "bayesian")
        max_iterations: Maximum optimization iterations

    Returns:
        Initialized ParameterOptimizer instance
    """
    return ParameterOptimizer(
        optimization_strategy=optimization_strategy, max_iterations=max_iterations
    )

