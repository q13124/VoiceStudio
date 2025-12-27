"""
Engine Configuration Manager
Manages default engines, overrides, and installed engine tracking
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import os

# Import unified config loader (supports JSON, YAML, TOML)
try:
    from app.core.config.config_loader import ConfigLoader, load_config
    HAS_UNIFIED_CONFIG = True
except ImportError:
    HAS_UNIFIED_CONFIG = False

logger = logging.getLogger(__name__)


class EngineConfig:
    """
    Manages engine configuration: defaults, overrides, and installed engines.
    """
    
    def __init__(self, config_path: str = "engines/config.json"):
        """
        Initialize engine configuration.
        
        Args:
            config_path: Path to config.json file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {
            "defaults": {},
            "overrides": {},
            "installed": []
        }
        self.load()
    
    def load(self):
        """Load configuration from file (supports JSON, YAML, TOML)."""
        if self.config_path.exists():
            try:
                # Use unified config loader if available (supports YAML/TOML)
                if HAS_UNIFIED_CONFIG:
                    try:
                        self.config = load_config(self.config_path, validate=False)
                        logger.info(f"Loaded engine config from {self.config_path} (unified loader)")
                    except Exception as e:
                        logger.warning(f"Unified loader failed, falling back to JSON: {e}")
                        # Fallback to JSON
                        with open(self.config_path, 'r', encoding='utf-8') as f:
                            self.config = json.load(f)
                        logger.info(f"Loaded engine config from {self.config_path} (JSON fallback)")
                else:
                    # Fallback to JSON only
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        self.config = json.load(f)
                    logger.info(f"Loaded engine config from {self.config_path} (JSON)")
            except Exception as e:
                logger.error(f"Failed to load engine config: {e}")
                self.config = {
                    "defaults": {},
                    "overrides": {},
                    "installed": []
                }
        else:
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            self.save()  # Create default config file
    
    def save(self):
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved engine config to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save engine config: {e}")
    
    def get_default_engine(self, task_type: str) -> Optional[str]:
        """
        Get default engine for a task type.
        
        Args:
            task_type: Task type (e.g., "tts", "image_gen", "video_gen")
        
        Returns:
            Engine ID or None
        """
        # Check overrides first
        overrides = self.config.get("overrides", {})
        if task_type in overrides:
            return overrides[task_type]
        
        # Check defaults
        defaults = self.config.get("defaults", {})
        return defaults.get(task_type)
    
    def set_default_engine(self, task_type: str, engine_id: str):
        """
        Set default engine for a task type.
        
        Args:
            task_type: Task type
            engine_id: Engine ID
        """
        if "defaults" not in self.config:
            self.config["defaults"] = {}
        
        self.config["defaults"][task_type] = engine_id
        self.save()
        logger.info(f"Set default engine for {task_type}: {engine_id}")
    
    def set_override(self, task_type: str, engine_id: Optional[str]):
        """
        Set override engine for a task type.
        
        Args:
            task_type: Task type
            engine_id: Engine ID or None to clear override
        """
        if "overrides" not in self.config:
            self.config["overrides"] = {}
        
        if engine_id is None:
            self.config["overrides"].pop(task_type, None)
        else:
            self.config["overrides"][task_type] = engine_id
        
        self.save()
        logger.info(f"Set override for {task_type}: {engine_id}")
    
    def clear_override(self, task_type: str):
        """Clear override for a task type."""
        self.set_override(task_type, None)
    
    def get_installed_engines(self) -> List[str]:
        """
        Get list of installed engine IDs.
        
        Returns:
            List of engine IDs
        """
        return self.config.get("installed", [])
    
    def add_installed_engine(self, engine_id: str):
        """
        Add engine to installed list.
        
        Args:
            engine_id: Engine ID
        """
        if "installed" not in self.config:
            self.config["installed"] = []
        
        if engine_id not in self.config["installed"]:
            self.config["installed"].append(engine_id)
            self.save()
            logger.info(f"Added installed engine: {engine_id}")
    
    def remove_installed_engine(self, engine_id: str):
        """
        Remove engine from installed list.
        
        Args:
            engine_id: Engine ID
        """
        if "installed" in self.config:
            if engine_id in self.config["installed"]:
                self.config["installed"].remove(engine_id)
                self.save()
                logger.info(f"Removed installed engine: {engine_id}")
    
    def is_installed(self, engine_id: str) -> bool:
        """
        Check if engine is installed.
        
        Args:
            engine_id: Engine ID
        
        Returns:
            True if installed, False otherwise
        """
        return engine_id in self.get_installed_engines()
    
    def get_config(self) -> Dict[str, Any]:
        """Get full configuration dictionary."""
        return self.config.copy()
    
    def update_config(self, config: Dict[str, Any]):
        """
        Update configuration from dictionary.
        
        Args:
            config: Configuration dictionary
        """
        self.config.update(config)
        self.save()


# Global config instance
_config_instance: Optional[EngineConfig] = None


def get_engine_config(config_path: str = "engines/config.json") -> EngineConfig:
    """
    Get global engine configuration instance.
    
    Args:
        config_path: Path to config file
    
    Returns:
        EngineConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = EngineConfig(config_path)
    return _config_instance

