# api/utils.py
# Utility functions for VoiceStudio API

import os
import json
import base64
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
import aiofiles
import librosa
import numpy as np

class AudioUtils:
    """Audio processing utilities"""
    
    @staticmethod
    def decode_base64_audio(base64_data: str) -> bytes:
        """Decode base64 audio data"""
        try:
            return base64.b64decode(base64_data)
        except Exception as e:
            raise ValueError(f"Invalid base64 audio data: {e}")
    
    @staticmethod
    def encode_audio_base64(audio_data: bytes) -> str:
        """Encode audio data to base64"""
        return base64.b64encode(audio_data).decode('utf-8')
    
    @staticmethod
    async def save_temp_audio(audio_data: bytes, suffix: str = ".wav") -> str:
        """Save audio data to temporary file"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(audio_data)
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def get_audio_info(file_path: str) -> Dict[str, Any]:
        """Get audio file information"""
        try:
            y, sr = librosa.load(file_path)
            duration = len(y) / sr
            
            return {
                "sample_rate": sr,
                "duration": duration,
                "channels": 1 if y.ndim == 1 else y.shape[0],
                "samples": len(y)
            }
        except Exception as e:
            raise ValueError(f"Failed to get audio info: {e}")
    
    @staticmethod
    def validate_audio_format(file_path: str) -> bool:
        """Validate audio file format"""
        try:
            librosa.load(file_path, duration=1.0)
            return True
        except Exception:
            return False

class FileUtils:
    """File handling utilities"""
    
    @staticmethod
    def ensure_directory(path: str) -> None:
        """Ensure directory exists"""
        Path(path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Get file hash"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    @staticmethod
    async def cleanup_temp_files(file_paths: list) -> None:
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception:
                pass

class ValidationUtils:
    """Validation utilities"""
    
    @staticmethod
    def validate_text(text: str) -> bool:
        """Validate text input"""
        if not text or not text.strip():
            return False
        if len(text) > 10000:  # Max 10k characters
            return False
        return True
    
    @staticmethod
    def validate_language(language: str) -> bool:
        """Validate language code"""
        valid_languages = [
            "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "ja", "hu"
        ]
        return language in valid_languages
    
    @staticmethod
    def validate_engine(engine: str) -> bool:
        """Validate engine name"""
        valid_engines = ["xtts", "openvoice", "cosyvoice2", "coqui"]
        return engine in valid_engines

class ResponseUtils:
    """Response utilities"""
    
    @staticmethod
    def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create success response"""
        return {
            "success": True,
            "data": data,
            "timestamp": time.time()
        }
    
    @staticmethod
    def create_error_response(error: str, code: int = 400) -> Dict[str, Any]:
        """Create error response"""
        return {
            "success": False,
            "error": error,
            "code": code,
            "timestamp": time.time()
        }

class ConfigUtils:
    """Configuration utilities"""
    
    @staticmethod
    def load_api_config() -> Dict[str, Any]:
        """Load API configuration"""
        config_path = Path("config/voicestudio.config.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "api": {
                    "host": "0.0.0.0",
                    "port": 5188,
                    "max_file_size_mb": 100,
                    "max_concurrent_jobs": 10
                }
            }
    
    @staticmethod
    def get_engine_config(engine: str) -> Dict[str, Any]:
        """Get engine configuration"""
        engines_config = {
            "xtts": {
                "max_workers": 32,
                "languages": ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "ja", "hu"],
                "quality": "high",
                "latency": "normal"
            },
            "openvoice": {
                "max_workers": 16,
                "languages": ["en", "zh", "ja"],
                "quality": "high",
                "latency": "low"
            },
            "cosyvoice2": {
                "max_workers": 16,
                "languages": ["en", "zh", "ja"],
                "quality": "high",
                "latency": "normal"
            },
            "coqui": {
                "max_workers": 8,
                "languages": ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "ja", "hu"],
                "quality": "medium",
                "latency": "normal"
            }
        }
        return engines_config.get(engine, {})

import time
