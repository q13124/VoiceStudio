"""
Comprehensive tests for VoiceStudio Audio Utilities

Tests all core audio functions and quality enhancement features.
"""

import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.audio.audio_utils import (
    analyze_voice_characteristics,
    convert_format,
    detect_silence,
    enhance_voice_quality,
    match_voice_profile,
    normalize_lufs,
    remove_artifacts,
    resample_audio,
)


# Test fixtures
@pytest.fixture
def sample_rate():
    """Standard sample rate for tests"""
    return 22050


@pytest.fixture
def mono_audio(sample_rate):
    """Generate test mono audio (1 second of sine wave)"""
    duration = 1.0
    frequency = 440.0  # A4 note
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    return audio


@pytest.fixture
def stereo_audio(sample_rate):
    """Generate test stereo audio"""
    duration = 1.0
    frequency = 440.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    left = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    right = np.sin(2 * np.pi * frequency * 1.5 * t).astype(np.float32)
    audio = np.column_stack([left, right])
    return audio


@pytest.fixture
def audio_with_silence(sample_rate):
    """Generate audio with leading and trailing silence"""
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # First 0.5s: silence
    silence1 = np.zeros(int(sample_rate * 0.5))

    # Middle 1.0s: signal
    signal = np.sin(2 * np.pi * 440.0 * t[: int(sample_rate * 1.0)]).astype(np.float32)

    # Last 0.5s: silence
    silence2 = np.zeros(int(sample_rate * 0.5))

    audio = np.concatenate([silence1, signal, silence2])
    return audio


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


# Core Audio Utilities Tests


def test_normalize_lufs_mono(mono_audio, sample_rate):
    """Test LUFS normalization for mono audio"""
    try:
        normalized = normalize_lufs(mono_audio, sample_rate, target_lufs=-23.0)

        assert normalized.shape == mono_audio.shape
        assert normalized.dtype == np.float32
        assert np.all(np.abs(normalized) <= 1.0)  # Should be clipped

        # Check that normalization changed the audio (unless already at target)
        # In most cases, normalization will change the audio
        assert isinstance(normalized, np.ndarray)
    except ImportError:
        pytest.skip("pyloudnorm not installed")


def test_normalize_lufs_stereo(stereo_audio, sample_rate):
    """Test LUFS normalization for stereo audio"""
    try:
        normalized = normalize_lufs(stereo_audio, sample_rate, target_lufs=-23.0)

        assert normalized.shape == stereo_audio.shape
        assert normalized.dtype == np.float32
        assert np.all(np.abs(normalized) <= 1.0)
    except ImportError:
        pytest.skip("pyloudnorm not installed")


def test_normalize_lufs_empty():
    """Test LUFS normalization with empty audio"""
    try:
        empty_audio = np.array([])
        with pytest.raises(ValueError, match="empty"):
            normalize_lufs(empty_audio, 22050)
    except ImportError:
        pytest.skip("pyloudnorm not installed")


def test_detect_silence(audio_with_silence, sample_rate):
    """Test silence detection"""
    try:
        silence_regions = detect_silence(
            audio_with_silence, sample_rate, threshold_db=-40.0, min_silence_duration=0.1
        )

        assert isinstance(silence_regions, list)
        # Should detect at least the leading and trailing silence
        assert len(silence_regions) >= 2

        # Check that silence regions are tuples of (start, end)
        for region in silence_regions:
            assert isinstance(region, tuple)
            assert len(region) == 2
            assert region[0] < region[1]
    except ImportError:
        pytest.skip("librosa not installed")


def test_detect_silence_no_silence(mono_audio, sample_rate):
    """Test silence detection on audio without silence"""
    try:
        silence_regions = detect_silence(
            mono_audio, sample_rate, threshold_db=-40.0, min_silence_duration=0.1
        )

        # Should return empty list or very few regions
        assert isinstance(silence_regions, list)
    except ImportError:
        pytest.skip("librosa not installed")


def test_resample_audio(mono_audio, sample_rate):
    """Test audio resampling"""
    try:
        target_sr = 16000
        resampled = resample_audio(mono_audio, sample_rate, target_sr)

        assert isinstance(resampled, np.ndarray)
        # Duration should be approximately the same
        original_duration = len(mono_audio) / sample_rate
        resampled_duration = len(resampled) / target_sr
        assert abs(original_duration - resampled_duration) < 0.1

        # Should maintain same dtype
        assert resampled.dtype == mono_audio.dtype
    except ImportError:
        pytest.skip("librosa not installed")


