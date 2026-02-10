"""
OpenVoice v2 Engine Integration.

Task 4.4.2: Cross-lingual voice cloning.
Clone voice across different languages while preserving speaker identity.
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
class OpenVoiceV2Config:
    """Configuration for OpenVoice v2."""
    use_gpu: bool = True
    sample_rate: int = 24000
    # Voice conversion
    tau: float = 0.3  # Timbre conversion strength


class OpenVoiceV2Engine(BaseEngine):
    """
    OpenVoice v2 cross-lingual voice cloning.
    
    Features:
    - Cross-lingual cloning (synthesize in any language)
    - Flexible voice style control
    - Zero-shot voice cloning
    - Emotion and accent preservation
    
    Reference: https://github.com/myshell-ai/OpenVoice
    """
    
    ENGINE_ID = "openvoice_v2"
    ENGINE_NAME = "OpenVoice v2"
    SUPPORTED_LANGUAGES = ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "ja", "ko", "hu"]
    
    def __init__(self, config: Optional[OpenVoiceV2Config] = None):
        super().__init__()
        self.config = config or OpenVoiceV2Config()
        self._base_speaker = None
        self._tone_converter = None
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
        """Initialize OpenVoice v2 models."""
        try:
            logger.info("Loading OpenVoice v2 engine...")
            
            try:
                from openvoice import se_extractor
                from openvoice.api import BaseSpeakerTTS, ToneColorConverter
                import torch
                
                device = "cuda" if self.config.use_gpu and torch.cuda.is_available() else "cpu"
                
                # Load base speaker TTS
                self._base_speaker = BaseSpeakerTTS(
                    "checkpoints_v2/base_speakers/EN",
                    device=device,
                )
                
                # Load tone color converter
                self._tone_converter = ToneColorConverter(
                    "checkpoints_v2/converter",
                    device=device,
                )
                
                self._se_extractor = se_extractor
                
                logger.info(f"OpenVoice v2 loaded on {device}")
                
            except ImportError:
                logger.warning("openvoice not installed, using placeholder")
                self._base_speaker = None
                self._tone_converter = None
            
            self._loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load OpenVoice v2: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown and cleanup."""
        self._base_speaker = None
        self._tone_converter = None
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
        reference_sample_rate: int = 24000,
        language: str = "en",
        speed: float = 1.0,
    ) -> np.ndarray:
        """
        Synthesize speech with cross-lingual voice cloning.
        
        Args:
            text: Text to synthesize
            reference_audio: Reference audio for voice cloning
            reference_sample_rate: Reference sample rate
            language: Target language
            speed: Speaking speed
            
        Returns:
            Synthesized audio
        """
        if not self._loaded:
            await self.initialize()
        
        if self._base_speaker is not None and self._tone_converter is not None:
            return await self._synthesize_real(
                text, reference_audio, reference_sample_rate, language, speed
            )
        
        # Graceful degradation: Generate silence when openvoice library is not installed.
        # To enable full functionality, install openvoice: pip install openvoice
        # See: https://github.com/myshell-ai/OpenVoice for installation instructions.
        logger.warning("OpenVoice V2 model not loaded - returning silence. Install openvoice for actual synthesis.")
        duration = len(text) * 0.06
        samples = int(duration * self.config.sample_rate)
        return np.zeros(samples, dtype=np.float32)
    
    async def _synthesize_real(
        self,
        text: str,
        reference_audio: Optional[np.ndarray],
        reference_sample_rate: int,
        language: str,
        speed: float,
    ) -> np.ndarray:
        """Real synthesis using OpenVoice v2."""
        import tempfile
        import soundfile as sf
        
        # Step 1: Generate base speech
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            base_path = tmp.name
        
        self._base_speaker.tts(
            text,
            base_path,
            speaker=language.upper(),
            language=language,
            speed=speed,
        )
        
        # Step 2: Apply voice cloning if reference provided
        if reference_audio is not None:
            # Save reference for SE extraction
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                ref_path = tmp.name
                sf.write(ref_path, reference_audio, reference_sample_rate)
            
            # Extract speaker embedding
            target_se, _ = self._se_extractor.get_se(ref_path)
            
            # Convert tone
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                output_path = tmp.name
            
            self._tone_converter.convert(
                base_path,
                target_se,
                output_path,
                tau=self.config.tau,
            )
            
            audio, sr = sf.read(output_path)
        else:
            audio, sr = sf.read(base_path)
        
        return audio.astype(np.float32)
    
    async def extract_speaker_embedding(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """Extract speaker embedding for voice cloning."""
        if self._se_extractor is not None:
            import tempfile
            import soundfile as sf
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                sf.write(tmp.name, audio, sample_rate)
                se, _ = self._se_extractor.get_se(tmp.name)
                return se.cpu().numpy()
        
        return np.zeros(256)
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "voice_cloning": True,
            "cross_lingual": True,
            "languages": self.SUPPORTED_LANGUAGES,
            "sample_rate": self.config.sample_rate,
            "style_control": True,
        }
