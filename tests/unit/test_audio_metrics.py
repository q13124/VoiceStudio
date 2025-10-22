#!/usr/bin/env python3
"""
Unit tests for audio metrics extraction
"""

import pytest
import numpy as np
import tempfile
import io
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from services.metrics.audio_metrics import (
    AudioMetricsExtractor, AudioMetrics, extract_audio_metrics
)

class TestAudioMetrics:
    """Test audio metrics extraction functionality"""
    
    @pytest.fixture
    def mock_audio_data(self):
        """Create mock audio data"""
        sample_rate = 16000
        duration = 2.0
        samples = int(sample_rate * duration)
        
        # Create simple sine wave
        t = np.linspace(0, duration, samples)
        audio = 0.1 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
        
        return audio, sample_rate
    
    @pytest.fixture
    def mock_wav_bytes(self, mock_audio_data):
        """Create WAV file bytes"""
        audio, sample_rate = mock_audio_data
        
        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Create WAV file
        wav_buffer = io.BytesIO()
        
        # WAV header
        wav_buffer.write(b'RIFF')
        wav_buffer.write((36 + len(audio_int16) * 2).to_bytes(4, 'little'))
        wav_buffer.write(b'WAVEfmt ')
        wav_buffer.write((16).to_bytes(4, 'little'))
        wav_buffer.write((1).to_bytes(2, 'little'))  # PCM
        wav_buffer.write((1).to_bytes(2, 'little'))  # Mono
        wav_buffer.write(sample_rate.to_bytes(4, 'little'))
        wav_buffer.write((sample_rate * 2).to_bytes(4, 'little'))
        wav_buffer.write((2).to_bytes(2, 'little'))
        wav_buffer.write((16).to_bytes(2, 'little'))
        wav_buffer.write(b'data')
        wav_buffer.write((len(audio_int16) * 2).to_bytes(4, 'little'))
        
        # Write audio data
        wav_buffer.write(audio_int16.tobytes())
        
        return wav_buffer.getvalue()
    
    @pytest.fixture
    def temp_audio_file(self, mock_wav_bytes):
        """Create temporary audio file"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file.write(mock_wav_bytes)
        temp_file.close()
        
        yield temp_file.name
        
        # Cleanup
        Path(temp_file.name).unlink(missing_ok=True)
    
    def test_audio_metrics_dataclass(self):
        """Test AudioMetrics dataclass"""
        metrics = AudioMetrics(
            lufs=-16.0,
            clipping_percent=0.1,
            dc_offset=-60.0,
            head_silence_ms=50.0,
            tail_silence_ms=100.0,
            duration_ms=2000.0,
            sample_rate=16000,
            channels=1,
            rms_db=-20.0,
            peak_db=-6.0
        )
        
        assert metrics.lufs == -16.0
        assert metrics.clipping_percent == 0.1
        assert metrics.dc_offset == -60.0
        assert metrics.head_silence_ms == 50.0
        assert metrics.tail_silence_ms == 100.0
        assert metrics.duration_ms == 2000.0
        assert metrics.sample_rate == 16000
        assert metrics.channels == 1
        assert metrics.rms_db == -20.0
        assert metrics.peak_db == -6.0
    
    def test_audio_metrics_extractor_init(self):
        """Test AudioMetricsExtractor initialization"""
        extractor = AudioMetricsExtractor(use_ffmpeg=True)
        assert extractor.use_ffmpeg is True
        
        extractor = AudioMetricsExtractor(use_ffmpeg=False)
        assert extractor.use_ffmpeg is False
    
    @pytest.mark.asyncio
    async def test_extract_metrics_with_ffmpeg_success(self, mock_wav_bytes):
        """Test metrics extraction with ffmpeg"""
        extractor = AudioMetricsExtractor(use_ffmpeg=True)
        
        with patch.object(extractor, '_check_ffmpeg_availability', return_value=True), \
             patch.object(extractor, '_extract_with_ffmpeg') as mock_ffmpeg:
            
            expected_metrics = AudioMetrics(
                lufs=-16.0,
                clipping_percent=0.1,
                dc_offset=-60.0,
                head_silence_ms=50.0,
                tail_silence_ms=100.0,
                duration_ms=2000.0,
                sample_rate=16000,
                channels=1
            )
            mock_ffmpeg.return_value = expected_metrics
            
            result = await extractor.extract_metrics(mock_wav_bytes)
            
            assert result.lufs == -16.0
            assert result.clipping_percent == 0.1
            assert result.duration_ms == 2000.0
            mock_ffmpeg.assert_called_once_with(mock_wav_bytes)
    
    @pytest.mark.asyncio
    async def test_extract_metrics_with_pyln_fallback(self, mock_wav_bytes):
        """Test metrics extraction with pyloudnorm fallback"""
        extractor = AudioMetricsExtractor(use_ffmpeg=False)
        
        with patch('services.metrics.audio_metrics.PYLN_AVAILABLE', True), \
             patch.object(extractor, '_extract_with_pyln') as mock_pyln:
            
            expected_metrics = AudioMetrics(
                lufs=-16.0,
                clipping_percent=0.1,
                dc_offset=-60.0,
                head_silence_ms=50.0,
                tail_silence_ms=100.0,
                duration_ms=2000.0,
                sample_rate=16000,
                channels=1
            )
            mock_pyln.return_value = expected_metrics
            
            result = await extractor.extract_metrics(mock_wav_bytes)
            
            assert result.lufs == -16.0
            assert result.clipping_percent == 0.1
            assert result.duration_ms == 2000.0
            mock_pyln.assert_called_once_with(mock_wav_bytes)
    
    @pytest.mark.asyncio
    async def test_extract_metrics_from_file(self, temp_audio_file):
        """Test metrics extraction from file path"""
        extractor = AudioMetricsExtractor(use_ffmpeg=False)
        
        with patch('services.metrics.audio_metrics.PYLN_AVAILABLE', True), \
             patch.object(extractor, '_extract_with_pyln') as mock_pyln:
            
            expected_metrics = AudioMetrics(
                lufs=-16.0,
                clipping_percent=0.1,
                duration_ms=2000.0,
                sample_rate=16000
            )
            mock_pyln.return_value = expected_metrics
            
            result = await extractor.extract_metrics(temp_audio_file)
            
            assert result.lufs == -16.0
            assert result.clipping_percent == 0.1
            mock_pyln.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_metrics_file_not_found(self):
        """Test metrics extraction with non-existent file"""
        extractor = AudioMetricsExtractor()
        
        result = await extractor.extract_metrics("nonexistent.wav")
        
        assert result.lufs is None
        assert result.clipping_percent == 0.0
        assert result.duration_ms == 0.0
    
    @pytest.mark.asyncio
    async def test_extract_metrics_exception_handling(self, mock_wav_bytes):
        """Test metrics extraction exception handling"""
        extractor = AudioMetricsExtractor()
        
        with patch.object(extractor, '_extract_with_ffmpeg', side_effect=Exception("Test error")):
            result = await extractor.extract_metrics(mock_wav_bytes)
            
            # Should return empty metrics on error
            assert result.lufs is None
            assert result.clipping_percent == 0.0
    
    def test_calculate_clipping_percent(self):
        """Test clipping percentage calculation"""
        extractor = AudioMetricsExtractor()
        
        # Test with no clipping
        audio_no_clip = np.array([0.5, -0.5, 0.3, -0.3])
        clip_percent = extractor._calculate_clipping_percent(audio_no_clip)
        assert clip_percent == 0.0
        
        # Test with clipping
        audio_with_clip = np.array([0.5, -0.5, 0.99, -0.99, 1.0, -1.0])  # 4 out of 6 samples clip
        clip_percent = extractor._calculate_clipping_percent(audio_with_clip)
        assert abs(clip_percent - 66.67) < 0.01  # 4 out of 6 samples clip (66.67%)
    
    def test_calculate_dc_offset(self):
        """Test DC offset calculation"""
        extractor = AudioMetricsExtractor()
        
        # Test with no DC offset
        audio_no_dc = np.array([0.5, -0.5, 0.3, -0.3])
        dc_offset = extractor._calculate_dc_offset(audio_no_dc)
        assert dc_offset == -np.inf
        
        # Test with DC offset
        audio_with_dc = np.array([0.6, 0.4, 0.5, 0.5])  # DC = 0.5
        dc_offset = extractor._calculate_dc_offset(audio_with_dc)
        assert abs(dc_offset - 20 * np.log10(0.5)) < 0.001
    
    def test_calculate_silence(self):
        """Test silence calculation"""
        extractor = AudioMetricsExtractor()
        
        # Create audio with head and tail silence
        sample_rate = 16000
        audio = np.zeros(16000)  # 1 second of silence
        audio[1000:15000] = 0.1  # Add some signal in the middle
        
        head_silence, tail_silence = extractor._calculate_silence(audio, sample_rate)
        
        assert head_silence > 0  # Should detect head silence
        assert tail_silence > 0  # Should detect tail silence
    
    @pytest.mark.asyncio
    async def test_convenience_function(self, mock_wav_bytes):
        """Test convenience function"""
        with patch('services.metrics.audio_metrics.AudioMetricsExtractor') as mock_class:
            mock_extractor = Mock()
            mock_extractor.extract_metrics = AsyncMock(return_value=AudioMetrics(lufs=-16.0))
            mock_class.return_value = mock_extractor
            
            result = await extract_audio_metrics(mock_wav_bytes, use_ffmpeg=True)
            
            assert result.lufs == -16.0
            mock_class.assert_called_once_with(use_ffmpeg=True)
            mock_extractor.extract_metrics.assert_called_once_with(mock_wav_bytes)
    
    @pytest.mark.asyncio
    async def test_ffmpeg_loudnorm_parsing(self):
        """Test ffmpeg loudnorm output parsing"""
        extractor = AudioMetricsExtractor()
        
        # Mock ffmpeg stderr output with loudnorm data
        stderr_output = """
        [loudnorm @ 0x123456789] Input Integrated:    -16.0 LUFS
        [loudnorm @ 0x123456789] Input True Peak:    -1.5 dBTP
        [loudnorm @ 0x123456789] Input LRA:          11.0 LU
        {"input":{"i":"-16.0","tp":"-1.5","lra":"11.0","thresh":"-26.0"},"output":{"i":"-16.0","tp":"-1.5","lra":"11.0","thresh":"-26.0"}}
        """
        
        metrics = extractor._parse_ffmpeg_loudnorm(stderr_output)
        
        assert metrics.lufs == -16.0
        assert metrics.peak_db == -1.5
        assert metrics.rms_db == 11.0
    
    @pytest.mark.asyncio
    async def test_ffmpeg_loudnorm_parsing_invalid_json(self):
        """Test ffmpeg loudnorm parsing with invalid JSON"""
        extractor = AudioMetricsExtractor()
        
        stderr_output = "Invalid output without JSON"
        
        metrics = extractor._parse_ffmpeg_loudnorm(stderr_output)
        
        # Should return empty metrics on parsing failure
        assert metrics.lufs is None
        assert metrics.peak_db is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
