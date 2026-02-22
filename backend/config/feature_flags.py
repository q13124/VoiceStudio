"""
Feature flags for experimental and gated routes.

Arch Review Task 1.4: Local-first, no remote service.
Reads from config/feature_flags.json. Default: all experimental disabled.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_FLAGS = {
    "experimental.voice_morph": False,
    "experimental.style_transfer": False,
    "experimental.spatial_audio": False,
    "experimental.embedding_explorer": False,
    "experimental.ensemble": False,
    "experimental.instant_cloning": False,
    "experimental.realtime": False,
    "experimental.multi_voice": False,
    "experimental.multilingual": False,
    "experimental.rvc": False,
    "experimental.dubbing": False,
    "experimental.translation": False,
    "experimental.lip_sync": False,
    "experimental.advanced_audio": False,
    "experimental.face_swap": False,
    "experimental.image_gen": False,
    "experimental.video_gen": False,
    "experimental.pdf": False,
}

_flags: dict[str, bool] | None = None


def _config_path() -> Path:
    """Resolve feature_flags.json path. Prefer config/ at repo root."""
    # Repo root: backend/config/ -> backend -> repo root
    repo_root = Path(__file__).resolve().parent.parent.parent
    p = repo_root / "config" / "feature_flags.json"
    if p.exists():
        return p
    return Path(__file__).resolve().parent / "feature_flags.json"


def _load_flags() -> dict[str, bool]:
    """Load flags from JSON, merging with defaults."""
    global _flags
    if _flags is not None:
        return _flags
    _flags = dict(_DEFAULT_FLAGS)
    path = _config_path()
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                overrides = json.load(f)
            if isinstance(overrides, dict):
                for k, v in overrides.items():
                    if isinstance(v, bool):
                        _flags[k] = v
        except Exception as e:
            logger.warning("Could not load feature_flags.json: %s", e)
    return _flags


def is_enabled(flag: str) -> bool:
    """Return True if the feature flag is enabled."""
    return _load_flags().get(flag, False)


def get_all() -> dict[str, bool]:
    """Return all flags (for diagnostics)."""
    return dict(_load_flags())
