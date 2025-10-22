#!/usr/bin/env python3
"""
VoiceStudio Quality Scorer
Implements automatic quality scoring and auto-regeneration for consistent output
Based on ChatGPT strategic plan for Day 4-5 implementation
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
class QualityScore:
    """Quality score result"""
    overall_score: float  # 0-100
    similarity_score: float  # 0-100
    audio_quality_score: float  # 0-100
    prosody_score: float  # 0-100
    details: Dict[str, float]

@dataclass
class QualityConfig:
    """Configuration for quality scoring"""
    min_acceptable_score: float = 80.0
    max_regeneration_attempts: int = 3
    similarity_weight: float = 0.6
    audio_quality_weight: float = 0.3
    prosody_weight: float = 0.1
    sample_rate: int = 16000

class VoiceQualityScorer:
    """
    Voice quality scoring system
    Evaluates generated audio against reference for consistency
    """
    
    def __init__(self, config: Optional[QualityConfig] = None):
        self.config = config or QualityConfig()
        self.encoder = None
        self._initialize_encoder()
        
    def _initialize_encoder(self):
        """Initialize voice encoder"""
        if not RESEMBLYZER_AVAILABLE:
            raise ImportError("Resemblyzer not available. Install with: pip install resemblyzer")
        
        try:
            self.encoder = VoiceEncoder()
            logger.info("Voice quality scorer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize voice encoder: {e}")
            raise
    
    def calculate_similarity_score(self, reference_audio: np.ndarray, generated_audio: np.ndarray, 
                                 reference_sr: int, generated_sr: int) -> float:
        """
        Calculate voice similarity score using resemblyzer embeddings
        Returns score from 0-100
        """
        try:
            # Resample to same sample rate
            target_sr = self.config.sample_rate
            
            if reference_sr != target_sr:
                reference_audio = librosa.resample(reference_audio, orig_sr=reference_sr, target_sr=target_sr)
            
            if generated_sr != target_sr:
                generated_audio = librosa.resample(generated_audio, orig_sr=generated_sr, target_sr=target_sr)
            
            # Preprocess for resemblyzer
            ref_wav = preprocess_wav(reference_audio, target_sr)
            gen_wav = preprocess_wav(generated_audio, target_sr)
            
            # Extract embeddings
            ref_embedding = self.encoder.embed_utterance(ref_wav)
            gen_embedding = self.encoder.embed_utterance(gen_wav)
            
            # Calculate cosine similarity
            similarity = np.dot(ref_embedding, gen_embedding) / (
                np.linalg.norm(ref_embedding) * np.linalg.norm(gen_embedding)
            )
            
            # Convert to 0-100 scale
            similarity_score = max(0.0, min(100.0, (similarity + 1.0) * 50.0))
            
            logger.debug(f"Similarity score: {similarity_score:.2f}")
            return similarity_score
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def calculate_audio_quality_score(self, audio: np.ndarray, sample_rate: int) -> float:
        """
        Calculate audio quality score based on technical metrics
        Returns score from 0-100
        """
        try:
            # Signal-to-noise ratio
            signal_power = np.mean(audio ** 2)
            noise_floor = np.percentile(np.abs(audio), 5)
            snr = 10 * np.log10(signal_power / (noise_floor ** 2 + 1e-10))
            snr_score = max(0.0, min(100.0, (snr + 20) / 40 * 100))
            
            # Clipping detection
            clipping_ratio = np.sum(np.abs(audio) > 0.95) / len(audio)
            clipping_score = max(0.0, 100.0 - clipping_ratio * 1000)
            
            # Dynamic range
            dynamic_range = 20 * np.log10(np.max(np.abs(audio)) / (np.mean(np.abs(audio)) + 1e-10))
            dynamic_score = max(0.0, min(100.0, dynamic_range / 60 * 100))
            
            # Silence detection
            silence_threshold = 0.01
            silence_ratio = np.sum(np.abs(audio) < silence_threshold) / len(audio)
            silence_score = max(0.0, 100.0 - silence_ratio * 200)
            
            # Spectral centroid (brightness)
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
            centroid_mean = np.mean(spectral_centroids)
            centroid_score = max(0.0, min(100.0, centroid_mean / 4000 * 100))
            
            # Combine scores
            audio_quality_score = (
                snr_score * 0.3 +
                clipping_score * 0.25 +
                dynamic_score * 0.2 +
                silence_score * 0.15 +
                centroid_score * 0.1
            )
            
            logger.debug(f"Audio quality breakdown: SNR={snr_score:.1f}, Clipping={clipping_score:.1f}, "
                        f"Dynamic={dynamic_score:.1f}, Silence={silence_score:.1f}, Centroid={centroid_score:.1f}")
            
            return max(0.0, min(100.0, audio_quality_score))
            
        except Exception as e:
            logger.error(f"Audio quality calculation failed: {e}")
            return 50.0  # Default moderate score
    
    def calculate_prosody_score(self, reference_audio: np.ndarray, generated_audio: np.ndarray,
                              reference_sr: int, generated_sr: int) -> float:
        """
        Calculate prosody similarity score
        Compares rhythm, pitch patterns, and speaking rate
        """
        try:
            # Resample to same sample rate
            target_sr = 22050  # Higher sample rate for better prosody analysis
            
            if reference_sr != target_sr:
                reference_audio = librosa.resample(reference_audio, orig_sr=reference_sr, target_sr=target_sr)
            
            if generated_sr != target_sr:
                generated_audio = librosa.resample(generated_audio, orig_sr=generated_sr, target_sr=target_sr)
            
            # Extract pitch (F0)
            ref_pitch = librosa.yin(reference_audio, fmin=50, fmax=400)
            gen_pitch = librosa.yin(generated_audio, fmin=50, fmax=400)
            
            # Remove NaN values
            ref_pitch = ref_pitch[~np.isnan(ref_pitch)]
            gen_pitch = gen_pitch[~np.isnan(gen_pitch)]
            
            if len(ref_pitch) == 0 or len(gen_pitch) == 0:
                return 50.0  # Default score if pitch extraction fails
            
            # Pitch statistics comparison
            ref_pitch_mean = np.mean(ref_pitch)
            gen_pitch_mean = np.mean(gen_pitch)
            pitch_mean_score = max(0.0, 100.0 - abs(ref_pitch_mean - gen_pitch_mean) / ref_pitch_mean * 100)
            
            ref_pitch_std = np.std(ref_pitch)
            gen_pitch_std = np.std(gen_pitch)
            pitch_std_score = max(0.0, 100.0 - abs(ref_pitch_std - gen_pitch_std) / ref_pitch_std * 100)
            
            # Speaking rate comparison
            ref_duration = len(reference_audio) / target_sr
            gen_duration = len(generated_audio) / target_sr
            duration_ratio = min(ref_duration, gen_duration) / max(ref_duration, gen_duration)
            duration_score = duration_ratio * 100
            
            # Combine prosody scores
            prosody_score = (
                pitch_mean_score * 0.4 +
                pitch_std_score * 0.4 +
                duration_score * 0.2
            )
            
            logger.debug(f"Prosody breakdown: Pitch mean={pitch_mean_score:.1f}, "
                        f"Pitch std={pitch_std_score:.1f}, Duration={duration_score:.1f}")
            
            return max(0.0, min(100.0, prosody_score))
            
        except Exception as e:
            logger.error(f"Prosody calculation failed: {e}")
            return 50.0  # Default moderate score
    
    def score_quality(self, reference_audio: Union[str, Path, np.ndarray], 
                     generated_audio: Union[str, Path, np.ndarray],
                     reference_sr: Optional[int] = None,
                     generated_sr: Optional[int] = None) -> QualityScore:
        """
        Calculate comprehensive quality score
        """
        try:
            # Load audio if paths provided
            if isinstance(reference_audio, (str, Path)):
                reference_audio, reference_sr = librosa.load(str(reference_audio), sr=None)
            
            if isinstance(generated_audio, (str, Path)):
                generated_audio, generated_sr = librosa.load(str(generated_audio), sr=None)
            
            if reference_sr is None or generated_sr is None:
                raise ValueError("Sample rates must be provided for numpy arrays")
            
            logger.info("Calculating quality scores...")
            
            # Calculate individual scores
            similarity_score = self.calculate_similarity_score(
                reference_audio, generated_audio, reference_sr, generated_sr
            )
            
            audio_quality_score = self.calculate_audio_quality_score(generated_audio, generated_sr)
            
            prosody_score = self.calculate_prosody_score(
                reference_audio, generated_audio, reference_sr, generated_sr
            )
            
            # Calculate weighted overall score
            overall_score = (
                similarity_score * self.config.similarity_weight +
                audio_quality_score * self.config.audio_quality_weight +
                prosody_score * self.config.prosody_weight
            )
            
            details = {
                "similarity": similarity_score,
                "audio_quality": audio_quality_score,
                "prosody": prosody_score,
                "similarity_weight": self.config.similarity_weight,
                "audio_quality_weight": self.config.audio_quality_weight,
                "prosody_weight": self.config.prosody_weight
            }
            
            quality_score = QualityScore(
                overall_score=overall_score,
                similarity_score=similarity_score,
                audio_quality_score=audio_quality_score,
                prosody_score=prosody_score,
                details=details
            )
            
            logger.info(f"Quality score: {overall_score:.2f} "
                       f"(Similarity: {similarity_score:.2f}, "
                       f"Audio: {audio_quality_score:.2f}, "
                       f"Prosody: {prosody_score:.2f})")
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Quality scoring failed: {e}")
            return QualityScore(
                overall_score=0.0,
                similarity_score=0.0,
                audio_quality_score=0.0,
                prosody_score=0.0,
                details={"error": str(e)}
            )
    
    def is_acceptable_quality(self, quality_score: QualityScore) -> bool:
        """Check if quality score meets minimum threshold"""
        return quality_score.overall_score >= self.config.min_acceptable_score
    
    async def score_quality_async(self, reference_audio: Union[str, Path, np.ndarray],
                                generated_audio: Union[str, Path, np.ndarray],
                                reference_sr: Optional[int] = None,
                                generated_sr: Optional[int] = None) -> QualityScore:
        """Asynchronous version of quality scoring"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=2) as executor:
            return await loop.run_in_executor(
                executor, self.score_quality, reference_audio, generated_audio, reference_sr, generated_sr
            )

