"""
Output Chain Processor for VoiceStudio Voice Engine Router
"""
from __future__ import annotations
import tempfile
import subprocess
from pathlib import Path
from typing import Optional

from services.audio.output_chain import OutputChain
from services.audio.metrics import which_path

def _run_ffmpeg(cmd: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run ffmpeg command with timeout"""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)

def process_output_chain(wav_path: Path, chain: OutputChain) -> Path:
    """
    Process audio through output chain: trim → fade → dither → write
    Returns path to processed audio file
    """
    if not chain.enabled:
        return wav_path
    
    ffmpeg = which_path("ffmpeg")
    if not ffmpeg:
        raise FileNotFoundError("ffmpeg not found for output chain processing")
    
    # Build filter chain
    filters = []
    
    # 1. Trim silence (if specified)
    if chain.trim_ms > 0:
        trim_sec = chain.trim_ms / 1000.0
        filters.append(f"atrim=start={trim_sec}")
    
    # 2. Fade in/out (if specified)
    if chain.fade_ms > 0:
        fade_sec = chain.fade_ms / 1000.0
        filters.append(f"afade=t=in:st=0:d={fade_sec}")
        filters.append(f"afade=t=out:st=-{fade_sec}:d={fade_sec}")
    
    # 3. Dithering (if enabled)
    if chain.dither:
        filters.append("adither")
    
    # 4. EBU R128 normalization (if enabled)
    if chain.normalize_r128:
        filters.append("loudnorm=I=-23:TP=-2:LRA=11")
    
    # 5. Existing effects
    if chain.deess:
        filters.append("highpass=f=5000,lowpass=f=10000")
    
    if chain.noise_reduction:
        filters.append("afftdn")
    
    if chain.target_lufs is not None:
        filters.append(f"loudnorm=I={chain.target_lufs}")
    
    # Create output file
    output_path = wav_path.parent / f"processed_{wav_path.name}"
    
    # Build ffmpeg command
    filter_chain = ",".join(filters) if filters else "anull"
    
    cmd = f'"{ffmpeg}" -hide_banner -nostats -i "{wav_path}" -af "{filter_chain}" -y "{output_path}"'
    
    try:
        result = _run_ffmpeg(cmd)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg processing failed: {result.stderr}")
        
        return output_path
    except Exception as e:
        # Clean up output file on error
        try:
            output_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise e

def process_audio_bytes_with_chain(audio_bytes: bytes, chain: Optional[OutputChain]) -> bytes:
    """
    Process audio bytes through output chain
    Returns processed audio bytes
    """
    if not chain or not chain.enabled:
        return audio_bytes
    
    # Write input to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as input_file:
        input_file.write(audio_bytes)
        input_path = Path(input_file.name)
    
    try:
        # Process through chain
        output_path = process_output_chain(input_path, chain)
        
        # Read processed audio
        with open(output_path, "rb") as f:
            processed_bytes = f.read()
        
        return processed_bytes
    
    finally:
        # Clean up temp files
        try:
            input_path.unlink(missing_ok=True)
            if 'output_path' in locals():
                output_path.unlink(missing_ok=True)
        except Exception:
            pass
