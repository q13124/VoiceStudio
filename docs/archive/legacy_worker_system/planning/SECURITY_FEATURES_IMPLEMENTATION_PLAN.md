# Security Features Implementation Plan
## Audio Watermarking & Deepfake Detection

**Date:** 2025-01-27  
**Status:** Planning Phase  
**Priority:** CRITICAL (Phase 18)  
**Timeline:** 50-70 days

---

## 📋 Executive Summary

This document provides a detailed implementation plan for two critical security features:
1. **Audio Watermarking** - Content protection and forensic tracking
2. **Deepfake Detection** - Authenticity verification and fraud prevention

These features are essential for legal compliance, ethical use, and building trust in VoiceStudio's voice cloning technology.

---

## 🏗️ Architecture Overview

### Directory Structure

```
app/core/security/
├── __init__.py
├── watermarking.py          # Audio watermarking implementation
├── deepfake_detector.py     # Deepfake detection implementation
├── models.py                # Security data models
└── database.py              # Watermark/detection database

backend/api/routes/
├── security.py              # Security API endpoints
└── watermarking.py          # Watermarking-specific endpoints

src/VoiceStudio.App/
├── Views/Panels/
│   ├── WatermarkingView.xaml
│   ├── WatermarkingView.xaml.cs
│   ├── DeepfakeDetectionView.xaml
│   └── DeepfakeDetectionView.xaml.cs
├── ViewModels/
│   ├── WatermarkingViewModel.cs
│   └── DeepfakeDetectionViewModel.cs
└── Services/
    └── SecurityService.cs   # C# service for security operations
```

---

## 1. AUDIO WATERMARKING IMPLEMENTATION

### 1.1 Core Watermarking Module

**File:** `app/core/security/watermarking.py`

