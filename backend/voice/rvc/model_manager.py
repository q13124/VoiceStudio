"""
RVC Model Manager.

Task 4.1.2: Model discovery, downloading, and management.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RVCModelInfo:
    """Information about an RVC model."""

    id: str
    name: str
    version: str

    # Paths
    model_path: str
    index_path: str | None = None

    # Metadata
    description: str = ""
    author: str = ""
    category: str = "general"

    # Quality info
    training_epochs: int = 0
    sample_rate: int = 40000

    # Tags
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "model_path": self.model_path,
            "index_path": self.index_path,
            "description": self.description,
            "author": self.author,
            "category": self.category,
            "training_epochs": self.training_epochs,
            "sample_rate": self.sample_rate,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RVCModelInfo:
        return cls(
            id=data["id"],
            name=data["name"],
            version=data.get("version", "unknown"),
            model_path=data["model_path"],
            index_path=data.get("index_path"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            category=data.get("category", "general"),
            training_epochs=data.get("training_epochs", 0),
            sample_rate=data.get("sample_rate", 40000),
            tags=data.get("tags", []),
        )


class RVCModelManager:
    """
    Manages RVC models.

    Features:
    - Model discovery from directories
    - Model metadata management
    - Download from HuggingFace
    - Model organization
    """

    MODELS_DIR = Path("models/rvc")
    REGISTRY_FILE = "registry.json"

    def __init__(self, models_dir: Path | None = None):
        """
        Initialize model manager.

        Args:
            models_dir: Directory for models
        """
        self._models_dir = models_dir or self.MODELS_DIR
        self._models_dir.mkdir(parents=True, exist_ok=True)

        self._registry: dict[str, RVCModelInfo] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        """Load model registry from disk."""
        registry_path = self._models_dir / self.REGISTRY_FILE

        if registry_path.exists():
            try:
                with open(registry_path) as f:
                    data = json.load(f)

                for model_data in data.get("models", []):
                    info = RVCModelInfo.from_dict(model_data)
                    self._registry[info.id] = info

                logger.info(f"Loaded {len(self._registry)} models from registry")

            except Exception as e:
                logger.error(f"Failed to load registry: {e}")

    def _save_registry(self) -> None:
        """Save model registry to disk."""
        registry_path = self._models_dir / self.REGISTRY_FILE

        data = {"models": [info.to_dict() for info in self._registry.values()]}

        with open(registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def discover_models(self) -> list[RVCModelInfo]:
        """
        Discover models in the models directory.

        Returns:
            List of discovered models
        """
        discovered = []

        for model_path in self._models_dir.glob("**/*.pth"):
            # Check if already registered
            model_id = model_path.stem

            if model_id in self._registry:
                discovered.append(self._registry[model_id])
                continue

            # Look for accompanying index
            index_path = model_path.with_suffix(".index")
            if not index_path.exists():
                # Try .index file with same name
                index_path = model_path.parent / f"{model_id}.index"

            # Create info
            info = RVCModelInfo(
                id=model_id,
                name=model_id.replace("_", " ").replace("-", " ").title(),
                version="unknown",
                model_path=str(model_path),
                index_path=str(index_path) if index_path.exists() else None,
            )

            # Register
            self._registry[model_id] = info
            discovered.append(info)

            logger.info(f"Discovered model: {model_id}")

        self._save_registry()
        return discovered

    def get_model(self, model_id: str) -> RVCModelInfo | None:
        """Get model info by ID."""
        return self._registry.get(model_id)

    def list_models(
        self,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> list[RVCModelInfo]:
        """
        List available models.

        Args:
            category: Filter by category
            tags: Filter by tags

        Returns:
            List of matching models
        """
        models = list(self._registry.values())

        if category:
            models = [m for m in models if m.category == category]

        if tags:
            models = [m for m in models if any(t in m.tags for t in tags)]

        return models

    def register_model(self, info: RVCModelInfo) -> None:
        """
        Register a model.

        Args:
            info: Model information
        """
        self._registry[info.id] = info
        self._save_registry()
        logger.info(f"Registered model: {info.id}")

    def unregister_model(self, model_id: str) -> bool:
        """
        Unregister a model.

        Args:
            model_id: Model ID

        Returns:
            True if removed
        """
        if model_id in self._registry:
            del self._registry[model_id]
            self._save_registry()
            return True
        return False

    def delete_model(self, model_id: str, delete_files: bool = False) -> bool:
        """
        Delete a model.

        Args:
            model_id: Model ID
            delete_files: Whether to delete files

        Returns:
            True if deleted
        """
        info = self._registry.get(model_id)

        if not info:
            return False

        if delete_files:
            # Delete model file
            model_path = Path(info.model_path)
            if model_path.exists():
                model_path.unlink()

            # Delete index file
            if info.index_path:
                index_path = Path(info.index_path)
                if index_path.exists():
                    index_path.unlink()

        return self.unregister_model(model_id)

    def update_model_info(
        self,
        model_id: str,
        **kwargs,
    ) -> RVCModelInfo | None:
        """
        Update model information.

        Args:
            model_id: Model ID
            **kwargs: Fields to update

        Returns:
            Updated info or None
        """
        info = self._registry.get(model_id)

        if not info:
            return None

        for key, value in kwargs.items():
            if hasattr(info, key):
                setattr(info, key, value)

        self._save_registry()
        return info

    async def download_model(
        self,
        url: str,
        model_id: str,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> RVCModelInfo | None:
        """
        Download a model from URL.

        Task 4.1.9: Implement actual model downloading.

        Args:
            url: Model URL (HuggingFace, direct, etc.)
            model_id: ID for the model
            progress_callback: Progress callback (bytes_downloaded, total_bytes)

        Returns:
            Model info or None
        """
        logger.info(f"Downloading model from: {url}")

        try:
            import os
            from urllib.parse import unquote, urlparse

            import aiohttp

            # Determine filename from URL
            parsed = urlparse(url)
            filename = unquote(os.path.basename(parsed.path))
            if not filename.endswith((".pth", ".onnx", ".pt")):
                filename = f"{model_id}.pth"

            output_path = self._models_dir / filename

            # Handle HuggingFace URLs
            if "huggingface.co" in url:
                url = self._convert_hf_url(url)

            # Download with progress
            async with aiohttp.ClientSession() as session, session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Download failed: HTTP {response.status}")
                    return None

                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(output_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback:
                            progress_callback(downloaded, total_size)

            logger.info(f"Downloaded model to: {output_path}")

            # Register the model
            return await self.register_model(
                model_id=model_id,
                path=str(output_path),
                name=model_id.replace("_", " ").title(),
                description=f"Downloaded from {parsed.netloc}",
            )

        except ImportError:
            logger.error("aiohttp required for model download: pip install aiohttp")
            return None
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    def _convert_hf_url(self, url: str) -> str:
        """Convert HuggingFace page URL to direct download URL."""
        # Convert: huggingface.co/user/repo/blob/main/file.pth
        # To: huggingface.co/user/repo/resolve/main/file.pth
        if "/blob/" in url:
            url = url.replace("/blob/", "/resolve/")
        return url

    def get_stats(self) -> dict[str, Any]:
        """Get manager statistics."""
        return {
            "total_models": len(self._registry),
            "models_dir": str(self._models_dir),
            "categories": list({m.category for m in self._registry.values()}),
        }
