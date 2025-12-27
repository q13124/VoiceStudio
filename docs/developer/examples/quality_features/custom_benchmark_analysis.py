"""
Example: Custom Benchmark Analysis

This example demonstrates how to perform custom analysis
on quality benchmarking results.
"""

from statistics import mean, stdev
from typing import Any, Dict, List


class BenchmarkResult:
    """Benchmark result model."""
    
    def __init__(self, engine: str, success: bool, quality_metrics: Dict, performance: Dict, error: str = None):
        self.engine = engine
        self.success = success
        self.quality_metrics = quality_metrics
        self.performance = performance
        self.error = error


def analyze_benchmark_results(results: List[BenchmarkResult]) -> Dict[str, Any]:
    """
    Perform custom analysis on benchmark results.
    
    Args:
        results: List of benchmark results
    
    Returns:
        Analysis with recommendations
    """
    successful_results = [r for r in results if r.success]
    
    if not successful_results:
        return {
            "error": "No successful benchmarks",
            "recommendations": ["Check engine availability", "Verify profile/audio exists"]
        }
    
    analysis = {
        "best_engine": None,
        "fastest_engine": None,
        "most_consistent": None,
        "best_value_engine": None,  # Best quality/performance ratio
        "recommendations": [],
        "statistics": {}
    }
    
    # Find best quality engine (highest MOS)
    if successful_results:
        best_quality = max(
            successful_results,
            key=lambda r: r.quality_metrics.get("mos_score", 0)
        )
        analysis["best_engine"] = {
            "engine": best_quality.engine,
            "mos_score": best_quality.quality_metrics.get("mos_score", 0)
        }
    
    # Find fastest engine (lowest synthesis time)
    if successful_results:
        fastest = min(
            successful_results,
            key=lambda r: r.performance.get("synthesis_time", float('inf'))
        )
        analysis["fastest_engine"] = {
            "engine": fastest.engine,
            "synthesis_time": fastest.performance.get("synthesis_time", 0)
        }
    
    # Find most consistent engine (lowest variance in metrics)
    if len(successful_results) > 1:
        # Calculate variance for each engine (using multiple metrics)
        variances = {}
        for result in successful_results:
            metrics = result.quality_metrics
            values = [
                metrics.get("mos_score", 0),
                metrics.get("similarity", 0),
                metrics.get("naturalness", 0)
            ]
            variance = stdev(values) if len(values) > 1 else 0.0
            variances[result.engine] = variance
        
        most_consistent_engine = min(variances, key=variances.get)
        analysis["most_consistent"] = {
            "engine": most_consistent_engine,
            "variance": variances[most_consistent_engine]
        }
    
    # Find best value engine (quality/performance ratio)
    if successful_results:
        value_scores = {}
        for result in successful_results:
            mos = result.quality_metrics.get("mos_score", 0)
            time = result.performance.get("synthesis_time", 1.0)
            value_score = mos / time if time > 0 else 0
            value_scores[result.engine] = value_score
        
        best_value = max(value_scores, key=value_scores.get)
        analysis["best_value_engine"] = {
            "engine": best_value,
            "value_score": value_scores[best_value]
        }
    
    # Generate recommendations
    if analysis["best_engine"] and analysis["fastest_engine"]:
        best = analysis["best_engine"]["engine"]
        fastest = analysis["fastest_engine"]["engine"]
        
        if best != fastest:
            analysis["recommendations"].append(
                f"Use '{best}' for maximum quality, '{fastest}' for speed"
            )
    
    if analysis["best_value_engine"]:
        value_engine = analysis["best_value_engine"]["engine"]
        analysis["recommendations"].append(
            f"'{value_engine}' offers the best quality/performance ratio"
        )
    
    # Calculate statistics
    if successful_results:
        mos_scores = [r.quality_metrics.get("mos_score", 0) for r in successful_results]
        synthesis_times = [r.performance.get("synthesis_time", 0) for r in successful_results]
        
        analysis["statistics"] = {
            "average_mos": mean(mos_scores),
            "average_synthesis_time": mean(synthesis_times),
            "mos_range": (min(mos_scores), max(mos_scores)),
            "time_range": (min(synthesis_times), max(synthesis_times))
        }
    
    return analysis


# Example usage
if __name__ == "__main__":
    # Sample benchmark results
    results = [
        BenchmarkResult(
            engine="xtts",
            success=True,
            quality_metrics={"mos_score": 4.0, "similarity": 0.85, "naturalness": 0.80},
            performance={"synthesis_time": 2.5, "initialization_time": 1.0}
        ),
        BenchmarkResult(
            engine="chatterbox",
            success=True,
            quality_metrics={"mos_score": 4.3, "similarity": 0.90, "naturalness": 0.85},
            performance={"synthesis_time": 5.0, "initialization_time": 2.0}
        ),
        BenchmarkResult(
            engine="tortoise",
            success=True,
            quality_metrics={"mos_score": 4.5, "similarity": 0.95, "naturalness": 0.90},
            performance={"synthesis_time": 15.0, "initialization_time": 3.0}
        )
    ]
    
    # Perform analysis
    analysis = analyze_benchmark_results(results)
    
    print("Custom Benchmark Analysis:")
    print(f"  Best Engine: {analysis['best_engine']['engine']} (MOS: {analysis['best_engine']['mos_score']:.2f})")
    print(f"  Fastest Engine: {analysis['fastest_engine']['engine']} ({analysis['fastest_engine']['synthesis_time']:.1f}s)")
    print(f"  Best Value Engine: {analysis['best_value_engine']['engine']} (Score: {analysis['best_value_engine']['value_score']:.3f})")
    print(f"\n  Recommendations:")
    for rec in analysis["recommendations"]:
        print(f"    • {rec}")
    print(f"\n  Statistics:")
    stats = analysis["statistics"]
    print(f"    Average MOS: {stats['average_mos']:.2f}")
    print(f"    Average Time: {stats['average_synthesis_time']:.1f}s")
    print(f"    MOS Range: {stats['mos_range'][0]:.2f} - {stats['mos_range'][1]:.2f}")

