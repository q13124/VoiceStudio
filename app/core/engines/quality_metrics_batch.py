"""
Quality Metrics Batch Processing

Enhanced batch processing with:
- Parallel processing
- Progress tracking
- Optimized batch calculations
- Error handling
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np

from .quality_metrics import calculate_all_metrics

logger = logging.getLogger(__name__)

# Try importing joblib for parallel processing
try:
    from joblib import Parallel, delayed

    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False
    logger.debug("joblib not available. Parallel processing will be limited.")

# Try importing tqdm for progress bars
try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

    def tqdm(x, **kwargs):
        return x  # No-op if tqdm not available

    logger.debug("tqdm not available. Progress bars will be disabled.")


class BatchProgressTracker:
    """Progress tracker for batch processing."""

    def __init__(
        self,
        total: int,
        description: str = "Processing",
        show_progress: bool = True,
    ):
        """
        Initialize progress tracker.

        Args:
            total: Total number of items
            description: Description for progress display
            show_progress: Whether to show progress
        """
        self.total = total
        self.description = description
        self.show_progress = show_progress
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()

        if self.show_progress and HAS_TQDM:
            self.pbar = tqdm(
                total=total,
                desc=description,
                unit="file",
                ncols=100,
            )
        else:
            self.pbar = None

    def update(self, count: int = 1, failed: bool = False):
        """
        Update progress.

        Args:
            count: Number of items completed
            failed: Whether items failed
        """
        self.completed += count
        if failed:
            self.failed += count

        if self.pbar:
            self.pbar.update(count)
            if failed:
                self.pbar.set_postfix({"failed": self.failed})
        else:
            if self.completed % max(1, self.total // 10) == 0:
                logger.info(
                    f"{self.description}: {self.completed}/{self.total} "
                    f"({self.completed/self.total*100:.1f}%)"
                )

    def finish(self):
        """Finish progress tracking."""
        if self.pbar:
            self.pbar.close()

        elapsed = time.time() - self.start_time
        logger.info(
            f"{self.description} completed: {self.completed}/{self.total} "
            f"({self.failed} failed) in {elapsed:.2f}s"
        )


def _process_single_audio(
    audio_path: str | Path,
    reference_path: str | Path | None = None,
    sample_rate: int = 22050,
    use_cache: bool = True,
) -> tuple[str, dict[str, Any] | None, str | None]:
    """
    Process a single audio file for quality metrics.

    Args:
        audio_path: Path to audio file
        reference_path: Optional path to reference audio
        sample_rate: Sample rate
        use_cache: Whether to use cache

    Returns:
        Tuple of (audio_path, metrics_dict, error_message)
    """
    try:
        metrics = calculate_all_metrics(
            audio=audio_path,
            reference_audio=reference_path,
            sample_rate=sample_rate,
            use_cache=use_cache,
        )
        return (str(audio_path), metrics, None)
    except Exception as e:
        error_msg = f"Error processing {audio_path}: {e!s}"
        logger.warning(error_msg)
        return (str(audio_path), None, error_msg)


def calculate_quality_metrics_batch(
    audio_files: list[str | Path],
    reference_files: list[str | Path] | None = None,
    sample_rate: int = 22050,
    use_cache: bool = True,
    parallel: bool = True,
    max_workers: int | None = None,
    use_processes: bool = False,
    show_progress: bool = True,
) -> dict[str, Any]:
    """
    Calculate quality metrics for a batch of audio files with parallel processing.

    Args:
        audio_files: List of audio file paths
        reference_files: Optional list of reference audio file paths
        sample_rate: Target sample rate
        use_cache: Whether to use cache for metrics
        parallel: Whether to use parallel processing
        max_workers: Maximum number of workers (None = auto)
        use_processes: Whether to use processes instead of threads
        show_progress: Whether to show progress bar

    Returns:
        Dictionary containing:
        - results: Dict mapping file paths to metrics
        - errors: Dict mapping file paths to error messages
        - summary: Summary statistics
        - timing: Processing timing information
    """
    start_time = time.time()

    if not audio_files:
        return {
            "results": {},
            "errors": {},
            "summary": {"total": 0, "successful": 0, "failed": 0},
            "timing": {"total_time": 0.0},
        }

    # Prepare tasks
    tasks = []
    for i, audio_path in enumerate(audio_files):
        reference_path = (
            reference_files[i] if reference_files and i < len(reference_files) else None
        )
        tasks.append((audio_path, reference_path))

    # Initialize progress tracker
    progress = BatchProgressTracker(
        total=len(tasks),
        description="Calculating quality metrics",
        show_progress=show_progress,
    )

    results = {}
    errors = {}

    if parallel:
        # Use parallel processing
        executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
        workers = max_workers if max_workers else None

        with executor_class(max_workers=workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(
                    _process_single_audio,
                    audio_path,
                    reference_path,
                    sample_rate,
                    use_cache,
                ): (audio_path, reference_path)
                for audio_path, reference_path in tasks
            }

            # Process completed tasks
            for future in as_completed(futures):
                audio_path, reference_path = futures[future]
                try:
                    path, metrics, error = future.result()
                    if error:
                        errors[path] = error
                        progress.update(1, failed=True)
                    else:
                        results[path] = metrics
                        progress.update(1, failed=False)
                except Exception as e:
                    error_msg = f"Unexpected error: {e!s}"
                    errors[str(audio_path)] = error_msg
                    progress.update(1, failed=True)
                    logger.error(f"Error processing {audio_path}: {e}")

    else:
        # Sequential processing
        for audio_path, reference_path in tasks:
            path, metrics, error = _process_single_audio(
                audio_path, reference_path, sample_rate, use_cache
            )
            if error:
                errors[path] = error
                progress.update(1, failed=True)
            else:
                results[path] = metrics
                progress.update(1, failed=False)

    progress.finish()

    # Calculate summary statistics
    total_time = time.time() - start_time
    successful = len(results)
    failed = len(errors)

    summary = {
        "total": len(audio_files),
        "successful": successful,
        "failed": failed,
        "success_rate": successful / len(audio_files) if audio_files else 0.0,
    }

    # Calculate average metrics if pandas available
    try:
        import pandas as pd

        if results:
            # Convert results to DataFrame for statistics
            metrics_list = []
            for path, metrics in results.items():
                if metrics:
                    row = {"file": path}
                    row.update(metrics)
                    metrics_list.append(row)

            if metrics_list:
                df = pd.DataFrame(metrics_list)
                summary["average_metrics"] = df.select_dtypes(include=[np.number]).mean().to_dict()
                summary["std_metrics"] = df.select_dtypes(include=[np.number]).std().to_dict()
    except ImportError:
        logger.debug("pandas not available for batch metric summaries")

    return {
        "results": results,
        "errors": errors,
        "summary": summary,
        "timing": {
            "total_time": total_time,
            "time_per_file": total_time / len(audio_files) if audio_files else 0.0,
        },
    }


def calculate_quality_metrics_batch_optimized(
    audio_files: list[str | Path],
    reference_files: list[str | Path] | None = None,
    sample_rate: int = 22050,
    use_cache: bool = True,
    batch_size: int = 10,
    show_progress: bool = True,
) -> dict[str, Any]:
    """
    Calculate quality metrics for a batch using optimized batch processing.

    Uses joblib for efficient parallel processing with batching.

    Args:
        audio_files: List of audio file paths
        reference_files: Optional list of reference audio file paths
        sample_rate: Target sample rate
        use_cache: Whether to use cache
        batch_size: Batch size for processing
        show_progress: Whether to show progress

    Returns:
        Dictionary with results, errors, and summary
    """
    if not HAS_JOBLIB:
        # Fallback to standard batch processing
        logger.warning("joblib not available, using standard batch processing")
        return calculate_quality_metrics_batch(
            audio_files=audio_files,
            reference_files=reference_files,
            sample_rate=sample_rate,
            use_cache=use_cache,
            parallel=True,
            show_progress=show_progress,
        )

    start_time = time.time()

    # Prepare tasks
    tasks = []
    for i, audio_path in enumerate(audio_files):
        reference_path = (
            reference_files[i] if reference_files and i < len(reference_files) else None
        )
        tasks.append((audio_path, reference_path))

    # Process with joblib
    results_list = Parallel(n_jobs=-1, batch_size=batch_size, verbose=0)(
        delayed(_process_single_audio)(audio_path, reference_path, sample_rate, use_cache)
        for audio_path, reference_path in tasks
    )

    # Process results
    results = {}
    errors = {}

    for path, metrics, error in results_list:
        if error:
            errors[path] = error
        else:
            results[path] = metrics

    total_time = time.time() - start_time

    # Calculate summary
    summary = {
        "total": len(audio_files),
        "successful": len(results),
        "failed": len(errors),
        "success_rate": len(results) / len(audio_files) if audio_files else 0.0,
    }

    return {
        "results": results,
        "errors": errors,
        "summary": summary,
        "timing": {
            "total_time": total_time,
            "time_per_file": total_time / len(audio_files) if audio_files else 0.0,
        },
    }


# Export
__all__ = [
    "BatchProgressTracker",
    "calculate_quality_metrics_batch",
    "calculate_quality_metrics_batch_optimized",
]
