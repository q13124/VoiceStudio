"""
Language Detection Engine.

Task 4.2.2: Auto-detect source language from audio.
Supports 99+ languages with confidence scores.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class LanguageInfo:
    """Information about a detected language."""
    code: str
    name: str
    confidence: float
    script: str = "Latin"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "confidence": self.confidence,
            "script": self.script,
        }


# Language database with names and scripts
LANGUAGE_DB = {
    "en": ("English", "Latin"),
    "es": ("Spanish", "Latin"),
    "fr": ("French", "Latin"),
    "de": ("German", "Latin"),
    "it": ("Italian", "Latin"),
    "pt": ("Portuguese", "Latin"),
    "nl": ("Dutch", "Latin"),
    "pl": ("Polish", "Latin"),
    "ru": ("Russian", "Cyrillic"),
    "uk": ("Ukrainian", "Cyrillic"),
    "zh": ("Chinese", "Han"),
    "ja": ("Japanese", "Japanese"),
    "ko": ("Korean", "Hangul"),
    "ar": ("Arabic", "Arabic"),
    "hi": ("Hindi", "Devanagari"),
    "th": ("Thai", "Thai"),
    "vi": ("Vietnamese", "Latin"),
    "id": ("Indonesian", "Latin"),
    "ms": ("Malay", "Latin"),
    "tl": ("Tagalog", "Latin"),
    "tr": ("Turkish", "Latin"),
    "cs": ("Czech", "Latin"),
    "el": ("Greek", "Greek"),
    "hu": ("Hungarian", "Latin"),
    "ro": ("Romanian", "Latin"),
    "sv": ("Swedish", "Latin"),
    "da": ("Danish", "Latin"),
    "fi": ("Finnish", "Latin"),
    "no": ("Norwegian", "Latin"),
    "he": ("Hebrew", "Hebrew"),
    "fa": ("Persian", "Arabic"),
    "bn": ("Bengali", "Bengali"),
    "ta": ("Tamil", "Tamil"),
    "te": ("Telugu", "Telugu"),
    "mr": ("Marathi", "Devanagari"),
    "gu": ("Gujarati", "Gujarati"),
    "kn": ("Kannada", "Kannada"),
    "ml": ("Malayalam", "Malayalam"),
    "pa": ("Punjabi", "Gurmukhi"),
    "ur": ("Urdu", "Arabic"),
}


class LanguageDetector:
    """
    Multi-modal language detection engine.
    
    Supports detection from:
    - Audio (using Whisper)
    - Text (using statistical/ML methods)
    
    Features:
    - 99+ language support
    - Confidence scores
    - Top-k predictions
    - Script detection
    """
    
    def __init__(self):
        self._whisper_model = None
        self._text_detector = None
        self._loaded = False
    
    async def load(self) -> bool:
        """Load detection models."""
        try:
            # Load Whisper for audio detection
            try:
                import whisper
                self._whisper_model = whisper.load_model("base")
                logger.info("Loaded Whisper for audio language detection")
            except ImportError:
                logger.warning("Whisper not available")
            
            # Load text detector
            try:
                import langdetect
                self._text_detector = "langdetect"
                logger.info("Using langdetect for text detection")
            except ImportError:
                try:
                    from lingua import Language, LanguageDetectorBuilder
                    self._text_detector = LanguageDetectorBuilder.from_all_languages().build()
                    logger.info("Using lingua for text detection")
                except ImportError:
                    logger.warning("No text detector available")
            
            self._loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load language detector: {e}")
            return False
    
    async def detect_from_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
        top_k: int = 1,
    ) -> List[LanguageInfo]:
        """
        Detect language from audio.
        
        Args:
            audio: Audio samples
            sample_rate: Sample rate
            top_k: Number of top predictions to return
            
        Returns:
            List of LanguageInfo sorted by confidence
        """
        if not self._loaded:
            await self.load()
        
        if self._whisper_model is not None:
            try:
                import whisper
                
                # Resample to 16kHz if needed
                if sample_rate != 16000:
                    try:
                        import librosa
                        audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)
                    except ImportError:
                        logger.debug("librosa not available for resampling in language detection")
                
                # Pad/trim to 30 seconds
                audio_30s = whisper.pad_or_trim(audio)
                mel = whisper.log_mel_spectrogram(audio_30s).to(self._whisper_model.device)
                
                # Detect language
                _, probs = self._whisper_model.detect_language(mel)
                
                # Sort by probability
                sorted_langs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
                
                results = []
                for code, conf in sorted_langs[:top_k]:
                    name, script = LANGUAGE_DB.get(code, (code.upper(), "Unknown"))
                    results.append(LanguageInfo(
                        code=code,
                        name=name,
                        confidence=float(conf),
                        script=script,
                    ))
                
                return results
                
            except Exception as e:
                logger.error(f"Whisper detection failed: {e}")
        
        # Fallback
        return [LanguageInfo(code="en", name="English", confidence=0.5, script="Latin")]
    
    async def detect_from_text(
        self,
        text: str,
        top_k: int = 1,
    ) -> List[LanguageInfo]:
        """
        Detect language from text.
        
        Args:
            text: Input text
            top_k: Number of top predictions
            
        Returns:
            List of LanguageInfo sorted by confidence
        """
        if not self._loaded:
            await self.load()
        
        if not text.strip():
            return [LanguageInfo(code="unknown", name="Unknown", confidence=0.0)]
        
        # Try langdetect
        if self._text_detector == "langdetect":
            try:
                import langdetect
                from langdetect import detect_langs
                
                detected = detect_langs(text)
                
                results = []
                for det in detected[:top_k]:
                    code = det.lang
                    name, script = LANGUAGE_DB.get(code, (code.upper(), "Unknown"))
                    results.append(LanguageInfo(
                        code=code,
                        name=name,
                        confidence=det.prob,
                        script=script,
                    ))
                
                return results
                
            except Exception as e:
                logger.debug(f"langdetect failed: {e}")
        
        # Try lingua
        elif hasattr(self._text_detector, "detect_multiple_languages_of"):
            try:
                results_raw = self._text_detector.detect_multiple_languages_of(text)
                
                results = []
                for result in results_raw[:top_k]:
                    code = result.language.iso_code_639_1.name.lower()
                    name, script = LANGUAGE_DB.get(code, (code.upper(), "Unknown"))
                    results.append(LanguageInfo(
                        code=code,
                        name=name,
                        confidence=result.value,
                        script=script,
                    ))
                
                return results
                
            except Exception as e:
                logger.debug(f"lingua failed: {e}")
        
        # Character-based heuristic fallback
        return self._detect_by_characters(text, top_k)
    
    def _detect_by_characters(self, text: str, top_k: int) -> List[LanguageInfo]:
        """Detect language by character analysis."""
        scores: Dict[str, float] = {}
        
        for char in text:
            code = ord(char)
            
            # CJK
            if 0x4E00 <= code <= 0x9FFF:
                scores["zh"] = scores.get("zh", 0) + 1
            # Hiragana/Katakana
            elif 0x3040 <= code <= 0x30FF:
                scores["ja"] = scores.get("ja", 0) + 1
            # Hangul
            elif 0xAC00 <= code <= 0xD7AF:
                scores["ko"] = scores.get("ko", 0) + 1
            # Cyrillic
            elif 0x0400 <= code <= 0x04FF:
                scores["ru"] = scores.get("ru", 0) + 1
            # Arabic
            elif 0x0600 <= code <= 0x06FF:
                scores["ar"] = scores.get("ar", 0) + 1
            # Devanagari
            elif 0x0900 <= code <= 0x097F:
                scores["hi"] = scores.get("hi", 0) + 1
            # Thai
            elif 0x0E00 <= code <= 0x0E7F:
                scores["th"] = scores.get("th", 0) + 1
            # Greek
            elif 0x0370 <= code <= 0x03FF:
                scores["el"] = scores.get("el", 0) + 1
            # Hebrew
            elif 0x0590 <= code <= 0x05FF:
                scores["he"] = scores.get("he", 0) + 1
            # Latin with diacritics
            elif 0x00C0 <= code <= 0x00FF:
                scores["la"] = scores.get("la", 0) + 0.5
        
        # Default to English for plain Latin
        if not scores:
            scores["en"] = 1.0
        
        # Normalize
        total = sum(scores.values())
        normalized = {k: v / total for k, v in scores.items()}
        
        # Sort and return top-k
        sorted_langs = sorted(normalized.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for code, conf in sorted_langs[:top_k]:
            name, script = LANGUAGE_DB.get(code, (code.upper(), "Unknown"))
            results.append(LanguageInfo(
                code=code,
                name=name,
                confidence=conf,
                script=script,
            ))
        
        return results
    
    async def detect_mixed(
        self,
        audio: Optional[np.ndarray],
        text: Optional[str],
        sample_rate: int = 16000,
    ) -> LanguageInfo:
        """
        Detect language using both audio and text.
        
        Combines confidence from both sources for better accuracy.
        """
        audio_result = None
        text_result = None
        
        if audio is not None and len(audio) > 0:
            audio_results = await self.detect_from_audio(audio, sample_rate, top_k=1)
            if audio_results:
                audio_result = audio_results[0]
        
        if text is not None and text.strip():
            text_results = await self.detect_from_text(text, top_k=1)
            if text_results:
                text_result = text_results[0]
        
        # Combine results
        if audio_result and text_result:
            if audio_result.code == text_result.code:
                # Matching - boost confidence
                return LanguageInfo(
                    code=audio_result.code,
                    name=audio_result.name,
                    confidence=min(1.0, (audio_result.confidence + text_result.confidence) / 1.5),
                    script=audio_result.script,
                )
            else:
                # Conflict - prefer audio (usually more reliable)
                if audio_result.confidence > text_result.confidence:
                    return audio_result
                return text_result
        
        return audio_result or text_result or LanguageInfo(
            code="en", name="English", confidence=0.5, script="Latin"
        )
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    @property
    def supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return list(LANGUAGE_DB.keys())
    
    def get_language_info(self, code: str) -> Optional[LanguageInfo]:
        """Get information about a language by code."""
        if code in LANGUAGE_DB:
            name, script = LANGUAGE_DB[code]
            return LanguageInfo(code=code, name=name, confidence=1.0, script=script)
        return None