```python
"""
Audio Watermarking Module
Embeds inaudible watermarks in synthesized audio for forensic tracking.
"""

import numpy as np
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional, Tuple, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class WatermarkMethod:
    """Watermarking method types."""
    SPREAD_SPECTRUM = "spread_spectrum"
    ECHO_HIDING = "echo_hiding"
    PHASE_CODING = "phase_coding"
    FREQUENCY_DOMAIN = "frequency_domain"


class AudioWatermarker:
    """
    Embeds and extracts watermarks from audio.
    
    Supports multiple watermarking techniques:
    - Spread spectrum: Robust to compression
    - Echo hiding: Inaudible, preserves quality
    - Phase coding: Frequency domain modification
    - Frequency domain: FFT coefficient embedding
    """
    
    def __init__(
        self,
        default_method: str = WatermarkMethod.SPREAD_SPECTRUM,
        default_strength: float = 0.5
    ):
        """
        Initialize watermarker.
        
        Args:
            default_method: Default watermarking method
            default_strength: Default watermark strength (0.0-1.0)
        """
        self.default_method = default_method
        self.default_strength = default_strength
    
    def embed_watermark(
        self,
        audio: np.ndarray,
        sample_rate: int,
        watermark_data: Dict[str, any],
        method: Optional[str] = None,
        strength: Optional[float] = None,
        key: Optional[str] = None
    ) -> Tuple[np.ndarray, str]:
        """
        Embed watermark in audio.
        
        Args:
            audio: Audio array (mono or stereo)
            sample_rate: Sample rate in Hz
            watermark_data: Dictionary with watermark metadata
                - user_id: User identifier
                - engine: Engine used for synthesis
                - timestamp: Creation timestamp
                - session_id: Session identifier
                - purpose: Purpose of synthesis
            method: Watermarking method (default: self.default_method)
            strength: Watermark strength 0.0-1.0 (default: self.default_strength)
            key: Optional encryption key for watermark
        
        Returns:
            Tuple of (watermarked_audio, watermark_id)
        """
        method = method or self.default_method
        strength = strength or self.default_strength
        
        # Generate watermark ID
        watermark_id = self._generate_watermark_id(watermark_data)
        
        # Encode watermark data
        watermark_bits = self._encode_watermark_data(watermark_data, watermark_id)
        
        # Apply watermarking based on method
        if method == WatermarkMethod.SPREAD_SPECTRUM:
            watermarked = self._embed_spread_spectrum(
                audio, watermark_bits, strength, key
            )
        elif method == WatermarkMethod.ECHO_HIDING:
            watermarked = self._embed_echo_hiding(
                audio, watermark_bits, strength, sample_rate
            )
        elif method == WatermarkMethod.PHASE_CODING:
            watermarked = self._embed_phase_coding(
                audio, watermark_bits, strength, sample_rate
            )
        elif method == WatermarkMethod.FREQUENCY_DOMAIN:
            watermarked = self._embed_frequency_domain(
                audio, watermark_bits, strength, sample_rate
            )
        else:
            raise ValueError(f"Unknown watermarking method: {method}")
        
        logger.info(f"Watermark embedded: {watermark_id} (method: {method}, strength: {strength})")
        
        return watermarked, watermark_id
    
    def extract_watermark(
        self,
        audio: np.ndarray,
        sample_rate: int,
        watermark_id: Optional[str] = None,
        method: Optional[str] = None,
        key: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Extract watermark from audio.
        
        Args:
            audio: Audio array
            sample_rate: Sample rate in Hz
            watermark_id: Expected watermark ID (optional)
            method: Watermarking method (optional, auto-detect if None)
            key: Encryption key (if used)
        
        Returns:
            Dictionary with:
            - watermark_id: Extracted watermark ID
            - watermark_data: Extracted metadata
            - confidence: Extraction confidence (0.0-1.0)
            - method: Detected method
            - verified: Whether watermark matches expected ID
        """
        # Try different methods if not specified
        methods_to_try = [method] if method else [
            WatermarkMethod.SPREAD_SPECTRUM,
            WatermarkMethod.ECHO_HIDING,
            WatermarkMethod.PHASE_CODING,
            WatermarkMethod.FREQUENCY_DOMAIN
        ]
        
        best_result = None
        best_confidence = 0.0
        
        for try_method in methods_to_try:
            try:
                if try_method == WatermarkMethod.SPREAD_SPECTRUM:
                    result = self._extract_spread_spectrum(audio, key)
                elif try_method == WatermarkMethod.ECHO_HIDING:
                    result = self._extract_echo_hiding(audio, sample_rate)
                elif try_method == WatermarkMethod.PHASE_CODING:
                    result = self._extract_phase_coding(audio, sample_rate)
                elif try_method == WatermarkMethod.FREQUENCY_DOMAIN:
                    result = self._extract_frequency_domain(audio, sample_rate)
                else:
                    continue
                
                if result["confidence"] > best_confidence:
                    best_confidence = result["confidence"]
                    best_result = result
                    best_result["method"] = try_method
                    
            except Exception as e:
                logger.debug(f"Extraction failed for {try_method}: {e}")
                continue
        
        if best_result is None:
            return {
                "watermark_id": None,
                "watermark_data": None,
                "confidence": 0.0,
                "method": None,
                "verified": False,
                "error": "No watermark detected"
            }
        
        # Verify against expected ID if provided
        if watermark_id:
            best_result["verified"] = (
                best_result.get("watermark_id") == watermark_id
            )
        else:
            best_result["verified"] = None
        
        return best_result
    
    def detect_tampering(
        self,
        audio: np.ndarray,
        sample_rate: int,
        original_watermark_id: str,
        original_watermark_data: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Detect if watermark has been tampered with or removed.
        
        Args:
            audio: Audio to check
            sample_rate: Sample rate in Hz
            original_watermark_id: Original watermark ID
            original_watermark_data: Original watermark metadata
        
        Returns:
            Dictionary with tampering detection results:
            - is_tampered: Whether tampering detected
            - confidence: Tampering confidence (0.0-1.0)
            - watermark_present: Whether watermark still present
            - watermark_intact: Whether watermark matches original
            - tampering_type: Type of tampering detected
            - details: Detailed analysis
        """
        # Extract watermark
        extracted = self.extract_watermark(
            audio, sample_rate, watermark_id=original_watermark_id
        )
        
        # Check if watermark is present
        watermark_present = extracted["watermark_id"] is not None
        
        # Check if watermark matches
        watermark_intact = extracted.get("verified", False)
        
        # Analyze confidence
        confidence = extracted.get("confidence", 0.0)
        
        # Determine tampering type
        tampering_type = None
        if not watermark_present:
            tampering_type = "removal"
        elif not watermark_intact:
            tampering_type = "modification"
        elif confidence < 0.7:
            tampering_type = "degradation"
        
        is_tampered = tampering_type is not None
        
        return {
            "is_tampered": is_tampered,
            "confidence": 1.0 - confidence if is_tampered else confidence,
            "watermark_present": watermark_present,
            "watermark_intact": watermark_intact,
            "tampering_type": tampering_type,
            "details": {
                "extracted_watermark_id": extracted.get("watermark_id"),
                "extraction_confidence": confidence,
                "original_watermark_id": original_watermark_id
            }
        }
    
    # Private methods for watermarking techniques
    
    def _generate_watermark_id(self, data: Dict) -> str:
        """Generate unique watermark ID from data."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _encode_watermark_data(self, data: Dict, watermark_id: str) -> np.ndarray:
        """Encode watermark data into bit array."""
        # Combine data and ID
        combined = {**data, "watermark_id": watermark_id}
        data_str = json.dumps(combined, sort_keys=True)
        
        # Convert to bits
        data_bytes = data_str.encode()
        bits = np.unpackbits(np.frombuffer(data_bytes, dtype=np.uint8))
        
        return bits
    
    def _embed_spread_spectrum(
        self,
        audio: np.ndarray,
        watermark_bits: np.ndarray,
        strength: float,
        key: Optional[str] = None
    ) -> np.ndarray:
        """Embed watermark using spread spectrum technique."""
        # Implementation: Use pseudo-random sequence to spread watermark
        # across frequency spectrum
        watermarked = audio.copy()
        
        # Generate pseudo-random sequence (use key if provided)
        np.random.seed(hash(key) if key else 42)
        sequence = np.random.randn(len(watermark_bits), len(audio))
        
        # Embed bits
        for i, bit in enumerate(watermark_bits):
            if bit:
                watermarked += strength * sequence[i] * 0.01
        
        return watermarked
    
    def _extract_spread_spectrum(
        self,
        audio: np.ndarray,
        key: Optional[str] = None
    ) -> Dict[str, any]:
        """Extract watermark using spread spectrum technique."""
        # Implementation: Correlate with known sequence
        # This is a simplified version - full implementation would
        # decode the actual watermark data
        return {
            "watermark_id": None,  # Would extract from bits
            "watermark_data": None,
            "confidence": 0.5  # Placeholder
        }
    
    def _embed_echo_hiding(
        self,
        audio: np.ndarray,
        watermark_bits: np.ndarray,
        strength: float,
        sample_rate: int
    ) -> np.ndarray:
        """Embed watermark using echo hiding technique."""
        # Implementation: Add inaudible echoes with encoded data
        watermarked = audio.copy()
        
        # Echo delay (inaudible range: 1-10ms)
        delay_samples = int(sample_rate * 0.005)  # 5ms delay
        
        for i, bit in enumerate(watermark_bits):
            if bit:
                # Add echo at specific delay
                echo = np.zeros_like(audio)
                echo[delay_samples:] = audio[:-delay_samples] * strength * 0.1
                watermarked += echo
        
        return watermarked
    
    def _extract_echo_hiding(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Dict[str, any]:
        """Extract watermark using echo hiding technique."""
        # Implementation: Detect echoes and decode bits
        return {
            "watermark_id": None,
            "watermark_data": None,
            "confidence": 0.5
        }
    
    def _embed_phase_coding(
        self,
        audio: np.ndarray,
        watermark_bits: np.ndarray,
        strength: float,
        sample_rate: int
    ) -> np.ndarray:
        """Embed watermark using phase coding technique."""
        # Implementation: Modify phase in frequency domain
        import scipy.fft as fft
        
        # Convert to frequency domain
        fft_audio = fft.fft(audio)
        phases = np.angle(fft_audio)
        magnitudes = np.abs(fft_audio)
        
        # Modify phases based on watermark bits
        phase_mod = strength * 0.1  # Small phase modification
        
        for i, bit in enumerate(watermark_bits):
            if i < len(phases):
                if bit:
                    phases[i] += phase_mod
                else:
                    phases[i] -= phase_mod
        
        # Convert back to time domain
        watermarked = fft.ifft(magnitudes * np.exp(1j * phases))
        return np.real(watermarked)
    
    def _extract_phase_coding(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Dict[str, any]:
        """Extract watermark using phase coding technique."""
        # Implementation: Analyze phase patterns
        return {
            "watermark_id": None,
            "watermark_data": None,
            "confidence": 0.5
        }
    
    def _embed_frequency_domain(
        self,
        audio: np.ndarray,
        watermark_bits: np.ndarray,
        strength: float,
        sample_rate: int
    ) -> np.ndarray:
        """Embed watermark in frequency domain."""
        import scipy.fft as fft
        
        # Convert to frequency domain
        fft_audio = fft.fft(audio)
        magnitudes = np.abs(fft_audio)
        
        # Embed in FFT coefficients
        for i, bit in enumerate(watermark_bits):
            if i < len(magnitudes):
                if bit:
                    magnitudes[i] *= (1 + strength * 0.01)
                else:
                    magnitudes[i] *= (1 - strength * 0.01)
        
        # Convert back to time domain
        watermarked = fft.ifft(magnitudes * np.exp(1j * np.angle(fft_audio)))
        return np.real(watermarked)
    
    def _extract_frequency_domain(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Dict[str, any]:
        """Extract watermark from frequency domain."""
        # Implementation: Analyze FFT coefficient patterns
        return {
            "watermark_id": None,
            "watermark_data": None,
            "confidence": 0.5
        }
```

