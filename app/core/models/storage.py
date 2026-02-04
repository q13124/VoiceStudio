"""
Model Storage Management

Manages model storage under %PROGRAMDATA%/VoiceStudio/models/<engine>/
Provides model fetching, updating, and checksum verification.
"""

import os
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

# ProgramData path for Windows
PROGRAMDATA = os.getenv("PROGRAMDATA", os.path.expanduser("~"))
MODELS_BASE_DIR = Path(PROGRAMDATA) / "VoiceStudio" / "models"


@dataclass
class ModelInfo:
    """Information about a stored model."""
    engine: str
    model_name: str
    model_path: str
    checksum: str
    size: int
    version: Optional[str] = None
    downloaded_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ModelInfo":
        """Create from dictionary."""
        return cls(**data)


class ModelStorage:
    """Manages model storage and retrieval."""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize model storage.
        
        Args:
            base_dir: Base directory for models (defaults to %PROGRAMDATA%/VoiceStudio/models)
        """
        self.base_dir = base_dir or MODELS_BASE_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._registry_file = self.base_dir / "model_registry.json"
        self._registry: Dict[str, ModelInfo] = {}
        self._load_registry()

    def _load_registry(self):
        """Load model registry from disk."""
        if self._registry_file.exists():
            try:
                with open(self._registry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._registry = {
                        key: ModelInfo.from_dict(value)
                        for key, value in data.items()
                    }
                logger.info(f"Loaded {len(self._registry)} models from registry")
            except Exception as e:
                logger.error(f"Failed to load model registry: {e}")
                self._registry = {}
        else:
            self._registry = {}

    def _save_registry(self):
        """Save model registry to disk atomically (tmp + replace)."""
        tmp_path = None
        try:
            data = {
                key: info.to_dict()
                for key, info in self._registry.items()
            }
            tmp_path = Path(str(self._registry_file) + ".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, self._registry_file)
            logger.debug("Saved model registry")
        except Exception as e:
            logger.error(f"Failed to save model registry: {e}")
            if tmp_path and tmp_path.exists():
                try:
                    tmp_path.unlink()
                # Best effort - failure is acceptable here
                except Exception:
                    pass

    def get_engine_dir(self, engine: str) -> Path:
        """Get the storage directory for an engine."""
        engine_dir = self.base_dir / engine
        engine_dir.mkdir(parents=True, exist_ok=True)
        return engine_dir

    def calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA256 checksum as hex string
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def register_model(
        self,
        engine: str,
        model_name: str,
        model_path: str,
        version: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> ModelInfo:
        """
        Register a model in the storage system.
        
        Args:
            engine: Engine name (e.g., "xtts_v2")
            model_name: Name of the model
            model_path: Path to the model file/directory
            version: Model version (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            ModelInfo object
        """
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"Model path does not exist: {model_path}")

        # Calculate checksum
        if path.is_file():
            checksum = self.calculate_checksum(path)
            size = path.stat().st_size
        else:
            # For directories, calculate checksum of all files
            checksum = self._calculate_directory_checksum(path)
            size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())

        # Create model info
        now = datetime.utcnow().isoformat()
        model_key = f"{engine}:{model_name}"
        
        model_info = ModelInfo(
            engine=engine,
            model_name=model_name,
            model_path=str(model_path),
            checksum=checksum,
            size=size,
            version=version,
            downloaded_at=now,
            updated_at=now,
            metadata=metadata or {}
        )

        # Register
        self._registry[model_key] = model_info
        self._save_registry()

        logger.info(f"Registered model: {model_key}")
        return model_info

    def _calculate_directory_checksum(self, dir_path: Path) -> str:
        """Calculate checksum for a directory (all files)."""
        sha256 = hashlib.sha256()
        for file_path in sorted(dir_path.rglob("*")):
            if file_path.is_file():
                sha256.update(str(file_path.relative_to(dir_path)).encode())
                with open(file_path, "rb") as f:
                    sha256.update(f.read())
        return sha256.hexdigest()

    def get_model(self, engine: str, model_name: str) -> Optional[ModelInfo]:
        """Get model information."""
        model_key = f"{engine}:{model_name}"
        return self._registry.get(model_key)

    def list_models(self, engine: Optional[str] = None) -> List[ModelInfo]:
        """List all registered models, optionally filtered by engine."""
        models = list(self._registry.values())
        if engine:
            models = [m for m in models if m.engine == engine]
        return models

    def verify_model(self, engine: str, model_name: str) -> Tuple[bool, Optional[str]]:
        """
        Verify a model's checksum.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        model_info = self.get_model(engine, model_name)
        if not model_info:
            return False, "Model not found in registry"

        path = Path(model_info.model_path)
        if not path.exists():
            return False, "Model file/directory does not exist"

        try:
            if path.is_file():
                current_checksum = self.calculate_checksum(path)
            else:
                current_checksum = self._calculate_directory_checksum(path)

            if current_checksum != model_info.checksum:
                return False, f"Checksum mismatch: expected {model_info.checksum[:16]}..., got {current_checksum[:16]}..."

            return True, None
        except Exception as e:
            return False, f"Verification error: {str(e)}"

    def update_model_checksum(self, engine: str, model_name: str) -> Optional[ModelInfo]:
        """Update model checksum (e.g., after model update)."""
        model_info = self.get_model(engine, model_name)
        if not model_info:
            return None

        path = Path(model_info.model_path)
        if not path.exists():
            return None

        # Recalculate checksum
        if path.is_file():
            checksum = self.calculate_checksum(path)
            size = path.stat().st_size
        else:
            checksum = self._calculate_directory_checksum(path)
            size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())

        # Update
        model_info.checksum = checksum
        model_info.size = size
        model_info.updated_at = datetime.utcnow().isoformat()
        
        self._registry[f"{engine}:{model_name}"] = model_info
        self._save_registry()

        logger.info(f"Updated checksum for {engine}:{model_name}")
        return model_info

    def delete_model(self, engine: str, model_name: str) -> bool:
        """Delete a model from registry (does not delete files)."""
        model_key = f"{engine}:{model_name}"
        if model_key in self._registry:
            del self._registry[model_key]
            self._save_registry()
            logger.info(f"Deleted model from registry: {model_key}")
            return True
        return False

    def get_storage_stats(self) -> Dict:
        """Get storage statistics."""
        total_size = sum(m.size for m in self._registry.values())
        engine_counts = {}
        for model in self._registry.values():
            engine_counts[model.engine] = engine_counts.get(model.engine, 0) + 1

        return {
            "total_models": len(self._registry),
            "total_size": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "total_size_gb": total_size / (1024 * 1024 * 1024),
            "engines": engine_counts,
            "base_dir": str(self.base_dir)
        }

