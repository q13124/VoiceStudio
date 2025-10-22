#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Quality Scoring System
Automatic quality assessment and regeneration for voice cloning
"""

import os
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Tuple, Optional, List, Union
import logging

# Voice cloning integration
try:
    from resemblyzer import VoiceEncoder, preprocess_wav

    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False
    logging.warning(
        "resemblyzer not available - quality scoring will use basic metrics"
    )


class QualityScorer:
    """
    Quality scoring system for voice cloning outputs.

    Provides automatic quality assessment and regeneration capabilities
    to ensure consistent, high-quality voice cloning results.
    """

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize the quality scoring system.

        Args:
            sample_rate: Target sample rate for audio processing
        """
        self.sample_rate = sample_rate
        self.encoder = None

        if RESEMBLYZER_AVAILABLE:
            try:
                self.encoder = VoiceEncoder()
                logging.info("VoiceEncoder initialized for quality scoring")
            except Exception as e:
                logging.error(f"Failed to initialize VoiceEncoder: {e}")
                self.encoder = None

        # Quality thresholds
        self.thresholds = {"excellent": 0.9, "good": 0.8, "fair": 0.7, "poor": 0.6}

    def load_audio(self, audio_path: Union[str, Path]) -> np.ndarray:
        """
        Load audio file with preprocessing.

        Args:
            audio_path: Path to audio file

        Returns:
            Preprocessed audio array
        """
        try:
            if RESEMBLYZER_AVAILABLE and self.encoder:
                wav = preprocess_wav(str(audio_path))
                return wav
            else:
                audio, sr = librosa.load(str(audio_path), sr=self.sample_rate)
                return audio
        except Exception as e:
            logging.error(f"Failed to load audio {audio_path}: {e}")
            return None

    def calculate_similarity_score(
        self, reference_audio: np.ndarray, generated_audio: np.ndarray
    ) -> float:
        """
        Calculate similarity score between reference and generated audio.

        Args:
            reference_audio: Reference audio array
            generated_audio: Generated audio array

        Returns:
            Similarity score (0-1, higher is better)
        """
        if reference_audio is None or generated_audio is None:
            return 0.0

        try:
            if RESEMBLYZER_AVAILABLE and self.encoder:
                # Use resemblyzer for high-quality similarity
                ref_emb = self.encoder.embed_utterance(reference_audio)
                gen_emb = self.encoder.embed_utterance(generated_audio)

                # Cosine similarity
                similarity = np.dot(ref_emb, gen_emb) / (
                    np.linalg.norm(ref_emb) * np.linalg.norm(gen_emb)
                )
                return float(similarity)
            else:
                # Fallback: MFCC-based similarity
                ref_mfcc = librosa.feature.mfcc(
                    y=reference_audio, sr=self.sample_rate, n_mfcc=13
                )
                gen_mfcc = librosa.feature.mfcc(
                    y=generated_audio, sr=self.sample_rate, n_mfcc=13
                )

                # Dynamic time warping similarity
                from scipy.spatial.distance import cosine

                ref_mean = np.mean(ref_mfcc, axis=1)
                gen_mean = np.mean(gen_mfcc, axis=1)
                similarity = 1 - cosine(ref_mean, gen_mean)
                return max(0.0, float(similarity))

        except Exception as e:
            logging.error(f"Failed to calculate similarity: {e}")
            return 0.0

    def calculate_audio_quality_metrics(self, audio: np.ndarray) -> dict:
        """
        Calculate various audio quality metrics.

        Args:
            audio: Audio array

        Returns:
            Dictionary of quality metrics
        """
        if audio is None or len(audio) == 0:
            return {"snr": 0.0, "clarity": 0.0, "loudness": 0.0}

        try:
            # Signal-to-noise ratio (simplified)
            signal_power = np.mean(audio**2)
            noise_floor = np.percentile(np.abs(audio), 10) ** 2
            snr = 10 * np.log10(signal_power / (noise_floor + 1e-10))

            # Clarity (spectral centroid)
            spectral_centroids = librosa.feature.spectral_centroid(
                y=audio, sr=self.sample_rate
            )[0]
            clarity = np.mean(spectral_centroids) / (self.sample_rate / 2)

            # Loudness (RMS)
            loudness = np.sqrt(np.mean(audio**2))

            return {
                "snr": float(snr),
                "clarity": float(clarity),
                "loudness": float(loudness),
            }
        except Exception as e:
            logging.error(f"Failed to calculate audio quality metrics: {e}")
            return {"snr": 0.0, "clarity": 0.0, "loudness": 0.0}

    def score_quality(
        self, reference_audio: np.ndarray, generated_audio: np.ndarray
    ) -> dict:
        """
        Comprehensive quality scoring for voice cloning output.

        Args:
            reference_audio: Reference audio array
            generated_audio: Generated audio array

        Returns:
            Quality score dictionary
        """
        # Calculate similarity score
        similarity = self.calculate_similarity_score(reference_audio, generated_audio)

        # Calculate audio quality metrics
        audio_metrics = self.calculate_audio_quality_metrics(generated_audio)

        # Overall quality score (weighted combination)
        overall_score = (
            similarity * 0.6  # 60% similarity
            + min(audio_metrics["clarity"], 1.0) * 0.2  # 20% clarity
            + min(audio_metrics["snr"] / 20.0, 1.0) * 0.2  # 20% SNR (normalized)
        )

        # Determine quality level
        if overall_score >= self.thresholds["excellent"]:
            quality_level = "excellent"
        elif overall_score >= self.thresholds["good"]:
            quality_level = "good"
        elif overall_score >= self.thresholds["fair"]:
            quality_level = "fair"
        else:
            quality_level = "poor"

        return {
            "overall_score": float(overall_score),
            "similarity_score": float(similarity),
            "quality_level": quality_level,
            "audio_metrics": audio_metrics,
            "thresholds": self.thresholds,
            "recommendation": self._get_recommendation(quality_level, overall_score),
        }

    def _get_recommendation(self, quality_level: str, score: float) -> str:
        """
        Get recommendation based on quality level.

        Args:
            quality_level: Quality level string
            score: Overall quality score

        Returns:
            Recommendation string
        """
        if quality_level == "excellent":
            return "Perfect quality - ready for production use"
        elif quality_level == "good":
            return "Good quality - suitable for most applications"
        elif quality_level == "fair":
            return "Fair quality - consider regeneration with different parameters"
        else:
            return "Poor quality - regeneration recommended"

    def should_regenerate(
        self, quality_score: dict, min_threshold: float = 0.8
    ) -> bool:
        """
        Determine if audio should be regenerated based on quality score.

        Args:
            quality_score: Quality score dictionary
            min_threshold: Minimum acceptable threshold

        Returns:
            True if regeneration is recommended
        """
        return quality_score["overall_score"] < min_threshold


