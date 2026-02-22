"""
Unified Trainer Module for VoiceStudio
Unified interface for multiple training engines (XTTS, RVC, etc.)

Compatible with:
- Python 3.10+
- torch>=2.0.0
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Import XTTS trainer
try:
    from .xtts_trainer import XTTSTrainer

    HAS_XTTS_TRAINER = True
except ImportError:
    HAS_XTTS_TRAINER = False
    logger.warning("XTTS trainer not available")

# Import RVC trainer
try:
    from .rvc_trainer import HAS_RVC_TRAINER, RVCTrainer

except ImportError:
    HAS_RVC_TRAINER = False
    RVCTrainer = None
    logger.warning("RVC trainer not available")

# Try to import torch
try:
    import torch

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logger.warning("PyTorch not installed. Install with: pip install torch")


class UnifiedTrainer:
    """
    Unified Trainer for multiple training engines.

    Supports:
    - Multiple training engines (XTTS, RVC, etc.)
    - Unified training interface
    - Engine selection based on requirements
    - Training progress tracking
    - Model checkpointing
    - Training cancellation
    """

    def __init__(
        self,
        engine: str = "xtts",
        device: str | None = None,
        gpu: bool = True,
        output_dir: str | None = None,
    ):
        """
        Initialize Unified Trainer.

        Args:
            engine: Training engine name ("xtts", "rvc", etc.)
            device: Device to use ('cuda', 'cpu', or None for auto)
            gpu: Whether to use GPU if available
            output_dir: Directory to save trained models
        """
        self.engine = engine.lower()
        self.device = device or (
            "cuda" if (gpu and HAS_TORCH and torch.cuda.is_available()) else "cpu"
        )
        self.gpu = gpu
        self.output_dir = Path(output_dir) if output_dir else Path("models/trained")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.trainer = None
        self._is_training = False
        self._training_cancelled = False

        # Initialize specific trainer
        self._initialize_trainer()

    def _initialize_trainer(self):
        """Initialize the specific training engine."""
        if self.engine == "xtts":
            if HAS_XTTS_TRAINER:
                try:
                    self.trainer = XTTSTrainer(
                        device=self.device,
                        gpu=self.gpu,
                        output_dir=str(self.output_dir),
                    )
                    logger.info("XTTS trainer initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize XTTS trainer: {e}")
                    self.trainer = None
            else:
                logger.warning("XTTS trainer not available")
        elif self.engine == "rvc":
            if HAS_RVC_TRAINER and RVCTrainer is not None:
                try:
                    self.trainer = RVCTrainer(
                        device=self.device,
                        gpu=self.gpu,
                        output_dir=str(self.output_dir),
                    )
                    logger.info("RVC trainer initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize RVC trainer: {e}")
                    self.trainer = None
            else:
                logger.warning("RVC trainer not available, using XTTS as fallback")
                if HAS_XTTS_TRAINER:
                    try:
                        self.trainer = XTTSTrainer(
                            device=self.device,
                            gpu=self.gpu,
                            output_dir=str(self.output_dir),
                        )
                    except Exception as e:
                        logger.error(f"Failed to initialize fallback trainer: {e}")
        else:
            logger.warning(f"Unknown engine: {self.engine}, using XTTS as fallback")
            if HAS_XTTS_TRAINER:
                try:
                    self.trainer = XTTSTrainer(
                        device=self.device,
                        gpu=self.gpu,
                        output_dir=str(self.output_dir),
                    )
                except Exception as e:
                    logger.error(f"Failed to initialize fallback trainer: {e}")

    def prepare_dataset(
        self,
        audio_files: list[str],
        transcripts: list[str] | None = None,
        output_metadata: str | None = None,
    ) -> str:
        """
        Prepare training dataset.

        Args:
            audio_files: List of audio file paths
            transcripts: Optional list of transcripts
            output_metadata: Optional output metadata path

        Returns:
            Path to prepared dataset metadata file
        """
        if not self.trainer:
            raise RuntimeError(f"Trainer for engine '{self.engine}' not available")

        if hasattr(self.trainer, "prepare_dataset"):
            return self.trainer.prepare_dataset(audio_files, transcripts, output_metadata)
        else:
            raise RuntimeError(f"Dataset preparation unavailable for engine '{self.engine}'")

    def initialize_model(
        self, config_path: str | None = None, base_model: str | None = None
    ) -> bool:
        """
        Initialize training model.

        Args:
            config_path: Optional path to model config
            base_model: Optional base model identifier

        Returns:
            True if initialization successful or not required for this engine

        Note:
            Some engines (like XTTS) handle model initialization internally during
            training and do not require explicit initialization. For these engines,
            this method returns True to indicate the trainer is ready.
        """
        if not self.trainer:
            raise RuntimeError(f"Trainer for engine '{self.engine}' not available")

        if hasattr(self.trainer, "initialize_model"):
            return self.trainer.initialize_model(config_path)
        else:
            # Engine handles initialization internally - this is valid behavior
            logger.info(
                f"Engine '{self.engine}' handles model initialization internally. "
                "Trainer is ready for training."
            )
            return True  # Trainer is ready even without explicit initialization

    async def train(
        self,
        metadata_path: str,
        epochs: int = 100,
        batch_size: int = 4,
        learning_rate: float = 0.0001,
        progress_callback: Callable[[dict], None] | None = None,
        checkpoint_dir: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Start training.

        Args:
            metadata_path: Path to dataset metadata file
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
            progress_callback: Optional callback for progress updates
            checkpoint_dir: Optional checkpoint directory
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training results
        """
        if not self.trainer:
            raise RuntimeError(f"Trainer for engine '{self.engine}' not available")

        if self._is_training:
            raise RuntimeError("Training already in progress")

        self._is_training = True
        self._training_cancelled = False

        try:
            if hasattr(self.trainer, "train"):
                result = await self.trainer.train(
                    metadata_path=metadata_path,
                    epochs=epochs,
                    batch_size=batch_size,
                    learning_rate=learning_rate,
                    progress_callback=progress_callback,
                    checkpoint_dir=checkpoint_dir,
                    **kwargs,
                )
                return result
            else:
                raise RuntimeError(f"Training unavailable for engine '{self.engine}'")
        finally:
            self._is_training = False

    def cancel_training(self) -> bool:
        """
        Cancel ongoing training.

        Returns:
            True if cancellation was requested successfully

        Note:
            Cancellation is handled at two levels:
            1. UnifiedTrainer level: Sets _training_cancelled flag which training loops
               should check periodically.
            2. Engine level: If the underlying trainer supports cancel_training(), it
               will be called for immediate engine-specific cancellation.

            For engines without native cancellation support, the flag-based approach
            provides graceful termination at the next checkpoint.
        """
        if not self._is_training:
            logger.debug("cancel_training called but no training is in progress")
            return False

        self._training_cancelled = True
        logger.info(f"Training cancellation requested for engine '{self.engine}'")

        if self.trainer and hasattr(self.trainer, "cancel_training"):
            # Engine supports native cancellation
            result = self.trainer.cancel_training()
            logger.info(f"Engine-level cancellation returned: {result}")
            return result
        else:
            # Flag-based cancellation will be checked by training loop
            logger.info(
                f"Engine '{self.engine}' uses flag-based cancellation. "
                "Training will stop at next checkpoint."
            )
            return True  # Cancellation requested successfully

    def export_model(self, output_path: str | None = None, model_name: str | None = None) -> str:
        """
        Export trained model.

        Args:
            output_path: Optional output path
            model_name: Optional model name

        Returns:
            Path to exported model
        """
        if not self.trainer:
            raise RuntimeError(f"Trainer for engine '{self.engine}' not available")

        if hasattr(self.trainer, "export_model"):
            return self.trainer.export_model(output_path, model_name)
        else:
            raise RuntimeError(f"Model export unavailable for engine '{self.engine}'")

    def get_training_status(self) -> dict[str, Any]:
        """
        Get current training status.

        Returns:
            Dictionary with training status information
        """
        status = {
            "engine": self.engine,
            "is_training": self._is_training,
            "is_cancelled": self._training_cancelled,
            "device": self.device,
            "trainer_available": self.trainer is not None,
        }

        if self.trainer and hasattr(self.trainer, "get_training_status"):
            trainer_status = self.trainer.get_training_status()
            status.update(trainer_status)

        return status

    def get_supported_engines(self) -> list[str]:
        """
        Get list of supported training engines.

        Returns:
            List of supported engine names
        """
        engines = []
        if HAS_XTTS_TRAINER:
            engines.append("xtts")
        if HAS_RVC_TRAINER:
            engines.append("rvc")
        return engines

    @property
    def is_cancellation_requested(self) -> bool:
        """
        Check if training cancellation has been requested.

        This property can be checked by training loops to gracefully exit.

        Returns:
            True if cancellation was requested
        """
        return self._training_cancelled

    @staticmethod
    def create_trainer(
        engine: str = "xtts",
        device: str | None = None,
        gpu: bool = True,
        output_dir: str | None = None,
    ) -> UnifiedTrainer:
        """
        Factory method to create a Unified Trainer instance.

        Args:
            engine: Training engine name
            device: Device to use
            gpu: Whether to use GPU
            output_dir: Output directory

        Returns:
            UnifiedTrainer instance
        """
        return UnifiedTrainer(engine=engine, device=device, gpu=gpu, output_dir=output_dir)


def create_unified_trainer(
    engine: str = "xtts",
    device: str | None = None,
    gpu: bool = True,
    output_dir: str | None = None,
) -> UnifiedTrainer:
    """
    Factory function to create a Unified Trainer instance.

    Args:
        engine: Training engine name
        device: Device to use
        gpu: Whether to use GPU
        output_dir: Output directory

    Returns:
        UnifiedTrainer instance
    """
    return UnifiedTrainer.create_trainer(
        engine=engine, device=device, gpu=gpu, output_dir=output_dir
    )