class QualityGatedGenerator:
    """
    Generator with automatic quality gating and regeneration
    """
    
    def __init__(self, generator_func, scorer: Optional[VoiceQualityScorer] = None):
        self.generator_func = generator_func
        self.scorer = scorer or VoiceQualityScorer()
        self.config = self.scorer.config
        
    def generate_with_quality_gate(self, text: str, voice_profile, 
                                 reference_audio: Union[str, Path, np.ndarray],
                                 reference_sr: Optional[int] = None) -> Tuple[np.ndarray, QualityScore, int]:
        """
        Generate voice with automatic quality gating
        Returns: (best_audio, best_score, attempts_made)
        """
        best_audio = None
        best_score = None
        attempts_made = 0
        
        logger.info(f"Generating with quality gate (max {self.config.max_regeneration_attempts} attempts)...")
        
        for attempt in range(self.config.max_regeneration_attempts):
            attempts_made += 1
            logger.info(f"Generation attempt {attempt + 1}/{self.config.max_regeneration_attempts}")
            
            try:
                # Generate audio
                generated_audio, generated_sr = self.generator_func(text, voice_profile)
                
                # Score quality
                quality_score = self.scorer.score_quality(
                    reference_audio, generated_audio, reference_sr, generated_sr
                )
                
                # Check if this is the best attempt so far
                if best_score is None or quality_score.overall_score > best_score.overall_score:
                    best_audio = generated_audio
                    best_score = quality_score
                    logger.info(f"New best score: {quality_score.overall_score:.2f}")
                
                # Check if quality is acceptable
                if self.scorer.is_acceptable_quality(quality_score):
                    logger.info(f"✅ Acceptable quality achieved: {quality_score.overall_score:.2f}")
                    return generated_audio, quality_score, attempts_made
                
                logger.info(f"Quality below threshold: {quality_score.overall_score:.2f} < {self.config.min_acceptable_score}")
                
            except Exception as e:
                logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                continue
        
        logger.warning(f"⚠️  Maximum attempts reached. Best score: {best_score.overall_score:.2f}")
        return best_audio, best_score, attempts_made

