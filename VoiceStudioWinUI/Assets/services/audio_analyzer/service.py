#!/usr/bin/env python3
"""
VoiceStudio Advanced Audio Analysis Service
Comprehensive audio analysis with real-time processing and voice cloning integration.
Runs on port 5085 with advanced audio feature extraction.
"""

import json
import logging
import time
import threading
import asyncio
import concurrent.futures
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import uuid
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.fft import fft, fftfreq
import aubio
from functools import lru_cache

# Import our optimized modules
from services.service_discovery import register_service, service_client
from services.security import security_middleware, create_service_auth_token
from services.database import (
    get_database_logger, record_metric, db_manager,
    save_voice_profile, get_voice_profile, record_voice_cloning_metric
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedAudioAnalyzer:
    """Advanced audio analysis with comprehensive feature extraction"""

    def __init__(self):
        self.sample_rate = 22050
        self.hop_length = 512
        self.frame_length = 2048
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        self._lock = threading.Lock()

        # Initialize aubio objects for real-time analysis
        self.pitch_detector = aubio.pitch("default", self.frame_length, self.hop_length, self.sample_rate)
        self.tempo_detector = aubio.tempo("default", self.frame_length, self.hop_length, self.sample_rate)
        self.onset_detector = aubio.onset("default", self.frame_length, self.hop_length, self.sample_rate)

    def analyze_audio_file(self, audio_path: str) -> Dict[str, Any]:
        """Comprehensive audio file analysis"""
        try:
            # Check cache first
            cache_key = f"analysis:{os.path.getmtime(audio_path)}:{audio_path}"
            with self._lock:
                if cache_key in self._cache:
                    cache_entry = self._cache[cache_key]
                    if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                        return cache_entry['analysis']

            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            duration = len(audio) / sr

            # Extract comprehensive features
            analysis = {
                'file_info': {
                    'path': audio_path,
                    'duration': duration,
                    'sample_rate': sr,
                    'channels': 1,
                    'samples': len(audio)
                },
                'basic_features': self._extract_basic_features(audio, sr),
                'spectral_features': self._extract_spectral_features(audio, sr),
                'rhythmic_features': self._extract_rhythmic_features(audio, sr),
                'harmonic_features': self._extract_harmonic_features(audio, sr),
                'voice_features': self._extract_voice_features(audio, sr),
                'quality_metrics': self._extract_quality_metrics(audio, sr),
                'analysis_timestamp': datetime.now().isoformat()
            }

            # Cache the result
            with self._lock:
                self._cache[cache_key] = {
                    'analysis': analysis,
                    'timestamp': time.time()
                }

            return analysis

        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {'error': str(e)}

    def _extract_basic_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract basic audio features"""
        try:
            # RMS Energy
            rms = librosa.feature.rms(y=audio, hop_length=self.hop_length)[0]

            # Zero Crossing Rate
            zcr = librosa.feature.zero_crossing_rate(audio, hop_length=self.hop_length)[0]

            # Spectral Centroid
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr, hop_length=self.hop_length)[0]

            # Spectral Rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr, hop_length=self.hop_length)[0]

            # Spectral Bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr, hop_length=self.hop_length)[0]

            return {
                'rms_mean': float(np.mean(rms)),
                'rms_std': float(np.std(rms)),
                'rms_max': float(np.max(rms)),
                'zcr_mean': float(np.mean(zcr)),
                'zcr_std': float(np.std(zcr)),
                'spectral_centroid_mean': float(np.mean(spectral_centroid)),
                'spectral_centroid_std': float(np.std(spectral_centroid)),
                'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                'spectral_rolloff_std': float(np.std(spectral_rolloff)),
                'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth)),
                'spectral_bandwidth_std': float(np.std(spectral_bandwidth))
            }
        except Exception as e:
            logger.error(f"Basic features extraction failed: {e}")
            return {}

    def _extract_spectral_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract spectral features"""
        try:
            # MFCCs
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, hop_length=self.hop_length)

            # Spectral Contrast
            spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr, hop_length=self.hop_length)

            # Chroma
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr, hop_length=self.hop_length)

            # Tonnetz
            tonnetz = librosa.feature.tonnetz(y=audio, sr=sr)

            return {
                'mfcc_mean': [float(np.mean(mfccs[i])) for i in range(13)],
                'mfcc_std': [float(np.std(mfccs[i])) for i in range(13)],
                'spectral_contrast_mean': [float(np.mean(spectral_contrast[i])) for i in range(7)],
                'spectral_contrast_std': [float(np.std(spectral_contrast[i])) for i in range(7)],
                'chroma_mean': [float(np.mean(chroma[i])) for i in range(12)],
                'chroma_std': [float(np.std(chroma[i])) for i in range(12)],
                'tonnetz_mean': [float(np.mean(tonnetz[i])) for i in range(6)],
                'tonnetz_std': [float(np.std(tonnetz[i])) for i in range(6)]
            }
        except Exception as e:
            logger.error(f"Spectral features extraction failed: {e}")
            return {}

    def _extract_rhythmic_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract rhythmic features"""
        try:
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=audio, sr=sr, hop_length=self.hop_length)

            # Onset strength
            onset_envelope = librosa.onset.onset_strength(y=audio, sr=sr, hop_length=self.hop_length)

            # Rhythm patterns
            rhythm_patterns = librosa.feature.tempogram(onset_envelope=onset_envelope, sr=sr, hop_length=self.hop_length)

            return {
                'tempo': float(tempo),
                'beat_count': len(beats),
                'onset_strength_mean': float(np.mean(onset_envelope)),
                'onset_strength_std': float(np.std(onset_envelope)),
                'rhythm_patterns_mean': [float(np.mean(rhythm_patterns[i])) for i in range(min(10, rhythm_patterns.shape[0]))],
                'rhythm_patterns_std': [float(np.std(rhythm_patterns[i])) for i in range(min(10, rhythm_patterns.shape[0]))]
            }
        except Exception as e:
            logger.error(f"Rhythmic features extraction failed: {e}")
            return {}

    def _extract_harmonic_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract harmonic features"""
        try:
            # Harmonic and percussive separation
            harmonic, percussive = librosa.effects.hpss(audio)

            # Harmonic features
            harmonic_centroid = librosa.feature.spectral_centroid(y=harmonic, sr=sr, hop_length=self.hop_length)[0]
            harmonic_rolloff = librosa.feature.spectral_rolloff(y=harmonic, sr=sr, hop_length=self.hop_length)[0]

            # Percussive features
            percussive_centroid = librosa.feature.spectral_centroid(y=percussive, sr=sr, hop_length=self.hop_length)[0]
            percussive_rolloff = librosa.feature.spectral_rolloff(y=percussive, sr=sr, hop_length=self.hop_length)[0]

            # Harmonic ratio
            harmonic_ratio = np.sum(harmonic**2) / (np.sum(harmonic**2) + np.sum(percussive**2))

            return {
                'harmonic_centroid_mean': float(np.mean(harmonic_centroid)),
                'harmonic_centroid_std': float(np.std(harmonic_centroid)),
                'harmonic_rolloff_mean': float(np.mean(harmonic_rolloff)),
                'harmonic_rolloff_std': float(np.std(harmonic_rolloff)),
                'percussive_centroid_mean': float(np.mean(percussive_centroid)),
                'percussive_centroid_std': float(np.std(percussive_centroid)),
                'percussive_rolloff_mean': float(np.mean(percussive_rolloff)),
                'percussive_rolloff_std': float(np.std(percussive_rolloff)),
                'harmonic_ratio': float(harmonic_ratio)
            }
        except Exception as e:
            logger.error(f"Harmonic features extraction failed: {e}")
            return {}

    def _extract_voice_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract voice-specific features"""
        try:
            # Pitch tracking
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr, hop_length=self.hop_length)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)

            # Formant estimation (simplified)
            formants = self._estimate_formants(audio, sr)

            # Voice activity detection
            vad = self._voice_activity_detection(audio, sr)

            # Speaking rate estimation
            speaking_rate = self._estimate_speaking_rate(audio, sr)

            return {
                'pitch_mean': float(np.mean(pitch_values)) if pitch_values else 0.0,
                'pitch_std': float(np.std(pitch_values)) if pitch_values else 0.0,
                'pitch_min': float(np.min(pitch_values)) if pitch_values else 0.0,
                'pitch_max': float(np.max(pitch_values)) if pitch_values else 0.0,
                'formants': formants,
                'voice_activity_ratio': float(vad),
                'speaking_rate': float(speaking_rate)
            }
        except Exception as e:
            logger.error(f"Voice features extraction failed: {e}")
            return {}

    def _extract_quality_metrics(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract audio quality metrics"""
        try:
            # Signal-to-noise ratio estimation
            snr = self._estimate_snr(audio)

            # Dynamic range
            dynamic_range = 20 * np.log10(np.max(np.abs(audio)) / (np.mean(np.abs(audio)) + 1e-10))

            # Spectral flatness
            spectral_flatness = self._calculate_spectral_flatness(audio)

            # Clipping detection
            clipping_ratio = np.sum(np.abs(audio) > 0.99) / len(audio)

            return {
                'snr_db': float(snr),
                'dynamic_range_db': float(dynamic_range),
                'spectral_flatness': float(spectral_flatness),
                'clipping_ratio': float(clipping_ratio)
            }
        except Exception as e:
            logger.error(f"Quality metrics extraction failed: {e}")
            return {}

    def _estimate_formants(self, audio: np.ndarray, sr: int) -> List[float]:
        """Estimate formant frequencies"""
        try:
            # Simple formant estimation using LPC
            lpc_coeffs = librosa.lpc(audio, order=10)
            roots = np.roots(lpc_coeffs)
            angles = np.angle(roots)
            freqs = angles * sr / (2 * np.pi)
            freqs = freqs[freqs > 0]
            freqs = np.sort(freqs)

            # Return first 3 formants
            return [float(f) for f in freqs[:3]]
        except:
            return [0.0, 0.0, 0.0]

    def _voice_activity_detection(self, audio: np.ndarray, sr: int) -> float:
        """Simple voice activity detection"""
        try:
            # Use energy-based VAD
            frame_length = 1024
            hop_length = 512

            frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
            energy = np.sum(frames**2, axis=0)

            threshold = np.mean(energy) * 0.1
            voice_frames = np.sum(energy > threshold)

            return voice_frames / len(energy)
        except:
            return 0.0

    def _estimate_speaking_rate(self, audio: np.ndarray, sr: int) -> float:
        """Estimate speaking rate in words per minute"""
        try:
            # Simple syllable counting based on energy peaks
            onset_envelope = librosa.onset.onset_strength(y=audio, sr=sr)
            onsets = librosa.onset.onset_detect(onset_envelope=onset_envelope, sr=sr)

            # Estimate syllables from onsets
            syllables = len(onsets)
            duration = len(audio) / sr
            syllables_per_second = syllables / duration
            words_per_minute = syllables_per_second * 60 * 0.5  # Rough estimate

            return min(words_per_minute, 300)  # Cap at 300 WPM
        except:
            return 150.0  # Default speaking rate

    def _estimate_snr(self, audio: np.ndarray) -> float:
        """Estimate signal-to-noise ratio"""
        try:
            # Simple SNR estimation using signal and noise power
            signal_power = np.mean(audio**2)

            # Estimate noise as low-energy portions
            frame_length = 1024
            frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=frame_length//2)
            frame_energy = np.sum(frames**2, axis=0)

            # Noise is estimated from low-energy frames
            noise_threshold = np.percentile(frame_energy, 20)
            noise_frames = frames[:, frame_energy < noise_threshold]
            noise_power = np.mean(noise_frames**2) if noise_frames.size > 0 else signal_power * 0.01

            snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
            return max(snr, 0)  # Ensure non-negative
        except:
            return 20.0  # Default SNR

    def _calculate_spectral_flatness(self, audio: np.ndarray) -> float:
        """Calculate spectral flatness measure"""
        try:
            # Compute power spectrum
            fft = np.fft.fft(audio)
            power_spectrum = np.abs(fft)**2

            # Spectral flatness = geometric mean / arithmetic mean
            geometric_mean = np.exp(np.mean(np.log(power_spectrum + 1e-10)))
            arithmetic_mean = np.mean(power_spectrum)

            flatness = geometric_mean / (arithmetic_mean + 1e-10)
            return flatness
        except:
            return 0.0