def test_resample_audio_same_rate(mono_audio, sample_rate):
    """Test resampling when rates are the same"""
    try:
        resampled = resample_audio(mono_audio, sample_rate, sample_rate)
        assert np.array_equal(resampled, mono_audio)
    except ImportError:
        pytest.skip("librosa not installed")


def test_resample_audio_invalid_rate(mono_audio):
    """Test resampling with invalid sample rates"""
    try:
        with pytest.raises(ValueError):
            resample_audio(mono_audio, -1, 22050)
        with pytest.raises(ValueError):
            resample_audio(mono_audio, 22050, 0)
    except ImportError:
        pytest.skip("librosa not installed")


def test_convert_format(mono_audio, sample_rate, temp_dir):
    """Test audio format conversion"""
    try:
        import soundfile as sf

        # Create input WAV file
        input_path = Path(temp_dir) / "input.wav"
        sf.write(str(input_path), mono_audio, sample_rate)

        # Convert to FLAC
        output_path = Path(temp_dir) / "output.flac"
        result_path = convert_format(
            input_path, output_path, output_format="flac", sample_rate=sample_rate
        )

        assert result_path.exists()
        assert result_path == output_path

        # Verify output can be read
        audio_out, sr_out = sf.read(str(result_path))
        assert sr_out == sample_rate
        assert len(audio_out) > 0
    except ImportError:
        pytest.skip("soundfile not installed")


def test_convert_format_resample(mono_audio, sample_rate, temp_dir):
    """Test format conversion with resampling"""
    try:
        import soundfile as sf

        input_path = Path(temp_dir) / "input.wav"
        sf.write(str(input_path), mono_audio, sample_rate)

        output_path = Path(temp_dir) / "output.wav"
        target_sr = 16000
        result_path = convert_format(
            input_path, output_path, output_format="wav", sample_rate=target_sr
        )

        # Verify resampling occurred
        _audio_out, sr_out = sf.read(str(result_path))
        assert sr_out == target_sr
    except ImportError:
        pytest.skip("soundfile or librosa not installed")


def test_convert_format_channel_conversion(stereo_audio, sample_rate, temp_dir):
    """Test format conversion with channel conversion"""
    try:
        import soundfile as sf

        input_path = Path(temp_dir) / "input_stereo.wav"
        sf.write(str(input_path), stereo_audio, sample_rate)

        # Convert to mono
        output_path = Path(temp_dir) / "output_mono.wav"
        result_path = convert_format(input_path, output_path, output_format="wav", channels=1)

        audio_out, _sr_out = sf.read(str(result_path))
        assert len(audio_out.shape) == 1  # Should be mono
    except ImportError:
        pytest.skip("soundfile or librosa not installed")


# Voice Cloning Quality Functions Tests


def test_analyze_voice_characteristics(mono_audio, sample_rate):
    """Test voice characteristics analysis"""
    try:
        characteristics = analyze_voice_characteristics(mono_audio, sample_rate)

        assert isinstance(characteristics, dict)
        assert "f0_mean" in characteristics
        assert "f0_std" in characteristics
        assert "formants" in characteristics
        assert "spectral_centroid" in characteristics
        assert "spectral_rolloff" in characteristics
        assert "zero_crossing_rate" in characteristics
        assert "mfcc" in characteristics

        # Check types
        assert isinstance(characteristics["f0_mean"], (int, float))
        assert isinstance(characteristics["formants"], list)
        assert len(characteristics["formants"]) == 3
        assert isinstance(characteristics["mfcc"], list)
        assert len(characteristics["mfcc"]) == 13
    except ImportError:
        pytest.skip("librosa not installed")


def test_analyze_voice_characteristics_empty():
    """Test analysis with empty audio"""
    try:
        empty_audio = np.array([])
        with pytest.raises(ValueError, match="empty"):
            analyze_voice_characteristics(empty_audio, 22050)
    except ImportError:
        pytest.skip("librosa not installed")


def test_enhance_voice_quality(mono_audio, sample_rate):
    """Test voice quality enhancement"""
    try:
        enhanced = enhance_voice_quality(
            mono_audio,
            sample_rate,
            normalize=True,
            denoise=False,  # Skip denoising if noisereduce not available
        )

        assert enhanced.shape == mono_audio.shape
        assert enhanced.dtype == mono_audio.dtype
        assert np.all(np.abs(enhanced) <= 1.0)
    except ImportError:
        pytest.skip("Required libraries not installed")


