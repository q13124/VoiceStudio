#!/usr/bin/env python3
"""
VoiceStudio Voice Cloning Integration Bridge
Bridges multi-reference fusion system with existing TTS engines
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
from dataclasses import dataclass
import numpy as np

# Import our fusion and quality systems
from workers.ops.voice_fusion import VoiceFusion, FusionConfig, VoiceProfile
from workers.ops.quality_scorer import VoiceQualityScorer, QualityConfig, QualityScore

logger = logging.getLogger(__name__)

@dataclass
class VoiceCloningRequest:
    """Voice cloning request with multi-reference support"""
    text: str
    audio_files: List[Union[str, Path]]
    voice_settings: Optional[Dict[str, Any]] = None
    quality_threshold: float = 80.0
    use_caching: bool = True

@dataclass
class VoiceCloningResult:
    """Voice cloning result with quality metrics"""
    audio_data: np.ndarray
    sample_rate: int
    quality_score: Optional[QualityScore] = None
    processing_time: float = 0.0
    fusion_stats: Optional[Dict[str, Any]] = None
    cached: bool = False

class VoiceCloningIntegration:
    """
    Integration bridge between fusion system and TTS engines
    """
    
    def __init__(self, fusion_config: Optional[FusionConfig] = None, 
                 quality_config: Optional[QualityConfig] = None):
        self.fusion_config = fusion_config or FusionConfig()
        self.quality_config = quality_config or QualityConfig()
        
        # Initialize systems
        self.voice_fusion = VoiceFusion(self.fusion_config)
        self.quality_scorer = VoiceQualityScorer(self.quality_config)
        
        # Simple in-memory cache for voice profiles
        self._voice_cache: Dict[str, VoiceProfile] = {}
        
        logger.info("Voice cloning integration initialized")
    
    def _generate_cache_key(self, audio_files: List[Union[str, Path]]) -> str:
        """Generate cache key for voice profile"""
        import hashlib
        file_paths = [str(Path(f).resolve()) for f in audio_files]
        file_paths.sort()  # Ensure consistent ordering
        content = "|".join(file_paths)
        return hashlib.md5(content.encode()).hexdigest()
    
    async def clone_voice_multi_reference(self, request: VoiceCloningRequest) -> VoiceCloningResult:
        """
        Clone voice using multiple reference files with fusion
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing multi-reference voice cloning: {len(request.audio_files)} files")
            
            # Check cache first
            cache_key = self._generate_cache_key(request.audio_files)
            cached_profile = None
            
            if request.use_caching and cache_key in self._voice_cache:
                cached_profile = self._voice_cache[cache_key]
                logger.info("Using cached voice profile")
            
            # Create or retrieve voice profile
            if cached_profile:
                voice_profile = cached_profile
                cached = True
            else:
                # Fuse multiple audio files into single embedding
                fused_embedding = await self.voice_fusion.fuse_voices_async(request.audio_files)
                
                if fused_embedding is None:
                    raise ValueError("Failed to create fused voice embedding")
                
                # Create voice profile
                voice_profile = VoiceProfile(
                    embedding=fused_embedding,
                    quality_score=0.8,  # Default for fused profiles
                    duration=0.0,  # Not applicable for embeddings
                    sample_rate=self.fusion_config.sample_rate,
                    file_path="fused_profile"
                )
                
                # Cache the profile
                if request.use_caching:
                    self._voice_cache[cache_key] = voice_profile
                
                cached = False
            
            # Get fusion statistics
            fusion_stats = self.voice_fusion.get_fusion_stats(request.audio_files)
            
            # Generate audio using TTS engine (placeholder for now)
            # In real implementation, this would call the actual TTS engine
            audio_data, sample_rate = await self._generate_audio_with_engine(
                request.text, voice_profile, request.voice_settings
            )
            
            # Calculate quality score if reference audio available
            quality_score = None
            if len(request.audio_files) > 0:
                try:
                    quality_score = self.quality_scorer.score_quality(
                        request.audio_files[0], audio_data, 
                        reference_sr=self.fusion_config.sample_rate,
                        generated_sr=sample_rate
                    )
                except Exception as e:
                    logger.warning(f"Quality scoring failed: {e}")
            
            processing_time = time.time() - start_time
            
            result = VoiceCloningResult(
                audio_data=audio_data,
                sample_rate=sample_rate,
                quality_score=quality_score,
                processing_time=processing_time,
                fusion_stats=fusion_stats,
                cached=cached
            )
            
            logger.info(f"Voice cloning completed in {processing_time:.2f}s, "
                       f"quality: {quality_score.overall_score if quality_score else 'N/A'}")
            
            return result
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            raise
    
    async def _generate_audio_with_engine(self, text: str, voice_profile: VoiceProfile, 
                                        voice_settings: Optional[Dict[str, Any]]) -> Tuple[np.ndarray, int]:
        """
        Generate audio using TTS engine (placeholder implementation)
        In real implementation, this would integrate with XTTS or other engines
        """
        # Placeholder: Generate silence for now
        # Real implementation would call: engine.generate(text, voice_profile.embedding)
        duration = len(text) * 0.1  # Rough estimate: 100ms per character
        sample_rate = 22050
        samples = int(duration * sample_rate)
        
        # Generate simple sine wave as placeholder
        t = np.linspace(0, duration, samples)
        frequency = 440  # A4 note
        audio_data = 0.1 * np.sin(2 * np.pi * frequency * t)
        
        return audio_data, sample_rate
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get voice profile cache statistics"""
        return {
            "cached_profiles": len(self._voice_cache),
            "cache_keys": list(self._voice_cache.keys()),
            "memory_usage": sum(sys.getsizeof(profile) for profile in self._voice_cache.values())
        }
    
    def clear_cache(self):
        """Clear voice profile cache"""
        self._voice_cache.clear()
        logger.info("Voice profile cache cleared")

# Convenience functions for easy integration
async def clone_voice_multi_reference(text: str, audio_files: List[Union[str, Path]], 
                                   voice_settings: Optional[Dict[str, Any]] = None,
                                   quality_threshold: float = 80.0) -> VoiceCloningResult:
    """
    Convenience function for multi-reference voice cloning
    """
    request = VoiceCloningRequest(
        text=text,
        audio_files=audio_files,
        voice_settings=voice_settings,
        quality_threshold=quality_threshold
    )
    
    integration = VoiceCloningIntegration()
    return await integration.clone_voice_multi_reference(request)

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_integration():
        """Test the voice cloning integration"""
        logging.basicConfig(level=logging.INFO)
        
        # Example files (replace with actual paths)
        test_files = [
            "sample1.wav",
            "sample2.wav",
            "sample3.wav"
        ]
        
        # Check if test files exist
        existing_files = [f for f in test_files if Path(f).exists()]
        
        if existing_files:
            print(f"Testing voice cloning integration with {len(existing_files)} files...")
            
            try:
                result = await clone_voice_multi_reference(
                    text="Hello, this is a test of multi-reference voice cloning.",
                    audio_files=existing_files
                )
                
                print(f"✅ Voice cloning successful!")
                print(f"📊 Processing time: {result.processing_time:.2f}s")
                print(f"🎵 Audio shape: {result.audio_data.shape}")
                print(f"🔊 Sample rate: {result.sample_rate}")
                
                if result.quality_score:
                    print(f"📈 Quality score: {result.quality_score.overall_score:.2f}")
                
                if result.fusion_stats:
                    print(f"🔗 Fusion stats: {result.fusion_stats}")
                
            except Exception as e:
                print(f"❌ Voice cloning failed: {e}")
        else:
            print("ℹ️  No test files found. Place some audio files to test.")
    
    asyncio.run(test_integration())
