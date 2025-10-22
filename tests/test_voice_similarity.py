# tests/test_voice_similarity.py
# Tests for voice similarity scoring system

import pytest
import numpy as np
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_similarity_analyzer import VoiceSimilarityAnalyzer, VoiceFeatures

class TestVoiceSimilarityAnalyzer:
    def setup_method(self):
        """Setup test environment"""
        self.analyzer = VoiceSimilarityAnalyzer()
        
        # Create test audio files
        self.create_test_audio_files()
    
    def create_test_audio_files(self):
        """Create test audio files"""
        # Create temporary audio files with different characteristics
        self.test_files = []
        
        # File 1: High frequency content
        audio1 = self.generate_test_audio(frequency=440, duration=2.0)
        self.test_files.append(self.save_test_audio(audio1, "test1.wav"))
        
        # File 2: Low frequency content
        audio2 = self.generate_test_audio(frequency=220, duration=2.0)
        self.test_files.append(self.save_test_audio(audio2, "test2.wav"))
        
        # File 3: Similar to file 1
        audio3 = self.generate_test_audio(frequency=440, duration=2.0)
        self.test_files.append(self.save_test_audio(audio3, "test3.wav"))
    
    def generate_test_audio(self, frequency=440, duration=2.0, sample_rate=22050):
        """Generate test audio signal"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = np.sin(2 * np.pi * frequency * t)
        return audio
    
    def save_test_audio(self, audio, filename):
        """Save test audio to temporary file"""
        import librosa
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        librosa.output.write_wav(temp_file.name, audio, 22050)
        return temp_file.name
    
    def teardown_method(self):
        """Cleanup test files"""
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def test_feature_extraction(self):
        """Test voice feature extraction"""
        features = self.analyzer.extract_voice_features(self.test_files[0])
        
        assert isinstance(features, VoiceFeatures)
        assert features.mfcc is not None
        assert features.spectral_centroid is not None
        assert features.pitch is not None
        assert features.prosody_features is not None
        assert features.timbre_features is not None
    
    def test_spectral_similarity(self):
        """Test spectral similarity calculation"""
        features1 = self.analyzer.extract_voice_features(self.test_files[0])
        features2 = self.analyzer.extract_voice_features(self.test_files[1])
        
        score = self.analyzer.calculate_spectral_similarity(features1, features2)
        
        assert score.score >= 0.0
        assert score.score <= 1.0
        assert score.confidence >= 0.0
        assert score.confidence <= 1.0
    
    def test_mfcc_similarity(self):
        """Test MFCC similarity calculation"""
        features1 = self.analyzer.extract_voice_features(self.test_files[0])
        features2 = self.analyzer.extract_voice_features(self.test_files[1])
        
        score = self.analyzer.calculate_mfcc_similarity(features1, features2)
        
        assert score.score >= 0.0
        assert score.score <= 1.0
        assert score.confidence >= 0.0
        assert score.confidence <= 1.0
    
    def test_pitch_similarity(self):
        """Test pitch similarity calculation"""
        features1 = self.analyzer.extract_voice_features(self.test_files[0])
        features2 = self.analyzer.extract_voice_features(self.test_files[1])
        
        score = self.analyzer.calculate_pitch_similarity(features1, features2)
        
        assert score.score >= 0.0
        assert score.score <= 1.0
        assert score.confidence >= 0.0
        assert score.confidence <= 1.0
    
    def test_overall_similarity(self):
        """Test overall similarity calculation"""
        features1 = self.analyzer.extract_voice_features(self.test_files[0])
        features2 = self.analyzer.extract_voice_features(self.test_files[1])
        
        score = self.analyzer.calculate_overall_similarity(features1, features2)
        
        assert score.score >= 0.0
        assert score.score <= 1.0
        assert score.confidence >= 0.0
        assert score.confidence <= 1.0
    
    def test_voice_comparison(self):
        """Test complete voice comparison"""
        results = self.analyzer.compare_voices(self.test_files[0], self.test_files[1])
        
        assert "similarity_scores" in results
        assert "overall" in results["similarity_scores"]
        assert results["similarity_scores"]["overall"]["score"] >= 0.0
        assert results["similarity_scores"]["overall"]["score"] <= 1.0
    
    def test_batch_comparison(self):
        """Test batch voice comparison"""
        results = self.analyzer.batch_compare_voices(
            self.test_files[0], 
            self.test_files[1:]
        )
        
        assert "comparisons" in results
        assert len(results["comparisons"]) == 2
        assert all("overall_similarity" in comp for comp in results["comparisons"])
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        vec1 = np.array([1, 2, 3])
        vec2 = np.array([1, 2, 3])
        
        similarity = self.analyzer.cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 1e-6
        
        vec3 = np.array([-1, -2, -3])
        similarity = self.analyzer.cosine_similarity(vec1, vec3)
        assert abs(similarity - (-1.0)) < 1e-6
    
    def test_quality_levels(self):
        """Test quality level determination"""
        # Test different similarity scores
        assert self.analyzer.get_quality_level(0.95) == "excellent"
        assert self.analyzer.get_quality_level(0.85) == "good"
        assert self.analyzer.get_quality_level(0.75) == "fair"
        assert self.analyzer.get_quality_level(0.65) == "poor"
        assert self.analyzer.get_quality_level(0.45) == "very_poor"

if __name__ == "__main__":
    pytest.main([__file__])