### 1.2 Watermark Database

**File:** `app/core/security/database.py`

```python
"""
Watermark Database
Stores watermark metadata and tracking information.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class WatermarkDatabase:
    """Database for storing watermark metadata."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize watermark database.
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = Path.home() / ".voicestudio" / "watermarks.db"
        
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Watermarks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watermarks (
                watermark_id TEXT PRIMARY KEY,
                user_id TEXT,
                engine TEXT,
                timestamp TEXT,
                session_id TEXT,
                purpose TEXT,
                method TEXT,
                strength REAL,
                audio_path TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Verification history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                watermark_id TEXT,
                verified_at TEXT,
                verified_by TEXT,
                result TEXT,
                confidence REAL,
                FOREIGN KEY (watermark_id) REFERENCES watermarks(watermark_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_watermark(
        self,
        watermark_id: str,
        watermark_data: Dict,
        method: str,
        strength: float,
        audio_path: Optional[str] = None
    ):
        """Store watermark metadata."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO watermarks
            (watermark_id, user_id, engine, timestamp, session_id, purpose,
             method, strength, audio_path, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            watermark_id,
            watermark_data.get("user_id"),
            watermark_data.get("engine"),
            watermark_data.get("timestamp"),
            watermark_data.get("session_id"),
            watermark_data.get("purpose"),
            method,
            strength,
            audio_path,
            json.dumps(watermark_data)
        ))
        
        conn.commit()
        conn.close()
    
    def get_watermark(self, watermark_id: str) -> Optional[Dict]:
        """Retrieve watermark metadata."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM watermarks WHERE watermark_id = ?
        """, (watermark_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return {
            "watermark_id": row[0],
            "user_id": row[1],
            "engine": row[2],
            "timestamp": row[3],
            "session_id": row[4],
            "purpose": row[5],
            "method": row[6],
            "strength": row[7],
            "audio_path": row[8],
            "metadata": json.loads(row[9]) if row[9] else {},
            "created_at": row[10]
        }
    
    def log_verification(
        self,
        watermark_id: str,
        result: str,
        confidence: float,
        verified_by: Optional[str] = None
    ):
        """Log watermark verification."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO verifications
            (watermark_id, verified_at, verified_by, result, confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (
            watermark_id,
            datetime.now().isoformat(),
            verified_by,
            result,
            confidence
        ))
        
        conn.commit()
        conn.close()
```

