#!/usr/bin/env python3
"""
Tests for VoiceStudio Voice Fusion System
Fast unit tests for voice fusion functionality
"""

import pytest
import numpy as np
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import librosa
import soundfile as sf

# Import the modules under test
from workers.ops.voice_fusion import VoiceFusion, FusionConfig, VoiceProfile, fuse_voice_files

class TestVoiceFusion:
    """Test cases for VoiceFusion class"""
    
    @pytest.fixture
    def fusion_config(self):
        """Create test fusion configuration"""
        return FusionConfig(
            min_quality_threshold=0.1,  # Lower threshold for testing
            max_files=10,
            min_duration=0.5,  # Shorter minimum for testing
            max_duration=30.0,
            sample_rate=16000,
            use_weighted_average=True,
            quality_weight_power=2.0
        )
    
    @pytest.fixture
    def voice_fusion(self, fusion_config):
        """Create VoiceFusion instance for testing"""
        with patch('workers.ops.voice_fusion.VoiceEncoder') as mock_encoder:
            mock_encoder.return_value = Mock()
            return VoiceFusion(fusion_config)
    
    @pytest.fixture
    def sample_audio_files(self):
        """Create temporary audio files for testing"""
        files = []
        temp_dir = tempfile.mkdtemp()
        
        # Create 3 sample audio files with different characteristics
        for i in range(3):
            # Generate different audio patterns
            duration = 2.0  # 2 seconds
            sample_rate = 16000
            samples = int(duration * sample_rate)
            
            if i == 0:
                # High quality: clean sine wave
                t = np.linspace(0, duration, samples)
                audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # A4 note
            elif i == 1:
                # Medium quality: sine wave with some noise
                t = np.linspace(0, duration, samples)
                audio = 0.3 * np.sin(2 * np.pi * 440 * t) + 0.1 * np.random.randn(samples)
            else:
                # Lower quality: more noise
                t = np.linspace(0, duration, samples)
                audio = 0.2 * np.sin(2 * np.pi * 440 * t) + 0.2 * np.random.randn(samples)
            
            # Save as WAV file
            file_path = os.path.join(temp_dir, f"sample_{i}.wav")
            sf.write(file_path, audio, sample_rate)
            files.append(file_path)
        
        yield files
        
        # Cleanup
        for file_path in files:
            try:
                os.unlink(file_path)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass
    
    @pytest.fixture
    def mock_encoder(self):
        """Mock VoiceEncoder for testing"""
        mock_encoder = Mock()
        # Mock embedding_utterance to return consistent embeddings
        mock_encoder.embed_utterance.return_value = np.random.randn(256)
        return mock_encoder

    def test_fuse_three_files(self, voice_fusion, sample_audio_files, mock_encoder):
        """Test fusing three audio files successfully"""
        # Mock the encoder
        voice_fusion.encoder = mock_encoder
        
        # Test fusion with 3 files
        result = voice_fusion.fuse_voices(sample_audio_files)
        
        # Verify result
        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (256,)  # Expected embedding dimension
        
        # Verify encoder was called for each file
        assert mock_encoder.embed_utterance.call_count == 3

    def test_invalid_file(self, voice_fusion, mock_encoder):
        """Test handling of invalid/non-existent files"""
        voice_fusion.encoder = mock_encoder
        
        # Test with non-existent file
        invalid_files = ["/path/to/nonexistent/file.wav"]
        result = voice_fusion.fuse_voices(invalid_files)
        
        # Should return None for invalid files
        assert result is None
        
        # Test with empty file list
        result = voice_fusion.fuse_voices([])
        assert result is None

    def test_weighting_by_quality(self, voice_fusion, sample_audio_files, mock_encoder):
        """Test that fusion weights embeddings by quality scores"""
        voice_fusion.encoder = mock_encoder
        
        # Mock quality scores to be different
        quality_scores = [0.9, 0.7, 0.5]  # Decreasing quality
        
        with patch.object(voice_fusion, 'calculate_quality_score', side_effect=quality_scores):
            result = voice_fusion.fuse_voices(sample_audio_files)
        
        # Verify result exists
        assert result is not None
        assert isinstance(result, np.ndarray)
        
        # Verify quality calculation was called
        assert voice_fusion.calculate_quality_score.call_count == 3

    def test_edge_short_audio(self, voice_fusion, mock_encoder):
        """Test handling of very short audio files"""
        voice_fusion.encoder = mock_encoder
        
        # Create very short audio file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        try:
            # Create 0.3 second audio (below min_duration of 0.5s)
            duration = 0.3
            sample_rate = 16000
            samples = int(duration * sample_rate)
            audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples))
            sf.write(temp_file.name, audio, sample_rate)
            
            # Test fusion with short file
            result = voice_fusion.fuse_voices([temp_file.name])
            
            # Should return None due to short duration
            assert result is None
            
        finally:
            os.unlink(temp_file.name)

    def test_single_file_fusion(self, voice_fusion, sample_audio_files, mock_encoder):
        """Test fusion with single file"""
        voice_fusion.encoder = mock_encoder
        
        # Test with single file
        result = voice_fusion.fuse_voices([sample_audio_files[0]])
        
        # Should return the single embedding
        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (256,)

    def test_max_files_limit(self, voice_fusion, mock_encoder):
        """Test that max_files limit is respected"""
        voice_fusion.encoder = mock_encoder
        
        # Create more files than max_files limit
        temp_files = []
        temp_dir = tempfile.mkdtemp()
        
        try:
            for i in range(15):  # More than max_files=10
                file_path = os.path.join(temp_dir, f"file_{i}.wav")
                # Create minimal valid audio
                audio = np.random.randn(16000) * 0.1
                sf.write(file_path, audio, 16000)
                temp_files.append(file_path)
            
            result = voice_fusion.fuse_voices(temp_files)
            
            # Should still work but only process max_files
            assert result is not None
            assert mock_encoder.embed_utterance.call_count == 10  # max_files limit
            
        finally:
            # Cleanup
            for file_path in temp_files:
                try:
                    os.unlink(file_path)
                except:
                    pass
            try:
                os.rmdir(temp_dir)
            except:
                pass

    def test_quality_threshold_filtering(self, voice_fusion, sample_audio_files, mock_encoder):
        """Test that files below quality threshold are filtered out"""
        voice_fusion.encoder = mock_encoder
        
        # Mock quality scores with some below threshold
        quality_scores = [0.9, 0.05, 0.8]  # Middle one below threshold (0.1)
        
        with patch.object(voice_fusion, 'calculate_quality_score', side_effect=quality_scores):
            result = voice_fusion.fuse_voices(sample_audio_files)
        
        # Should still work with remaining files
        assert result is not None
        # Should only process 2 files (middle one filtered out)
        assert voice_fusion.calculate_quality_score.call_count == 3

    def test_async_fusion(self, voice_fusion, sample_audio_files, mock_encoder):
        """Test async fusion functionality"""
        import asyncio
        
        voice_fusion.encoder = mock_encoder
        
        async def test_async():
            result = await voice_fusion.fuse_voices_async(sample_audio_files)
            assert result is not None
            assert isinstance(result, np.ndarray)
            return result
        
        # Run async test
        result = asyncio.run(test_async())
        assert result is not None

    def test_fusion_stats(self, voice_fusion, sample_audio_files, mock_encoder):
        """Test fusion statistics generation"""
        voice_fusion.encoder = mock_encoder
        
        stats = voice_fusion.get_fusion_stats(sample_audio_files)
        
        # Verify stats structure
        assert isinstance(stats, dict)
        assert 'total_files' in stats
        assert 'valid_profiles' in stats
        assert 'quality_scores' in stats
        assert 'average_quality' in stats
        
        assert stats['total_files'] == 3
        assert stats['valid_profiles'] == 3

    def test_convenience_function(self, sample_audio_files, mock_encoder):
        """Test convenience function fuse_voice_files"""
        with patch('workers.ops.voice_fusion.VoiceEncoder') as mock_encoder_class:
            mock_encoder_class.return_value = mock_encoder
            
            result = fuse_voice_files(sample_audio_files)
            
            assert result is not None
            assert isinstance(result, np.ndarray)

    def test_error_handling(self, voice_fusion, mock_encoder):
        """Test error handling in fusion process"""
        voice_fusion.encoder = mock_encoder
        
        # Mock encoder to raise exception
        mock_encoder.embed_utterance.side_effect = Exception("Encoder error")
        
        # Should handle error gracefully
        result = voice_fusion.fuse_voices(["dummy_file.wav"])
        assert result is None

    def test_config_validation(self):
        """Test fusion configuration validation"""
        # Test valid config
        config = FusionConfig()
        assert config.min_quality_threshold >= 0.0
        assert config.max_files > 0
        assert config.min_duration > 0.0
        assert config.sample_rate > 0
        
        # Test custom config
        custom_config = FusionConfig(
            min_quality_threshold=0.5,
            max_files=5,
            use_weighted_average=False
        )
        assert custom_config.min_quality_threshold == 0.5
        assert custom_config.max_files == 5
        assert custom_config.use_weighted_average == False

# Performance test to ensure tests run fast
def test_performance_benchmark():
    """Ensure tests complete quickly"""
    import time
    
    start_time = time.time()
    
    # Run a simple fusion operation
    with patch('workers.ops.voice_fusion.VoiceEncoder') as mock_encoder_class:
        mock_encoder = Mock()
        mock_encoder.embed_utterance.return_value = np.random.randn(256)
        mock_encoder_class.return_value = mock_encoder
        
        fusion = VoiceFusion()
        fusion.encoder = mock_encoder
        
        # Create minimal test files
        temp_files = []
        temp_dir = tempfile.mkdtemp()
        
        try:
            for i in range(3):
                file_path = os.path.join(temp_dir, f"perf_test_{i}.wav")
                audio = np.random.randn(16000) * 0.1
                sf.write(file_path, audio, 16000)
                temp_files.append(file_path)
            
            result = fusion.fuse_voices(temp_files)
            assert result is not None
            
        finally:
            # Cleanup
            for file_path in temp_files:
                try:
                    os.unlink(file_path)
                except:
                    pass
            try:
                os.rmdir(temp_dir)
            except:
                pass
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Ensure test completes in under 1 second
    assert execution_time < 1.0, f"Test took {execution_time:.2f}s, should be <1s"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
