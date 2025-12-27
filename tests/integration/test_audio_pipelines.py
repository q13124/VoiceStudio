"""
Audio Pipeline Integration Tests

Tests complete audio processing pipelines including preprocessing, enhancement, and post-processing.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


def generate_test_audio(duration_seconds: float = 1.0, sample_rate: int = 22050) -> np.ndarray:
    """Generate test audio signal."""
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), False)
    audio = np.sin(2 * np.pi * 440.0 * t)
    audio = audio * 0.5
    return audio.astype(np.float32)


class TestAudioPipelines:
    """Test complete audio processing pipelines."""

    def test_preprocessing_pipeline(self):
        """Test complete preprocessing pipeline."""
        try:
            from app.core.audio import EnhancedPreprocessor, create_enhanced_preprocessor

            # Create preprocessor
            preprocessor = create_enhanced_preprocessor(sample_rate=24000)

            # Generate test audio
            audio = generate_test_audio(duration_seconds=2.0, sample_rate=24000)

            # Process through pipeline
            processed = preprocessor.process(
                audio,
                remove_dc=True,
                highpass_cutoff=80.0,
                denoise=True,
                normalize=True,
                trim_silence=True
            )

            assert processed is not None, "Preprocessing returned None"
            assert isinstance(processed, np.ndarray), "Preprocessing returned wrong type"
            assert len(processed) > 0, "Preprocessing returned empty audio"

        except ImportError:
            pytest.skip("Preprocessing modules not available")

    def test_enhancement_pipeline(self):
        """Test complete enhancement pipeline."""
        try:
            from app.core.audio import enhance_voice_quality

            # Generate test audio
            audio = generate_test_audio(duration_seconds=2.0, sample_rate=24000)

            # Enhance
            enhanced = enhance_voice_quality(
                audio,
                sample_rate=24000,
                normalize=True,
                denoise=True,
                remove_artifacts=True
            )

            assert enhanced is not None, "Enhancement returned None"
            assert isinstance(enhanced, np.ndarray), "Enhancement returned wrong type"
            assert len(enhanced) > 0, "Enhancement returned empty audio"

        except ImportError:
            pytest.skip("Enhancement modules not available")

    def test_optimized_pipeline(self):
        """Test optimized batch processing pipeline."""
        try:
            from app.core.audio.pipeline_optimized import (
                OptimizedAudioPipeline,
                create_optimized_pipeline,
            )

            # Create pipeline
            pipeline = create_optimized_pipeline(sample_rate=24000)

            # Generate test audio files (simulated)
            audio_arrays = [
                generate_test_audio(duration_seconds=1.0, sample_rate=24000)
                for _ in range(3)
            ]

            # Process batch
            results = pipeline.process_batch(
                audio_arrays,
                max_workers=2,
                preprocessing=True,
                enhancement=True,
                postprocessing=True
            )

            assert results is not None, "Batch processing returned None"
            assert len(results) == len(audio_arrays), \
                "Batch processing returned wrong number of results"
            assert all(isinstance(audio, np.ndarray) for audio in results), \
                "Batch processing returned wrong types"

        except ImportError:
            pytest.skip("Optimized pipeline not available")

    def test_quality_metrics_pipeline(self):
        """Test quality metrics calculation pipeline."""
        try:
            from app.core.engines.quality_metrics import calculate_all_metrics

            # Generate test audio
            audio = generate_test_audio(duration_seconds=2.0, sample_rate=24000)
            reference = generate_test_audio(duration_seconds=2.0, sample_rate=24000)

            # Calculate metrics
            metrics = calculate_all_metrics(
                audio,
                reference_audio=reference,
                sample_rate=24000,
                use_cache=True
            )

            assert metrics is not None, "Metrics calculation returned None"
            assert isinstance(metrics, dict), "Metrics returned wrong type"
            assert "mos_score" in metrics or "similarity" in metrics, \
                "Metrics missing expected keys"

        except ImportError:
            pytest.skip("Quality metrics not available")

    def test_effects_pipeline(self):
        """Test effects processing pipeline."""
        try:
            from app.core.audio import PostFXProcessor, create_post_fx_processor

            # Create processor
            processor = create_post_fx_processor(sample_rate=24000)

            # Configure effects
            processor.set_compressor(
                threshold=-12.0,
                ratio=4.0,
                attack=5.0,
                release=50.0
            )

            processor.set_reverb(
                room_size=0.5,
                damping=0.3,
                wet_level=0.2
            )

            # Generate test audio
            audio = generate_test_audio(duration_seconds=2.0, sample_rate=24000)

            # Process
            processed = processor.process(audio)

            assert processed is not None, "Effects processing returned None"
            assert isinstance(processed, np.ndarray), "Effects processing returned wrong type"
            assert len(processed) > 0, "Effects processing returned empty audio"

        except ImportError:
            pytest.skip("Effects processing not available")

    def test_mastering_pipeline(self):
        """Test mastering pipeline."""
        try:
            from app.core.audio import MasteringRack, create_mastering_rack

            # Create mastering rack
            rack = create_mastering_rack(sample_rate=24000)

            # Configure mastering
            rack.set_multiband_compressor(
                low_threshold=-12.0,
                mid_threshold=-10.0,
                high_threshold=-8.0
            )

            rack.set_limiter(
                threshold=-1.0,
                release=50.0
            )

            rack.set_loudness_target(-23.0)

            # Generate test audio
            audio = generate_test_audio(duration_seconds=2.0, sample_rate=24000)

            # Master
            mastered = rack.master(audio)

            assert mastered is not None, "Mastering returned None"
            assert isinstance(mastered, np.ndarray), "Mastering returned wrong type"
            assert len(mastered) > 0, "Mastering returned empty audio"

        except ImportError:
            pytest.skip("Mastering not available")

    def test_complete_audio_workflow(self):
        """Test complete audio processing workflow."""
        try:
            from app.core.audio import (
                EnhancedPreprocessor,
                create_enhanced_preprocessor,
                enhance_voice_quality,
                PostFXProcessor,
                create_post_fx_processor,
            )

            # Generate test audio
            audio = generate_test_audio(duration_seconds=2.0, sample_rate=24000)

            # Step 1: Preprocess
            preprocessor = create_enhanced_preprocessor(sample_rate=24000)
            processed = preprocessor.process(
                audio,
                remove_dc=True,
                denoise=True,
                normalize=True
            )

            # Step 2: Enhance
            enhanced = enhance_voice_quality(
                processed,
                sample_rate=24000,
                normalize=True,
                denoise=True
            )

            # Step 3: Apply effects
            processor = create_post_fx_processor(sample_rate=24000)
            processor.set_compressor(threshold=-12.0, ratio=4.0, attack=5.0, release=50.0)
            final = processor.process(enhanced)

            assert final is not None, "Complete workflow returned None"
            assert isinstance(final, np.ndarray), "Complete workflow returned wrong type"
            assert len(final) > 0, "Complete workflow returned empty audio"

        except ImportError:
            pytest.skip("Audio processing modules not available")

