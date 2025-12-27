# Quality Features Developer Guide

Complete developer guide for extending and customizing quality testing and comparison features in VoiceStudio Quantum+.

## Overview

This guide provides detailed instructions for developers who want to extend, customize, or integrate quality testing and comparison features into their own applications.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Extending A/B Testing](#extending-ab-testing)
3. [Customizing Engine Recommendations](#customizing-engine-recommendations)
4. [Adding New Quality Metrics](#adding-new-quality-metrics)
5. [Extending Quality Benchmarking](#extending-quality-benchmarking)
6. [Customizing Quality Dashboard](#customizing-quality-dashboard)
7. [Plugin Development](#plugin-development)
8. [Code Examples](#code-examples)

---

## Getting Started

### Prerequisites

- Python 3.10+ for backend development
- C# .NET 8 for frontend development
- Understanding of FastAPI and WinUI 3
- Familiarity with voice synthesis engines

### Project Structure

```
VoiceStudio/
├── backend/api/routes/
│   ├── eval_abx.py          # A/B testing endpoints
│   └── quality.py           # Recommendation, benchmarking, dashboard
├── app/core/engines/
│   └── quality_optimizer.py # Recommendation algorithm
├── src/VoiceStudio.App/
│   ├── Views/Panels/
│   │   └── ABTestingView.xaml
│   └── ViewModels/
│       └── ABTestingViewModel.cs
└── docs/developer/
    └── QUALITY_FEATURES_DEVELOPER_GUIDE.md (this file)
```

---

## Extending A/B Testing

### Adding Custom Comparison Metrics

**Backend Extension:**

```python
# backend/api/routes/eval_abx.py

def calculate_custom_metrics(audio_path: str) -> Dict[str, Any]:
    """Calculate custom quality metrics."""
    # Your custom metric calculation
    return {
        "custom_metric_1": value1,
        "custom_metric_2": value2
    }

@router.post("/start")
def start(req: AbxStartRequest) -> ApiOk:
    # ... existing code ...
    
    # Add custom metrics
    sample_a_metrics = calculate_custom_metrics(sample_a_path)
    sample_b_metrics = calculate_custom_metrics(sample_b_path)
    
    # Include in comparison
    comparison["custom_metrics"] = {
        "sample_a": sample_a_metrics,
        "sample_b": sample_b_metrics
    }
    
    return ApiOk()
```

**Frontend Extension:**

```csharp
// src/VoiceStudio.App/ViewModels/ABTestingViewModel.cs

public string CustomMetricsDisplay
{
    get
    {
        if (TestResults?.CustomMetrics == null)
            return "No custom metrics";
        
        var custom = TestResults.CustomMetrics;
        return $"Custom Metric 1: {custom.SampleA.Metric1:F2}\n" +
               $"Custom Metric 2: {custom.SampleB.Metric2:F2}";
    }
}
```

### Adding New Comparison Algorithms

```python
# backend/api/routes/eval_abx.py

def compare_samples_advanced(sample_a: Dict, sample_b: Dict) -> Dict:
    """Advanced comparison algorithm."""
    # Your custom comparison logic
    winner = determine_winner(sample_a, sample_b)
    
    return {
        "overall_winner": winner,
        "confidence": calculate_confidence(sample_a, sample_b),
        "detailed_analysis": perform_detailed_analysis(sample_a, sample_b)
    }
```

---

## Customizing Engine Recommendations

### Adding New Engines to Recommendations

**Step 1: Define Engine Characteristics**

```python
# app/core/engines/quality_optimizer.py

ENGINE_CHARACTERISTICS = {
    "xtts": {
        "tier": "standard",
        "mos_range": (3.5, 4.2),
        "similarity_range": (0.80, 0.90),
        "naturalness_range": (0.75, 0.85),
        "speed": "fast"
    },
    "chatterbox": {
        "tier": "high",
        "mos_range": (4.0, 4.5),
        "similarity_range": (0.85, 0.95),
        "naturalness_range": (0.80, 0.90),
        "speed": "medium"
    },
    "tortoise": {
        "tier": "ultra",
        "mos_range": (4.2, 4.8),
        "similarity_range": (0.90, 0.98),
        "naturalness_range": (0.85, 0.95),
        "speed": "slow"
    },
    "your_new_engine": {  # Add your engine
        "tier": "high",
        "mos_range": (4.0, 4.4),
        "similarity_range": (0.85, 0.93),
        "naturalness_range": (0.80, 0.88),
        "speed": "medium"
    }
}
```

**Step 2: Update Recommendation Algorithm**

```python
# app/core/engines/quality_optimizer.py

def suggest_engine(self, target_metrics: Optional[Dict] = None) -> str:
    """Suggest engine with custom logic."""
    # Your custom recommendation logic
    scores = {}
    
    for engine_name, characteristics in ENGINE_CHARACTERISTICS.items():
        score = self._calculate_engine_score(
            engine_name,
            characteristics,
            target_metrics or self.target_metrics
        )
        scores[engine_name] = score
    
    # Return engine with highest score
    return max(scores, key=scores.get)
```

### Customizing Scoring Algorithm

```python
# app/core/engines/quality_optimizer.py

def _calculate_engine_score(
    self,
    engine_name: str,
    characteristics: Dict,
    target_metrics: Dict
) -> float:
    """Custom scoring algorithm."""
    score = 0.0
    
    # Tier match score (0-40 points)
    tier_match = self._calculate_tier_match(characteristics["tier"], self.target_tier)
    score += tier_match * 40
    
    # MOS score match (0-30 points)
    if "mos_score" in target_metrics:
        mos_match = self._calculate_metric_match(
            characteristics["mos_range"],
            target_metrics["mos_score"]
        )
        score += mos_match * 30
    
    # Similarity match (0-20 points)
    if "similarity" in target_metrics:
        similarity_match = self._calculate_metric_match(
            characteristics["similarity_range"],
            target_metrics["similarity"]
        )
        score += similarity_match * 20
    
    # Speed bonus (0-10 points)
    speed_bonus = self._calculate_speed_bonus(characteristics["speed"])
    score += speed_bonus * 10
    
    return score
```

---

## Adding New Quality Metrics

### Backend Metric Calculation

```python
# app/core/engines/quality_metrics.py

def calculate_custom_metric(audio_path: str, reference_path: Optional[str] = None) -> float:
    """Calculate a custom quality metric."""
    import librosa
    import numpy as np
    
    # Load audio
    audio, sr = librosa.load(audio_path, sr=None)
    
    # Your custom metric calculation
    # Example: Spectral centroid stability
    spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
    stability = 1.0 / (1.0 + np.std(spectral_centroids))
    
    return float(stability)

def calculate_all_metrics(audio_path: str, reference_path: Optional[str] = None) -> Dict[str, Any]:
    """Calculate all quality metrics including custom ones."""
    metrics = {
        "mos_score": calculate_mos_score(audio_path),
        "similarity": calculate_similarity(audio_path, reference_path),
        "naturalness": calculate_naturalness(audio_path),
        "snr_db": calculate_snr(audio_path),
        # Add custom metrics
        "custom_stability": calculate_custom_metric(audio_path, reference_path)
    }
    
    return metrics
```

### Frontend Metric Display

```csharp
// src/VoiceStudio.App/ViewModels/ABTestingViewModel.cs

public string ExtendedMetricsDisplay
{
    get
    {
        if (SampleA?.QualityMetrics == null)
            return "No metrics available";
        
        var qm = SampleA.QualityMetrics;
        return $"MOS: {qm.MosScore:F2}\n" +
               $"Similarity: {qm.Similarity:F3}\n" +
               $"Naturalness: {qm.Naturalness:F3}\n" +
               $"SNR: {qm.SnrDb:F1} dB\n" +
               $"Custom Stability: {qm.CustomStability:F3}";  // New metric
    }
}
```

---

## Extending Quality Benchmarking

### Adding Custom Benchmark Types

```python
# backend/api/routes/quality.py

class CustomBenchmarkRequest(BaseModel):
    """Custom benchmark request."""
    profile_id: Optional[str] = None
    test_texts: List[str]  # Multiple test texts
    engines: List[str]
    benchmark_type: str = "standard"  # standard, speed, quality, custom
    custom_metrics: Optional[List[str]] = None

@router.post("/benchmark/custom", response_model=BenchmarkResponse)
async def run_custom_benchmark(request: CustomBenchmarkRequest):
    """Run custom benchmark with multiple texts."""
    results = []
    
    for test_text in request.test_texts:
        for engine_name in request.engines:
            # Run synthesis
            audio_result = await synthesize_with_engine(
                engine_name,
                request.profile_id,
                test_text
            )
            
            # Calculate metrics (including custom)
            metrics = calculate_all_metrics(
                audio_result["audio_path"],
                custom_metrics=request.custom_metrics
            )
            
            results.append({
                "engine": engine_name,
                "test_text": test_text,
                "quality_metrics": metrics
            })
    
    # Aggregate results
    aggregated = aggregate_custom_benchmark_results(results)
    
    return BenchmarkResponse(
        results=aggregated,
        total_engines=len(request.engines),
        successful_engines=len([r for r in aggregated if r["success"]])
    )
```

### Adding Benchmark Presets

```python
# backend/api/routes/quality.py

BENCHMARK_PRESETS = {
    "quick": {
        "engines": ["xtts", "chatterbox"],
        "test_text": "Quick test.",
        "enhance_quality": False
    },
    "comprehensive": {
        "engines": None,  # All engines
        "test_text": "This is a comprehensive benchmark test.",
        "enhance_quality": True
    },
    "speed_focused": {
        "engines": ["xtts", "chatterbox"],
        "test_text": "Speed test.",
        "enhance_quality": False,
        "focus": "performance"
    }
}

@router.post("/benchmark/preset")
async def run_benchmark_preset(preset_name: str, profile_id: str):
    """Run benchmark with preset configuration."""
    preset = BENCHMARK_PRESETS.get(preset_name)
    if not preset:
        raise HTTPException(404, f"Preset '{preset_name}' not found")
    
    request = BenchmarkRequest(
        profile_id=profile_id,
        test_text=preset["test_text"],
        engines=preset.get("engines"),
        enhance_quality=preset.get("enhance_quality", True)
    )
    
    return await run_benchmark(request)
```

---

## Customizing Quality Dashboard

### Adding Custom Dashboard Widgets

```python
# backend/api/routes/quality.py

@router.get("/dashboard/custom")
async def get_custom_dashboard(
    project_id: Optional[str] = None,
    days: int = 30,
    widgets: Optional[List[str]] = None
):
    """Get custom dashboard with specified widgets."""
    widgets = widgets or ["overview", "trends"]
    
    dashboard_data = {}
    
    if "overview" in widgets:
        dashboard_data["overview"] = await get_dashboard_overview(project_id, days)
    
    if "trends" in widgets:
        dashboard_data["trends"] = await get_dashboard_trends(project_id, days)
    
    if "distribution" in widgets:
        dashboard_data["distribution"] = await get_dashboard_distribution(project_id, days)
    
    if "custom_analysis" in widgets:
        dashboard_data["custom_analysis"] = await perform_custom_analysis(project_id, days)
    
    return dashboard_data
```

### Adding Custom Alerts

```python
# backend/api/routes/quality.py

def generate_custom_alerts(quality_data: Dict) -> List[Dict]:
    """Generate custom quality alerts."""
    alerts = []
    
    # Custom alert: Quality degradation
    if quality_data.get("trend", {}).get("mos_score_trend") == "decreasing":
        alerts.append({
            "type": "quality_degradation",
            "severity": "high",
            "message": "Quality is decreasing over time",
            "recommendation": "Review recent synthesis settings"
        })
    
    # Custom alert: Engine performance
    if quality_data.get("engine_performance", {}).get("slow_engines"):
        alerts.append({
            "type": "performance_issue",
            "severity": "medium",
            "message": "Some engines are performing slowly",
            "recommendation": "Consider using faster engines"
        })
    
    return alerts
```

---

## Plugin Development

### Creating a Quality Feature Plugin

**Plugin Structure:**

```python
# plugins/quality_custom/quality_custom_plugin.py

from app.core.plugins_api import QualityFeaturePlugin

class CustomQualityPlugin(QualityFeaturePlugin):
    """Custom quality feature plugin."""
    
    def get_plugin_info(self):
        return {
            "name": "Custom Quality Features",
            "version": "1.0.0",
            "description": "Custom quality testing features"
        }
    
    def extend_ab_testing(self, test_request, test_results):
        """Extend A/B testing with custom logic."""
        # Your custom A/B testing extension
        test_results["custom_analysis"] = self.custom_analysis(test_request)
        return test_results
    
    def extend_benchmarking(self, benchmark_request, benchmark_results):
        """Extend benchmarking with custom logic."""
        # Your custom benchmarking extension
        benchmark_results["custom_metrics"] = self.calculate_custom_metrics(benchmark_results)
        return benchmark_results
```

**Plugin Manifest:**

```json
{
  "plugin_id": "quality_custom",
  "name": "Custom Quality Features",
  "version": "1.0.0",
  "type": "quality_feature",
  "entry_point": "quality_custom_plugin.CustomQualityPlugin",
  "dependencies": []
}
```

---

## Code Examples

### Example 1: Custom A/B Testing Comparison

```python
# Custom comparison algorithm

def custom_ab_comparison(sample_a: Dict, sample_b: Dict) -> Dict:
    """Custom A/B comparison with weighted scoring."""
    weights = {
        "mos_score": 0.4,
        "similarity": 0.3,
        "naturalness": 0.2,
        "snr_db": 0.1
    }
    
    scores = {}
    for sample_name, sample_data in [("A", sample_a), ("B", sample_b)]:
        score = 0.0
        metrics = sample_data["quality_metrics"]
        
        for metric, weight in weights.items():
            normalized_value = normalize_metric(metric, metrics[metric])
            score += normalized_value * weight
        
        scores[sample_name] = score
    
    winner = "A" if scores["A"] > scores["B"] else "B"
    
    return {
        "overall_winner": winner,
        "scores": scores,
        "difference": abs(scores["A"] - scores["B"])
    }
```

### Example 2: Custom Engine Recommendation

```python
# Custom recommendation with user preferences

def recommend_engine_with_preferences(
    requirements: Dict,
    user_preferences: Dict
) -> str:
    """Recommend engine considering user preferences."""
    base_recommendation = get_engine_recommendation(requirements)
    
    # Adjust based on preferences
    if user_preferences.get("preferred_engine"):
        preferred = user_preferences["preferred_engine"]
        if engine_meets_requirements(preferred, requirements):
            return preferred
    
    if user_preferences.get("speed_priority") == "high":
        # Prefer faster engines
        return recommend_fast_engine(requirements)
    
    return base_recommendation
```

### Example 3: Custom Benchmark Analysis

```python
# Custom benchmark analysis

def analyze_benchmark_results(results: List[BenchmarkResult]) -> Dict:
    """Perform custom analysis on benchmark results."""
    analysis = {
        "best_engine": None,
        "fastest_engine": None,
        "most_consistent": None,
        "recommendations": []
    }
    
    # Find best quality engine
    best_quality = max(results, key=lambda r: r.quality_metrics["mos_score"])
    analysis["best_engine"] = best_quality.engine
    
    # Find fastest engine
    fastest = min(results, key=lambda r: r.performance["synthesis_time"])
    analysis["fastest_engine"] = fastest.engine
    
    # Find most consistent
    most_consistent = min(results, key=lambda r: r.quality_metrics.get("variance", 0))
    analysis["most_consistent"] = most_consistent.engine
    
    # Generate recommendations
    if best_quality.engine != fastest.engine:
        analysis["recommendations"].append(
            f"Use {best_quality.engine} for quality, {fastest.engine} for speed"
        )
    
    return analysis
```

---

## Best Practices

### Performance

1. **Cache Results:** Cache recommendation and benchmark results when possible
2. **Async Processing:** Use async for long-running operations
3. **Progress Updates:** Provide WebSocket updates for benchmarks
4. **Resource Management:** Limit concurrent operations

### Error Handling

1. **Graceful Degradation:** Fall back to simpler algorithms if advanced features fail
2. **Clear Error Messages:** Provide actionable error messages
3. **Logging:** Log errors for debugging
4. **Validation:** Validate all inputs

### Code Organization

1. **Separation of Concerns:** Keep business logic separate from API routes
2. **Reusability:** Create reusable utility functions
3. **Documentation:** Document all custom extensions
4. **Testing:** Write tests for custom features

---

## Troubleshooting

### Common Issues

**Issue: Recommendations not accurate**
- Check engine characteristics are correct
- Verify quality metrics calculation
- Review scoring algorithm weights

**Issue: Benchmarks too slow**
- Use parallel processing
- Limit number of engines
- Use shorter test texts

**Issue: Dashboard not updating**
- Check data aggregation logic
- Verify database queries (if using database)
- Check caching configuration

---

## Resources

- [Quality Features Architecture](QUALITY_FEATURES_ARCHITECTURE.md)
- [Quality Features Diagrams](QUALITY_FEATURES_DIAGRAMS.md)
- [API Reference](../api/API_REFERENCE.md)
- [Code Examples](../api/examples/)

---

**Last Updated:** 2025-01-27  
**Version:** 1.0.0

