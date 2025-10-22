#!/usr/bin/env python3
"""
Unit tests for async voice fusion functionality
"""

import asyncio
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import io

from workers.ops.voice_fusion import (
    VoiceFusion, FusionConfig, VoiceProfile,
    fuse_voice_files, fuse_voice_files_async
)

class TestAsyncVoiceFusion:
    """Test async voice fusion functionality"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock fusion config"""
        return FusionConfig(
            min_quality_threshold=0.1,
            max_files=5,
            min_duration=0.5,
            max_duration=10.0,
            sample_rate=16000,
            use_weighted_average=True,
            quality_weight_power=2.0
        )
    
    @pytest.fixture
    def mock_voice_profile(self):
        """Mock voice profile"""
        return VoiceProfile(
            embedding=np.random.rand(256),
            quality_score=0.8,
            duration=2.0,
            sample_rate=16000,
            file_path="test.wav"
        )
    
    @pytest.fixture
    def mock_audio_files(self):
        """Create temporary audio files for testing"""
        files = []
        for i in range(3):
            # Create a simple WAV file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            
            # Write minimal WAV header + some audio data
            sample_rate = 16000
            duration = 1.0
            samples = int(sample_rate * duration)
            
            # WAV header
            temp_file.write(b'RIFF')
            temp_file.write((36 + samples * 2).to_bytes(4, 'little'))
            temp_file.write(b'WAVEfmt ')
            temp_file.write((16).to_bytes(4, 'little'))
            temp_file.write((1).to_bytes(2, 'little'))  # PCM
            temp_file.write((1).to_bytes(2, 'little'))  # Mono
            temp_file.write(sample_rate.to_bytes(4, 'little'))
            temp_file.write((sample_rate * 2).to_bytes(4, 'little'))
            temp_file.write((2).to_bytes(2, 'little'))
            temp_file.write((16).to_bytes(2, 'little'))
            temp_file.write(b'data')
            temp_file.write((samples * 2).to_bytes(4, 'little'))
            
            # Write some audio data (simple sine wave)
            for n in range(samples):
                sample = int(32767 * 0.1 * np.sin(2 * np.pi * 440 * n / sample_rate))
                temp_file.write(sample.to_bytes(2, 'little', signed=True))
            
            temp_file.close()
            files.append(temp_file.name)
        
        yield files
        
        # Cleanup
        for file_path in files:
            Path(file_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_extract_voice_profile_async_success(self, mock_config, mock_audio_files):
        """Test successful async voice profile extraction"""
        fusion = VoiceFusion(mock_config)
        
        # Mock resemblyzer components
        with patch('workers.ops.voice_fusion.RESEMBLYZER_AVAILABLE', True), \
             patch('workers.ops.voice_fusion.preprocess_wav') as mock_preprocess, \
             patch.object(fusion.encoder, 'embed_utterance') as mock_embed, \
             patch.object(fusion, 'calculate_quality_score') as mock_quality:
            
            mock_preprocess.return_value = np.random.rand(16000)
            mock_embed.return_value = np.random.rand(256)
            mock_quality.return_value = 0.8
            
            profile = await fusion.extract_voice_profile(mock_audio_files[0])
            
            assert profile is not None
            assert profile.quality_score == 0.8
            assert profile.duration > 0
            assert profile.sample_rate == 16000
            assert profile.file_path == mock_audio_files[0]
    
    @pytest.mark.asyncio
    async def test_extract_voice_profile_async_file_not_found(self, mock_config):
        """Test async voice profile extraction with non-existent file"""
        fusion = VoiceFusion(mock_config)
        
        profile = await fusion.extract_voice_profile("nonexistent.wav")
        
        assert profile is None
    
    @pytest.mark.asyncio
    async def test_extract_voice_profile_async_low_quality(self, mock_config, mock_audio_files):
        """Test async voice profile extraction with low quality audio"""
        fusion = VoiceFusion(mock_config)
        
        with patch('workers.ops.voice_fusion.RESEMBLYZER_AVAILABLE', True), \
             patch('workers.ops.voice_fusion.preprocess_wav') as mock_preprocess, \
             patch.object(fusion.encoder, 'embed_utterance') as mock_embed, \
             patch.object(fusion, 'calculate_quality_score') as mock_quality:
            
            mock_preprocess.return_value = np.random.rand(16000)
            mock_embed.return_value = np.random.rand(256)
            mock_quality.return_value = 0.05  # Below threshold
            
            profile = await fusion.extract_voice_profile(mock_audio_files[0])
            
            assert profile is None
    
    @pytest.mark.asyncio
    async def test_fuse_voices_async_success(self, mock_config, mock_audio_files):
        """Test successful async voice fusion"""
        fusion = VoiceFusion(mock_config)
        
        # Mock voice profiles
        profiles = [
            VoiceProfile(
                embedding=np.random.rand(256),
                quality_score=0.8,
                duration=2.0,
                sample_rate=16000,
                file_path=f"test{i}.wav"
            ) for i in range(3)
        ]
        
        with patch.object(fusion, 'extract_voice_profile', side_effect=profiles):
            result = await fusion.fuse_voices(mock_audio_files)
            
            assert result is not None
            assert isinstance(result, np.ndarray)
            assert result.shape == (256,)
    
    @pytest.mark.asyncio
    async def test_fuse_voices_async_no_valid_profiles(self, mock_config, mock_audio_files):
        """Test async voice fusion with no valid profiles"""
        fusion = VoiceFusion(mock_config)
        
        with patch.object(fusion, 'extract_voice_profile', return_value=None):
            result = await fusion.fuse_voices(mock_audio_files)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fuse_voices_async_single_profile(self, mock_config, mock_audio_files):
        """Test async voice fusion with single valid profile"""
        fusion = VoiceFusion(mock_config)
        
        profile = VoiceProfile(
            embedding=np.random.rand(256),
            quality_score=0.8,
            duration=2.0,
            sample_rate=16000,
            file_path="test.wav"
        )
        
        with patch.object(fusion, 'extract_voice_profile', return_value=profile):
            result = await fusion.fuse_voices([mock_audio_files[0]])
            
            assert result is not None
            assert np.array_equal(result, profile.embedding)
    
    @pytest.mark.asyncio
    async def test_fuse_voices_async_with_exceptions(self, mock_config, mock_audio_files):
        """Test async voice fusion handling exceptions"""
        fusion = VoiceFusion(mock_config)
        
        # Mock one success, one exception
        def mock_extract(file_path):
            if file_path == mock_audio_files[0]:  # First file succeeds
                return VoiceProfile(
                    embedding=np.random.rand(256),
                    quality_score=0.8,
                    duration=2.0,
                    sample_rate=16000,
                    file_path=file_path
                )
            else:  # Other files fail
                raise Exception("Processing failed")
        
        with patch.object(fusion, 'extract_voice_profile', side_effect=mock_extract):
            result = await fusion.fuse_voices(mock_audio_files)
            
            # Should still work with the one valid profile
            assert result is not None
            assert isinstance(result, np.ndarray)
    
    @pytest.mark.asyncio
    async def test_get_fusion_stats_async(self, mock_config, mock_audio_files):
        """Test async fusion statistics"""
        fusion = VoiceFusion(mock_config)
        
        profiles = [
            VoiceProfile(
                embedding=np.random.rand(256),
                quality_score=0.8,
                duration=2.0,
                sample_rate=16000,
                file_path=f"test{i}.wav"
            ) for i in range(2)
        ]
        
        with patch.object(fusion, 'extract_voice_profile', side_effect=profiles):
            stats = await fusion.get_fusion_stats(mock_audio_files)
            
            assert "total_files" in stats
            assert "valid_profiles" in stats
            assert "quality_scores" in stats
            assert "durations" in stats
            assert "average_quality" in stats
            assert stats["total_files"] == len(mock_audio_files)
            assert stats["valid_profiles"] == 2
            assert stats["average_quality"] == 0.8
    
    def test_fuse_voices_sync_wrapper(self, mock_config, mock_audio_files):
        """Test synchronous wrapper for backward compatibility"""
        fusion = VoiceFusion(mock_config)
        
        profiles = [
            VoiceProfile(
                embedding=np.random.rand(256),
                quality_score=0.8,
                duration=2.0,
                sample_rate=16000,
                file_path=f"test{i}.wav"
            ) for i in range(2)
        ]
        
        with patch.object(fusion, 'extract_voice_profile', side_effect=profiles):
            result = fusion.fuse_voices_sync(mock_audio_files)
            
            assert result is not None
            assert isinstance(result, np.ndarray)
    
    @pytest.mark.asyncio
    async def test_convenience_function_async(self, mock_config, mock_audio_files):
        """Test async convenience function"""
        profiles = [
            VoiceProfile(
                embedding=np.random.rand(256),
                quality_score=0.8,
                duration=2.0,
                sample_rate=16000,
                file_path=f"test{i}.wav"
            ) for i in range(2)
        ]
        
        with patch('workers.ops.voice_fusion.VoiceFusion') as mock_fusion_class:
            mock_fusion = Mock()
            mock_fusion.fuse_voices = AsyncMock(return_value=np.random.rand(256))
            mock_fusion_class.return_value = mock_fusion
            
            result = await fuse_voice_files_async(mock_audio_files, mock_config)
            
            assert result is not None
            assert isinstance(result, np.ndarray)
            mock_fusion.fuse_voices.assert_called_once_with(mock_audio_files)
    
    def test_convenience_function_sync(self, mock_config, mock_audio_files):
        """Test sync convenience function"""
        profiles = [
            VoiceProfile(
                embedding=np.random.rand(256),
                quality_score=0.8,
                duration=2.0,
                sample_rate=16000,
                file_path=f"test{i}.wav"
            ) for i in range(2)
        ]
        
        with patch('workers.ops.voice_fusion.VoiceFusion') as mock_fusion_class:
            mock_fusion = Mock()
            mock_fusion.fuse_voices_sync.return_value = np.random.rand(256)
            mock_fusion_class.return_value = mock_fusion
            
            result = fuse_voice_files(mock_audio_files, mock_config)
            
            assert result is not None
            assert isinstance(result, np.ndarray)
            mock_fusion.fuse_voices_sync.assert_called_once_with(mock_audio_files)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
