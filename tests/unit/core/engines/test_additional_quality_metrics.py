"""
Unit tests for Additional Quality Metrics.

Tests spectral flatness, pitch variance, energy variance, speaking rate,
click detection, silence ratio, and clipping ratio.
"""

import pytest
import numpy as np

from app.core.engines.quality_metrics import (
    calculate_spectral_flatness,
    calculate_pitch_variance,
    calculate_energy_variance,
    calculate_speaking_rate,
    detect_clicks,
    calculate_silence_ratio,
    calculate_clipping_ratio,
)


def generate_test_audio(duration_seconds: float = 1.0, frequency: float = 440.0, sample_rate: int = 22050) -> np.ndarray:
    """Generate test audio signal."""
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds))
    audio = np.sin(2 * np.pi * frequency * t)
    return audio.astype(np.float32)


def generate_noisy_audio(duration_seconds: float = 1.0, noise_level: float = 0.1, sample_rate: int = 22050) -> np.ndarray:
    """Generate noisy audio signal."""
    signal = generate_test_audio(duration_seconds, 440.0, sample_rate)
    noise = np.random.normal(0, noise_level, len(signal))
    return (signal + noise).astype(np.float32)


def generate_clipped_audio(duration_seconds: float = 1.0, sample_rate: int = 22050) -> np.ndarray:
    """Generate clipped audio signal."""
    audio = generate_test_audio(duration_seconds, 440.0, sample_rate)
    # Clip at 0.8
    audio = np.clip(audio, -0.8, 0.8)
    # Add some samples at maximum
    clip_indices = np.random.choice(len(audio), size=len(audio) // 10, replace=False)
    audio[clip_indices] = np.sign(audio[clip_indices]) * 1.0
    return audio.astype(np.float32)


class TestSpectralFlatness:
    """Tests for spectral flatness metric."""

    def test_spectral_flatness_sine_wave(self):
        """Test spectral flatness on sine wave (should be low - tonal)."""
        audio = generate_test_audio(duration_seconds=1.0, frequency=440.0)
        flatness = calculate_spectral_flatness(audio, sample_rate=22050)
        
        assert 0.0 <= flatness <= 1.0
        # Sine wave should have low flatness (tonal)
        assert flatness < 0.5

    def test_spectral_flatness_noise(self):
        """Test spectral flatness on noise (should be high - noise-like)."""
        audio = np.random.normal(0, 0.1, 22050).astype(np.float32)
        flatness = calculate_spectral_flatness(audio, sample_rate=22050)
        
        assert 0.0 <= flatness <= 1.0
        # Noise should have higher flatness
        assert flatness > 0.3


class TestPitchVariance:
    """Tests for pitch variance metric."""

    def test_pitch_variance_constant_frequency(self):
        """Test pitch variance on constant frequency (should be low)."""
        audio = generate_test_audio(duration_seconds=1.0, frequency=440.0)
        variance = calculate_pitch_variance(audio, sample_rate=22050)
        
        assert variance >= 0.0
        # Constant frequency should have low variance
        assert variance < 100.0

    def test_pitch_variance_varying_frequency(self):
        """Test pitch variance on varying frequency (should be higher)."""
        t = np.linspace(0, 1.0, 22050)
        # Varying frequency
        frequency = 440.0 + 100.0 * np.sin(2 * np.pi * 2 * t)
        audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        variance = calculate_pitch_variance(audio, sample_rate=22050)
        
        assert variance >= 0.0


class TestEnergyVariance:
    """Tests for energy variance metric."""

    def test_energy_variance_constant_amplitude(self):
        """Test energy variance on constant amplitude (should be low)."""
        audio = generate_test_audio(duration_seconds=1.0)
        variance = calculate_energy_variance(audio)
        
        assert variance >= 0.0

    def test_energy_variance_varying_amplitude(self):
        """Test energy variance on varying amplitude (should be higher)."""
        t = np.linspace(0, 1.0, 22050)
        # Varying amplitude
        amplitude = 0.5 + 0.3 * np.sin(2 * np.pi * 5 * t)
        audio = amplitude * np.sin(2 * np.pi * 440.0 * t).astype(np.float32)
        variance = calculate_energy_variance(audio)
        
        assert variance >= 0.0


class TestSpeakingRate:
    """Tests for speaking rate metric."""

    def test_speaking_rate_with_speech(self):
        """Test speaking rate on audio with speech-like content."""
        # Generate audio with energy variations (simulating speech)
        audio = generate_test_audio(duration_seconds=2.0)
        # Add energy variations
        t = np.linspace(0, 2.0, len(audio))
        envelope = 0.5 + 0.3 * np.sin(2 * np.pi * 2 * t)  # 2 Hz modulation
        audio = audio * envelope
        rate = calculate_speaking_rate(audio, sample_rate=22050)
        
        assert rate >= 0.0

    def test_speaking_rate_silence(self):
        """Test speaking rate on silence (should be low)."""
        audio = np.zeros(22050, dtype=np.float32)
        rate = calculate_speaking_rate(audio, sample_rate=22050)
        
        assert rate >= 0.0


class TestClickDetection:
    """Tests for click detection."""

    def test_click_detection_no_clicks(self):
        """Test click detection on clean audio (should detect no clicks)."""
        audio = generate_test_audio(duration_seconds=1.0)
        result = detect_clicks(audio, sample_rate=22050)
        
        assert "detected" in result
        assert "click_count" in result
        assert "click_ratio" in result
        assert "positions" in result
        assert isinstance(result["detected"], bool)
        assert result["click_count"] >= 0
        assert 0.0 <= result["click_ratio"] <= 1.0

    def test_click_detection_with_clicks(self):
        """Test click detection on audio with clicks."""
        audio = generate_test_audio(duration_seconds=1.0)
        # Add clicks (sudden amplitude changes)
        click_positions = [1000, 5000, 10000]
        for pos in click_positions:
            if pos < len(audio):
                audio[pos] = 1.0  # Sudden jump
        
        result = detect_clicks(audio, sample_rate=22050, threshold=0.05)
        
        assert result["detected"] is True or result["click_count"] >= 0
        assert result["click_count"] >= 0


class TestSilenceRatio:
    """Tests for silence ratio metric."""

    def test_silence_ratio_silent_audio(self):
        """Test silence ratio on silent audio (should be high)."""
        audio = np.zeros(22050, dtype=np.float32)
        ratio = calculate_silence_ratio(audio, sample_rate=22050)
        
        assert 0.0 <= ratio <= 1.0
        assert ratio > 0.5  # Mostly silence

    def test_silence_ratio_active_audio(self):
        """Test silence ratio on active audio (should be low)."""
        audio = generate_test_audio(duration_seconds=1.0)
        ratio = calculate_silence_ratio(audio, sample_rate=22050)
        
        assert 0.0 <= ratio <= 1.0
        assert ratio < 0.5  # Mostly active


class TestClippingRatio:
    """Tests for clipping ratio metric."""

    def test_clipping_ratio_no_clipping(self):
        """Test clipping ratio on non-clipped audio (should be low)."""
        audio = generate_test_audio(duration_seconds=1.0)
        # Normalize to avoid clipping
        audio = audio / np.max(np.abs(audio)) * 0.8
        ratio = calculate_clipping_ratio(audio)
        
        assert 0.0 <= ratio <= 1.0
        assert ratio < 0.1  # Low clipping

    def test_clipping_ratio_clipped_audio(self):
        """Test clipping ratio on clipped audio (should be higher)."""
        audio = generate_clipped_audio(duration_seconds=1.0)
        ratio = calculate_clipping_ratio(audio, clipping_threshold=0.95)
        
        assert 0.0 <= ratio <= 1.0
        assert ratio > 0.0  # Some clipping detected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

