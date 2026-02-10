"""
Language Detection and Support.

Task 4.2.2: Language detection and supported languages.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class LanguageInfo:
    """Information about a supported language."""
    
    code: str  # ISO 639-1 code
    name: str
    native_name: str
    
    # Capability flags
    tts_supported: bool = True
    stt_supported: bool = True
    translation_supported: bool = True
    
    # Quality info
    quality_tier: str = "standard"  # basic, standard, premium


class SupportedLanguages:
    """Registry of supported languages."""
    
    LANGUAGES: Dict[str, LanguageInfo] = {
        "en": LanguageInfo("en", "English", "English", quality_tier="premium"),
        "es": LanguageInfo("es", "Spanish", "Español", quality_tier="premium"),
        "fr": LanguageInfo("fr", "French", "Français", quality_tier="premium"),
        "de": LanguageInfo("de", "German", "Deutsch", quality_tier="premium"),
        "it": LanguageInfo("it", "Italian", "Italiano", quality_tier="standard"),
        "pt": LanguageInfo("pt", "Portuguese", "Português", quality_tier="standard"),
        "ru": LanguageInfo("ru", "Russian", "Русский", quality_tier="standard"),
        "zh": LanguageInfo("zh", "Chinese", "中文", quality_tier="premium"),
        "ja": LanguageInfo("ja", "Japanese", "日本語", quality_tier="premium"),
        "ko": LanguageInfo("ko", "Korean", "한국어", quality_tier="standard"),
        "ar": LanguageInfo("ar", "Arabic", "العربية", quality_tier="standard"),
        "hi": LanguageInfo("hi", "Hindi", "हिन्दी", quality_tier="standard"),
        "nl": LanguageInfo("nl", "Dutch", "Nederlands", quality_tier="standard"),
        "pl": LanguageInfo("pl", "Polish", "Polski", quality_tier="basic"),
        "tr": LanguageInfo("tr", "Turkish", "Türkçe", quality_tier="basic"),
        "vi": LanguageInfo("vi", "Vietnamese", "Tiếng Việt", quality_tier="basic"),
        "th": LanguageInfo("th", "Thai", "ไทย", quality_tier="basic"),
        "id": LanguageInfo("id", "Indonesian", "Bahasa Indonesia", quality_tier="basic"),
        "uk": LanguageInfo("uk", "Ukrainian", "Українська", quality_tier="basic"),
        "cs": LanguageInfo("cs", "Czech", "Čeština", quality_tier="basic"),
    }
    
    @classmethod
    def get(cls, code: str) -> Optional[LanguageInfo]:
        """Get language info by code."""
        return cls.LANGUAGES.get(code.lower())
    
    @classmethod
    def list_all(cls) -> List[LanguageInfo]:
        """List all supported languages."""
        return list(cls.LANGUAGES.values())
    
    @classmethod
    def list_for_tts(cls) -> List[LanguageInfo]:
        """List languages with TTS support."""
        return [lang for lang in cls.LANGUAGES.values() if lang.tts_supported]
    
    @classmethod
    def list_for_translation(cls) -> List[LanguageInfo]:
        """List languages with translation support."""
        return [lang for lang in cls.LANGUAGES.values() if lang.translation_supported]
    
    @classmethod
    def is_supported(cls, code: str) -> bool:
        """Check if a language is supported."""
        return code.lower() in cls.LANGUAGES
    
    @classmethod
    def get_pairs(cls) -> List[Tuple[str, str]]:
        """Get all supported translation pairs."""
        codes = list(cls.LANGUAGES.keys())
        pairs = []
        for i, src in enumerate(codes):
            for dst in codes[i+1:]:
                pairs.append((src, dst))
                pairs.append((dst, src))
        return pairs


class LanguageDetector:
    """
    Automatic language detection.
    
    Features:
    - Audio-based detection
    - Text-based detection
    - Confidence scoring
    """
    
    def __init__(self):
        """Initialize language detector."""
        self._model = None
        self._loaded = False
    
    async def load(self) -> bool:
        """Load detection model."""
        # Placeholder for model loading
        self._model = {"type": "whisper", "loaded": True}
        self._loaded = True
        return True
    
    async def detect_from_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
    ) -> Tuple[str, float]:
        """
        Detect language from audio.
        
        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
            
        Returns:
            Tuple of (language_code, confidence)
        """
        if not self._loaded:
            await self.load()
        
        # Task 4.2.11: Use Whisper for language detection
        try:
            import whisper
            
            # Load or reuse Whisper model
            if not hasattr(self, "_whisper_model"):
                self._whisper_model = whisper.load_model("base")
            
            # Whisper expects 16kHz audio
            if sample_rate != 16000:
                try:
                    import librosa
                    audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
                except ImportError:
                    logger.debug("librosa not available for resampling to 16kHz")
            
            # Detect language (first 30 seconds max)
            audio_30s = whisper.pad_or_trim(audio_data)
            mel = whisper.log_mel_spectrogram(audio_30s).to(self._whisper_model.device)
            
            _, probs = self._whisper_model.detect_language(mel)
            
            # Get highest probability language
            detected_lang = max(probs, key=probs.get)
            confidence = probs[detected_lang]
            
            return (detected_lang, confidence)
            
        except ImportError:
            logger.warning("Whisper not available for language detection")
        except Exception as e:
            logger.error(f"Whisper language detection failed: {e}")
        
        # Fallback to placeholder
        return ("en", 0.5)
    
    async def detect_from_text(self, text: str) -> Tuple[str, float]:
        """
        Detect language from text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (language_code, confidence)
        """
        if not text.strip():
            return ("unknown", 0.0)
        
        # Simple heuristic detection
        # In production, use langdetect or similar
        
        # Check for common character ranges
        for char in text:
            code = ord(char)
            
            if 0x4E00 <= code <= 0x9FFF:
                return ("zh", 0.8)
            elif 0x3040 <= code <= 0x309F or 0x30A0 <= code <= 0x30FF:
                return ("ja", 0.8)
            elif 0xAC00 <= code <= 0xD7AF:
                return ("ko", 0.8)
            elif 0x0400 <= code <= 0x04FF:
                return ("ru", 0.8)
            elif 0x0600 <= code <= 0x06FF:
                return ("ar", 0.8)
        
        # Default to English for Latin text
        return ("en", 0.6)
    
    async def detect_multiple(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        top_k: int = 3,
    ) -> List[Tuple[str, float]]:
        """
        Detect multiple possible languages.
        
        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
            top_k: Number of results
            
        Returns:
            List of (language_code, confidence) tuples
        """
        # Task 4.2.12: Return confidence-ranked language predictions
        try:
            import whisper
            
            # Load or reuse Whisper model
            if not hasattr(self, "_whisper_model"):
                self._whisper_model = whisper.load_model("base")
            
            # Prepare audio
            if sample_rate != 16000:
                try:
                    import librosa
                    audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
                except ImportError:
                    logger.debug("librosa not available for resampling to 16kHz")
            
            # Detect language probabilities
            audio_30s = whisper.pad_or_trim(audio_data)
            mel = whisper.log_mel_spectrogram(audio_30s).to(self._whisper_model.device)
            
            _, probs = self._whisper_model.detect_language(mel)
            
            # Sort by confidence and take top-k
            sorted_langs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            
            return sorted_langs[:top_k]
            
        except ImportError:
            logger.warning("Whisper not available for multi-language detection")
        except Exception as e:
            logger.error(f"Multi-language detection failed: {e}")
        
        # Fallback
        return [
            ("en", 0.7),
            ("es", 0.2),
            ("fr", 0.1),
        ][:top_k]
