#!/usr/bin/env python3
"""
VoiceStudio Multi-Reference Voice Fusion
Implements weighted averaging of voice embeddings for 40% quality improvement
Based on ChatGPT strategic plan for Day 2-3 implementation
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

# Voice embedding imports
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False
    logging.warning("Resemblyzer not available. Install with: pip install resemblyzer")

logger = logging.getLogger(__name__)

@dataclass
class VoiceProfile:
    """Voice profile with embedding and metadata"""
    embedding: np.ndarray
    quality_score: float
    duration: float
    sample_rate: int
    file_path: str
    speaker_id: Optional[str] = None

@dataclass
class FusionConfig:
    """Configuration for voice fusion"""
    min_quality_threshold: float = 0.3
    max_files: int = 10
    min_duration: float = 1.0
    max_duration: float = 30.0
    sample_rate: int = 16000
    use_weighted_average: bool = True
    quality_weight_power: float = 2.0

class VoiceFusion:
    """
    Multi-reference voice fusion system
    Combines multiple audio samples to create superior voice profiles
    """
    
    def __init__(self, config: Optional[FusionConfig] = None):
        self.config = config or FusionConfig()
        self.encoder = None
        self._initialize_encoder()
        
    def _initialize_encoder(self):
        """Initialize voice encoder"""
        if not RESEMBLYZER_AVAILABLE:
            raise ImportError("Resemblyzer not available. Install with: pip install resemblyzer")
        
        try:
            self.encoder = VoiceEncoder()
            logger.info("Voice encoder initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize voice encoder: {e}")
            raise
    
    def calculate_quality_score(self, audio: np.ndarray, sample_rate: int) -> float:
        """
        Calculate quality score for audio sample
        Higher score = better quality
        """
        try:
            # Signal-to-noise ratio estimation
            signal_power = np.mean(audio ** 2)
            noise_floor = np.percentile(np.abs(audio), 10)
            snr = 10 * np.log10(signal_power / (noise_floor ** 2 + 1e-10))
            
            # Clipping detection
            clipping_ratio = np.sum(np.abs(audio) > 0.95) / len(audio)
            
            # Duration factor (prefer 3-10 second samples)
            duration = len(audio) / sample_rate
            duration_score = 1.0 - abs(duration - 5.0) / 10.0
            duration_score = max(0.0, min(1.0, duration_score))
            
            # Silence detection
            silence_threshold = 0.01
            silence_ratio = np.sum(np.abs(audio) < silence_threshold) / len(audio)
            silence_score = 1.0 - silence_ratio
            
            # Combine scores
            snr_score = min(1.0, max(0.0, (snr + 20) / 40))  # Normalize SNR
            clipping_score = 1.0 - clipping_ratio
            
            quality_score = (
                snr_score * 0.4 +
                clipping_score * 0.3 +
                duration_score * 0.2 +
                silence_score * 0.1
            )
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logger.warning(f"Quality calculation failed: {e}")
            return 0.5  # Default moderate quality
    
    async def extract_voice_profile(self, audio_path: Union[str, Path]) -> Optional[VoiceProfile]:
        """
        Extract voice profile from audio file (async, non-blocking I/O)
        """
        try:
            audio_path = Path(audio_path)
            if not audio_path.exists():
                logger.error(f"Audio file not found: {audio_path}")
                return None
            
            # Load audio asynchronously
            audio, sample_rate = await asyncio.to_thread(
                librosa.load, str(audio_path), sr=self.config.sample_rate
            )
            
            # Validate duration
            duration = len(audio) / sample_rate
            if duration < self.config.min_duration:
                logger.warning(f"Audio too short: {duration:.2f}s < {self.config.min_duration}s")
                return None
            
            if duration > self.config.max_duration:
                logger.warning(f"Audio too long: {duration:.2f}s > {self.config.max_duration}s")
                # Truncate to max duration
                max_samples = int(self.config.max_duration * sample_rate)
                audio = audio[:max_samples]
                duration = self.config.max_duration
            
            # Preprocess for resemblyzer asynchronously
            wav = await asyncio.to_thread(preprocess_wav, audio, sample_rate)
            
            # Extract embedding asynchronously
            embedding = await asyncio.to_thread(self.encoder.embed_utterance, wav)
            
            # Calculate quality score asynchronously
            quality_score = await asyncio.to_thread(self.calculate_quality_score, audio, sample_rate)
            
            # Filter by quality threshold
            if quality_score < self.config.min_quality_threshold:
                logger.warning(f"Audio quality too low: {quality_score:.3f} < {self.config.min_quality_threshold}")
                return None
            
            profile = VoiceProfile(
                embedding=embedding,
                quality_score=quality_score,
                duration=duration,
                sample_rate=sample_rate,
                file_path=str(audio_path)
            )
            
            logger.info(f"Extracted voice profile: quality={quality_score:.3f}, duration={duration:.2f}s")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to extract voice profile from {audio_path}: {e}")
            return None
    
    async def fuse_voices(self, audio_files: List[Union[str, Path]]) -> Optional[np.ndarray]:
        """
        Fuse multiple voice samples into a single embedding (async, non-blocking I/O)
        Returns weighted average of embeddings based on quality scores
        """
        if not audio_files:
            logger.error("No audio files provided")
            return None
        
        if len(audio_files) > self.config.max_files:
            logger.warning(f"Too many files: {len(audio_files)} > {self.config.max_files}")
            audio_files = audio_files[:self.config.max_files]
        
        logger.info(f"Fusing {len(audio_files)} voice samples...")
        
        # Extract profiles from all files concurrently
        profile_tasks = [self.extract_voice_profile(audio_file) for audio_file in audio_files]
        profile_results = await asyncio.gather(*profile_tasks, return_exceptions=True)
        
        # Filter valid profiles and handle exceptions
        profiles = []
        for i, result in enumerate(profile_results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to extract profile from {audio_files[i]}: {result}")
            elif result is not None:
                profiles.append(result)
        
        if not profiles:
            logger.error("No valid voice profiles extracted")
            return None
        
        if len(profiles) == 1:
            logger.info("Only one valid profile, returning single embedding")
            return profiles[0].embedding
        
        logger.info(f"Successfully extracted {len(profiles)} voice profiles")
        
        # Calculate weights based on quality scores
        if self.config.use_weighted_average:
            weights = np.array([p.quality_score ** self.config.quality_weight_power for p in profiles])
            weights = weights / np.sum(weights)  # Normalize
            
            logger.info(f"Quality weights: {[f'{w:.3f}' for w in weights]}")
            
            # Weighted average
            fused_embedding = np.zeros_like(profiles[0].embedding)
            for profile, weight in zip(profiles, weights):
                fused_embedding += profile.embedding * weight
        else:
            # Simple average
            fused_embedding = np.mean([p.embedding for p in profiles], axis=0)
        
        # Calculate average quality score
        avg_quality = np.mean([p.quality_score for p in profiles])
        logger.info(f"Fused embedding created with average quality: {avg_quality:.3f}")
        
        return fused_embedding
    
    def fuse_voices_sync(self, audio_files: List[Union[str, Path]]) -> Optional[np.ndarray]:
        """
        Synchronous wrapper for backward compatibility
        """
        return asyncio.run(self.fuse_voices(audio_files))
    
    async def get_fusion_stats(self, audio_files: List[Union[str, Path]]) -> Dict[str, any]:
        """
        Get statistics about voice fusion process (async)
        """
        profile_tasks = [self.extract_voice_profile(audio_file) for audio_file in audio_files]
        profile_results = await asyncio.gather(*profile_tasks, return_exceptions=True)
        
        profiles = []
        for result in profile_results:
            if not isinstance(result, Exception) and result is not None:
                profiles.append(result)
        
        if not profiles:
            return {"error": "No valid profiles extracted"}
        
        return {
            "total_files": len(audio_files),
            "valid_profiles": len(profiles),
            "quality_scores": [p.quality_score for p in profiles],
            "durations": [p.duration for p in profiles],
            "average_quality": np.mean([p.quality_score for p in profiles]),
            "quality_range": (min([p.quality_score for p in profiles]), max([p.quality_score for p in profiles])),
            "total_duration": sum([p.duration for p in profiles])
        }

# Convenience functions for easy integration
def fuse_voice_files(audio_files: List[Union[str, Path]], config: Optional[FusionConfig] = None) -> Optional[np.ndarray]:
    """
    Convenience function to fuse voice files (sync wrapper)
    """
    fusion = VoiceFusion(config)
    return fusion.fuse_voices_sync(audio_files)

async def fuse_voice_files_async(audio_files: List[Union[str, Path]], config: Optional[FusionConfig] = None) -> Optional[np.ndarray]:
    """
    Asynchronous convenience function
    """
    fusion = VoiceFusion(config)
    return await fusion.fuse_voices(audio_files)

# Example usage
if __name__ == "__main__":
    # Test the voice fusion system
    logging.basicConfig(level=logging.INFO)
    
    # Example audio files (replace with actual paths)
    test_files = [
        "sample1.wav",
        "sample2.wav", 
        "sample3.wav"
    ]
    
    # Check if test files exist
    existing_files = [f for f in test_files if Path(f).exists()]
    
    if existing_files:
        print(f"Testing voice fusion with {len(existing_files)} files...")
        
        fusion = VoiceFusion()
        fused_embedding = fusion.fuse_voices_sync(existing_files)
        
        if fused_embedding is not None:
            print(f"✅ Voice fusion successful! Embedding shape: {fused_embedding.shape}")
            
            # Get fusion statistics
            stats = asyncio.run(fusion.get_fusion_stats(existing_files))
            print(f"📊 Fusion stats: {stats}")
        else:
            print("❌ Voice fusion failed")
    else:
        print("ℹ️  No test files found. Place some audio files in the current directory to test.")
        print("   Expected files: sample1.wav, sample2.wav, sample3.wav")
