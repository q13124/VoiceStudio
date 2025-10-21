#!/usr/bin/env python3
"""
VoiceStudio Assistant Voice Cloning Service
Integrates voice cloning capabilities into the Assistant Service.
"""

import os
import sys
import json
import logging
import time
import asyncio
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
import numpy as np
import soundfile as sf

# Add VSDML to path for voice cloning imports
vsdml_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "VoiceStudio", "workers", "python", "vsdml")
sys.path.append(vsdml_path)

try:
    from TTS.api import TTS
    import torch
    import librosa
    import whisperx
    VOICE_CLONING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Voice cloning dependencies not available: {e}")
    VOICE_CLONING_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceCloningService:
    """Voice cloning service integrated with Assistant Service"""

    def __init__(self):
        self.status = "initializing"
        self.models_loaded = {}
        self.temp_dir = None
        self.cuda_available = False
        self.initialization_time = None

        if VOICE_CLONING_AVAILABLE:
            self._initialize_voice_cloning()
        else:
            self.status = "unavailable"
            logger.error("Voice cloning dependencies not available")

    def _initialize_voice_cloning(self):
        """Initialize voice cloning capabilities"""
        try:
            logger.info("Initializing voice cloning service...")
            start_time = time.time()

            # Check CUDA availability
            self.cuda_available = torch.cuda.is_available()
            logger.info(f"CUDA available: {self.cuda_available}")

            # Create temporary directory for processing
            self.temp_dir = tempfile.mkdtemp(prefix="voicestudio_assistant_")
            logger.info(f"Created temp directory: {self.temp_dir}")

            # Load basic TTS model
            logger.info("Loading basic TTS model...")
            self.models_loaded["basic"] = TTS(
                model_name="tts_models/en/ljspeech/tacotron2-DDC",
                progress_bar=False,
                gpu=self.cuda_available
            )

            # Load XTTS v2 voice cloning model
            logger.info("Loading XTTS v2 voice cloning model...")
            self.models_loaded["xtts_v2"] = TTS(
                model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                progress_bar=False,
                gpu=self.cuda_available
            )

            self.initialization_time = time.time() - start_time
            self.status = "ready"
            logger.info(f"Voice cloning service initialized in {self.initialization_time:.2f}s")

        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to initialize voice cloning: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get voice cloning service status"""
        return {
            "status": self.status,
            "cuda_available": self.cuda_available,
            "models_loaded": list(self.models_loaded.keys()),
            "initialization_time": self.initialization_time,
            "temp_directory": self.temp_dir,
            "dependencies_available": VOICE_CLONING_AVAILABLE
        }

    async def synthesize_speech(self, text: str, model_type: str = "basic",
                              speaker_wav: Optional[str] = None,
                              language: str = "en") -> Dict[str, Any]:
        """Synthesize speech from text"""
        if not VOICE_CLONING_AVAILABLE:
            return {"error": "Voice cloning dependencies not available"}

        if self.status != "ready":
            return {"error": f"Voice cloning service not ready: {self.status}"}

        if model_type not in self.models_loaded:
            return {"error": f"Model {model_type} not loaded"}

        try:
            start_time = time.time()
            logger.info(f"Synthesizing speech: '{text[:50]}...' with {model_type}")

            model = self.models_loaded[model_type]

            # Generate audio
            if model_type == "xtts_v2" and speaker_wav:
                # Voice cloning with reference audio
                wav = model.tts(text=text, speaker_wav=speaker_wav, language=language)
            elif model_type == "xtts_v2":
                # Use default speaker for XTTS
                wav = model.tts(text=text, language=language)
            else:
                # Basic TTS
                speaker = model.speakers[0] if model.is_multi_speaker else None
                wav = model.tts(text=text, speaker=speaker)

            # Save audio to temporary file
            output_path = os.path.join(self.temp_dir, f"output_{int(time.time())}.wav")
            sf.write(output_path, wav, 22050)

            synthesis_time = time.time() - start_time
            audio_duration = len(wav) / 22050
            rtf = synthesis_time / audio_duration if audio_duration > 0 else float('inf')

            result = {
                "success": True,
                "audio_path": output_path,
                "text": text,
                "model_used": model_type,
                "synthesis_time": synthesis_time,
                "audio_duration": audio_duration,
                "real_time_factor": rtf,
                "sample_rate": 22050,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Speech synthesis completed in {synthesis_time:.2f}s (RTF: {rtf:.2f})")
            return result

        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return {"error": f"Speech synthesis failed: {str(e)}"}

    async def clone_voice(self, text: str, reference_audio_path: str,
                         language: str = "en") -> Dict[str, Any]:
        """Clone voice using reference audio"""
        if not VOICE_CLONING_AVAILABLE:
            return {"error": "Voice cloning dependencies not available"}

        if self.status != "ready":
            return {"error": f"Voice cloning service not ready: {self.status}"}

        if "xtts_v2" not in self.models_loaded:
            return {"error": "XTTS v2 model not loaded"}

        try:
            start_time = time.time()
            logger.info(f"Cloning voice for text: '{text[:50]}...'")

            # Validate reference audio
            if not os.path.exists(reference_audio_path):
                return {"error": f"Reference audio file not found: {reference_audio_path}"}

            # Load and validate audio
            try:
                y, sr = librosa.load(reference_audio_path, sr=None)
                if len(y) < 22050:  # Less than 1 second
                    return {"error": "Reference audio too short (minimum 1 second required)"}
            except Exception as e:
                return {"error": f"Invalid reference audio file: {str(e)}"}

            # Perform voice cloning
            model = self.models_loaded["xtts_v2"]
            wav = model.tts(text=text, speaker_wav=reference_audio_path, language=language)

            # Save cloned audio
            output_path = os.path.join(self.temp_dir, f"cloned_{int(time.time())}.wav")
            sf.write(output_path, wav, 22050)

            cloning_time = time.time() - start_time
            audio_duration = len(wav) / 22050
            rtf = cloning_time / audio_duration if audio_duration > 0 else float('inf')

            result = {
                "success": True,
                "audio_path": output_path,
                "text": text,
                "reference_audio": reference_audio_path,
                "language": language,
                "cloning_time": cloning_time,
                "audio_duration": audio_duration,
                "real_time_factor": rtf,
                "sample_rate": 22050,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Voice cloning completed in {cloning_time:.2f}s (RTF: {rtf:.2f})")
            return result

        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return {"error": f"Voice cloning failed: {str(e)}"}

    async def transcribe_audio(self, audio_path: str, language: str = "en") -> Dict[str, Any]:
        """Transcribe audio to text using WhisperX"""
        if not VOICE_CLONING_AVAILABLE:
            return {"error": "Voice cloning dependencies not available"}

        try:
            start_time = time.time()
            logger.info(f"Transcribing audio: {audio_path}")

            # Load WhisperX model
            device = "cuda" if self.cuda_available else "cpu"
            model = whisperx.load_model("base", device, compute_type="float16" if self.cuda_available else "int8")

            # Transcribe
            audio = whisperx.load_audio(audio_path)
            result = model.transcribe(audio, batch_size=16)

            # Load alignment model and align
            model_a, metadata = whisperx.load_align_model(language_code=language, device=device)
            result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

            transcription_time = time.time() - start_time

            # Extract text
            text = " ".join([segment["text"] for segment in result["segments"]])

            result = {
                "success": True,
                "text": text,
                "segments": result["segments"],
                "language": language,
                "transcription_time": transcription_time,
                "audio_duration": len(audio) / 16000,  # WhisperX uses 16kHz
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Transcription completed in {transcription_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {"error": f"Transcription failed: {str(e)}"}

    async def get_available_models(self) -> Dict[str, Any]:
        """Get list of available TTS models"""
        if not VOICE_CLONING_AVAILABLE:
            return {"error": "Voice cloning dependencies not available"}

        try:
            tts_api = TTS()
            models = tts_api.list_models()

            return {
                "success": True,
                "models": models,
                "loaded_models": list(self.models_loaded.keys()),
                "cuda_available": self.cuda_available,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return {"error": f"Failed to get models: {str(e)}"}

    async def cleanup_temp_files(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                logger.error(f"Failed to cleanup temp directory: {e}")

    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass

# Global voice cloning service instance
voice_cloning_service = VoiceCloningService()