---

## 2. DEEPFAKE DETECTION IMPLEMENTATION

### 2.1 Deepfake Detector Module

**File:** `app/core/security/deepfake_detector.py`

```python
"""
Deepfake Detection Module
Detects synthetic audio using multiple forensic analysis techniques.
"""

import numpy as np
from typing import Dict, List, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DeepfakeDetector:
    """
    Detects deepfake/synthetic audio using multiple detection methods.
    
    Methods:
    - Classifier: Deep learning model for synthetic audio detection
    - Artifact detection: Identifies synthesis artifacts
    - Statistical analysis: Compares to natural speech patterns
    - Frequency analysis: Detects unnatural frequency distributions
    """
    
    def __init__(self):
        """Initialize deepfake detector."""
        self.classifier_model = None  # Load pre-trained model
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained detection models."""
        # TODO: Load ASVspoof or custom models
        # For now, placeholder
        pass
    
    def detect(
        self,
        audio: np.ndarray,
        sample_rate: int,
        methods: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Detect if audio is a deepfake.
        
        Args:
            audio: Audio array
            sample_rate: Sample rate in Hz
            methods: List of detection methods to use
                - "classifier": Deep learning classifier
                - "artifact": Artifact detection
                - "statistical": Statistical analysis
                - "frequency": Frequency analysis
        
        Returns:
            Dictionary with detection results:
            - is_deepfake: Boolean (True if detected as fake)
            - confidence: Confidence score (0.0-1.0)
            - probability: Probability of being fake (0.0-1.0)
            - method_scores: Scores from each method
            - forensic_report: Detailed analysis
        """
        if methods is None:
            methods = ["classifier", "artifact", "statistical", "frequency"]
        
        method_scores = {}
        forensic_report = {
            "artifacts_detected": [],
            "anomalies": [],
            "statistical_deviations": [],
            "frequency_anomalies": []
        }
        
        # Run each detection method
        for method in methods:
            try:
                if method == "classifier":
                    score = self._classifier_detect(audio, sample_rate)
                    method_scores["classifier"] = score
                elif method == "artifact":
                    score, artifacts = self._artifact_detect(audio, sample_rate)
                    method_scores["artifact"] = score
                    forensic_report["artifacts_detected"].extend(artifacts)
                elif method == "statistical":
                    score, deviations = self._statistical_analyze(audio, sample_rate)
                    method_scores["statistical"] = score
                    forensic_report["statistical_deviations"].extend(deviations)
                elif method == "frequency":
                    score, anomalies = self._frequency_analyze(audio, sample_rate)
                    method_scores["frequency"] = score
                    forensic_report["frequency_anomalies"].extend(anomalies)
            except Exception as e:
                logger.warning(f"Detection method {method} failed: {e}")
                method_scores[method] = 0.5  # Neutral score on error
        
        # Combine scores (weighted average)
        weights = {
            "classifier": 0.4,
            "artifact": 0.3,
            "statistical": 0.2,
            "frequency": 0.1
        }
        
        probability = sum(
            method_scores.get(method, 0.5) * weights.get(method, 0.25)
            for method in methods
        )
        
        # Threshold for deepfake detection (0.6 = 60% probability)
        is_deepfake = probability > 0.6
        confidence = abs(probability - 0.5) * 2  # Convert to 0-1 confidence
        
        return {
            "is_deepfake": is_deepfake,
            "confidence": confidence,
            "probability": probability,
            "method_scores": method_scores,
            "forensic_report": forensic_report
        }
    
    def _classifier_detect(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> float:
        """
        Detect using deep learning classifier.
        
        Returns:
            Probability of being fake (0.0-1.0)
        """
        # TODO: Implement classifier detection
        # For now, placeholder that analyzes basic features
        import librosa
        
        # Extract features
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
        
        # Simple heuristic (replace with actual model)
        # Real audio tends to have more variation in MFCCs
        mfcc_variance = np.var(mfccs)
        if mfcc_variance < 0.1:  # Low variance might indicate synthetic
            return 0.7
        else:
            return 0.3
    
    def _artifact_detect(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> tuple[float, List[Dict]]:
        """
        Detect synthesis artifacts.
        
        Returns:
            Tuple of (probability, list of detected artifacts)
        """
        artifacts = []
        artifact_score = 0.0
        
        # Check for unnatural discontinuities
        diff = np.diff(audio)
        large_jumps = np.abs(diff) > np.std(diff) * 3
        if np.any(large_jumps):
            artifacts.append({
                "type": "discontinuity",
                "severity": "high",
                "count": np.sum(large_jumps)
            })
            artifact_score += 0.3
        
        # Check for unnatural frequency patterns
        import scipy.fft as fft
        fft_audio = fft.fft(audio)
        magnitudes = np.abs(fft_audio)
        
        # Look for unnatural peaks
        peaks = np.where(magnitudes > np.mean(magnitudes) * 2)[0]
        if len(peaks) > len(audio) * 0.1:  # Too many peaks
            artifacts.append({
                "type": "unnatural_peaks",
                "severity": "medium",
                "count": len(peaks)
            })
            artifact_score += 0.2
        
        # Normalize score to 0-1
        artifact_score = min(1.0, artifact_score)
        
        return artifact_score, artifacts
    
    def _statistical_analyze(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> tuple[float, List[Dict]]:
        """
        Statistical analysis of audio.
        
        Returns:
            Tuple of (probability, list of deviations)
        """
        deviations = []
        deviation_score = 0.0
        
        # Analyze pitch distribution
        import librosa
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sample_rate)
        
        # Real speech has natural pitch variation
        pitch_variance = np.var(pitches[pitches > 0])
        if pitch_variance < 10:  # Unnaturally stable pitch
            deviations.append({
                "type": "pitch_stability",
                "severity": "medium",
                "value": pitch_variance
            })
            deviation_score += 0.2
        
        # Analyze energy distribution
        energy = librosa.feature.rms(y=audio)[0]
        energy_variance = np.var(energy)
        if energy_variance < 0.001:  # Unnaturally constant energy
            deviations.append({
                "type": "energy_stability",
                "severity": "low",
                "value": energy_variance
            })
            deviation_score += 0.1
        
        deviation_score = min(1.0, deviation_score)
        
        return deviation_score, deviations
    
    def _frequency_analyze(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> tuple[float, List[Dict]]:
        """
        Frequency domain analysis.
        
        Returns:
            Tuple of (probability, list of anomalies)
        """
        anomalies = []
        anomaly_score = 0.0
        
        import scipy.fft as fft
        fft_audio = fft.fft(audio)
        magnitudes = np.abs(fft_audio)
        frequencies = np.fft.fftfreq(len(audio), 1/sample_rate)
        
        # Check for unnatural harmonic structure
        # Real speech has natural formants
        # Synthetic audio might have artificial harmonics
        
        # Find peaks in frequency domain
        peak_indices = np.where(magnitudes > np.mean(magnitudes) * 1.5)[0]
        
        # Check if peaks are evenly spaced (artificial pattern)
        if len(peak_indices) > 3:
            peak_freqs = frequencies[peak_indices]
            peak_diffs = np.diff(np.sort(peak_freqs))
            
            # Check for regular spacing (unnatural)
            if np.std(peak_diffs) < np.mean(peak_diffs) * 0.1:
                anomalies.append({
                    "type": "regular_harmonics",
                    "severity": "high",
                    "spacing": np.mean(peak_diffs)
                })
                anomaly_score += 0.3
        
        anomaly_score = min(1.0, anomaly_score)
        
        return anomaly_score, anomalies
    
    def batch_detect(
        self,
        audio_files: List[Union[str, Path]],
        methods: Optional[List[str]] = None,
        parallel: bool = True
    ) -> List[Dict[str, any]]:
        """
        Detect deepfakes in multiple audio files.
        
        Args:
            audio_files: List of audio file paths
            methods: Detection methods to use
            parallel: Whether to process in parallel
        
        Returns:
            List of detection results
        """
        results = []
        
        for audio_file in audio_files:
            try:
                import soundfile as sf
                audio, sample_rate = sf.read(str(audio_file))
                
                result = self.detect(audio, sample_rate, methods)
                result["file"] = str(audio_file)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {audio_file}: {e}")
                results.append({
                    "file": str(audio_file),
                    "error": str(e),
                    "is_deepfake": None,
                    "confidence": 0.0
                })
        
        return results
```

