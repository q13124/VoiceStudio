#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Coqui TTS Integration Service
Advanced Text-to-Speech integration using Coqui TTS
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import numpy as np
import torch
import torchaudio
import soundfile as sf
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from TTS.api import TTS
    from TTS.utils.manage import ModelManager

    # Fix PyTorch weights_only issue for Coqui TTS
    import torch.serialization
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
    from TTS.config.shared_configs import BaseDatasetConfig

    # Add all required Coqui TTS classes to safe globals
    torch.serialization.add_safe_globals(
        [XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig]
    )
    COQUI_AVAILABLE = True
except ImportError:
    logger.warning("Coqui TTS not available. Install with: pip install TTS")
    COQUI_AVAILABLE = False


@dataclass
class CoquiConfig:
    """Coqui TTS configuration parameters"""

    model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"
    vocoder_name: str = "vocoder_models/en/ljspeech/multiband-melgan"
    language: str = "en"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    use_cuda: bool = torch.cuda.is_available()
    output_format: str = "wav"
    sample_rate: int = 22050


class CoquiTTSService:
    """Coqui TTS Service for VoiceStudio"""

    def __init__(self, config: CoquiConfig):
        self.config = config
        self.tts = None
        self.model_manager = None
        self.is_loaded = False

        if not COQUI_AVAILABLE:
            logger.error("Coqui TTS is not available")
            return

    async def load_model(self, model_name: str = None, vocoder_name: str = None):
        """Load Coqui TTS model"""
        try:
            if not COQUI_AVAILABLE:
                return False

            logger.info("Initializing Coqui TTS...")

            # Initialize TTS
            self.tts = TTS(model_name or self.config.model_name)

            # Load vocoder if specified
            if vocoder_name or self.config.vocoder_name:
                logger.info(
                    f"Loading vocoder: {vocoder_name or self.config.vocoder_name}"
                )
                self.tts.to(self.config.device)

            self.is_loaded = True
            logger.info("Coqui TTS model loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load Coqui TTS model: {e}")
            return False

    async def synthesize(
        self,
        text: str,
        output_path: str = None,
        speaker_wav: str = None,
        language: str = None,
    ) -> Optional[np.ndarray]:
        """Synthesize speech from text"""
        try:
            if not self.is_loaded:
                logger.error("Coqui TTS model not loaded")
                return None

            logger.info(f"Synthesizing: '{text[:50]}...'")

            # Synthesize speech
            if output_path:
                self.tts.tts_to_file(text=text, file_path=output_path)
                logger.info(f"Speech saved to: {output_path}")
                return None
            else:
                # Return audio data
                wav = self.tts.tts(text=text)
                logger.info("Speech synthesis completed")
                return wav

        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return None

    async def clone_voice(
        self, text: str, speaker_wav: str, output_path: str = None
    ) -> Optional[np.ndarray]:
        """Clone voice using speaker reference"""
        try:
            if not self.is_loaded:
                logger.error("Coqui TTS model not loaded")
                return None

            logger.info(f"Cloning voice for text: '{text[:50]}...'")

            # Clone voice
            if output_path:
                self.tts.tts_to_file(
                    text=text, file_path=output_path, speaker_wav=speaker_wav
                )
                logger.info(f"Cloned voice saved to: {output_path}")
                return None
            else:
                wav = self.tts.tts(text=text, speaker_wav=speaker_wav)
                logger.info("Voice cloning completed")
                return wav

        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return None

    def get_available_models(self) -> List[str]:
        """Get list of available TTS models"""
        try:
            if not COQUI_AVAILABLE:
                return []

            if self.model_manager is None:
                self.model_manager = ModelManager()

            return self.model_manager.list_models()

        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []

    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        try:
            if not self.is_loaded or not COQUI_AVAILABLE:
                return []

            return self.tts.languages

        except Exception as e:
            logger.error(f"Failed to get available languages: {e}")
            return []


class CoquiTTSManager:
    """Coqui TTS Manager for VoiceStudio integration"""

    def __init__(self):
        self.services: Dict[str, CoquiTTSService] = {}
        self.default_config = CoquiConfig()

    async def create_service(
        self,
        service_id: str,
        model_name: str = None,
        vocoder_name: str = None,
        config: Optional[CoquiConfig] = None,
    ) -> bool:
        """Create a new Coqui TTS service"""
        try:
            if not COQUI_AVAILABLE:
                logger.error("Coqui TTS is not available")
                return False

            if config is None:
                config = self.default_config

            service = CoquiTTSService(config)
            success = await service.load_model(model_name, vocoder_name)

            if success:
                self.services[service_id] = service
                logger.info(f"Coqui TTS service '{service_id}' created successfully")
                return True
            else:
                logger.error(f"Failed to create Coqui TTS service '{service_id}'")
                return False

        except Exception as e:
            logger.error(f"Error creating Coqui TTS service: {e}")
            return False

    async def synthesize(
        self,
        service_id: str,
        text: str,
        output_path: str = None,
        speaker_wav: str = None,
    ) -> Optional[np.ndarray]:
        """Synthesize speech using specified TTS service"""
        if service_id not in self.services:
            logger.error(f"Coqui TTS service '{service_id}' not found")
            return None

        return await self.services[service_id].synthesize(
            text, output_path, speaker_wav
        )

    async def clone_voice(
        self, service_id: str, text: str, speaker_wav: str, output_path: str = None
    ) -> Optional[np.ndarray]:
        """Clone voice using specified TTS service"""
        if service_id not in self.services:
            logger.error(f"Coqui TTS service '{service_id}' not found")
            return None

        return await self.services[service_id].clone_voice(
            text, speaker_wav, output_path
        )

    def get_available_services(self) -> List[str]:
        """Get list of available TTS services"""
        return list(self.services.keys())

    def remove_service(self, service_id: str) -> bool:
        """Remove a TTS service"""
        if service_id in self.services:
            del self.services[service_id]
            logger.info(f"Coqui TTS service '{service_id}' removed")
            return True
        return False


# Global Coqui TTS manager instance
coqui_manager = CoquiTTSManager()


async def main():
    """Test Coqui TTS integration"""
    logger.info("Testing Coqui TTS integration...")

    if not COQUI_AVAILABLE:
        logger.error("Coqui TTS is not available")
        return

    # Create test service
    success = await coqui_manager.create_service(
        "test_coqui", "tts_models/en/ljspeech/tacotron2-DDC"
    )

    if success:
        logger.info("Coqui TTS integration test successful")

        # Test synthesis
        audio = await coqui_manager.synthesize(
            "test_coqui", "Hello, this is a test of Coqui TTS integration!"
        )

        if audio is not None:
            logger.info("Speech synthesis test successful")
        else:
            logger.error("Speech synthesis test failed")
    else:
        logger.error("Coqui TTS integration test failed")


if __name__ == "__main__":
    asyncio.run(main())
