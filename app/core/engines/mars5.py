"""
MARS5 Engine Integration.

Task 4.4.4: State-of-the-art TTS with prosody control.
High-quality, expressive speech synthesis.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

from app.core.engines.base import BaseEngine

logger = logging.getLogger(__name__)


@dataclass
class MARS5Config:
    """Configuration for MARS5."""
    model_size: str = "english"  # english, multilingual
    use_gpu: bool = True
    sample_rate: int = 24000
    # Generation params
    temperature: float = 0.7
    top_k: int = 100
    rep_penalty: float = 1.1


class MARS5Engine(BaseEngine):
    """
    MARS5 state-of-the-art TTS engine.
    
    Features:
    - Deep prosody modeling
    - Few-shot voice cloning
    - High-quality synthesis
    - Emotion and style control
    
    Reference: https://github.com/Camb-ai/MARS5-TTS
    """
    
    ENGINE_ID = "mars5"
    ENGINE_NAME = "MARS5"
    SUPPORTED_LANGUAGES = ["en"]
    
    def __init__(self, config: Optional[MARS5Config] = None):
        super().__init__()
        self.config = config or MARS5Config()
        self._model = None
        self._loaded = False
    
    def initialize(self) -> bool:
        """Sync wrapper for EngineProtocol compliance."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self._async_initialize())
        finally:
            loop.close()
    
    def cleanup(self) -> None:
        """Sync wrapper for EngineProtocol compliance."""
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.shutdown())
        finally:
            loop.close()
    
    async def _async_initialize(self) -> bool:
        """Initialize MARS5."""
        try:
            logger.info("Loading MARS5 engine...")
            
            try:
                import torch
                from mars5_tts import Mars5TTS
                
                device = "cuda" if self.config.use_gpu and torch.cuda.is_available() else "cpu"
                
                self._model = Mars5TTS.from_pretrained(
                    f"Camb-ai/mars5-{self.config.model_size}"
                ).to(device)
                
                self._device = device
                
                logger.info(f"MARS5 loaded on {device}")
                
            except ImportError:
                logger.warning("mars5-tts not installed, using placeholder")
                self._model = None
            
            self._loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load MARS5: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown and cleanup."""
        self._model = None
        self._loaded = False
        
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            logger.debug("torch not available for CUDA cache cleanup")
    
    async def synthesize(
        self,
        text: str,
        reference_audio: Optional[np.ndarray] = None,
        reference_transcript: Optional[str] = None,
        reference_sample_rate: int = 24000,
    ) -> np.ndarray:
        """
        Synthesize speech with MARS5.
        
        Args:
            text: Text to synthesize
            reference_audio: Optional reference for voice cloning
            reference_transcript: Transcript of reference audio
            reference_sample_rate: Reference sample rate
            
        Returns:
            Synthesized audio
        """
        if not self._loaded:
            await self.initialize()
        
        if self._model is not None:
            return await self._synthesize_real(
                text, reference_audio, reference_transcript, reference_sample_rate
            )
        
        # Graceful degradation: Generate silence when mars5-tts library is not installed.
        # To enable full functionality, install mars5-tts: pip install mars5-tts
        # See: https://github.com/Camb-ai/MARS5-TTS for installation instructions.
        logger.warning("MARS5 model not loaded - returning silence. Install mars5-tts for actual synthesis.")
        duration = len(text) * 0.06
        samples = int(duration * self.config.sample_rate)
        return np.zeros(samples, dtype=np.float32)
    
    async def _synthesize_real(
        self,
        text: str,
        reference_audio: Optional[np.ndarray],
        reference_transcript: Optional[str],
        reference_sample_rate: int,
    ) -> np.ndarray:
        """Real synthesis using MARS5."""
        import torch
        
        # Prepare reference
        ref_wav = None
        ref_text = None
        
        if reference_audio is not None:
            ref_wav = torch.from_numpy(reference_audio).float().to(self._device)
            if reference_sample_rate != self.config.sample_rate:
                import torchaudio
                ref_wav = torchaudio.functional.resample(
                    ref_wav, reference_sample_rate, self.config.sample_rate
                )
            ref_text = reference_transcript or ""
        
        # Generate
        with torch.no_grad():
            audio, _ = self._model.tts(
                text,
                ref_wav=ref_wav,
                ref_transcript=ref_text,
                temperature=self.config.temperature,
                top_k=self.config.top_k,
                rep_penalty=self.config.rep_penalty,
            )
        
        return audio.cpu().numpy()
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "voice_cloning": True,
            "few_shot": True,
            "languages": self.SUPPORTED_LANGUAGES,
            "sample_rate": self.config.sample_rate,
            "prosody_control": True,
        }