---

## 3. BACKEND API ENDPOINTS

### 3.1 Security Routes

**File:** `backend/api/routes/security.py`

```python
"""
Security API Routes
Endpoints for watermarking and deepfake detection.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
import numpy as np
import soundfile as sf
from io import BytesIO

from app.core.security.watermarking import AudioWatermarker, WatermarkMethod
from app.core.security.deepfake_detector import DeepfakeDetector
from app.core.security.database import WatermarkDatabase

router = APIRouter(prefix="/api/security", tags=["security"])

# Initialize services
watermarker = AudioWatermarker()
detector = DeepfakeDetector()
watermark_db = WatermarkDatabase()


@router.post("/watermark/embed")
async def embed_watermark(
    audio_file: UploadFile = File(...),
    user_id: str = Form(...),
    engine: str = Form(...),
    session_id: Optional[str] = Form(None),
    purpose: Optional[str] = Form("synthesis"),
    method: Optional[str] = Form(WatermarkMethod.SPREAD_SPECTRUM),
    strength: Optional[float] = Form(0.5)
):
    """
    Embed watermark in audio file.
    
    Returns watermarked audio and watermark ID.
    """
    try:
        # Load audio
        audio_data = await audio_file.read()
        audio, sample_rate = sf.read(BytesIO(audio_data))
        
        # Prepare watermark data
        from datetime import datetime
        watermark_data = {
            "user_id": user_id,
            "engine": engine,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "purpose": purpose
        }
        
        # Embed watermark
        watermarked_audio, watermark_id = watermarker.embed_watermark(
            audio=audio,
            sample_rate=sample_rate,
            watermark_data=watermark_data,
            method=method,
            strength=strength
        )
        
        # Store in database
        watermark_db.store_watermark(
            watermark_id=watermark_id,
            watermark_data=watermark_data,
            method=method,
            strength=strength
        )
        
        # Save watermarked audio
        output_buffer = BytesIO()
        sf.write(output_buffer, watermarked_audio, sample_rate, format='WAV')
        output_buffer.seek(0)
        
        return {
            "watermark_id": watermark_id,
            "watermarked_audio": output_buffer.getvalue(),
            "sample_rate": sample_rate
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/watermark/verify")
async def verify_watermark(
    audio_file: UploadFile = File(...),
    watermark_id: Optional[str] = Form(None)
):
    """
    Verify watermark in audio file.
    """
    try:
        # Load audio
        audio_data = await audio_file.read()
        audio, sample_rate = sf.read(BytesIO(audio_data))
        
        # Extract watermark
        result = watermarker.extract_watermark(
            audio=audio,
            sample_rate=sample_rate,
            watermark_id=watermark_id
        )
        
        # Log verification
        if result["watermark_id"]:
            watermark_db.log_verification(
                watermark_id=result["watermark_id"],
                result="verified" if result.get("verified") else "failed",
                confidence=result.get("confidence", 0.0)
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-deepfake")
async def detect_deepfake(
    audio_file: UploadFile = File(...),
    methods: Optional[str] = Form(None)  # Comma-separated: "classifier,artifact"
):
    """
    Detect if audio is a deepfake.
    """
    try:
        # Load audio
        audio_data = await audio_file.read()
        audio, sample_rate = sf.read(BytesIO(audio_data))
        
        # Parse methods
        method_list = None
        if methods:
            method_list = [m.strip() for m in methods.split(",")]
        
        # Detect
        result = detector.detect(
            audio=audio,
            sample_rate=sample_rate,
            methods=method_list
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-deepfake/batch")
async def batch_detect_deepfake(
    audio_files: List[UploadFile] = File(...),
    methods: Optional[str] = Form(None)
):
    """
    Batch detect deepfakes in multiple audio files.
    """
    try:
        # Save files temporarily
        import tempfile
        import os
        
        temp_files = []
        for audio_file in audio_files:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.write(await audio_file.read())
            temp_file.close()
            temp_files.append(temp_file.name)
        
        # Parse methods
        method_list = None
        if methods:
            method_list = [m.strip() for m in methods.split(",")]
        
        # Batch detect
        results = detector.batch_detect(
            audio_files=temp_files,
            methods=method_list
        )
        
        # Cleanup
        for temp_file in temp_files:
            os.unlink(temp_file)
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watermark/{watermark_id}")
async def get_watermark_info(watermark_id: str):
    """
    Get watermark metadata.
    """
    watermark = watermark_db.get_watermark(watermark_id)
    if watermark is None:
        raise HTTPException(status_code=404, detail="Watermark not found")
    
    return watermark
```

