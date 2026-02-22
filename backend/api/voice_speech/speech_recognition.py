"""
Speech Recognition Integration
Integrates vosk library for offline speech recognition.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Try importing vosk
HAS_VOSK = False
try:
    import json

    from vosk import Model, SetLogLevel

    HAS_VOSK = True
except ImportError:
    logger.warning("vosk not available.")


class SpeechRecognizer:
    """
    Speech recognition using vosk library.
    """

    def __init__(self, model_path: str | None = None):
        """
        Initialize speech recognizer.

        Args:
            model_path: Path to vosk model (auto-download if None)
        """
        self.vosk_available = HAS_VOSK
        self._model = None
        self._model_path = model_path

    def _load_model(self):
        """Lazy load the vosk model."""
        if not self.vosk_available:
            raise ImportError("vosk library not available")

        if self._model is None:
            try:
                SetLogLevel(-1)  # Disable vosk logging

                if self._model_path:
                    self._model = Model(self._model_path)
                else:
                    # Try to use default model location
                    # In production, you'd want to manage model downloads
                    logger.warning(
                        "No model path provided. Vosk requires a model to be downloaded."
                    )
                    raise ValueError("Vosk model path required")

                logger.info("Vosk model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading Vosk model: {e}", exc_info=True)
                raise

    def recognize(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
    ) -> dict[str, Any]:
        """
        Recognize speech in audio.

        Args:
            audio: Audio signal (mono, int16 or float32)
            sample_rate: Sample rate (should be 16000 for vosk)

        Returns:
            Dictionary with recognition results
        """
        if not self.vosk_available:
            raise ImportError("vosk library not available")

        try:
            self._load_model()

            # Create recognizer
            from vosk import KaldiRecognizer

            rec = KaldiRecognizer(self._model, sample_rate)
            rec.SetWords(True)

            # Ensure audio is int16
            if audio.dtype != np.int16:
                # Normalize and convert to int16
                if audio.dtype == np.float32 or audio.dtype == np.float64:
                    audio = (audio * 32767).astype(np.int16)
                else:
                    audio = audio.astype(np.int16)

            # Process audio in chunks
            results = []
            chunk_size = 4000  # Process in chunks

            for i in range(0, len(audio), chunk_size):
                chunk = audio[i : i + chunk_size]
                chunk_bytes = chunk.tobytes()

                if rec.AcceptWaveform(chunk_bytes):
                    result = json.loads(rec.Result())
                    if result.get("text"):
                        results.append(result)

            # Get final result
            final_result = json.loads(rec.FinalResult())

            # Combine all results
            all_text = " ".join([r.get("text", "") for r in results])
            if final_result.get("text"):
                all_text += " " + final_result.get("text", "")

            return {
                "text": all_text.strip(),
                "words": final_result.get("result", []),
                "confidence": final_result.get("confidence", 0.0),
            }
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}", exc_info=True)
            raise
