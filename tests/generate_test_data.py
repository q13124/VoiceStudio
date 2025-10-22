#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Test Data Generator
Generate comprehensive test data for voice cloning accuracy testing
"""

import json
import numpy as np
from pathlib import Path
import random


class TestDataGenerator:
    def __init__(self, test_data_path):
        self.test_data_path = Path(test_data_path)
        self.reference_path = self.test_data_path / "reference_audio"
        self.text_path = self.test_data_path / "test_texts"
        # Ensure directories exist
        self.reference_path.mkdir(parents=True, exist_ok=True)
        self.text_path.mkdir(parents=True, exist_ok=True)
        (self.test_data_path / "expected_outputs").mkdir(parents=True, exist_ok=True)

    def generate_reference_audio(self, count=10):
        """Generate synthetic reference audio for testing"""
        for i in range(count):
            # Generate synthetic speech-like audio
            duration = random.uniform(3, 10)
            sample_rate = 22050
            samples = int(duration * sample_rate)

            # Create speech-like signal with formants
            t = np.linspace(0, duration, samples)

            # Base frequency (fundamental)
            f0 = random.uniform(80, 200)

            # Formants (speech characteristics)
            formants = [
                random.uniform(200, 800),  # F1
                random.uniform(800, 2000),  # F2
                random.uniform(2000, 3000),  # F3
            ]

            # Generate signal
            signal = np.zeros(samples)
            for harmonic in range(1, 10):
                freq = f0 * harmonic
                amplitude = 1.0 / harmonic
                signal += amplitude * np.sin(2 * np.pi * freq * t)

                # Add formant filtering
                for formant in formants:
                    if abs(freq - formant) < 100:
                        signal += amplitude * 0.5 * np.sin(2 * np.pi * freq * t)

            # Add noise
            noise = np.random.normal(0, 0.1, samples)
            signal += noise

            # Normalize
            signal = signal / np.max(np.abs(signal)) * 0.8

            # Save audio
            output_path = self.reference_path / f"reference_{i:03d}.wav"
            import soundfile as sf

            sf.write(str(output_path), signal, sample_rate)

        print(f"Generated {count} reference audio files")

    def generate_test_texts(self):
        """Generate comprehensive test texts"""
        test_texts = {
            "short": [
                "Hello, this is a test.",
                "Good morning, everyone.",
                "Thank you for listening.",
                "Welcome to VoiceStudio.",
                "This is amazing technology.",
            ],
            "medium": [
                "Welcome to VoiceStudio Ultimate, the professional voice cloning platform. This system provides high-quality voice synthesis using advanced artificial intelligence technology.",
                "Voice cloning technology has revolutionized the way we create audio content. From podcasts to audiobooks, the possibilities are endless with professional-grade voice synthesis.",
                "The alignment lane feature allows precise control over word-level prosody, enabling creators to fine-tune timing, pitch, speed, and energy for each word in their content.",
                "Real-time DSP processing ensures professional audio quality with sub-50 millisecond latency, making VoiceStudio suitable for live applications and real-time voice conversion.",
            ],
            "long": [
                "VoiceStudio Ultimate represents the cutting edge of voice cloning technology, combining multiple advanced engines including XTTS-v2, OpenVoice V2, and CosyVoice 2. Each engine offers unique capabilities optimized for different languages and use cases. The intelligent routing system automatically selects the best engine based on language, quality requirements, and latency constraints. This ensures optimal performance for every voice cloning task, whether it's creating content for podcasts, audiobooks, or professional broadcasting applications.",
                "The professional audio processing pipeline includes advanced DSP modules such as de-essing, equalization, compression, proximity effects, and LUFS normalization. These tools work together to deliver broadcast-quality audio output that meets professional standards. The artifact killer system uses heatmap-driven micro-repair to automatically detect and fix audio artifacts, ensuring consistent quality across all generated content. Watermarking and policy enforcement provide content protection and compliance features essential for commercial applications.",
            ],
            "multilingual": {
                "en": "Hello, this is English text for testing voice cloning accuracy.",
                "es": "Hola, este es texto en español para probar la precisión de clonación de voz.",
                "fr": "Bonjour, ceci est du texte français pour tester la précision du clonage vocal.",
                "de": "Hallo, dies ist deutscher Text zum Testen der Sprachklonierungsgenauigkeit.",
                "zh": "你好，这是中文文本，用于测试语音克隆的准确性。",
                "ja": "こんにちは、これは音声クローニングの精度をテストするための日本語テキストです。",
            },
            "emotional": [
                "I'm so excited about this new technology!",
                "This is absolutely incredible and amazing.",
                "I feel sad about the current situation.",
                "I'm angry about what happened yesterday.",
                "I'm surprised by this unexpected result.",
            ],
            "technical": [
                "The neural network architecture utilizes transformer-based models with attention mechanisms for improved prosody modeling and voice similarity.",
                "Quantization techniques reduce model size while maintaining quality, enabling efficient deployment on various hardware configurations.",
                "Speaker embedding extraction uses deep learning methods to capture unique vocal characteristics and enable accurate voice cloning.",
                "Real-time processing requires optimized inference pipelines with minimal latency while maintaining high-quality audio output.",
            ],
        }

        # Save test texts
        for category, texts in test_texts.items():
            if isinstance(texts, dict):
                for lang, text in texts.items():
                    text_file = self.text_path / f"{category}_{lang}.txt"
                    with open(text_file, "w", encoding="utf-8") as f:
                        f.write(text)
            else:
                for i, text in enumerate(texts):
                    text_file = self.text_path / f"{category}_{i:03d}.txt"
                    with open(text_file, "w", encoding="utf-8") as f:
                        f.write(text)

        print("Generated comprehensive test texts")

    def generate_expected_outputs(self):
        """Generate expected output specifications"""
        expected_outputs = {
            "quality_metrics": {
                "voice_similarity": {
                    "threshold": 0.90,
                    "description": "Similarity between cloned and reference voice",
                },
                "pronunciation_accuracy": {
                    "threshold": 0.85,
                    "description": "Accuracy of pronunciation and phoneme recognition",
                },
                "prosody_match": {
                    "threshold": 0.80,
                    "description": "Match of rhythm, stress, and intonation patterns",
                },
                "emotion_preservation": {
                    "threshold": 0.75,
                    "description": "Preservation of emotional characteristics",
                },
            },
            "performance_metrics": {
                "processing_time": {
                    "target_ms": 5000,
                    "max_ms": 10000,
                    "description": "Time to process voice cloning request",
                },
                "memory_usage": {
                    "target_mb": 2048,
                    "max_mb": 4096,
                    "description": "Peak memory usage during processing",
                },
                "cpu_utilization": {
                    "target_percent": 50,
                    "max_percent": 80,
                    "description": "CPU utilization during processing",
                },
            },
            "audio_quality": {
                "snr": {
                    "target_db": 20,
                    "min_db": 15,
                    "description": "Signal-to-noise ratio",
                },
                "clarity_score": {
                    "target": 0.90,
                    "min": 0.80,
                    "description": "Audio clarity and intelligibility",
                },
                "naturalness_score": {
                    "target": 0.85,
                    "min": 0.75,
                    "description": "Naturalness of generated speech",
                },
            },
        }

        output_path = self.test_data_path / "expected_outputs" / "quality_specs.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(expected_outputs, f, indent=2)

        print(f"Generated expected outputs: {output_path}")


def main():
    # Use repo-relative path for CI compatibility
    repo_root = Path(__file__).parent.parent
    test_data_path = repo_root / "tests" / "data"
    generator = TestDataGenerator(test_data_path)

    print("VoiceStudio Ultimate - Test Data Generator")
    print("=" * 50)

    generator.generate_reference_audio(20)
    generator.generate_test_texts()
    generator.generate_expected_outputs()

    print("=" * 50)
    print("Test data generation complete!")


if __name__ == "__main__":
    main()