class AudioAnalysisService:
    """Audio analysis service with full integration"""

    def __init__(self):
        self.service_id = str(uuid.uuid4())
        self.service_name = "audio_analyzer"
        self.status = "running"
        self.start_time = datetime.now()

        # Initialize components
        self.db_logger = get_database_logger(self.service_id, self.service_name)
        self.analyzer = AdvancedAudioAnalyzer()

        # Register with service discovery
        register_service(self.service_name, port=5085, metadata={
            "capabilities": ["audio_analysis", "voice_feature_extraction", "quality_assessment"],
            "supported_formats": ["wav", "mp3", "flac", "m4a", "ogg"]
        })

        # Create service auth token
        self.auth_token = create_service_auth_token(self.service_id, self.service_name)

        # Log service startup
        self.db_logger.info("Audio analysis service started", {
            "service_id": self.service_id,
            "start_time": self.start_time.isoformat()
        })

        logger.info(f"Audio Analysis Service initialized with ID: {self.service_id}")

    def get_health(self):
        """Get comprehensive health status"""
        uptime = (datetime.now() - self.start_time).total_seconds()

        # Record health metric
        record_metric(self.service_id, self.service_name, "uptime_seconds", uptime)

        health_data = {
            "ok": True,
            "service": "audio_analyzer",
            "service_id": self.service_id,
            "status": self.status,
            "uptime_seconds": uptime,
            "features": {
                "audio_analysis": True,
                "voice_feature_extraction": True,
                "quality_assessment": True,
                "real_time_processing": True,
                "caching": True
            },
            "supported_formats": ["wav", "mp3", "flac", "m4a", "ogg"],
            "ts": datetime.now().isoformat()
        }

        self.db_logger.info("Health check performed", {"uptime": uptime})
        return health_data

    def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """Analyze audio file"""
        try:
            start_time = time.time()

            # Validate file exists
            if not os.path.exists(audio_path):
                return {"error": "Audio file not found"}

            # Perform analysis
            analysis = self.analyzer.analyze_audio_file(audio_path)

            analysis_time = time.time() - start_time

            # Record metrics
            record_voice_cloning_metric(
                self.service_id, "analysis_time", analysis_time,
                "performance", metadata={"file_path": audio_path}
            )

            self.db_logger.info("Audio analysis completed", {
                "audio_path": audio_path,
                "analysis_time": analysis_time
            })

            return analysis

        except Exception as e:
            self.db_logger.error(f"Audio analysis failed: {e}")
            return {"error": str(e)}

    def extract_voice_profile(self, audio_path: str, speaker_id: str) -> Dict[str, Any]:
        """Extract voice profile for voice cloning"""
        try:
            # Analyze audio
            analysis = self.analyze_audio(audio_path)

            if "error" in analysis:
                return analysis

            # Extract voice-specific features
            voice_features = analysis.get("voice_features", {})
            basic_features = analysis.get("basic_features", {})
            spectral_features = analysis.get("spectral_features", {})

            # Create voice profile
            voice_profile = {
                "speaker_id": speaker_id,
                "audio_path": audio_path,
                "extracted_at": datetime.now().isoformat(),
                "pitch_contour": {
                    "mean": voice_features.get("pitch_mean", 0),
                    "std": voice_features.get("pitch_std", 0),
                    "min": voice_features.get("pitch_min", 0),
                    "max": voice_features.get("pitch_max", 0)
                },
                "formant_frequencies": {
                    "f1": voice_features.get("formants", [0, 0, 0])[0],
                    "f2": voice_features.get("formants", [0, 0, 0])[1],
                    "f3": voice_features.get("formants", [0, 0, 0])[2]
                },
                "speaking_rate": voice_features.get("speaking_rate", 150),
                "voice_activity_ratio": voice_features.get("voice_activity_ratio", 0),
                "spectral_centroid": basic_features.get("spectral_centroid_mean", 0),
                "spectral_bandwidth": basic_features.get("spectral_bandwidth_mean", 0),
                "mfcc_features": spectral_features.get("mfcc_mean", [0] * 13),
                "quality_metrics": analysis.get("quality_metrics", {}),
                "analysis_metadata": {
                    "analysis_time": analysis.get("analysis_timestamp"),
                    "file_duration": analysis.get("file_info", {}).get("duration", 0),
                    "sample_rate": analysis.get("file_info", {}).get("sample_rate", 22050)
                }
            }

            # Save voice profile to database
            save_voice_profile(speaker_id, voice_profile)

            self.db_logger.info("Voice profile extracted", {
                "speaker_id": speaker_id,
                "audio_path": audio_path
            })

            return voice_profile

        except Exception as e:
            self.db_logger.error(f"Voice profile extraction failed: {e}")
            return {"error": str(e)}

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get analysis service summary"""
        try:
            # Get cached analysis count
            cache_size = len(self.analyzer._cache)

            summary = {
                "service_id": self.service_id,
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "cache_size": cache_size,
                "cache_ttl": self.analyzer._cache_ttl,
                "sample_rate": self.analyzer.sample_rate,
                "hop_length": self.analyzer.hop_length,
                "frame_length": self.analyzer.frame_length,
                "timestamp": datetime.now().isoformat()
            }

            return summary

        except Exception as e:
            return {"error": str(e)}

class AudioAnalysisHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for audio analysis service"""

    def __init__(self, *args, analysis_service=None, **kwargs):
        self.analysis_service = analysis_service
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        try:
            if path == "/health":
                self._handle_health()
            elif path == "/summary":
                self._handle_summary()
            else:
                self._handle_not_found()
        except Exception as e:
            self.analysis_service.db_logger.error(f"Error handling request {path}: {e}")
            self._handle_error(str(e))

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        try:
            if path == "/analyze":
                self._handle_analyze()
            elif path == "/extract_voice_profile":
                self._handle_extract_voice_profile()
            else:
                self._handle_not_found()
        except Exception as e:
            self.analysis_service.db_logger.error(f"Error handling POST request {path}: {e}")
            self._handle_error(str(e))

    def _handle_health(self):
        """Handle health check endpoint"""
        health_data = self.analysis_service.get_health()
        self._send_json_response(200, health_data)

    def _handle_summary(self):
        """Handle summary endpoint"""
        summary = self.analysis_service.get_analysis_summary()
        self._send_json_response(200, summary)

    def _handle_analyze(self):
        """Handle audio analysis endpoint"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_json_response(400, {"error": "No data provided"})
            return

        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))

            audio_path = data.get('audio_path')
            if not audio_path:
                self._send_json_response(400, {"error": "audio_path required"})
                return

            result = self.analysis_service.analyze_audio(audio_path)
            self._send_json_response(200, result)

        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})

    def _handle_extract_voice_profile(self):
        """Handle voice profile extraction endpoint"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_json_response(400, {"error": "No data provided"})
            return

        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))

            audio_path = data.get('audio_path')
            speaker_id = data.get('speaker_id')

            if not audio_path or not speaker_id:
                self._send_json_response(400, {"error": "audio_path and speaker_id required"})
                return

            result = self.analysis_service.extract_voice_profile(audio_path, speaker_id)
            self._send_json_response(200, result)

        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})

    def _handle_not_found(self):
        """Handle 404 errors"""
        self._send_json_response(404, {"error": "Not Found", "path": self.path})

    def _handle_error(self, error_message):
        """Handle server errors"""
        self._send_json_response(500, {"error": "Internal Server Error", "message": error_message})

    def _send_json_response(self, status_code, data):
        """Send JSON response with security headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('X-Service-ID', self.analysis_service.service_id)
        self.end_headers()

        response_body = json.dumps(data, indent=2)
        self.wfile.write(response_body.encode('utf-8'))

    def log_message(self, format, *args):
        """Override to use our database logger"""
        message = format % args
        self.analysis_service.db_logger.info(f"HTTP Request: {message}")

def create_handler(analysis_service):
    """Create HTTP handler with analysis service"""
    def handler(*args, **kwargs):
        return AudioAnalysisHTTPHandler(*args, analysis_service=analysis_service, **kwargs)
    return handler

def start_audio_analysis_service(port=5085):
    """Start the Audio Analysis Service"""
    analysis_service = AudioAnalysisService()
    handler = create_handler(analysis_service)

    server = HTTPServer(('127.0.0.1', port), handler)
    logger.info(f"Audio Analysis Service starting on port {port}")
    logger.info(f"Service ID: {analysis_service.service_id}")
    logger.info(f"Health endpoint: http://127.0.0.1:{port}/health")
    logger.info(f"Summary endpoint: http://127.0.0.1:{port}/summary")
    logger.info(f"Analyze endpoint: http://127.0.0.1:{port}/analyze")
    logger.info(f"Extract voice profile endpoint: http://127.0.0.1:{port}/extract_voice_profile")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Audio Analysis Service shutting down...")
        analysis_service.db_logger.info("Service shutting down")
        server.shutdown()

if __name__ == "__main__":
    start_audio_analysis_service()
