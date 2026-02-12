"""
Fish Speech Engine Integration.

Task 4.4.1: Latest voice cloning model integration.
High-quality, fast voice cloning with minimal reference audio.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from app.core.engines.base import EngineProtocol

logger = logging.getLogger(__name__)


@dataclass
class FishSpeechConfig:
    """Configuration for Fish Speech engine."""
    model_path: Optional[str] = None
    use_gpu: bool = True
    sample_rate: int = 44100
    # Fish Speech specific
    temperature: float = 0.7
    top_p: float = 0.9
    repetition_penalty: float = 1.2
    max_length: int = 2048


class FishSpeechEngine(EngineProtocol):
    """
    Fish Speech voice cloning engine.
    
    Features:
    - Zero-shot voice cloning
    - Multilingual support (Chinese, English, Japanese, Korean)
    - Fast inference
    - High-quality output at 44.1kHz
    
    Reference: https://github.com/fishaudio/fish-speech
    """
    
    ENGINE_ID = "fish_speech"
    ENGINE_NAME = "Fish Speech"
    SUPPORTED_LANGUAGES = ["en", "zh", "ja", "ko"]
    
    def __init__(self, config: Optional[FishSpeechConfig] = None):
        super().__init__()
        self.config = config or FishSpeechConfig()
        self._model = None
        self._vocoder = None
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
        """Initialize Fish Speech models."""
        try:
            logger.info("Loading Fish Speech engine...")
            
            # Try loading Fish Speech
            try:
                from fish_speech.models import VQGANModel, LLaMAModel
                import torch
                
                device = "cuda" if self.config.use_gpu and torch.cuda.is_available() else "cpu"
                
                # Load VQGAN (semantic encoder/decoder)
                vqgan = VQGANModel.from_pretrained("fishaudio/fish-speech-1.2")
                vqgan.to(device)
                
                # Load LLaMA (text-to-semantic)
                llama = LLaMAModel.from_pretrained("fishaudio/fish-speech-1.2-sft")
                llama.to(device)
                
                self._model = {
                    "vqgan": vqgan,
                    "llama": llama,
                    "device": device,
                }
                
                logger.info(f"Fish Speech loaded on {device}")
                
            except ImportError:
                logger.warning("fish-speech not installed, using placeholder")
                self._model = {"placeholder": True}
            
            self._loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Fish Speech: {e}")
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
        
        logger.info("Fish Speech engine shutdown")
    
    async def synthesize(
        self,
        text: str,
        reference_audio: Optional[np.ndarray] = None,
        reference_sample_rate: int = 44100,
        language: str = "en",
    ) -> np.ndarray:
        """
        Synthesize speech with optional voice cloning.
        
        Args:
            text: Text to synthesize
            reference_audio: Optional reference for voice cloning
            reference_sample_rate: Reference audio sample rate
            language: Language code
            
        Returns:
            Synthesized audio at 44.1kHz
        """
        if not self._loaded:
            await self.initialize()
        
        if self._model and not self._model.get("placeholder"):
            return await self._synthesize_real(
                text, reference_audio, reference_sample_rate, language
            )
        
        # Graceful degradation: Generate silence when fish-speech library is not installed.
        # To enable full functionality, install fish-speech: pip install fish-speech
        # See: https://github.com/fishaudio/fish-speech for installation instructions.
        logger.warning("Fish Speech model not loaded - returning silence. Install fish-speech for actual synthesis.")
        duration = len(text) * 0.06  # ~60ms per character
        samples = int(duration * self.config.sample_rate)
        return np.zeros(samples, dtype=np.float32)
    
    async def _synthesize_real(
        self,
        text: str,
        reference_audio: Optional[np.ndarray],
        reference_sample_rate: int,
        language: str,
    ) -> np.ndarray:
        """Real synthesis using Fish Speech."""
        import torch
        
        vqgan = self._model["vqgan"]
        llama = self._model["llama"]
        device = self._model["device"]
        
        # Extract speaker embedding from reference
        speaker_codes = None
        if reference_audio is not None:
            # Encode reference to semantic tokens
            ref_tensor = torch.from_numpy(reference_audio).float().to(device)
            speaker_codes = vqgan.encode(ref_tensor.unsqueeze(0))
        
        # Generate semantic tokens from text
        tokens = llama.generate(
            text,
            speaker_codes=speaker_codes,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            max_length=self.config.max_length,
        )
        
        # Decode to audio
        with torch.no_grad():
            audio = vqgan.decode(tokens)
        
        return audio.squeeze().cpu().numpy()
    
    async def clone_voice(
        self,
        reference_audio: np.ndarray,
        sample_rate: int,
    ) -> Dict[str, Any]:
        """
        Create voice embedding from reference audio.
        
        Args:
            reference_audio: Reference audio samples
            sample_rate: Reference sample rate
            
        Returns:
            Voice profile dictionary
        """
        if not self._loaded:
            await self.initialize()
        
        if self._model and not self._model.get("placeholder"):
            import torch
            
            vqgan = self._model["vqgan"]
            device = self._model["device"]
            
            # Resample if needed
            if sample_rate != self.config.sample_rate:
                try:
                    import librosa
                    reference_audio = librosa.resample(
                        reference_audio,
                        orig_sr=sample_rate,
                        target_sr=self.config.sample_rate,
                    )
                except ImportError:
                    logger.debug("librosa not available for resampling")
            
            ref_tensor = torch.from_numpy(reference_audio).float().to(device)
            codes = vqgan.encode(ref_tensor.unsqueeze(0))
            
            return {
                "engine": "fish_speech",
                "codes": codes.cpu().numpy(),
                "sample_rate": self.config.sample_rate,
            }
        
        return {"engine": "fish_speech", "placeholder": True}
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "voice_cloning": True,
            "zero_shot": True,
            "languages": self.SUPPORTED_LANGUAGES,
            "sample_rate": self.config.sample_rate,
            "streaming": False,
        }