---

## 4. FRONTEND IMPLEMENTATION

### 4.1 C# Service

**File:** `src/VoiceStudio.App/Services/SecurityService.cs`

```csharp
using System;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text.Json;

namespace VoiceStudio.App.Services
{
    public class SecurityService
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;

        public SecurityService(HttpClient httpClient, string baseUrl = "http://localhost:8000")
        {
            _httpClient = httpClient;
            _baseUrl = baseUrl;
        }

        public async Task<WatermarkResult> EmbedWatermarkAsync(
            byte[] audioData,
            string userId,
            string engine,
            string sessionId = null,
            string purpose = "synthesis",
            string method = "spread_spectrum",
            double strength = 0.5
        )
        {
            var formData = new MultipartFormDataContent();
            formData.Add(new ByteArrayContent(audioData), "audio_file", "audio.wav");
            formData.Add(new StringContent(userId), "user_id");
            formData.Add(new StringContent(engine), "engine");
            if (!string.IsNullOrEmpty(sessionId))
                formData.Add(new StringContent(sessionId), "session_id");
            formData.Add(new StringContent(purpose), "purpose");
            formData.Add(new StringContent(method), "method");
            formData.Add(new StringContent(strength.ToString()), "strength");

            var response = await _httpClient.PostAsync($"{_baseUrl}/api/security/watermark/embed", formData);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<WatermarkResult>(json);
        }

        public async Task<DeepfakeDetectionResult> DetectDeepfakeAsync(
            byte[] audioData,
            string[] methods = null
        )
        {
            var formData = new MultipartFormDataContent();
            formData.Add(new ByteArrayContent(audioData), "audio_file", "audio.wav");
            if (methods != null && methods.Length > 0)
                formData.Add(new StringContent(string.Join(",", methods)), "methods");

            var response = await _httpClient.PostAsync($"{_baseUrl}/api/security/detect-deepfake", formData);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<DeepfakeDetectionResult>(json);
        }
    }

    public class WatermarkResult
    {
        public string WatermarkId { get; set; }
        public byte[] WatermarkedAudio { get; set; }
        public int SampleRate { get; set; }
    }

    public class DeepfakeDetectionResult
    {
        public bool IsDeepfake { get; set; }
        public double Confidence { get; set; }
        public double Probability { get; set; }
        public Dictionary<string, double> MethodScores { get; set; }
        public ForensicReport ForensicReport { get; set; }
    }

    public class ForensicReport
    {
        public List<Artifact> ArtifactsDetected { get; set; }
        public List<Anomaly> Anomalies { get; set; }
        public List<Deviation> StatisticalDeviations { get; set; }
        public List<Anomaly> FrequencyAnomalies { get; set; }
    }
}
```