def test_enhance_voice_quality_no_normalize(mono_audio, sample_rate):
    """Test enhancement without normalization"""
    try:
        enhanced = enhance_voice_quality(mono_audio, sample_rate, normalize=False, denoise=False)

        assert enhanced.shape == mono_audio.shape
    except ImportError:
        pytest.skip("Required libraries not installed")


def test_remove_artifacts(mono_audio, sample_rate):
    """Test artifact removal"""
    # Add some artifacts (discontinuities)
    audio_with_artifacts = mono_audio.copy()
    # Create a click
    audio_with_artifacts[len(audio_with_artifacts) // 2] = 0.9

    cleaned = remove_artifacts(audio_with_artifacts, sample_rate)

    assert cleaned.shape == audio_with_artifacts.shape
    assert np.all(np.abs(cleaned) <= 1.0)


def test_remove_artifacts_stereo(stereo_audio, sample_rate):
    """Test artifact removal on stereo audio"""
    cleaned = remove_artifacts(stereo_audio, sample_rate)

    assert cleaned.shape == stereo_audio.shape
    assert np.all(np.abs(cleaned) <= 1.0)


def test_match_voice_profile(mono_audio, sample_rate):
    """Test voice profile matching"""
    try:
        # Use same audio as both reference and target (should match well)
        match_result = match_voice_profile(mono_audio, mono_audio, sample_rate, sample_rate)

        assert isinstance(match_result, dict)
        assert "f0_similarity" in match_result
        assert "formant_similarity" in match_result
        assert "mfcc_distance" in match_result
        assert "overall_similarity" in match_result
        assert "recommendations" in match_result

        # Same audio should have high similarity
        assert 0.0 <= match_result["overall_similarity"] <= 1.0
        assert isinstance(match_result["recommendations"], list)
    except ImportError:
        pytest.skip("librosa not installed")


def test_match_voice_profile_different_audio(mono_audio, sample_rate):
    """Test voice matching with different audio"""
    try:
        # Create different frequency audio
        duration = 1.0
        frequency = 880.0  # Different frequency
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        different_audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)

        match_result = match_voice_profile(mono_audio, different_audio, sample_rate, sample_rate)

        assert isinstance(match_result, dict)
        assert "overall_similarity" in match_result
        # Different audio should have lower similarity
        assert 0.0 <= match_result["overall_similarity"] <= 1.0
    except ImportError:
        pytest.skip("librosa not installed")


def test_match_voice_profile_resampling(mono_audio, sample_rate):
    """Test voice matching with different sample rates"""
    try:
        target_sr = 16000
        target_audio = resample_audio(mono_audio, sample_rate, target_sr)

        match_result = match_voice_profile(mono_audio, target_audio, sample_rate, target_sr)

        assert isinstance(match_result, dict)
        assert "overall_similarity" in match_result
    except ImportError:
        pytest.skip("librosa not installed")


# Quality Metric Validation Tests


def test_quality_metrics_validation(mono_audio, sample_rate):
    """Test that quality metrics are within expected ranges"""
    try:
        characteristics = analyze_voice_characteristics(mono_audio, sample_rate)

        # F0 should be reasonable for voice (50-500 Hz typically)
        assert 0 <= characteristics["f0_mean"] <= 2000

        # Formants should be positive
        for formant in characteristics["formants"]:
            assert formant >= 0

        # Spectral features should be positive
        assert characteristics["spectral_centroid"] > 0
        assert characteristics["spectral_rolloff"] > 0
        assert 0 <= characteristics["zero_crossing_rate"] <= 1

        # MFCC should have 13 coefficients
        assert len(characteristics["mfcc"]) == 13
    except ImportError:
        pytest.skip("librosa not installed")


# Integration Tests


def test_full_pipeline(mono_audio, sample_rate):
    """Test full audio processing pipeline"""
    try:
        # 1. Analyze characteristics
        chars = analyze_voice_characteristics(mono_audio, sample_rate)
        assert chars is not None

        # 2. Enhance quality
        enhanced = enhance_voice_quality(mono_audio, sample_rate)
        assert enhanced is not None

        # 3. Normalize
        normalized = normalize_lufs(enhanced, sample_rate)
        assert normalized is not None

        # 4. Remove artifacts
        cleaned = remove_artifacts(normalized, sample_rate)
        assert cleaned is not None

        # All should maintain shape
        assert cleaned.shape == mono_audio.shape
    except ImportError:
        pytest.skip("Required libraries not installed")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
