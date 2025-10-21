"""
Audio processing service with robust input normalization and diarization.
Optimized with parallel processing, intelligent caching, and memory management.

This module handles audio input normalization, transcription, and speaker diarization
with proper error handling, path validation, and performance optimizations.
"""

import os
import logging
import asyncio
import concurrent.futures
from typing import Union, List, Optional, Any, Dict
from pathlib import Path
from functools import lru_cache
import time
import threading
import hashlib
import json
from cachetools import TTLCache, LRUCache
import psutil
from datetime import datetime
import librosa
import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)


class EnhancedAudioProcessor:
    """Enhanced audio processor with advanced optimizations, caching, and voice cloning capabilities."""
    
    def __init__(self, diarize_model=None, max_workers: int = 4, cache_size: int = 1000):
        """Initialize the enhanced audio processor.
        
        Args:
            diarize_model: Optional diarization model instance
            max_workers: Maximum number of parallel workers for processing
            cache_size: Maximum number of items to cache
        """
        self.diarize_model = diarize_model
        self.max_workers = max_workers
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
        # Enhanced caching with multiple cache types
        self._file_cache = TTLCache(maxsize=cache_size, ttl=300)  # 5 minutes
        self._metadata_cache = TTLCache(maxsize=cache_size//2, ttl=600)  # 10 minutes
        self._processing_cache = LRUCache(maxsize=cache_size//4)  # LRU for processed results
        self._cache_lock = threading.RLock()
        
        # Voice cloning specific components
        self.voice_cloning_models = {
            'gpt_sovits': None,
            'openvoice': None,
            'coqui_xtts': None,
            'tortoise_tts': None,
            'rvc': None
        }
        
        # Voice cloning caches
        self._voice_profile_cache = TTLCache(maxsize=cache_size//2, ttl=1800)  # 30 minutes
        self._voice_model_cache = LRUCache(maxsize=100)  # Keep models in memory
        
        # Performance metrics
        self._metrics = {
            "files_processed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "processing_time_total": 0.0,
            "parallel_batches": 0,
            "errors": 0,
            # Voice cloning metrics
            "voice_clones_created": 0,
            "voice_similarity_avg": 0.0,
            "voice_processing_time_avg": 0.0,
            "cache_hits_voice": 0,
            "cache_misses_voice": 0
        }
        
        # Memory management
        self._max_memory_usage = 0.8  # 80% of available memory
        self._memory_check_interval = 100  # Check every 100 operations
        
        # Voice cloning capabilities
        self.voice_cloning_models = {
            'gpt_sovits': None,
            'openvoice': None,
            'coqui_xtts': None,
            'tortoise_tts': None,
            'rvc': None
        }
        
        # Voice cloning caches
        self._voice_profile_cache = TTLCache(maxsize=cache_size//2, ttl=1800)  # 30 minutes
        self._voice_model_cache = LRUCache(maxsize=100)  # Keep models in memory
        
        # Voice cloning metrics
        self._voice_cloning_metrics = {
            "voice_clones_created": 0,
            "voice_similarity_avg": 0.0,
            "processing_time_avg": 0.0,
            "cache_hits_voice": 0,
            "cache_misses_voice": 0
        }
        
    def process_audio_batch(
        self,
        args: dict,
        min_speakers: int = 1,
        max_speakers: int = 10,
        **diarizer_kwargs
    ) -> List[dict]:
        """
        Process a batch of audio inputs with normalization and optional diarization.
        Enhanced with intelligent caching and parallel processing.
        
        Args:
            args: Dictionary containing 'audio' key with input(s)
            min_speakers: Minimum number of speakers for diarization
            max_speakers: Maximum number of speakers for diarization
            **diarizer_kwargs: Additional arguments for diarization model
            
        Returns:
            List of processed results preserving input order
        """
        start_time = time.time()
        self._metrics["parallel_batches"] += 1
        
        # Check memory usage
        if self._metrics["files_processed"] % self._memory_check_interval == 0:
            self._check_memory_usage()
        
        # 1) Normalize inputs and capture original paths up front
        inp_audio = args.pop("audio")
        if isinstance(inp_audio, (str, bytes, os.PathLike)):
            inp_list = [inp_audio]
        else:
            inp_list = list(inp_audio)

        # Keep absolute file paths (None for non-file inputs)
        audio_paths = []
        for a in inp_list:
            if isinstance(a, (str, bytes, os.PathLike)):
                p = os.fspath(a)
                audio_paths.append(os.path.abspath(p))
            else:
                audio_paths.append(None)

        # Check cache for existing results
        cached_results = self._get_cached_results(inp_list, audio_paths)
        uncached_indices = [i for i, result in enumerate(cached_results) if result is None]
        
        if not uncached_indices:
            # All results were cached
            self._metrics["cache_hits"] += len(cached_results)
            logger.info(f"All {len(cached_results)} results served from cache")
            return cached_results

        # Process uncached audio inputs in parallel
        results = cached_results.copy()
        futures = []
        
        for i in uncached_indices:
            audio_input = inp_list[i]
            audio_path = audio_paths[i]
            
            future = self._executor.submit(
                self._process_single_audio_enhanced, 
                audio_input, 
                audio_path, 
                i
            )
            futures.append((i, future))
        
        # Collect results in order
        for i, future in futures:
            try:
                result = future.result(timeout=300)  # 5 minute timeout
                results[i] = result
                
                # Cache the result
                self._cache_result(audio_paths[i], result)
                
            except concurrent.futures.TimeoutError:
                logger.error(f"Audio processing timeout for input {i}")
                results[i] = {
                    'index': i,
                    'audio_path': audio_paths[i],
                    'error': 'Processing timeout',
                    'transcription': None,
                    'diarization': None
                }
                self._metrics["errors"] += 1
            except Exception as e:
                logger.error(f"Audio processing failed for input {i}: {e}")
                results[i] = {
                    'index': i,
                    'audio_path': audio_paths[i],
                    'error': str(e),
                    'transcription': None,
                    'diarization': None
                }
                self._metrics["errors"] += 1

        # 2) Diarization section (parallel processing with caching)
        diarization_futures = []
        for i, result in enumerate(results):
            audio_for_diar = audio_paths[i] if i < len(audio_paths) else None

            # Validate: must be a string path and exist
            if isinstance(audio_for_diar, str) and os.path.exists(audio_for_diar):
                # Check if diarization is cached
                diarization_key = self._get_diarization_cache_key(audio_for_diar, min_speakers, max_speakers)
                cached_diarization = self._get_from_cache(diarization_key)
                
                if cached_diarization is not None:
                    result['diarization'] = cached_diarization
                    self._metrics["cache_hits"] += 1
                else:
                    future = self._executor.submit(
                        self._process_diarization_enhanced,
                        audio_for_diar,
                        result,
                        min_speakers,
                        max_speakers,
                        diarizer_kwargs
                    )
                    diarization_futures.append((i, future, diarization_key))
            else:
                logger.warning(
                    "Skipping diarization (could not locate audio for session): %r",
                    audio_for_diar,
                )
                result['diarization'] = None

        # Collect diarization results
        for i, future, cache_key in diarization_futures:
            try:
                diarize_result = future.result(timeout=180)  # 3 minute timeout
                results[i]['diarization'] = diarize_result
                
                # Cache the diarization result
                self._set_cache(cache_key, diarize_result)
                
            except concurrent.futures.TimeoutError:
                logger.warning(f"Diarization timeout for audio {i}")
                results[i]['diarization'] = None
                self._metrics["errors"] += 1
            except Exception as e:
                logger.warning(f"Diarization failed for audio {i}: {e}")
                results[i]['diarization'] = None
                self._metrics["errors"] += 1

        # Update metrics
        processing_time = time.time() - start_time
        self._metrics["processing_time_total"] += processing_time
        self._metrics["files_processed"] += len(inp_list)
        self._metrics["cache_misses"] += len(uncached_indices)

        logger.info(f"Processed {len(inp_list)} audio files in {processing_time:.2f}s "
                  f"(avg: {processing_time/len(inp_list):.2f}s per file)")
        
        return results
    
    def _get_cached_results(self, inp_list: List, audio_paths: List) -> List[Optional[dict]]:
        """Get cached results for audio inputs"""
        cached_results = []
        
        for i, audio_path in enumerate(audio_paths):
            if audio_path and os.path.exists(audio_path):
                cache_key = self._get_processing_cache_key(audio_path)
                cached_result = self._get_from_cache(cache_key)
                cached_results.append(cached_result)
            else:
                cached_results.append(None)
        
        return cached_results
    
    def _cache_result(self, audio_path: Optional[str], result: dict):
        """Cache a processing result"""
        if audio_path:
            cache_key = self._get_processing_cache_key(audio_path)
            self._set_cache(cache_key, result)
    
    def _get_processing_cache_key(self, audio_path: str) -> str:
        """Generate cache key for processing results"""
        # Use file path, size, and modification time for cache key
        try:
            stat = os.stat(audio_path)
            key_data = f"{audio_path}:{stat.st_size}:{stat.st_mtime}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except OSError:
            return hashlib.md5(audio_path.encode()).hexdigest()
    
    def _get_diarization_cache_key(self, audio_path: str, min_speakers: int, max_speakers: int) -> str:
        """Generate cache key for diarization results"""
        base_key = self._get_processing_cache_key(audio_path)
        return f"diarization:{base_key}:{min_speakers}:{max_speakers}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get value from appropriate cache"""
        with self._cache_lock:
            # Try processing cache first (most specific)
            if cache_key in self._processing_cache:
                return self._processing_cache[cache_key]
            
            # Try metadata cache
            if cache_key in self._metadata_cache:
                return self._metadata_cache[cache_key]
            
            # Try file cache
            if cache_key in self._file_cache:
                return self._file_cache[cache_key]
        
        return None
    
    def _set_cache(self, cache_key: str, value: Any):
        """Set value in appropriate cache"""
        with self._cache_lock:
            # Use processing cache for results
            self._processing_cache[cache_key] = value
    
    def _check_memory_usage(self):
        """Check and manage memory usage"""
        try:
            process = psutil.Process()
            memory_percent = process.memory_percent()
            
            if memory_percent > self._max_memory_usage * 100:
                logger.warning(f"High memory usage: {memory_percent:.1f}%")
                self._cleanup_cache()
                
        except Exception as e:
            logger.debug(f"Memory check failed: {e}")
    
    def _cleanup_cache(self):
        """Clean up cache to free memory"""
        with self._cache_lock:
            # Clear oldest entries from processing cache
            if len(self._processing_cache) > self._processing_cache.maxsize // 2:
                # Remove oldest 25% of entries
                items_to_remove = len(self._processing_cache) // 4
                for _ in range(items_to_remove):
                    try:
                        self._processing_cache.popitem(last=False)
                    except KeyError:
                        break
            
            logger.info("Cache cleanup completed")
    
    def _process_single_audio_enhanced(self, audio_input: Any, audio_path: Optional[str], index: int) -> dict:
        """Enhanced single audio processing with better error handling"""
        try:
            result = self._transcribe_audio_enhanced(audio_input, audio_path)
            result['index'] = index
            result['processing_time'] = time.time()
            return result
        except Exception as e:
            logger.error(f"Transcription failed for input {index}: {e}")
            return {
                'index': index,
                'audio_path': audio_path,
                'error': str(e),
                'transcription': None,
                'diarization': None,
                'processing_time': time.time()
            }
    
    def _process_diarization_enhanced(self, audio_path: str, result: dict, min_speakers: int, 
                                    max_speakers: int, diarizer_kwargs: dict) -> Optional[dict]:
        """Enhanced diarization processing with better error handling"""
        try:
            if self.diarize_model:
                diarize_result = self.diarize_model(
                    audio_path,
                    min_speakers=min_speakers,
                    max_speakers=max_speakers,
                    **diarizer_kwargs
                )
                logger.info(f"Successfully diarized audio: {audio_path}")
                return diarize_result
            else:
                logger.warning("No diarization model available")
                return None
        except Exception as e:
            logger.warning(f"Diarization failed for {audio_path}: {e}")
            return None
    
    def _transcribe_audio_enhanced(self, audio_input: Any, audio_path: Optional[str]) -> dict:
        """
        Enhanced transcription logic with better error handling and metadata.
        
        Replace this method with your actual transcription implementation.
        
        Args:
            audio_input: The audio input (path, bytes, or other)
            audio_path: Absolute path if input is a file
            
        Returns:
            Dictionary containing transcription results
        """
        # This is a placeholder - replace with your actual transcription logic
        return {
            'audio_path': audio_path,
            'transcription': f"Enhanced transcription for {audio_input}",
            'diarization': None,
            'error': None,
            'metadata': {
                'processed_at': datetime.now().isoformat(),
                'processor_version': '2.0.0'
            }
        }
    
    def validate_audio_path(self, path: str) -> bool:
        """
        Validate that an audio file path exists and is readable.
        Enhanced with better caching and validation.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is valid, False otherwise
        """
        cache_key = f"validation:{path}"
        
        # Check cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            is_valid = (
                isinstance(path, str) and 
                os.path.exists(path) and 
                os.path.isfile(path) and
                os.access(path, os.R_OK)
            )
            
            # Cache the result
            self._set_cache(cache_key, is_valid)
            
            return is_valid
        except Exception:
            return False
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        Get comprehensive information about an audio file with enhanced caching.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with audio file information
        """
        cache_key = f"info:{audio_path}"
        
        # Check cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            if not self.validate_audio_path(audio_path):
                return {'error': 'Invalid audio path'}
                
            stat = os.stat(audio_path)
            info = {
                'path': audio_path,
                'size_bytes': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'exists': True,
                'readable': os.access(audio_path, os.R_OK),
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime,
                'error': None,
                'metadata': {
                    'file_extension': os.path.splitext(audio_path)[1].lower(),
                    'is_audio_file': os.path.splitext(audio_path)[1].lower() in ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
                }
            }
            
            # Cache the result
            self._set_cache(cache_key, info)
            
            return info
        except Exception as e:
            error_info = {
                'path': audio_path,
                'size_bytes': 0,
                'size_mb': 0,
                'exists': False,
                'readable': False,
                'error': str(e)
            }
            
            # Cache error result too
            self._set_cache(cache_key, error_info)
            
            return error_info
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics including voice cloning"""
        cache_hit_rate = (
            self._metrics["cache_hits"] / 
            max(1, self._metrics["cache_hits"] + self._metrics["cache_misses"])
        )
        
        avg_processing_time = (
            self._metrics["processing_time_total"] / 
            max(1, self._metrics["files_processed"])
        )
        
        return {
            "files_processed": self._metrics["files_processed"],
            "cache_hits": self._metrics["cache_hits"],
            "cache_misses": self._metrics["cache_misses"],
            "cache_hit_rate": cache_hit_rate,
            "processing_time_total": self._metrics["processing_time_total"],
            "avg_processing_time": avg_processing_time,
            "parallel_batches": self._metrics["parallel_batches"],
            "errors": self._metrics["errors"],
            "error_rate": self._metrics["errors"] / max(1, self._metrics["files_processed"]),
            "cache_sizes": {
                "file_cache": len(self._file_cache),
                "metadata_cache": len(self._metadata_cache),
                "processing_cache": len(self._processing_cache),
                "voice_profile_cache": len(self._voice_profile_cache),
                "voice_model_cache": len(self._voice_model_cache)
            },
            "voice_cloning": self.get_voice_cloning_metrics()
        }
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        with self._cache_lock:
            # TTLCache handles expiration automatically, but we can force cleanup
            self._file_cache.clear()
            self._metadata_cache.clear()
            self._processing_cache.clear()
    
    # Voice Cloning Methods
    
    async def extract_voice_profile(self, audio_path: str) -> Dict[str, Any]:
        """Extract comprehensive voice profile from audio"""
        # Check cache first
        cache_key = f"voice_profile:{audio_path}"
        cached_profile = self._get_from_cache(cache_key)
        if cached_profile:
            self._metrics["cache_hits_voice"] += 1
            return cached_profile
        
        # Extract voice profile using worker
        profile = await self._extract_voice_profile_worker(audio_path)
        
        # Cache result
        self._set_cache(cache_key, profile)
        self._metrics["cache_misses_voice"] += 1
        
        return profile
    
    async def clone_voice(self, reference_audio: str, target_text: str, 
                         speaker_id: Optional[str] = None, model_type: str = "gpt_sovits") -> Dict[str, Any]:
        """Clone voice using reference audio and target text"""
        start_time = time.time()
        
        # Extract voice profile
        voice_profile = await self.extract_voice_profile(reference_audio)
        
        # Generate voice clone
        cloned_audio = await self._generate_voice_clone(voice_profile, target_text, model_type)
        
        # Update metrics
        processing_time = time.time() - start_time
        self._metrics["voice_processing_time_avg"] = (
            (self._metrics["voice_processing_time_avg"] * 
             self._metrics["voice_clones_created"] + processing_time) /
            (self._metrics["voice_clones_created"] + 1)
        )
        self._metrics["voice_clones_created"] += 1
        
        return {
            "cloned_audio": cloned_audio,
            "voice_profile": voice_profile,
            "processing_time": processing_time,
            "speaker_id": speaker_id,
            "model_type": model_type
        }
    
    async def _extract_voice_profile_worker(self, audio_path: str) -> Dict[str, Any]:
        """Extract voice profile using worker"""
        try:
            # Use existing audio processing infrastructure
            audio, sr = librosa.load(audio_path, sr=22050)
            
            # Extract voice characteristics
            voice_profile = {
                'speaker_embedding': self._extract_speaker_embedding(audio),
                'pitch_contour': self._extract_pitch_contour(audio, sr),
                'formant_frequencies': self._extract_formant_frequencies(audio, sr),
                'speaking_rate': self._extract_speaking_rate(audio, sr),
                'breathing_patterns': self._extract_breathing_patterns(audio, sr),
                'emotion_patterns': self._extract_emotion_patterns(audio, sr),
                'audio_length': len(audio) / sr,
                'sample_rate': sr,
                'extracted_at': datetime.now().isoformat()
            }
            
            return voice_profile
        except Exception as e:
            logger.error(f"Voice profile extraction failed: {e}")
            return {}
    
    async def _generate_voice_clone(self, voice_profile: Dict[str, Any], 
                                   target_text: str, model_type: str) -> str:
        """Generate voice clone using worker"""
        try:
            # Load appropriate model
            model = await self._load_voice_cloning_model(model_type)
            
            if model is None:
                # Fallback to basic text-to-speech
                return await self._basic_tts_fallback(target_text, voice_profile)
            
            # Generate voice clone
            cloned_audio = await self._generate_with_model(model, target_text, voice_profile)
            
            return cloned_audio
        except Exception as e:
            logger.error(f"Voice clone generation failed: {e}")
            return await self._basic_tts_fallback(target_text, voice_profile)
    
    def _extract_speaker_embedding(self, audio: np.ndarray) -> np.ndarray:
        """Extract speaker embedding from audio"""
        try:
            # Use MFCC features as speaker embedding
            mfcc = librosa.feature.mfcc(y=audio, sr=22050, n_mfcc=13)
            return np.mean(mfcc, axis=1)
        except Exception as e:
            logger.warning(f"Speaker embedding extraction failed: {e}")
            return np.zeros(13)
    
    def _extract_pitch_contour(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract pitch contour information"""
        try:
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                return {
                    'mean_pitch': np.mean(pitch_values),
                    'pitch_range': np.max(pitch_values) - np.min(pitch_values),
                    'pitch_std': np.std(pitch_values)
                }
            return {'mean_pitch': 0, 'pitch_range': 0, 'pitch_std': 0}
        except Exception as e:
            logger.warning(f"Pitch contour extraction failed: {e}")
            return {'mean_pitch': 0, 'pitch_range': 0, 'pitch_std': 0}
    
    def _extract_formant_frequencies(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract formant frequencies"""
        try:
            # Use spectral centroid as a proxy for formant information
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            return {
                'mean_formant': np.mean(spectral_centroids),
                'formant_range': np.max(spectral_centroids) - np.min(spectral_centroids),
                'formant_std': np.std(spectral_centroids)
            }
        except Exception as e:
            logger.warning(f"Formant frequency extraction failed: {e}")
            return {'mean_formant': 0, 'formant_range': 0, 'formant_std': 0}
    
    def _extract_speaking_rate(self, audio: np.ndarray, sr: int) -> float:
        """Extract speaking rate (words per minute estimate)"""
        try:
            # Use spectral rolloff as a proxy for speaking rate
            rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            return np.mean(rolloff) / 1000  # Normalize
        except Exception as e:
            logger.warning(f"Speaking rate extraction failed: {e}")
            return 0.0
    
    def _extract_breathing_patterns(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract breathing patterns"""
        try:
            # Use zero crossing rate as a proxy for breathing patterns
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            return {
                'mean_zcr': np.mean(zcr),
                'zcr_std': np.std(zcr),
                'breathing_rate': np.mean(zcr) * sr / 2
            }
        except Exception as e:
            logger.warning(f"Breathing pattern extraction failed: {e}")
            return {'mean_zcr': 0, 'zcr_std': 0, 'breathing_rate': 0}
    
    def _extract_emotion_patterns(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract emotion patterns"""
        try:
            # Use spectral contrast as a proxy for emotion
            contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
            return {
                'mean_contrast': np.mean(contrast),
                'contrast_std': np.std(contrast),
                'emotion_intensity': np.mean(np.abs(contrast))
            }
        except Exception as e:
            logger.warning(f"Emotion pattern extraction failed: {e}")
            return {'mean_contrast': 0, 'contrast_std': 0, 'emotion_intensity': 0}
    
    async def _load_voice_cloning_model(self, model_type: str):
        """Load voice cloning model"""
        try:
            # Check if model is already loaded
            if self.voice_cloning_models[model_type] is not None:
                return self.voice_cloning_models[model_type]
            
            # For now, return None to use fallback
            # In a full implementation, you would load actual models here
            logger.info(f"Voice cloning model {model_type} would be loaded here")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load voice cloning model {model_type}: {e}")
            return None
    
    async def _generate_with_model(self, model, target_text: str, voice_profile: Dict[str, Any]) -> str:
        """Generate voice clone with loaded model"""
        try:
            # Placeholder for actual model generation
            # In a full implementation, this would use the loaded model
            logger.info(f"Generating voice clone with model for text: {target_text[:50]}...")
            
            # Return a placeholder audio file path
            return f"generated_voice_{int(time.time())}.wav"
            
        except Exception as e:
            logger.error(f"Model generation failed: {e}")
            raise
    
    async def _basic_tts_fallback(self, target_text: str, voice_profile: Dict[str, Any]) -> str:
        """Basic TTS fallback when models are not available"""
        try:
            logger.info(f"Using basic TTS fallback for text: {target_text[:50]}...")
            
            # Create a simple audio file as placeholder
            # In a real implementation, you would use a basic TTS system
            output_path = f"fallback_voice_{int(time.time())}.wav"
            
            # Create a simple sine wave as placeholder
            duration = len(target_text) * 0.1  # Rough estimate
            t = np.linspace(0, duration, int(22050 * duration))
            frequency = voice_profile.get('pitch_contour', {}).get('mean_pitch', 200) or 200
            audio = 0.3 * np.sin(2 * np.pi * frequency * t)
            
            # Save as WAV file
            import soundfile as sf
            sf.write(output_path, audio, 22050)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Basic TTS fallback failed: {e}")
            return f"error_voice_{int(time.time())}.wav"
    
    def get_voice_cloning_metrics(self) -> Dict[str, Any]:
        """Get voice cloning specific metrics"""
        return {
            "voice_clones_created": self._metrics["voice_clones_created"],
            "voice_similarity_avg": self._metrics["voice_similarity_avg"],
            "voice_processing_time_avg": self._metrics["voice_processing_time_avg"],
            "cache_hits_voice": self._metrics["cache_hits_voice"],
            "cache_misses_voice": self._metrics["cache_misses_voice"],
            "voice_cache_hit_rate": (
                self._metrics["cache_hits_voice"] / 
                max(1, self._metrics["cache_hits_voice"] + self._metrics["cache_misses_voice"])
            )
        }

    async def extract_voice_profile(self, audio_path: str) -> Dict[str, Any]:
        """Extract comprehensive voice profile from audio"""
        # Check cache first
        cache_key = f"voice_profile:{audio_path}"
        cached_profile = self._get_from_cache(cache_key)
        if cached_profile:
            self._voice_cloning_metrics["cache_hits_voice"] += 1
            return cached_profile
        
        # Extract voice profile
        profile = await self._extract_voice_profile_worker(audio_path)
        
        # Cache result
        self._set_cache(cache_key, profile)
        self._voice_cloning_metrics["cache_misses_voice"] += 1
        
        return profile
    
    async def clone_voice(self, reference_audio: str, target_text: str, 
                         speaker_id: Optional[str] = None, model_type: str = "gpt_sovits") -> Dict[str, Any]:
        """Clone voice using reference audio and target text"""
        start_time = time.time()
        
        # Extract voice profile
        voice_profile = await self.extract_voice_profile(reference_audio)
        
        # Generate voice clone
        cloned_audio = await self._generate_voice_clone(voice_profile, target_text, model_type)
        
        # Update metrics
        processing_time = time.time() - start_time
        self._voice_cloning_metrics["processing_time_avg"] = (
            (self._voice_cloning_metrics["processing_time_avg"] * 
             self._voice_cloning_metrics["voice_clones_created"] + processing_time) /
            (self._voice_cloning_metrics["voice_clones_created"] + 1)
        )
        self._voice_cloning_metrics["voice_clones_created"] += 1
        
        return {
            "cloned_audio": cloned_audio,
            "voice_profile": voice_profile,
            "processing_time": processing_time,
            "speaker_id": speaker_id,
            "model_type": model_type,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _extract_voice_profile_worker(self, audio_path: str) -> Dict[str, Any]:
        """Extract voice profile using worker"""
        try:
            # Load audio file
            audio, sr = librosa.load(audio_path, sr=22050)
            
            # Extract voice characteristics
            voice_profile = {
                'audio_length': len(audio) / sr,
                'sample_rate': sr,
                'speaker_embedding': self._extract_speaker_embedding(audio, sr),
                'pitch_contour': self._extract_pitch_contour(audio, sr),
                'formant_frequencies': self._extract_formant_frequencies(audio, sr),
                'speaking_rate': self._extract_speaking_rate(audio, sr),
                'breathing_patterns': self._extract_breathing_patterns(audio, sr),
                'emotion_patterns': self._extract_emotion_patterns(audio, sr),
                'audio_path': audio_path,
                'extracted_at': datetime.now().isoformat()
            }
            
            return voice_profile
        except Exception as e:
            logger.error(f"Voice profile extraction failed: {e}")
            return {
                'error': str(e),
                'audio_path': audio_path,
                'extracted_at': datetime.now().isoformat()
            }
    
    async def _generate_voice_clone(self, voice_profile: Dict[str, Any], 
                                   target_text: str, model_type: str) -> str:
        """Generate voice clone using worker"""
        try:
            # Load appropriate model
            model = self._load_voice_cloning_model(model_type)
            
            # Generate voice clone
            cloned_audio = model.generate(
                text=target_text,
                voice_profile=voice_profile
            )
            
            return cloned_audio
        except Exception as e:
            logger.error(f"Voice clone generation failed: {e}")
            return None
    
    def _extract_speaker_embedding(self, audio: np.ndarray, sr: int) -> List[float]:
        """Extract speaker embedding from audio"""
        try:
            # Use MFCC features as a simple speaker embedding
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            embedding = np.mean(mfcc, axis=1).tolist()
            return embedding
        except Exception as e:
            logger.error(f"Speaker embedding extraction failed: {e}")
            return [0.0] * 13
    
    def _extract_pitch_contour(self, audio: np.ndarray, sr: int) -> List[float]:
        """Extract pitch contour from audio"""
        try:
            # Extract pitch using librosa
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            return pitch_values[:100]  # Limit to first 100 values
        except Exception as e:
            logger.error(f"Pitch contour extraction failed: {e}")
            return []
    
    def _extract_formant_frequencies(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract formant frequencies from audio"""
        try:
            # Simple formant estimation using spectral peaks
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            freqs = librosa.fft_frequencies(sr=sr)
            
            # Find spectral peaks (simplified formant detection)
            peaks = librosa.util.peak_pick(magnitude.mean(axis=1), pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.05, wait=10)
            
            formants = {}
            if len(peaks) >= 4:
                formants['F1'] = float(freqs[peaks[0]])
                formants['F2'] = float(freqs[peaks[1]])
                formants['F3'] = float(freqs[peaks[2]])
                formants['F4'] = float(freqs[peaks[3]])
            else:
                formants['F1'] = 500.0
                formants['F2'] = 1500.0
                formants['F3'] = 2500.0
                formants['F4'] = 3500.0
            
            return formants
        except Exception as e:
            logger.error(f"Formant frequency extraction failed: {e}")
            return {'F1': 500.0, 'F2': 1500.0, 'F3': 2500.0, 'F4': 3500.0}
    
    def _extract_speaking_rate(self, audio: np.ndarray, sr: int) -> float:
        """Extract speaking rate from audio"""
        try:
            # Estimate speaking rate using onset detection
            onsets = librosa.onset.onset_detect(y=audio, sr=sr)
            if len(onsets) > 1:
                duration = len(audio) / sr
                rate = len(onsets) / duration
                return float(rate)
            else:
                return 2.0  # Default speaking rate
        except Exception as e:
            logger.error(f"Speaking rate extraction failed: {e}")
            return 2.0
    
    def _extract_breathing_patterns(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract breathing patterns from audio"""
        try:
            # Simple breathing pattern detection using energy
            frame_length = 2048
            hop_length = 512
            energy = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Find low energy regions (potential breathing)
            threshold = np.mean(energy) * 0.3
            low_energy_regions = energy < threshold
            
            breathing_info = {
                'breathing_pauses': int(np.sum(low_energy_regions)),
                'average_pause_length': float(np.mean(energy[low_energy_regions])) if np.any(low_energy_regions) else 0.0,
                'breathing_rhythm': 'regular' if np.std(energy) < np.mean(energy) * 0.5 else 'irregular'
            }
            
            return breathing_info
        except Exception as e:
            logger.error(f"Breathing pattern extraction failed: {e}")
            return {'breathing_pauses': 0, 'average_pause_length': 0.0, 'breathing_rhythm': 'unknown'}
    
    def _extract_emotion_patterns(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract emotion patterns from audio"""
        try:
            # Simple emotion detection using spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
            
            emotion_info = {
                'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                'zero_crossing_rate_mean': float(np.mean(zero_crossing_rate)),
                'emotion_prediction': self._predict_emotion(spectral_centroids, spectral_rolloff, zero_crossing_rate)
            }
            
            return emotion_info
        except Exception as e:
            logger.error(f"Emotion pattern extraction failed: {e}")
            return {'emotion_prediction': 'neutral'}
    
    def _predict_emotion(self, spectral_centroids: np.ndarray, spectral_rolloff: np.ndarray, 
                        zero_crossing_rate: np.ndarray) -> str:
        """Simple emotion prediction based on audio features"""
        try:
            centroid_mean = np.mean(spectral_centroids)
            rolloff_mean = np.mean(spectral_rolloff)
            zcr_mean = np.mean(zero_crossing_rate)
            
            # Simple rule-based emotion prediction
            if centroid_mean > 3000 and zcr_mean > 0.1:
                return 'excited'
            elif centroid_mean < 2000 and zcr_mean < 0.05:
                return 'calm'
            elif rolloff_mean > 8000:
                return 'happy'
            else:
                return 'neutral'
        except Exception:
            return 'neutral'
    
    def _load_voice_cloning_model(self, model_type: str):
        """Load voice cloning model"""
        try:
            if model_type in self.voice_cloning_models:
                if self.voice_cloning_models[model_type] is None:
                    # Simulate model loading
                    self.voice_cloning_models[model_type] = MockVoiceCloningModel(model_type)
                return self.voice_cloning_models[model_type]
            else:
                raise ValueError(f"Unknown model type: {model_type}")
        except Exception as e:
            logger.error(f"Failed to load model {model_type}: {e}")
            return MockVoiceCloningModel(model_type)
    
    def get_voice_cloning_metrics(self) -> Dict[str, Any]:
        """Get voice cloning performance metrics"""
        cache_hit_rate = (
            self._voice_cloning_metrics["cache_hits_voice"] / 
            max(1, self._voice_cloning_metrics["cache_hits_voice"] + self._voice_cloning_metrics["cache_misses_voice"])
        )
        
        return {
            "voice_clones_created": self._voice_cloning_metrics["voice_clones_created"],
            "voice_cache_hit_rate": cache_hit_rate,
            "voice_processing_time_avg": self._voice_cloning_metrics["processing_time_avg"],
            "voice_similarity_avg": self._voice_cloning_metrics["voice_similarity_avg"],
            "loaded_models": [model for model, instance in self.voice_cloning_models.items() if instance is not None]
        }
    
    def close(self):
        """Close the audio processor and cleanup resources"""
        self._executor.shutdown(wait=True)
        self.cleanup_cache()
        logger.info("Enhanced audio processor closed")


class MockVoiceCloningModel:
    """Mock voice cloning model for testing"""
    
    def __init__(self, model_type: str):
        self.model_type = model_type
        logger.info(f"Mock {model_type} model loaded")
    
    def generate(self, text: str, voice_profile: Dict[str, Any]) -> str:
        """Generate mock cloned audio"""
        # Simulate processing time
        time.sleep(1)
        
        # Create mock output filename
        output_filename = f"cloned_{self.model_type}_{hashlib.md5(text.encode()).hexdigest()[:8]}.wav"
        
        # Create mock audio file
        duration = len(text) * 0.1  # 0.1 seconds per character
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Generate mock audio based on voice profile
        if 'speaker_embedding' in voice_profile:
            # Use speaker embedding to influence the generated audio
            embedding = voice_profile['speaker_embedding']
            base_freq = 200 + (embedding[0] * 100) if len(embedding) > 0 else 200
        else:
            base_freq = 200
        
        # Generate sine wave with some variation
        audio = np.sin(2 * np.pi * base_freq * t) * 0.3
        audio += np.sin(2 * np.pi * base_freq * 1.5 * t) * 0.1  # Add harmonics
        
        # Add some noise to make it more realistic
        noise = np.random.normal(0, 0.05, len(audio))
        audio += noise
        
        # Save mock audio file
        sf.write(output_filename, audio, sample_rate)
        
        logger.info(f"Mock {self.model_type} generated audio: {output_filename}")
        return output_filename


# Backward compatibility
AudioProcessor = EnhancedAudioProcessor


# Example usage function
def process_audio_with_diarization(
    audio_inputs: Union[str, List[str], bytes, List[bytes]],
    diarize_model=None,
    min_speakers: int = 1,
    max_speakers: int = 10,
    **kwargs
) -> List[dict]:
    """
    Convenience function to process audio inputs with diarization.
    
    Args:
        audio_inputs: Single audio input or list of inputs
        diarize_model: Optional diarization model
        min_speakers: Minimum speakers for diarization
        max_speakers: Maximum speakers for diarization
        **kwargs: Additional arguments
        
    Returns:
        List of processed results
    """
    processor = EnhancedAudioProcessor(diarize_model)
    args = {'audio': audio_inputs}
    return processor.process_audio_batch(
        args,
        min_speakers=min_speakers,
        max_speakers=max_speakers,
        **kwargs
    )
    
    def process_audio_batch(
        self,
        args: dict,
        min_speakers: int = 1,
        max_speakers: int = 10,
        **diarizer_kwargs
    ) -> List[dict]:
        """
        Process a batch of audio inputs with normalization and optional diarization.
        Optimized with parallel processing for better performance.
        
        Args:
            args: Dictionary containing 'audio' key with input(s)
            min_speakers: Minimum number of speakers for diarization
            max_speakers: Maximum number of speakers for diarization
            **diarizer_kwargs: Additional arguments for diarization model
            
        Returns:
            List of processed results preserving input order
        """
        # 1) Normalize inputs and capture original paths up front
        inp_audio = args.pop("audio")
        if isinstance(inp_audio, (str, bytes, os.PathLike)):
            inp_list = [inp_audio]
        else:
            inp_list = list(inp_audio)

        # keep absolute file paths (None for non-file inputs)
        audio_paths = []
        for a in inp_list:
            if isinstance(a, (str, bytes, os.PathLike)):
                p = os.fspath(a)
                audio_paths.append(os.path.abspath(p))
            else:
                audio_paths.append(None)

        # Process audio inputs in parallel
        results = []
        futures = []
        
        for i, audio_input in enumerate(inp_list):
            future = self._executor.submit(
                self._process_single_audio, 
                audio_input, 
                audio_paths[i], 
                i
            )
            futures.append(future)
        
        # Collect results in order
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Audio processing failed: {e}")
                # Create error result to preserve order
                results.append({
                    'index': len(results),
                    'audio_path': audio_paths[len(results)] if len(results) < len(audio_paths) else None,
                    'error': str(e),
                    'transcription': None,
                    'diarization': None
                })
        
        # Sort results by index to preserve order
        results.sort(key=lambda x: x.get('index', 0))

        # 2) Diarization section (parallel processing)
        diarization_futures = []
        for i, result in enumerate(results):
            audio_for_diar = audio_paths[i] if i < len(audio_paths) else None

            # Validate: must be a string path and exist
            if isinstance(audio_for_diar, str) and os.path.exists(audio_for_diar):
                future = self._executor.submit(
                    self._process_diarization,
                    audio_for_diar,
                    result,
                    min_speakers,
                    max_speakers,
                    diarizer_kwargs
                )
                diarization_futures.append((i, future))
            else:
                logger.warning(
                    "Skipping diarization (could not locate audio for session): %r",
                    audio_for_diar,
                )
                result['diarization'] = None

        # Collect diarization results
        for i, future in diarization_futures:
            try:
                diarize_result = future.result()
                results[i]['diarization'] = diarize_result
            except Exception as e:
                logger.warning(f"Diarization failed for audio {i}: {e}")
                results[i]['diarization'] = None

        return results
    
    def _process_single_audio(self, audio_input: Any, audio_path: Optional[str], index: int) -> dict:
        """Process a single audio input (for parallel execution)"""
        try:
            result = self._transcribe_audio(audio_input, audio_path)
            result['index'] = index
            return result
        except Exception as e:
            logger.error(f"Transcription failed for input {index}: {e}")
            return {
                'index': index,
                'audio_path': audio_path,
                'error': str(e),
                'transcription': None,
                'diarization': None
            }
    
    def _process_diarization(self, audio_path: str, result: dict, min_speakers: int, 
                           max_speakers: int, diarizer_kwargs: dict) -> Optional[dict]:
        """Process diarization for a single audio file (for parallel execution)"""
        try:
            if self.diarize_model:
                diarize_result = self.diarize_model(
                    audio_path,
                    min_speakers=min_speakers,
                    max_speakers=max_speakers,
                    **diarizer_kwargs
                )
                logger.info(f"Successfully diarized audio: {audio_path}")
                return diarize_result
            else:
                logger.warning("No diarization model available")
                return None
        except Exception as e:
            logger.warning(f"Diarization failed for {audio_path}: {e}")
            return None
    
    def _transcribe_audio(self, audio_input: Any, audio_path: Optional[str]) -> dict:
        """
        Placeholder for transcription logic.
        
        Replace this method with your actual transcription implementation.
        
        Args:
            audio_input: The audio input (path, bytes, or other)
            audio_path: Absolute path if input is a file
            
        Returns:
            Dictionary containing transcription results
        """
        # This is a placeholder - replace with your actual transcription logic
        return {
            'audio_path': audio_path,
            'transcription': f"Transcription for {audio_input}",
            'diarization': None,
            'error': None
        }
    
    def validate_audio_path(self, path: str) -> bool:
        """
        Validate that an audio file path exists and is readable.
        Uses caching for better performance.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is valid, False otherwise
        """
        # Check cache first
        with self._cache_lock:
            if path in self._file_cache:
                cache_entry = self._file_cache[path]
                if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                    return cache_entry['valid']
        
        try:
            is_valid = isinstance(path, str) and os.path.exists(path) and os.path.isfile(path)
            
            # Cache the result
            with self._cache_lock:
                self._file_cache[path] = {
                    'valid': is_valid,
                    'timestamp': time.time()
                }
            
            return is_valid
        except Exception:
            return False
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        Get information about an audio file with caching.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with audio file information
        """
        # Check cache first
        with self._cache_lock:
            cache_key = f"info:{audio_path}"
            if cache_key in self._file_cache:
                cache_entry = self._file_cache[cache_key]
                if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                    return cache_entry['info']
        
        try:
            if not self.validate_audio_path(audio_path):
                return {'error': 'Invalid audio path'}
                
            stat = os.stat(audio_path)
            info = {
                'path': audio_path,
                'size_bytes': stat.st_size,
                'exists': True,
                'error': None
            }
            
            # Cache the result
            with self._cache_lock:
                self._file_cache[cache_key] = {
                    'info': info,
                    'timestamp': time.time()
                }
            
            return info
        except Exception as e:
            error_info = {
                'path': audio_path,
                'size_bytes': 0,
                'exists': False,
                'error': str(e)
            }
            
            # Cache error result too
            with self._cache_lock:
                self._file_cache[cache_key] = {
                    'info': error_info,
                    'timestamp': time.time()
                }
            
            return error_info
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        with self._cache_lock:
            expired_keys = [
                key for key, entry in self._file_cache.items()
                if current_time - entry['timestamp'] > self._cache_ttl
            ]
            for key in expired_keys:
                del self._file_cache[key]
    
    def close(self):
        """Close the audio processor and cleanup resources"""
        self._executor.shutdown(wait=True)
        self.cleanup_cache()
        logger.info("Audio processor closed")


# Example usage function
def process_audio_with_diarization(
    audio_inputs: Union[str, List[str], bytes, List[bytes]],
    diarize_model=None,
    min_speakers: int = 1,
    max_speakers: int = 10,
    **kwargs
) -> List[dict]:
    """
    Convenience function to process audio inputs with diarization.
    
    Args:
        audio_inputs: Single audio input or list of inputs
        diarize_model: Optional diarization model
        min_speakers: Minimum speakers for diarization
        max_speakers: Maximum speakers for diarization
        **kwargs: Additional arguments
        
    Returns:
        List of processed results
    """
    processor = AudioProcessor(diarize_model)
    args = {'audio': audio_inputs}
    return processor.process_audio_batch(
        args,
        min_speakers=min_speakers,
        max_speakers=max_speakers,
        **kwargs
    )
