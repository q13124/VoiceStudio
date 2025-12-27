"""
Base Engine Protocol for VoiceStudio
All engines must implement this protocol/interface
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)


class EngineProtocol(ABC):
    """
    Base protocol that all VoiceStudio engines must implement.
    
    This ensures consistent interface across all engines (XTTS, Whisper, RVC, etc.)
    """
    
    def __init__(self, device: Optional[str] = None, gpu: bool = True):
        """
        Initialize engine with device selection.
        
        Args:
            device: Device to use ('cuda', 'cpu', or None for auto)
            gpu: Whether to use GPU if available
        """
        self.device = device or ("cuda" if gpu else "cpu")
        self._initialized = False
        logger.info(f"{self.__class__.__name__} initialized (device: {self.device})")
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the engine model.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """
        Clean up resources and free memory.
        """
        pass
    
    def is_initialized(self) -> bool:
        """Check if engine is initialized."""
        return self._initialized
    
    def get_device(self) -> str:
        """Get current device."""
        return self.device
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get engine information.
        
        Returns:
            Dictionary with engine metadata
        """
        return {
            "name": self.__class__.__name__,
            "device": self.device,
            "initialized": self._initialized
        }

