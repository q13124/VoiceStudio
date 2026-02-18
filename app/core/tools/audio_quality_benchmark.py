"""
Audio Quality Benchmark Module for VoiceStudio
Comprehensive audio quality benchmarking and evaluation

Compatible with:
- Python 3.10+
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Import quality metrics (conditional to avoid circular imports)
HAS_QUALITY_METRICS = False
calculate_all_metrics = None
calculate_pesq_score = None
calculate_stoi_score = None
EnhancedQualityMetrics = None

try:
    import importlib.util

    # Try to import quality_metrics module directly
    spec = importlib.util.find_spec("app.core.engines.quality_metrics")
    if spec is not None:
        quality_metrics_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(quality_metrics_module)
            calculate_all_metrics = getattr(
                quality_metrics_module, "calculate_all_metrics", None
            )
            calculate_pesq_score = getattr(
                quality_metrics_module, "calculate_pesq_score", None
            )
            calculate_stoi_score = getattr(
                quality_metrics_module, "calculate_stoi_score", None
            )
            HAS_QUALITY_METRICS = calculate_all_metrics is not None
        except Exception as e:
            logger.warning(f"Failed to load quality_metrics: {e}")

    # Try to import enhanced_quality_metrics
    spec = importlib.util.find_spec("app.core.audio.enhanced_quality_metrics")
    if spec is not None:
        enhanced_metrics_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(enhanced_metrics_module)
            EnhancedQualityMetrics = getattr(
                enhanced_metrics_module, "EnhancedQualityMetrics", None
            )
        except Exception as e:
            logger.warning(f"Failed to load enhanced_quality_metrics: {e}")
except Exception as e:
    logger.warning(f"Quality metrics not available: {e}")

# Import engine router (conditional to avoid circular imports)
HAS_ENGINE_ROUTER = False
EngineRouter = None
global_router = None

try:
    import importlib.util

    # Try to import router module directly
    spec = importlib.util.find_spec("app.core.engines.router")
    if spec is not None:
        router_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(router_module)
            EngineRouter = router_module.EngineRouter
            global_router = getattr(router_module, "router", None)
            HAS_ENGINE_ROUTER = True
        except Exception as e:
            logger.warning(f"Failed to load engine router: {e}")
except Exception as e:
    logger.warning(f"Engine router not available: {e}")


class AudioQualityBenchmark:
    """
    Audio Quality Benchmark for comprehensive quality evaluation.

    Supports:
    - Multi-engine benchmarking
    - Quality metrics evaluation
    - Performance benchmarking
    - Comparative analysis
    - Report generation
    - Batch benchmarking
    """

    def __init__(
        self,
        engine_router: EngineRouter | None = None,
        sample_rate: int = 24000,
    ):
        """
        Initialize Audio Quality Benchmark.

        Args:
            engine_router: Engine router instance (uses global if None)
            sample_rate: Default sample rate for processing
        """
        self.engine_router = engine_router or (
            global_router if HAS_ENGINE_ROUTER else None
        )
        self.sample_rate = sample_rate
        self.quality_metrics = None

        if HAS_QUALITY_METRICS:
            try:
                self.quality_metrics = EnhancedQualityMetrics(sample_rate=sample_rate)
            except Exception as e:
                logger.warning(f"Failed to initialize quality metrics: {e}")

    def benchmark_engine(
        self,
        engine_name: str,
        reference_audio: str | Path,
        test_text: str,
        language: str = "en",
        speaker_wav: str | Path | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Benchmark a single engine.

        Args:
            engine_name: Engine name to benchmark
            reference_audio: Reference audio file path
            test_text: Text to synthesize
            language: Language code
            speaker_wav: Optional speaker reference audio
            **kwargs: Additional engine-specific parameters

        Returns:
            Dictionary with benchmark results
        """
        if not self.engine_router:
            raise RuntimeError("Engine router not available")

        results = {
            "engine": engine_name,
            "success": False,
            "error": None,
            "quality_metrics": {},
            "performance": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            # Get engine
            engine = self.engine_router.get_engine(engine_name, **kwargs)
            if not engine:
                raise ValueError(f"Engine '{engine_name}' not available")

            # Initialize if needed
            if not engine.is_initialized():
                init_start = time.time()
                engine.initialize()
                init_time = time.time() - init_start
                results["performance"]["initialization_time"] = init_time

            # Synthesize
            synth_start = time.time()
            speaker_ref = speaker_wav or reference_audio

            audio = engine.synthesize(
                text=test_text,
                speaker_wav=speaker_ref,
                language=language,
                enhance_quality=True,
                calculate_quality=True,
            )

            synth_time = time.time() - synth_start
            results["performance"]["synthesis_time"] = synth_time

            # Extract quality metrics if returned
            if isinstance(audio, tuple) and len(audio) == 2:
                audio_data, metrics = audio
            else:
                audio_data = audio
                metrics = None

            # Calculate quality metrics if not provided
            if not metrics and self.quality_metrics:
                try:
                    metrics = self.quality_metrics.calculate_all(
                        audio_data, self.sample_rate, include_advanced=True
                    )
                except Exception as e:
                    logger.warning(f"Quality calculation failed: {e}")

            # Calculate additional metrics using reference
            if metrics and isinstance(reference_audio, (str, Path)):
                try:
                    if HAS_QUALITY_METRICS:
                        ref_metrics = calculate_all_metrics(
                            str(reference_audio), audio_data, self.sample_rate
                        )
                        if ref_metrics:
                            metrics.update(ref_metrics)
                except Exception as e:
                    logger.warning(f"Reference comparison failed: {e}")

            results["quality_metrics"] = metrics or {}
            results["success"] = True

        except Exception as e:
            logger.error(f"Benchmark failed for {engine_name}: {e}")
            results["error"] = str(e)

        return results

    def benchmark_multiple_engines(
        self,
        engines: list[str],
        reference_audio: str | Path,
        test_text: str,
        language: str = "en",
        speaker_wav: str | Path | None = None,
        progress_callback: Callable[[dict], None] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """
        Benchmark multiple engines.

        Args:
            engines: List of engine names to benchmark
            reference_audio: Reference audio file path
            test_text: Text to synthesize
            language: Language code
            speaker_wav: Optional speaker reference audio
            progress_callback: Optional progress callback

        Returns:
            Dictionary mapping engine names to benchmark results
        """
        all_results = {}

        for idx, engine_name in enumerate(engines):
            if progress_callback:
                progress_callback(
                    {
                        "engine": engine_name,
                        "progress": idx / len(engines),
                        "status": "benchmarking",
                    }
                )

            results = self.benchmark_engine(
                engine_name=engine_name,
                reference_audio=reference_audio,
                test_text=test_text,
                language=language,
                speaker_wav=speaker_wav,
            )

            all_results[engine_name] = results

            if progress_callback:
                progress_callback(
                    {
                        "engine": engine_name,
                        "progress": (idx + 1) / len(engines),
                        "status": "completed",
                        "results": results,
                    }
                )

        return all_results

    def compare_engines(
        self, benchmark_results: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Compare benchmark results across engines.

        Args:
            benchmark_results: Dictionary of engine results from benchmark_multiple_engines

        Returns:
            Dictionary with comparative analysis
        """
        comparison = {
            "engines": list(benchmark_results.keys()),
            "successful_engines": [],
            "failed_engines": [],
            "quality_rankings": {},
            "performance_rankings": {},
            "best_engine": None,
            "summary": {},
        }

        successful_results = {}
        for engine_name, results in benchmark_results.items():
            if results.get("success"):
                successful_results[engine_name] = results
                comparison["successful_engines"].append(engine_name)
            else:
                comparison["failed_engines"].append(engine_name)

        if not successful_results:
            return comparison

        # Rank by quality metrics
        quality_scores = {}
        for engine_name, results in successful_results.items():
            metrics = results.get("quality_metrics", {})
            # Calculate overall quality score
            mos = metrics.get("mos_score", 0.0) or 0.0
            similarity = metrics.get("similarity", 0.0) or 0.0
            naturalness = metrics.get("naturalness", 0.0) or 0.0
            snr = metrics.get("snr_db", 0.0) or 0.0

            # Normalize and combine
            quality_score = (
                (mos / 5.0) * 0.4
                + similarity * 0.3
                + naturalness * 0.2
                + min(snr / 40.0, 1.0) * 0.1
            )
            quality_scores[engine_name] = quality_score

        # Rank by performance
        performance_scores = {}
        for engine_name, results in successful_results.items():
            perf = results.get("performance", {})
            synth_time = perf.get("synthesis_time", float("inf"))
            init_time = perf.get("initialization_time", 0.0)
            # Lower time = better performance
            performance_scores[engine_name] = 1.0 / (1.0 + synth_time + init_time)

        # Sort rankings
        quality_rankings = sorted(
            quality_scores.items(), key=lambda x: x[1], reverse=True
        )
        performance_rankings = sorted(
            performance_scores.items(), key=lambda x: x[1], reverse=True
        )

        comparison["quality_rankings"] = {
            rank + 1: {"engine": name, "score": score}
            for rank, (name, score) in enumerate(quality_rankings)
        }
        comparison["performance_rankings"] = {
            rank + 1: {"engine": name, "score": score}
            for rank, (name, score) in enumerate(performance_rankings)
        }

        if quality_rankings:
            comparison["best_engine"] = quality_rankings[0][0]

        # Summary statistics
        comparison["summary"] = {
            "total_engines": len(benchmark_results),
            "successful_count": len(successful_results),
            "failed_count": len(comparison["failed_engines"]),
            "average_quality": (
                sum(quality_scores.values()) / len(quality_scores)
                if quality_scores
                else 0.0
            ),
            "average_synthesis_time": (
                sum(
                    r.get("performance", {}).get("synthesis_time", 0.0)
                    for r in successful_results.values()
                )
                / len(successful_results)
                if successful_results
                else 0.0
            ),
        }

        return comparison

    def generate_report(
        self,
        benchmark_results: dict[str, dict[str, Any]],
        comparison: dict[str, Any] | None = None,
        output_path: str | Path | None = None,
    ) -> str:
        """
        Generate benchmark report.

        Args:
            benchmark_results: Dictionary of benchmark results
            comparison: Optional comparison results
            output_path: Optional output file path

        Returns:
            Report text
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("Audio Quality Benchmark Report")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.utcnow().isoformat()}")
        report_lines.append("")

        # Summary
        if comparison:
            report_lines.append("Summary")
            report_lines.append("-" * 80)
            summary = comparison.get("summary", {})
            report_lines.append(f"Total Engines: {summary.get('total_engines', 0)}")
            report_lines.append(f"Successful: {summary.get('successful_count', 0)}")
            report_lines.append(f"Failed: {summary.get('failed_count', 0)}")
            if comparison.get("best_engine"):
                report_lines.append(f"Best Engine: {comparison['best_engine']}")
            report_lines.append("")

        # Engine results
        report_lines.append("Engine Results")
        report_lines.append("-" * 80)
        for engine_name, results in benchmark_results.items():
            report_lines.append(f"\n{engine_name}")
            report_lines.append(
                f"  Status: {'SUCCESS' if results.get('success') else 'FAILED'}"
            )
            if results.get("error"):
                report_lines.append(f"  Error: {results['error']}")
            if results.get("quality_metrics"):
                metrics = results["quality_metrics"]
                report_lines.append(f"  MOS Score: {metrics.get('mos_score', 'N/A')}")
                report_lines.append(f"  Similarity: {metrics.get('similarity', 'N/A')}")
                report_lines.append(
                    f"  Naturalness: {metrics.get('naturalness', 'N/A')}"
                )
                report_lines.append(f"  SNR: {metrics.get('snr_db', 'N/A')} dB")
            if results.get("performance"):
                perf = results["performance"]
                report_lines.append(
                    f"  Synthesis Time: {perf.get('synthesis_time', 'N/A')}s"
                )
                if "initialization_time" in perf:
                    report_lines.append(f"  Init Time: {perf['initialization_time']}s")

        # Rankings
        if comparison and comparison.get("quality_rankings"):
            report_lines.append("\nQuality Rankings")
            report_lines.append("-" * 80)
            for rank, data in comparison["quality_rankings"].items():
                report_lines.append(f"  {rank}. {data['engine']}: {data['score']:.3f}")

        report_text = "\n".join(report_lines)

        # Save to file if requested
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(report_text, encoding="utf-8")
            logger.info(f"Report saved to: {output_path}")

        return report_text

    def save_results_json(
        self,
        benchmark_results: dict[str, dict[str, Any]],
        output_path: str | Path,
        comparison: dict[str, Any] | None = None,
    ):
        """
        Save benchmark results as JSON.

        Args:
            benchmark_results: Dictionary of benchmark results
            comparison: Optional comparison results
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "benchmark_results": benchmark_results,
            "comparison": comparison,
        }
        tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
        try:
            tmp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            os.replace(tmp_path, output_path)
        except Exception:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception as cleanup_e:
                    # GAP-PY-001: Best effort temp file cleanup
                    logger.debug(f"Failed to clean temp file {tmp_path}: {cleanup_e}")
            raise
        logger.info(f"Results saved to: {output_path}")


def create_audio_quality_benchmark(
    engine_router: EngineRouter | None = None,
    sample_rate: int = 24000,
) -> AudioQualityBenchmark:
    """
    Factory function to create an Audio Quality Benchmark instance.

    Args:
        engine_router: Engine router instance (uses global if None)
        sample_rate: Default sample rate for processing

    Returns:
        Initialized AudioQualityBenchmark instance
    """
    return AudioQualityBenchmark(engine_router=engine_router, sample_rate=sample_rate)