# Convenience functions
def score_voice_quality(reference_audio: Union[str, Path, np.ndarray],
                       generated_audio: Union[str, Path, np.ndarray],
                       reference_sr: Optional[int] = None,
                       generated_sr: Optional[int] = None,
                       config: Optional[QualityConfig] = None) -> QualityScore:
    """Convenience function for quality scoring"""
    scorer = VoiceQualityScorer(config)
    return scorer.score_quality(reference_audio, generated_audio, reference_sr, generated_sr)

# Example usage
if __name__ == "__main__":
    # Test the quality scorer
    logging.basicConfig(level=logging.INFO)
    
    # Example files (replace with actual paths)
    reference_file = "reference.wav"
    generated_file = "generated.wav"
    
    if Path(reference_file).exists() and Path(generated_file).exists():
        print("Testing voice quality scorer...")
        
        scorer = VoiceQualityScorer()
        quality_score = scorer.score_quality(reference_file, generated_file)
        
        print(f"✅ Quality scoring complete!")
        print(f"📊 Overall Score: {quality_score.overall_score:.2f}/100")
        print(f"🎯 Similarity: {quality_score.similarity_score:.2f}/100")
        print(f"🔊 Audio Quality: {quality_score.audio_quality_score:.2f}/100")
        print(f"🎵 Prosody: {quality_score.prosody_score:.2f}/100")
        
        if scorer.is_acceptable_quality(quality_score):
            print("✅ Quality meets minimum threshold")
        else:
            print("❌ Quality below minimum threshold")
    else:
        print("ℹ️  No test files found. Place reference.wav and generated.wav to test.")
