#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Voice Similarity Scoring System
Advanced voice similarity analysis and scoring algorithms
"""

import os
import json
import time
import numpy as np
import librosa
import torch
import torchaudio
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings("ignore")

class SimilarityMetric(Enum):
    """Voice similarity metrics"""
    SPECTRAL_SIMILARITY = "spectral_similarity"
    MFCC_SIMILARITY = "mfcc_similarity"
    PITCH_SIMILARITY = "pitch_similarity"
    PROSODY_SIMILARITY = "prosody_similarity"
    TIMBRE_SIMILARITY = "timbre_similarity"
    OVERALL_SIMILARITY = "overall_similarity"

@dataclass
class VoiceFeatures:
    """Voice feature representation"""
    mfcc: np.ndarray
    spectral_centroid: np.ndarray
    spectral_rolloff: np.ndarray
    spectral_bandwidth: np.ndarray
    zero_crossing_rate: np.ndarray
    rms_energy: np.ndarray
    pitch: np.ndarray
    pitch_magnitude: np.ndarray
    formants: List[np.ndarray]
    prosody_features: Dict[str, Any]
    timbre_features: Dict[str, Any]

@dataclass
class SimilarityScore:
    """Voice similarity score result"""
    metric: SimilarityMetric
    score: float
    confidence: float
    details: Dict[str, Any]

class VoiceSimilarityAnalyzer:
    """Advanced voice similarity analyzer"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/voicestudio.config.json"
        self.config = self.load_config()
        
        # Audio settings
        self.sample_rate = self.config.get("audio", {}).get("sample_rate", 22050)
        self.hop_length = self.config.get("audio", {}).get("hop_length", 512)
        self.n_fft = self.config.get("audio", {}).get("n_fft", 2048)
        
        # Feature extraction settings
        self.n_mfcc = self.config.get("similarity", {}).get("n_mfcc", 13)
        self.n_formants = self.config.get("similarity", {}).get("n_formants", 4)
        
        # Similarity settings
        self.weights = self.config.get("similarity", {}).get("weights", {
            "spectral": 0.25,
            "mfcc": 0.25,
            "pitch": 0.20,
            "prosody": 0.15,
            "timbre": 0.15
        })
        
        # Setup logging
        self.setup_logging()
        
        # Initialize models
        self.setup_models()
        
    def load_config(self) -> Dict:
        """Load configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "audio": {
                "sample_rate": 22050,
                "hop_length": 512,
                "n_fft": 2048
            },
            "similarity": {
                "n_mfcc": 13,
                "n_formants": 4,
                "weights": {
                    "spectral": 0.25,
                    "mfcc": 0.25,
                    "pitch": 0.20,
                    "prosody": 0.15,
                    "timbre": 0.15
                }
            }
        }
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_models(self):
        """Setup similarity analysis models"""
        try:
            # Initialize PyTorch models for advanced similarity
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.logger.info(f"Using device: {self.device}")
            
            # Load pre-trained models if available
            self.load_pretrained_models()
            
        except Exception as e:
            self.logger.warning(f"Model setup failed: {e}")
            self.device = torch.device("cpu")
    
    def load_pretrained_models(self):
        """Load pre-trained models for similarity analysis"""
        # Placeholder for pre-trained model loading
        # In production, this would load models like:
        # - Speaker verification models
        # - Voice embedding models
        # - Acoustic feature models
        pass
    
    def extract_voice_features(self, audio_path: str) -> VoiceFeatures:
        """Extract comprehensive voice features"""
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Basic spectral features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc, hop_length=self.hop_length)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=self.hop_length)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)
            rms_energy = librosa.feature.rms(y=y, hop_length=self.hop_length)
            
            # Pitch features
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=self.hop_length)
            pitch = pitches
            pitch_magnitude = magnitudes
            
            # Formant features
            formants = self.extract_formants(y, sr)
            
            # Prosody features
            prosody_features = self.extract_prosody_features(y, sr, pitches)
            
            # Timbre features
            timbre_features = self.extract_timbre_features(y, sr)
            
            return VoiceFeatures(
                mfcc=mfcc,
                spectral_centroid=spectral_centroid,
                spectral_rolloff=spectral_rolloff,
                spectral_bandwidth=spectral_bandwidth,
                zero_crossing_rate=zero_crossing_rate,
                rms_energy=rms_energy,
                pitch=pitch,
                pitch_magnitude=pitch_magnitude,
                formants=formants,
                prosody_features=prosody_features,
                timbre_features=timbre_features
            )
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            raise
    
    def extract_formants(self, y: np.ndarray, sr: int) -> List[np.ndarray]:
        """Extract formant frequencies"""
        try:
            # Use LPC to estimate formants
            formants = []
            
            # Process in frames
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.010 * sr)   # 10ms hop
            
            for i in range(0, len(y) - frame_length, hop_length):
                frame = y[i:i + frame_length]
                
                # Apply window
                windowed_frame = frame * np.hamming(len(frame))
                
                # LPC analysis
                try:
                    lpc_coeffs = librosa.lpc(windowed_frame, order=self.n_formants * 2)
                    roots = np.roots(lpc_coeffs)
                    
                    # Find formant frequencies
                    formant_freqs = []
                    for root in roots:
                        if np.iscomplex(root) and np.imag(root) > 0:
                            freq = np.angle(root) * sr / (2 * np.pi)
                            if 0 < freq < sr / 2:
                                formant_freqs.append(freq)
                    
                    formant_freqs = sorted(formant_freqs)[:self.n_formants]
                    formants.append(np.array(formant_freqs))
                    
                except Exception:
                    formants.append(np.zeros(self.n_formants))
            
            return formants
            
        except Exception as e:
            self.logger.warning(f"Formant extraction failed: {e}")
            return [np.zeros(self.n_formants)]
    
    def extract_prosody_features(self, y: np.ndarray, sr: int, pitches: np.ndarray) -> Dict[str, Any]:
        """Extract prosody features"""
        try:
            # Pitch statistics
            valid_pitches = pitches[pitches > 0]
            
            prosody = {
                "pitch_mean": np.mean(valid_pitches) if len(valid_pitches) > 0 else 0,
                "pitch_std": np.std(valid_pitches) if len(valid_pitches) > 0 else 0,
                "pitch_range": np.max(valid_pitches) - np.min(valid_pitches) if len(valid_pitches) > 0 else 0,
                "pitch_contour": np.mean(np.diff(valid_pitches)) if len(valid_pitches) > 1 else 0,
                
                # Rhythm features
                "rhythm_regularity": self.calculate_rhythm_regularity(y, sr),
                "speaking_rate": self.calculate_speaking_rate(y, sr),
                
                # Stress patterns
                "stress_pattern": self.calculate_stress_pattern(y, sr),
                
                # Intonation
                "intonation_pattern": self.calculate_intonation_pattern(valid_pitches)
            }
            
            return prosody
            
        except Exception as e:
            self.logger.warning(f"Prosody extraction failed: {e}")
            return {}
    
    def extract_timbre_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract timbre features"""
        try:
            # Spectral characteristics
            stft = librosa.stft(y, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude = np.abs(stft)
            
            timbre = {
                "spectral_centroid_mean": np.mean(librosa.feature.spectral_centroid(S=magnitude)),
                "spectral_centroid_std": np.std(librosa.feature.spectral_centroid(S=magnitude)),
                "spectral_rolloff_mean": np.mean(librosa.feature.spectral_rolloff(S=magnitude)),
                "spectral_rolloff_std": np.std(librosa.feature.spectral_rolloff(S=magnitude)),
                "spectral_bandwidth_mean": np.mean(librosa.feature.spectral_bandwidth(S=magnitude)),
                "spectral_bandwidth_std": np.std(librosa.feature.spectral_bandwidth(S=magnitude)),
                
                # Harmonic characteristics
                "harmonic_ratio": self.calculate_harmonic_ratio(y, sr),
                "noise_ratio": self.calculate_noise_ratio(y, sr),
                
                # Voice quality
                "voice_quality": self.calculate_voice_quality(y, sr),
                "breathiness": self.calculate_breathiness(y, sr),
                "roughness": self.calculate_roughness(y, sr)
            }
            
            return timbre
            
        except Exception as e:
            self.logger.warning(f"Timbre extraction failed: {e}")
            return {}
    
    def calculate_rhythm_regularity(self, y: np.ndarray, sr: int) -> float:
        """Calculate rhythm regularity"""
        try:
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=self.hop_length)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.hop_length)
            
            if len(onset_times) < 2:
                return 0.0
            
            # Calculate inter-onset intervals
            ioi = np.diff(onset_times)
            
            # Calculate regularity as inverse of coefficient of variation
            if np.mean(ioi) > 0:
                cv = np.std(ioi) / np.mean(ioi)
                regularity = 1.0 / (1.0 + cv)
                return regularity
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def calculate_speaking_rate(self, y: np.ndarray, sr: int) -> float:
        """Calculate speaking rate (syllables per second)"""
        try:
            # Simple syllable counting based on energy peaks
            rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
            
            # Find peaks in RMS energy
            from scipy.signal import find_peaks
            peaks, _ = find_peaks(rms, height=np.mean(rms) * 0.5)
            
            # Convert to time
            peak_times = librosa.frames_to_time(peaks, sr=sr, hop_length=self.hop_length)
            
            # Calculate syllables per second
            duration = len(y) / sr
            if duration > 0:
                return len(peak_times) / duration
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def calculate_stress_pattern(self, y: np.ndarray, sr: int) -> float:
        """Calculate stress pattern"""
        try:
            # Analyze energy and pitch patterns
            rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
            pitches, _ = librosa.piptrack(y=y, sr=sr, hop_length=self.hop_length)
            
            # Calculate stress as combination of energy and pitch
            stress_scores = []
            for i in range(len(rms)):
                energy_stress = rms[i] / np.max(rms) if np.max(rms) > 0 else 0
                pitch_stress = pitches[0, i] / np.max(pitches[pitches > 0]) if np.max(pitches[pitches > 0]) > 0 else 0
                stress_scores.append(energy_stress + pitch_stress)
            
            return np.mean(stress_scores)
            
        except Exception:
            return 0.0
    
    def calculate_intonation_pattern(self, pitches: np.ndarray) -> float:
        """Calculate intonation pattern"""
        try:
            if len(pitches) < 2:
                return 0.0
            
            # Calculate pitch contour slope
            pitch_slope = np.mean(np.diff(pitches))
            
            # Normalize by pitch range
            pitch_range = np.max(pitches) - np.min(pitches)
            if pitch_range > 0:
                normalized_slope = pitch_slope / pitch_range
                return normalized_slope
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def calculate_harmonic_ratio(self, y: np.ndarray, sr: int) -> float:
        """Calculate harmonic to noise ratio"""
        try:
            # Use HNR estimation
            stft = librosa.stft(y, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude = np.abs(stft)
            
            # Calculate harmonic and noise components
            harmonic, percussive = librosa.decompose.hpss(magnitude)
            
            # Calculate ratio
            harmonic_energy = np.sum(harmonic ** 2)
            noise_energy = np.sum(percussive ** 2)
            
            if noise_energy > 0:
                return harmonic_energy / noise_energy
            else:
                return 1.0
                
        except Exception:
            return 0.0
    
    def calculate_noise_ratio(self, y: np.ndarray, sr: int) -> float:
        """Calculate noise ratio"""
        try:
            # Calculate zero crossing rate as noise indicator
            zcr = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)
            return np.mean(zcr)
            
        except Exception:
            return 0.0
    
    def calculate_voice_quality(self, y: np.ndarray, sr: int) -> float:
        """Calculate overall voice quality"""
        try:
            # Combine multiple quality indicators
            hnr = self.calculate_harmonic_ratio(y, sr)
            noise_ratio = self.calculate_noise_ratio(y, sr)
            
            # Quality score (higher is better)
            quality = hnr * (1.0 - noise_ratio)
            return min(max(quality, 0.0), 1.0)
            
        except Exception:
            return 0.0
    
    def calculate_breathiness(self, y: np.ndarray, sr: int) -> float:
        """Calculate breathiness"""
        try:
            # Analyze high-frequency content
            stft = librosa.stft(y, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude = np.abs(stft)
            
            # High frequency energy
            freqs = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)
            high_freq_mask = freqs > sr * 0.3  # Above 30% of Nyquist
            
            high_freq_energy = np.sum(magnitude[high_freq_mask, :] ** 2)
            total_energy = np.sum(magnitude ** 2)
            
            if total_energy > 0:
                return high_freq_energy / total_energy
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def calculate_roughness(self, y: np.ndarray, sr: int) -> float:
        """Calculate voice roughness"""
        try:
            # Analyze amplitude modulation
            rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
            
            # Calculate modulation depth
            if len(rms) > 1:
                modulation = np.std(rms) / np.mean(rms) if np.mean(rms) > 0 else 0
                return modulation
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def calculate_spectral_similarity(self, features1: VoiceFeatures, features2: VoiceFeatures) -> SimilarityScore:
        """Calculate spectral similarity"""
        try:
            # Compare spectral features
            centroid_sim = self.cosine_similarity(
                features1.spectral_centroid.flatten(),
                features2.spectral_centroid.flatten()
            )
            
            rolloff_sim = self.cosine_similarity(
                features1.spectral_rolloff.flatten(),
                features2.spectral_rolloff.flatten()
            )
            
            bandwidth_sim = self.cosine_similarity(
                features1.spectral_bandwidth.flatten(),
                features2.spectral_bandwidth.flatten()
            )
            
            # Weighted average
            spectral_score = (centroid_sim * 0.4 + rolloff_sim * 0.3 + bandwidth_sim * 0.3)
            
            return SimilarityScore(
                metric=SimilarityMetric.SPECTRAL_SIMILARITY,
                score=spectral_score,
                confidence=0.8,
                details={
                    "centroid_similarity": centroid_sim,
                    "rolloff_similarity": rolloff_sim,
                    "bandwidth_similarity": bandwidth_sim
                }
            )
            
        except Exception as e:
            self.logger.error(f"Spectral similarity calculation failed: {e}")
            return SimilarityScore(
                metric=SimilarityMetric.SPECTRAL_SIMILARITY,
                score=0.0,
                confidence=0.0,
                details={"error": str(e)}
            )
    
    def calculate_mfcc_similarity(self, features1: VoiceFeatures, features2: VoiceFeatures) -> SimilarityScore:
        """Calculate MFCC similarity"""
        try:
            # Compare MFCC features
            mfcc_sim = self.cosine_similarity(
                features1.mfcc.flatten(),
                features2.mfcc.flatten()
            )
            
            return SimilarityScore(
                metric=SimilarityMetric.MFCC_SIMILARITY,
                score=mfcc_sim,
                confidence=0.9,
                details={"mfcc_similarity": mfcc_sim}
            )
            
        except Exception as e:
            self.logger.error(f"MFCC similarity calculation failed: {e}")
            return SimilarityScore(
                metric=SimilarityMetric.MFCC_SIMILARITY,
                score=0.0,
                confidence=0.0,
                details={"error": str(e)}
            )
    
    def calculate_pitch_similarity(self, features1: VoiceFeatures, features2: VoiceFeatures) -> SimilarityScore:
        """Calculate pitch similarity"""
        try:
            # Extract valid pitches
            pitches1 = features1.pitch[features1.pitch > 0]
            pitches2 = features2.pitch[features2.pitch > 0]
            
            if len(pitches1) == 0 or len(pitches2) == 0:
                return SimilarityScore(
                    metric=SimilarityMetric.PITCH_SIMILARITY,
                    score=0.0,
                    confidence=0.0,
                    details={"error": "No valid pitches found"}
                )
            
            # Compare pitch statistics
            pitch_mean_sim = 1.0 - abs(np.mean(pitches1) - np.mean(pitches2)) / max(np.mean(pitches1), np.mean(pitches2))
            pitch_std_sim = 1.0 - abs(np.std(pitches1) - np.std(pitches2)) / max(np.std(pitches1), np.std(pitches2))
            
            # Normalize to [0, 1]
            pitch_mean_sim = max(0.0, min(1.0, pitch_mean_sim))
            pitch_std_sim = max(0.0, min(1.0, pitch_std_sim))
            
            pitch_score = (pitch_mean_sim * 0.6 + pitch_std_sim * 0.4)
            
            return SimilarityScore(
                metric=SimilarityMetric.PITCH_SIMILARITY,
                score=pitch_score,
                confidence=0.7,
                details={
                    "pitch_mean_similarity": pitch_mean_sim,
                    "pitch_std_similarity": pitch_std_sim
                }
            )
            
        except Exception as e:
            self.logger.error(f"Pitch similarity calculation failed: {e}")
            return SimilarityScore(
                metric=SimilarityMetric.PITCH_SIMILARITY,
                score=0.0,
                confidence=0.0,
                details={"error": str(e)}
            )
    
    def calculate_prosody_similarity(self, features1: VoiceFeatures, features2: VoiceFeatures) -> SimilarityScore:
        """Calculate prosody similarity"""
        try:
            prosody1 = features1.prosody_features
            prosody2 = features2.prosody_features
            
            if not prosody1 or not prosody2:
                return SimilarityScore(
                    metric=SimilarityMetric.PROSODY_SIMILARITY,
                    score=0.0,
                    confidence=0.0,
                    details={"error": "No prosody features available"}
                )
            
            # Compare prosody features
            similarities = []
            
            for key in prosody1:
                if key in prosody2:
                    val1 = prosody1[key]
                    val2 = prosody2[key]
                    
                    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                        if max(abs(val1), abs(val2)) > 0:
                            sim = 1.0 - abs(val1 - val2) / max(abs(val1), abs(val2))
                            similarities.append(max(0.0, min(1.0, sim)))
                        else:
                            similarities.append(1.0)
            
            if similarities:
                prosody_score = np.mean(similarities)
            else:
                prosody_score = 0.0
            
            return SimilarityScore(
                metric=SimilarityMetric.PROSODY_SIMILARITY,
                score=prosody_score,
                confidence=0.6,
                details={"prosody_similarity": prosody_score}
            )
            
        except Exception as e:
            self.logger.error(f"Prosody similarity calculation failed: {e}")
            return SimilarityScore(
                metric=SimilarityMetric.PROSODY_SIMILARITY,
                score=0.0,
                confidence=0.0,
                details={"error": str(e)}
            )
    
    def calculate_timbre_similarity(self, features1: VoiceFeatures, features2: VoiceFeatures) -> SimilarityScore:
        """Calculate timbre similarity"""
        try:
            timbre1 = features1.timbre_features
            timbre2 = features2.timbre_features
            
            if not timbre1 or not timbre2:
                return SimilarityScore(
                    metric=SimilarityMetric.TIMBRE_SIMILARITY,
                    score=0.0,
                    confidence=0.0,
                    details={"error": "No timbre features available"}
                )
            
            # Compare timbre features
            similarities = []
            
            for key in timbre1:
                if key in timbre2:
                    val1 = timbre1[key]
                    val2 = timbre2[key]
                    
                    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                        if max(abs(val1), abs(val2)) > 0:
                            sim = 1.0 - abs(val1 - val2) / max(abs(val1), abs(val2))
                            similarities.append(max(0.0, min(1.0, sim)))
                        else:
                            similarities.append(1.0)
            
            if similarities:
                timbre_score = np.mean(similarities)
            else:
                timbre_score = 0.0
            
            return SimilarityScore(
                metric=SimilarityMetric.TIMBRE_SIMILARITY,
                score=timbre_score,
                confidence=0.7,
                details={"timbre_similarity": timbre_score}
            )
            
        except Exception as e:
            self.logger.error(f"Timbre similarity calculation failed: {e}")
            return SimilarityScore(
                metric=SimilarityMetric.TIMBRE_SIMILARITY,
                score=0.0,
                confidence=0.0,
                details={"error": str(e)}
            )
    
    def calculate_overall_similarity(self, features1: VoiceFeatures, features2: VoiceFeatures) -> SimilarityScore:
        """Calculate overall voice similarity"""
        try:
            # Calculate individual similarities
            spectral_score = self.calculate_spectral_similarity(features1, features2)
            mfcc_score = self.calculate_mfcc_similarity(features1, features2)
            pitch_score = self.calculate_pitch_similarity(features1, features2)
            prosody_score = self.calculate_prosody_similarity(features1, features2)
            timbre_score = self.calculate_timbre_similarity(features1, features2)
            
            # Weighted combination
            weights = self.weights
            overall_score = (
                spectral_score.score * weights["spectral"] +
                mfcc_score.score * weights["mfcc"] +
                pitch_score.score * weights["pitch"] +
                prosody_score.score * weights["prosody"] +
                timbre_score.score * weights["timbre"]
            )
            
            # Calculate confidence as average of individual confidences
            confidence = np.mean([
                spectral_score.confidence,
                mfcc_score.confidence,
                pitch_score.confidence,
                prosody_score.confidence,
                timbre_score.confidence
            ])
            
            return SimilarityScore(
                metric=SimilarityMetric.OVERALL_SIMILARITY,
                score=overall_score,
                confidence=confidence,
                details={
                    "spectral_score": spectral_score.score,
                    "mfcc_score": mfcc_score.score,
                    "pitch_score": pitch_score.score,
                    "prosody_score": prosody_score.score,
                    "timbre_score": timbre_score.score,
                    "weights": weights
                }
            )
            
        except Exception as e:
            self.logger.error(f"Overall similarity calculation failed: {e}")
            return SimilarityScore(
                metric=SimilarityMetric.OVERALL_SIMILARITY,
                score=0.0,
                confidence=0.0,
                details={"error": str(e)}
            )
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Normalize vectors
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(vec1, vec2) / (norm1 * norm2)
            
            # Ensure result is in [0, 1] range
            return max(0.0, min(1.0, similarity))
            
        except Exception:
            return 0.0
    
    def compare_voices(self, audio1_path: str, audio2_path: str) -> Dict[str, Any]:
        """Compare two voice files and return similarity scores"""
        try:
            self.logger.info(f"Comparing voices: {audio1_path} vs {audio2_path}")
            
            # Extract features from both audio files
            features1 = self.extract_voice_features(audio1_path)
            features2 = self.extract_voice_features(audio2_path)
            
            # Calculate all similarity scores
            spectral_score = self.calculate_spectral_similarity(features1, features2)
            mfcc_score = self.calculate_mfcc_similarity(features1, features2)
            pitch_score = self.calculate_pitch_similarity(features1, features2)
            prosody_score = self.calculate_prosody_similarity(features1, features2)
            timbre_score = self.calculate_timbre_similarity(features1, features2)
            overall_score = self.calculate_overall_similarity(features1, features2)
            
            # Compile results
            results = {
                "audio1_path": audio1_path,
                "audio2_path": audio2_path,
                "similarity_scores": {
                    "spectral": {
                        "score": spectral_score.score,
                        "confidence": spectral_score.confidence,
                        "details": spectral_score.details
                    },
                    "mfcc": {
                        "score": mfcc_score.score,
                        "confidence": mfcc_score.confidence,
                        "details": mfcc_score.details
                    },
                    "pitch": {
                        "score": pitch_score.score,
                        "confidence": pitch_score.confidence,
                        "details": pitch_score.details
                    },
                    "prosody": {
                        "score": prosody_score.score,
                        "confidence": prosody_score.confidence,
                        "details": prosody_score.details
                    },
                    "timbre": {
                        "score": timbre_score.score,
                        "confidence": timbre_score.confidence,
                        "details": timbre_score.details
                    },
                    "overall": {
                        "score": overall_score.score,
                        "confidence": overall_score.confidence,
                        "details": overall_score.details
                    }
                },
                "analysis_timestamp": time.time(),
                "config": {
                    "sample_rate": self.sample_rate,
                    "weights": self.weights
                }
            }
            
            self.logger.info(f"Voice comparison completed. Overall similarity: {overall_score.score:.3f}")
            return results
            
        except Exception as e:
            self.logger.error(f"Voice comparison failed: {e}")
            return {
                "error": str(e),
                "audio1_path": audio1_path,
                "audio2_path": audio2_path,
                "analysis_timestamp": time.time()
            }
    
    def batch_compare_voices(self, reference_path: str, comparison_paths: List[str]) -> Dict[str, Any]:
        """Compare reference voice with multiple comparison voices"""
        try:
            self.logger.info(f"Batch comparing {len(comparison_paths)} voices against reference: {reference_path}")
            
            results = {
                "reference_path": reference_path,
                "comparisons": [],
                "batch_timestamp": time.time()
            }
            
            # Extract reference features once
            reference_features = self.extract_voice_features(reference_path)
            
            for comparison_path in comparison_paths:
                try:
                    # Extract comparison features
                    comparison_features = self.extract_voice_features(comparison_path)
                    
                    # Calculate similarities
                    overall_score = self.calculate_overall_similarity(reference_features, comparison_features)
                    
                    comparison_result = {
                        "comparison_path": comparison_path,
                        "overall_similarity": overall_score.score,
                        "confidence": overall_score.confidence,
                        "details": overall_score.details
                    }
                    
                    results["comparisons"].append(comparison_result)
                    
                except Exception as e:
                    self.logger.error(f"Failed to compare {comparison_path}: {e}")
                    results["comparisons"].append({
                        "comparison_path": comparison_path,
                        "error": str(e)
                    })
            
            # Sort by similarity score
            results["comparisons"].sort(key=lambda x: x.get("overall_similarity", 0), reverse=True)
            
            self.logger.info(f"Batch comparison completed. Processed {len(results['comparisons'])} comparisons")
            return results
            
        except Exception as e:
            self.logger.error(f"Batch comparison failed: {e}")
            return {
                "error": str(e),
                "reference_path": reference_path,
                "batch_timestamp": time.time()
            }

def main():
    """Main function for testing voice similarity"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VoiceStudio Voice Similarity Analyzer")
    parser.add_argument("--reference", required=True, help="Reference voice file path")
    parser.add_argument("--comparison", help="Comparison voice file path")
    parser.add_argument("--batch", help="Batch comparison file with paths")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    analyzer = VoiceSimilarityAnalyzer()
    
    if args.batch:
        # Batch comparison
        with open(args.batch, 'r', encoding='utf-8') as f:
            comparison_paths = [line.strip() for line in f if line.strip()]
        
        results = analyzer.batch_compare_voices(args.reference, comparison_paths)
        
    else:
        # Single comparison
        if not args.comparison:
            print("Error: --comparison required for single comparison")
            return
        
        results = analyzer.compare_voices(args.reference, args.comparison)
    
    # Output results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {args.output}")
    else:
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
