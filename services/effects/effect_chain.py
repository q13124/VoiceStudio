"""
VoiceStudio — Output Effect Chain (optional)
"""
from __future__ import annotations
import io, numpy as np
from dataclasses import dataclass
from typing import Optional

try: 
    import soundfile as sf
except Exception: 
    sf=None

try: 
    import pyloudnorm as pyln
except Exception: 
    pyln=None

try: 
    import noisereduce as nr
except Exception: 
    nr=None

@dataclass
class ChainCfg:
    enabled: bool = False
    target_lufs: Optional[float] = None
    deess: bool = False
    noise_reduction: bool = False

def _read_wav(data: bytes):
    if sf is None: return None
    buf=io.BytesIO(data); y,sr=sf.read(buf, always_2d=False); return y,sr

def _write_wav(y: np.ndarray, sr: int) -> bytes:
    if sf is None: return b""
    buf=io.BytesIO(); sf.write(buf, y, sr, format="WAV", subtype="PCM_16"); return buf.getvalue()

def _lufs_normalize(y: np.ndarray, sr: int, target_lufs: float) -> np.ndarray:
    if pyln is None: return y
    meter=pyln.Meter(sr); loud=meter.integrated_loudness(y); return pyln.normalize.loudness(y, loud, target_lufs)

def _simple_deess(y: np.ndarray, sr: int) -> np.ndarray:
    try:
        from scipy.signal import butter, sosfilt
    except Exception: return y
    low=5000/(sr/2); high=10000/(sr/2); sos=butter(4,[low,high],btype='band',output='sos'); hf=sosfilt(sos,y); return y-0.3*hf

def _denoise(y: np.ndarray, sr: int) -> np.ndarray:
    if nr is None: return y
    return nr.reduce_noise(y=y, sr=sr)

def process_wav_bytes(data: bytes, cfg: ChainCfg) -> bytes:
    if not cfg.enabled or sf is None: return data
    try:
        read=_read_wav(data)
        if read is None: return data
        y,sr=read; y=y.astype('float32') if hasattr(y,'astype') else y
        
        if cfg.noise_reduction: y=_denoise(y,sr)
        if cfg.deess: y=_simple_deess(y,sr)
        if cfg.target_lufs is not None: y=_lufs_normalize(y,sr,cfg.target_lufs)
        
        return _write_wav(y,sr)
    except Exception:
        return data