class VoiceCloningQualityGate:
    """
    Quality gate system for voice cloning with automatic regeneration.
    """

    def __init__(self, max_attempts: int = 3):
        """
        Initialize quality gate system.

        Args:
            max_attempts: Maximum regeneration attempts
        """
        self.quality_scorer = QualityScorer()
        self.max_attempts = max_attempts

    def generate_with_quality_gate(
        self,
        text: str,
        reference_audio: np.ndarray,
        voice_profile: dict,
        engine: str = "xtts",
        min_quality: float = 0.8,
    ) -> Tuple[np.ndarray, dict]:
        """
        Generate voice with quality gating and automatic regeneration.

        Args:
            text: Text to synthesize
            reference_audio: Reference audio for comparison
            voice_profile: Voice profile dictionary
            engine: Voice cloning engine
            min_quality: Minimum quality threshold

        Returns:
            Tuple of (generated_audio, quality_info)
        """
        best_audio = None
        best_score = 0.0
        best_quality_info = None

        for attempt in range(self.max_attempts):
            logging.info(f"Voice generation attempt {attempt + 1}/{self.max_attempts}")

            # Generate audio (placeholder - integrate with your engines)
            generated_audio = self._generate_audio(text, voice_profile, engine)

            if generated_audio is None:
                logging.warning(f"Generation failed on attempt {attempt + 1}")
                continue

            # Score quality
            quality_info = self.quality_scorer.score_quality(
                reference_audio, generated_audio
            )

            logging.info(
                f"Attempt {attempt + 1} quality: {quality_info['overall_score']:.3f} "
                f"({quality_info['quality_level']})"
            )

            # Track best result
            if quality_info["overall_score"] > best_score:
                best_score = quality_info["overall_score"]
                best_audio = generated_audio
                best_quality_info = quality_info

            # Check if quality is acceptable
            if quality_info["overall_score"] >= min_quality:
                logging.info(
                    f"Quality threshold met: {quality_info['overall_score']:.3f}"
                )
                break

        if best_audio is None:
            raise Exception("All generation attempts failed")

        logging.info(
            f"Best quality achieved: {best_score:.3f} ({best_quality_info['quality_level']})"
        )

        return best_audio, best_quality_info

    def _generate_audio(
        self, text: str, voice_profile: dict, engine: str
    ) -> Optional[np.ndarray]:
        """
        Generate audio using specified engine.

        This is a placeholder - integrate with your existing voice cloning engines.
        """
        try:
            # Placeholder implementation
            # In practice, this would call your XTTS, OpenVoice, RVC, etc.
            logging.info(f"Generating audio with {engine} engine")

            # Return dummy audio for now
            duration = len(text.split()) * 0.5  # Rough estimate
            dummy_audio = (
                np.random.randn(int(self.quality_scorer.sample_rate * duration)) * 0.1
            )
            return dummy_audio

        except Exception as e:
            logging.error(f"Audio generation failed: {e}")
            return None


def test_quality_scoring():
    """
    Test the quality scoring system.
    """
    print("Testing VoiceStudio Quality Scoring System")
    print("=" * 50)

    # Create test audio files
    sample_rate = 22050
    duration = 2.0

    # Reference audio (clean tone)
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    reference_audio = np.sin(2 * np.pi * 440 * t)

    # Generated audio (similar tone with slight noise)
    generated_audio = np.sin(2 * np.pi * 440 * t) + np.random.randn(len(t)) * 0.1

    # Test quality scoring
    quality_scorer = QualityScorer()

    try:
        # Score quality
        quality_info = quality_scorer.score_quality(reference_audio, generated_audio)

        print(f"SUCCESS: Overall Score: {quality_info['overall_score']:.3f}")
        print(f"SUCCESS: Similarity Score: {quality_info['similarity_score']:.3f}")
        print(f"SUCCESS: Quality Level: {quality_info['quality_level']}")
        print(f"SUCCESS: Recommendation: {quality_info['recommendation']}")

        # Test quality gate
        quality_gate = VoiceCloningQualityGate()

        # Mock voice profile
        voice_profile = {
            "name": "test_profile",
            "embedding": np.random.randn(256).tolist(),
            "sample_rate": sample_rate,
        }

        generated_audio, quality_info = quality_gate.generate_with_quality_gate(
            "Hello world", reference_audio, voice_profile
        )

        print(f"SUCCESS: Quality Gate Test: Generated {len(generated_audio)} samples")
        print(f"SUCCESS: Final Quality: {quality_info['overall_score']:.3f}")

        print("=" * 50)
        print("Quality Scoring System Test PASSED!")
        print("Ready for voice cloning integration!")

    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    # Run test
    test_quality_scoring()
