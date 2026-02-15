"""
Quality Benchmarking Example

This example demonstrates how to use the quality benchmarking endpoint
to test multiple engines with the same input and compare quality metrics (IDEA 52).
"""

import time

import requests

BASE_URL = "http://localhost:8000/api"


def run_benchmark(profile_id=None, reference_audio_id=None, test_text="Hello, this is a quality benchmark test.",
                  language="en", engines=None, enhance_quality=True):
    """
    Run quality benchmark across multiple engines.

    Args:
        profile_id: Voice profile ID (alternative to reference_audio_id)
        reference_audio_id: Reference audio ID (alternative to profile_id)
        test_text: Text to synthesize for all engines
        language: Language code (default: "en")
        engines: List of engine names to test (if None, tests all available)
        enhance_quality: Enable quality enhancement (default: True)

    Returns:
        BenchmarkResponse with results for all engines
    """
    url = f"{BASE_URL}/quality/benchmark"

    data = {
        "test_text": test_text,
        "language": language,
        "enhance_quality": enhance_quality
    }

    if profile_id:
        data["profile_id"] = profile_id
    elif reference_audio_id:
        data["reference_audio_id"] = reference_audio_id
    else:
        raise ValueError("Either profile_id or reference_audio_id must be provided")

    if engines:
        data["engines"] = engines

    print("Running quality benchmark...")
    print(f"Test Text: {test_text}")
    if engines:
        print(f"Engines to test: {', '.join(engines)}")
    else:
        print("Testing all available engines")

    start_time = time.time()
    response = requests.post(url, json=data)
    response.raise_for_status()
    elapsed_time = time.time() - start_time

    result = response.json()

    print(f"\n✅ Benchmark complete! (took {elapsed_time:.1f} seconds)")
    print("\n📊 Benchmark Results:")
    print(f"  Total Engines: {result['total_engines']}")
    print(f"  Successful: {result['successful_engines']}")
    print(f"  Failed: {result['total_engines'] - result['successful_engines']}")

    if result.get('benchmark_id'):
        print(f"  Benchmark ID: {result['benchmark_id']}")

    print("\n📈 Per-Engine Results:")
    print("-" * 80)

    # Sort by MOS score (highest first)
    sorted_results = sorted(
        [r for r in result['results'] if r['success']],
        key=lambda x: x.get('quality_metrics', {}).get('mos_score', 0),
        reverse=True
    )

    for i, engine_result in enumerate(sorted_results, 1):
        engine = engine_result['engine']
        metrics = engine_result.get('quality_metrics', {})
        performance = engine_result.get('performance', {})

        print(f"\n{i}. {engine.upper()}")
        print("   Quality Metrics:")
        print(f"     MOS Score: {metrics.get('mos_score', 0):.2f}")
        print(f"     Similarity: {metrics.get('similarity', 0):.3f}")
        print(f"     Naturalness: {metrics.get('naturalness', 0):.3f}")
        print(f"     SNR: {metrics.get('snr_db', 0):.1f} dB")

        if performance:
            print("   Performance:")
            if 'synthesis_time' in performance:
                print(f"     Synthesis Time: {performance['synthesis_time']:.2f}s")
            if 'initialization_time' in performance:
                print(f"     Initialization Time: {performance['initialization_time']:.2f}s")

    # Show failed engines
    failed = [r for r in result['results'] if not r['success']]
    if failed:
        print("\n❌ Failed Engines:")
        for engine_result in failed:
            print(f"   {engine_result['engine']}: {engine_result.get('error', 'Unknown error')}")

    # Summary
    if sorted_results:
        best = sorted_results[0]
        print(f"\n🏆 Best Engine: {best['engine'].upper()}")
        print(f"   MOS Score: {best['quality_metrics'].get('mos_score', 0):.2f}")

    return result


def benchmark_comparison(profile_id, test_texts, engines=None):
    """
    Run benchmarks with multiple test texts and compare results.

    Args:
        profile_id: Voice profile ID
        test_texts: List of test texts to use
        engines: List of engines to test

    Returns:
        Dictionary of benchmark results per text
    """
    results = {}

    for i, text in enumerate(test_texts, 1):
        print(f"\n{'='*80}")
        print(f"Benchmark {i}/{len(test_texts)}: {text[:50]}...")
        print(f"{'='*80}")

        result = run_benchmark(
            profile_id=profile_id,
            test_text=text,
            engines=engines
        )

        results[f"test_{i}"] = result
        time.sleep(1)  # Brief pause between benchmarks

    # Aggregate results
    print(f"\n{'='*80}")
    print("Aggregate Results Across All Tests")
    print(f"{'='*80}")

    engine_scores = {}
    for _test_name, test_result in results.items():
        for engine_result in test_result['results']:
            if engine_result['success']:
                engine = engine_result['engine']
                mos = engine_result.get('quality_metrics', {}).get('mos_score', 0)

                if engine not in engine_scores:
                    engine_scores[engine] = []
                engine_scores[engine].append(mos)

    # Calculate averages
    print("\nAverage MOS Scores Across All Tests:")
    for engine, scores in sorted(engine_scores.items(),
                                 key=lambda x: sum(x[1])/len(x[1]), reverse=True):
        avg_mos = sum(scores) / len(scores)
        print(f"  {engine.upper()}: {avg_mos:.2f} (from {len(scores)} tests)")

    return results


# Example usage
if __name__ == "__main__":
    # Example 1: Basic benchmark
    print("Example 1: Basic Quality Benchmark")
    print("-" * 80)
    result = run_benchmark(
        profile_id="profile-123",
        test_text="This is a quality benchmark test to compare different engines.",
        engines=["xtts", "chatterbox", "tortoise"]
    )

    # Example 2: Benchmark all engines
    print("\n\nExample 2: Benchmark All Available Engines")
    print("-" * 80)
    result = run_benchmark(
        profile_id="profile-123",
        test_text="Testing all engines with the same input for comprehensive comparison."
    )

    # Example 3: Multiple test texts
    print("\n\nExample 3: Benchmark with Multiple Test Texts")
    print("-" * 80)
    results = benchmark_comparison(
        profile_id="profile-123",
        test_texts=[
            "Short test.",
            "This is a longer test sentence with more words to evaluate quality.",
            "Testing emotional content: I'm so excited about this feature!"
        ],
        engines=["xtts", "chatterbox", "tortoise"]
    )

