#!/usr/bin/env python3
"""
VoiceStudio Audio Metrics Module
Extracts objective audio quality metrics using ffmpeg loudnorm (fallback pyloudnorm)
"""

import asyncio
import io
import logging
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Union
import numpy as np

# Optional imports with fallbacks
try:
    import pyloudnorm as pyln
    PYLN_AVAILABLE = True
except ImportError:
    PYLN_AVAILABLE = False
    logging.warning("pyloudnorm not available. Install with: pip install pyloudnorm")

logger = logging.getLogger(__name__)

@dataclass
class AudioMetrics:
    """Audio quality metrics"""
    lufs: Optional[float] = None  # Loudness Units relative to Full Scale
    clipping_percent: float = 0.0  # Percentage of samples that clip
    dc_offset: float = 0.0  # DC offset in dB
    head_silence_ms: float = 0.0  # Silence at start in milliseconds
    tail_silence_ms: float = 0.0  # Silence at end in milliseconds
    duration_ms: float = 0.0  # Total duration in milliseconds
    sample_rate: int = 0  # Sample rate
    channels: int = 0  # Number of channels
    rms_db: Optional[float] = None  # RMS level in dB
    peak_db: Optional[float] = None  # Peak level in dB

class AudioMetricsExtractor:
    """Extracts objective audio quality metrics"""
    
    def __init__(self, use_ffmpeg: bool = True):
        self.use_ffmpeg = use_ffmpeg
        self._check_ffmpeg_availability()
    
    def _check_ffmpeg_availability(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("ffmpeg not available, falling back to pyloudnorm")
            self.use_ffmpeg = False
            return False
    
    async def extract_metrics(self, audio_data: Union[bytes, str, Path]) -> AudioMetrics:
        """
        Extract audio metrics from audio data
        """
        try:
            if isinstance(audio_data, (str, Path)):
                # Load from file
                audio_path = Path(audio_data)
                if not audio_path.exists():
                    logger.error(f"Audio file not found: {audio_path}")
                    return AudioMetrics()
                
                # Load audio data
                with open(audio_path, 'rb') as f:
                    audio_bytes = f.read()
            else:
                audio_bytes = audio_data
            
            # Extract metrics using preferred method
            if self.use_ffmpeg:
                metrics = await self._extract_with_ffmpeg(audio_bytes)
            else:
                metrics = await self._extract_with_pyln(audio_bytes)
            
            logger.info(f"Extracted audio metrics: LUFS={metrics.lufs}, clipping={metrics.clipping_percent:.2f}%")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to extract audio metrics: {e}")
            return AudioMetrics()
    
    async def _extract_with_ffmpeg(self, audio_bytes: bytes) -> AudioMetrics:
        """Extract metrics using ffmpeg loudnorm"""
        try:
            # Write audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            try:
                # Run ffmpeg loudnorm analysis
                cmd = [
                    "ffmpeg", "-i", temp_path,
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
                    "-f", "null", "-"
                ]
                
                result = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await result.communicate()
                
                if result.returncode != 0:
                    logger.warning(f"ffmpeg loudnorm failed: {stderr.decode()}")
                    return await self._extract_with_pyln(audio_bytes)
                
                # Parse ffmpeg output for loudnorm data
                stderr_str = stderr.decode()
                metrics = self._parse_ffmpeg_loudnorm(stderr_str)
                
                # Get additional metrics
                additional_metrics = await self._get_additional_ffmpeg_metrics(temp_path)
                metrics.update(additional_metrics)
                
                return metrics
                
            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.warning(f"ffmpeg extraction failed: {e}, falling back to pyloudnorm")
            return await self._extract_with_pyln(audio_bytes)
    
    def _parse_ffmpeg_loudnorm(self, stderr_output: str) -> AudioMetrics:
        """Parse ffmpeg loudnorm JSON output"""
        metrics = AudioMetrics()
        
        try:
            # Extract JSON from ffmpeg output
            lines = stderr_output.split('\n')
            json_start = False
            json_lines = []
            
            for line in lines:
                if '"input"' in line and '"output"' in line:
                    json_start = True
                if json_start:
                    json_lines.append(line)
                    if line.strip().endswith('}'):
                        break
            
            if json_lines:
                import json
                json_str = '\n'.join(json_lines)
                data = json.loads(json_str)
                
                # Extract loudnorm data
                if 'input' in data:
                    input_data = data['input']
                    metrics.lufs = float(input_data.get('i', 0))
                    metrics.rms_db = float(input_data.get('lra', 0))
                    metrics.peak_db = float(input_data.get('tp', 0))
                
        except Exception as e:
            logger.warning(f"Failed to parse ffmpeg loudnorm output: {e}")
        
        return metrics
    
    async def _get_additional_ffmpeg_metrics(self, audio_path: str) -> AudioMetrics:
        """Get additional metrics using ffmpeg"""
        metrics = AudioMetrics()
        
        try:
            # Get audio info
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", audio_path
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                import json
                data = json.loads(stdout.decode())
                
                if 'streams' in data and data['streams']:
                    stream = data['streams'][0]
                    metrics.sample_rate = int(stream.get('sample_rate', 0))
                    metrics.channels = int(stream.get('channels', 0))
                
                if 'format' in data:
                    format_data = data['format']
                    duration = float(format_data.get('duration', 0))
                    metrics.duration_ms = duration * 1000
            
        except Exception as e:
            logger.warning(f"Failed to get additional ffmpeg metrics: {e}")
        
        return metrics
    
    async def _extract_with_pyln(self, audio_bytes: bytes) -> AudioMetrics:
        """Extract metrics using pyloudnorm fallback"""
        if not PYLN_AVAILABLE:
            logger.error("pyloudnorm not available for fallback")
            return AudioMetrics()
        
        try:
            # Load audio using soundfile
            import soundfile as sf
            
            # Load from bytes
            audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
            
            metrics = AudioMetrics()
            metrics.sample_rate = sample_rate
            metrics.channels = 1 if audio_data.ndim == 1 else audio_data.shape[1]
            metrics.duration_ms = len(audio_data) / sample_rate * 1000
            
            # Calculate basic metrics
            metrics.clipping_percent = self._calculate_clipping_percent(audio_data)
            metrics.dc_offset = self._calculate_dc_offset(audio_data)
            metrics.head_silence_ms, metrics.tail_silence_ms = self._calculate_silence(audio_data, sample_rate)
            
            # Calculate LUFS using pyloudnorm
            try:
                meter = pyln.Meter(sample_rate)
                metrics.lufs = meter.integrated_loudness(audio_data)
            except Exception as e:
                logger.warning(f"pyloudnorm LUFS calculation failed: {e}")
            
            # Calculate RMS and peak
            rms = np.sqrt(np.mean(audio_data**2))
            metrics.rms_db = 20 * np.log10(rms) if rms > 0 else -np.inf
            metrics.peak_db = 20 * np.log10(np.max(np.abs(audio_data)))
            
            return metrics
            
        except Exception as e:
            logger.error(f"pyloudnorm extraction failed: {e}")
            return AudioMetrics()
    
    def _calculate_clipping_percent(self, audio_data: np.ndarray) -> float:
        """Calculate percentage of clipped samples"""
        clipped_samples = np.sum(np.abs(audio_data) >= 0.99)
        total_samples = audio_data.size
        return (clipped_samples / total_samples) * 100 if total_samples > 0 else 0.0
    
    def _calculate_dc_offset(self, audio_data: np.ndarray) -> float:
        """Calculate DC offset in dB"""
        dc_value = np.mean(audio_data)
        return 20 * np.log10(abs(dc_value)) if dc_value != 0 else -np.inf
    
    def _calculate_silence(self, audio_data: np.ndarray, sample_rate: int) -> tuple[float, float]:
        """Calculate head and tail silence in milliseconds"""
        threshold = 0.01  # Silence threshold
        
        # Find head silence
        head_silence_samples = 0
        for sample in audio_data:
            if abs(sample) > threshold:
                break
            head_silence_samples += 1
        
        # Find tail silence
        tail_silence_samples = 0
        for sample in reversed(audio_data):
            if abs(sample) > threshold:
                break
            tail_silence_samples += 1
        
        head_silence_ms = (head_silence_samples / sample_rate) * 1000
        tail_silence_ms = (tail_silence_samples / sample_rate) * 1000
        
        return head_silence_ms, tail_silence_ms

# Convenience function
async def extract_audio_metrics(audio_data: Union[bytes, str, Path], use_ffmpeg: bool = True) -> AudioMetrics:
    """
    Convenience function to extract audio metrics
    """
    extractor = AudioMetricsExtractor(use_ffmpeg=use_ffmpeg)
    return await extractor.extract_metrics(audio_data)

# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with a sample audio file
    test_file = "test_audio.wav"
    if Path(test_file).exists():
        print(f"Testing audio metrics extraction with {test_file}...")
        
        async def test():
            metrics = await extract_audio_metrics(test_file)
            print(f"📊 Audio Metrics:")
            print(f"   LUFS: {metrics.lufs}")
            print(f"   Clipping: {metrics.clipping_percent:.2f}%")
            print(f"   DC Offset: {metrics.dc_offset:.2f} dB")
            print(f"   Head Silence: {metrics.head_silence_ms:.1f} ms")
            print(f"   Tail Silence: {metrics.tail_silence_ms:.1f} ms")
            print(f"   Duration: {metrics.duration_ms:.1f} ms")
            print(f"   Sample Rate: {metrics.sample_rate} Hz")
            print(f"   Channels: {metrics.channels}")
        
        asyncio.run(test())
    else:
        print(f"ℹ️  Test file {test_file} not found. Place an audio file to test metrics extraction.")
