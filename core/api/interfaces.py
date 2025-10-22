#!/usr/bin/env python3
"""
VoiceStudio Core Interfaces
Defines contracts for voice cloning components
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path

@dataclass
class VoiceProfile:
    """Voice profile data structure"""
    embedding: np.ndarray
    quality_score: float
    duration: float
    sample_rate: int
    file_path: str
    speaker_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class VoiceGenerationRequest:
    """Voice generation request"""
    text: str
    voice_profile: VoiceProfile
    settings: Optional[Dict[str, Any]] = None
    language: str = "en"
    quality_mode: str = "balanced"

@dataclass
class VoiceGenerationResult:
    """Voice generation result"""
    audio_data: np.ndarray
    sample_rate: int
    processing_time: float
    quality_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class IVoiceEngine(ABC):
    """
    Interface for voice cloning engines
    """
    
    @abstractmethod
    async def generate_voice(self, request: VoiceGenerationRequest) -> VoiceGenerationResult:
        """
        Generate voice from text using voice profile
        
        Args:
            request: Voice generation request
            
        Returns:
            Voice generation result with audio data
        """
        pass
    
    @abstractmethod
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get engine information and capabilities
        
        Returns:
            Dictionary with engine metadata
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if engine is available and ready
        
        Returns:
            True if engine is ready for use
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the engine
        
        Returns:
            True if initialization successful
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """
        Cleanup engine resources
        """
        pass

class IVoiceProfileRepository(ABC):
    """
    Interface for voice profile storage and retrieval
    """
    
    @abstractmethod
    async def save_profile(self, profile: VoiceProfile, profile_id: str) -> bool:
        """
        Save voice profile
        
        Args:
            profile: Voice profile to save
            profile_id: Unique identifier for profile
            
        Returns:
            True if save successful
        """
        pass
    
    @abstractmethod
    async def load_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """
        Load voice profile by ID
        
        Args:
            profile_id: Profile identifier
            
        Returns:
            Voice profile or None if not found
        """
        pass
    
    @abstractmethod
    async def delete_profile(self, profile_id: str) -> bool:
        """
        Delete voice profile
        
        Args:
            profile_id: Profile identifier
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def list_profiles(self) -> List[str]:
        """
        List all available profile IDs
        
        Returns:
            List of profile identifiers
        """
        pass
    
    @abstractmethod
    async def profile_exists(self, profile_id: str) -> bool:
        """
        Check if profile exists
        
        Args:
            profile_id: Profile identifier
            
        Returns:
            True if profile exists
        """
        pass

class IVoiceFusion(ABC):
    """
    Interface for voice fusion operations
    """
    
    @abstractmethod
    async def fuse_voices(self, audio_files: List[Union[str, Path]]) -> Optional[np.ndarray]:
        """
        Fuse multiple voice samples into single embedding
        
        Args:
            audio_files: List of audio file paths
            
        Returns:
            Fused embedding or None if failed
        """
        pass
    
    @abstractmethod
    def get_fusion_stats(self, audio_files: List[Union[str, Path]]) -> Dict[str, Any]:
        """
        Get fusion statistics
        
        Args:
            audio_files: List of audio file paths
            
        Returns:
            Dictionary with fusion statistics
        """
        pass

class IVoiceQualityScorer(ABC):
    """
    Interface for voice quality scoring
    """
    
    @abstractmethod
    async def score_quality(self, reference_audio: Union[str, Path, np.ndarray],
                          generated_audio: Union[str, Path, np.ndarray],
                          reference_sr: Optional[int] = None,
                          generated_sr: Optional[int] = None) -> Dict[str, float]:
        """
        Score voice quality
        
        Args:
            reference_audio: Reference audio
            generated_audio: Generated audio
            reference_sr: Reference sample rate
            generated_sr: Generated sample rate
            
        Returns:
            Dictionary with quality scores
        """
        pass
    
    @abstractmethod
    def is_acceptable_quality(self, quality_scores: Dict[str, float]) -> bool:
        """
        Check if quality scores meet threshold
        
        Args:
            quality_scores: Quality score dictionary
            
        Returns:
            True if quality is acceptable
        """
        pass

# Factory interface for creating voice engines
class IVoiceEngineFactory(ABC):
    """
    Interface for voice engine factory
    """
    
    @abstractmethod
    def create_engine(self, engine_type: str) -> Optional[IVoiceEngine]:
        """
        Create voice engine by type
        
        Args:
            engine_type: Type of engine to create
            
        Returns:
            Voice engine instance or None if not supported
        """
        pass
    
    @abstractmethod
    def get_supported_engines(self) -> List[str]:
        """
        Get list of supported engine types
        
        Returns:
            List of supported engine type names
        """
        pass