---

## 5. IMPLEMENTATION TIMELINE

### Phase 1: Research & Setup (Week 1-2)
- [ ] Research watermarking algorithms
- [ ] Evaluate deepfake detection models
- [ ] Choose libraries and frameworks
- [ ] Set up database schema
- [ ] Create project structure

### Phase 2: Backend Core (Week 3-5)
- [ ] Implement watermarking module
- [ ] Implement deepfake detector
- [ ] Create database layer
- [ ] Build API endpoints
- [ ] Write unit tests

### Phase 3: Integration (Week 6-7)
- [ ] Integrate watermarking into synthesis pipeline
- [ ] Add automatic watermarking to engines
- [ ] Create verification endpoints
- [ ] Add batch processing

### Phase 4: Frontend (Week 8-9)
- [ ] Create C# SecurityService
- [ ] Build WatermarkingView UI
- [ ] Build DeepfakeDetectionView UI
- [ ] Create ViewModels
- [ ] Add settings integration

### Phase 5: Testing & Refinement (Week 10-12)
- [ ] Test watermark accuracy
- [ ] Test detection accuracy
- [ ] Performance optimization
- [ ] User testing
- [ ] Documentation

---

## 6. DEPENDENCIES

### Python Libraries
```txt
# Watermarking
numpy>=1.24.0
scipy>=1.10.0
librosa>=0.10.0

# Deepfake Detection
torch>=2.0.0  # For deep learning models
transformers>=4.30.0  # For pre-trained models
scikit-learn>=1.3.0

# Database
sqlite3  # Built-in
```

### C# NuGet Packages
```xml
<PackageReference Include="System.Net.Http.Json" Version="7.0.0" />
<PackageReference Include="System.Text.Json" Version="7.0.0" />
```

---

## 7. SUCCESS CRITERIA

### Watermarking
- [ ] Watermark embedded in < 100ms
- [ ] Watermark survives MP3 compression (128kbps)
- [ ] Extraction accuracy > 95%
- [ ] Inaudible to human ear
- [ ] Database tracks all watermarks

### Deepfake Detection
- [ ] Detection accuracy > 90%
- [ ] False positive rate < 5%
- [ ] Processing time < 2 seconds per file
- [ ] Supports batch processing
- [ ] Detailed forensic reports

---

**Status:** Ready for implementation  
**Next Step:** Begin Phase 1 (Research & Setup)

