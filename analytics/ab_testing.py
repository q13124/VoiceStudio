"""
VoiceStudio A/B Testing and Quality Prediction System
Implements A/B testing framework and ML-based quality prediction
"""

import numpy as np
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import random
import math

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    import joblib

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available, using simple quality prediction")


@dataclass
class ABTestConfig:
    """A/B test configuration"""

    test_id: str
    name: str
    description: str
    engines: List[str]
    traffic_split: Dict[str, float]  # engine_id -> percentage
    language: str
    quality_tier: str
    min_samples: int = 100
    max_duration_days: int = 7
    success_metric: str = "quality_score"  # quality_score, latency_ms, success_rate
    created_at: datetime = None
    status: str = "active"  # active, completed, paused

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ABTestResult:
    """A/B test result"""

    test_id: str
    engine_id: str
    user_id: str
    job_id: str
    metric_value: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class QualityPredictor:
    """ML-based quality prediction for engine selection"""

    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.feature_importance: Dict[str, List[str]] = {}
        self.model_accuracy: Dict[str, float] = {}
        self._lock = threading.Lock()

        if SKLEARN_AVAILABLE:
            self._init_models()

    def _init_models(self):
        """Initialize ML models for each engine"""
        engines = ["xtts", "openvoice", "coqui", "tortoise"]

        for engine in engines:
            # Random Forest for quality prediction
            self.models[f"{engine}_quality"] = RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42
            )

            # Feature importance tracking
            self.feature_importance[engine] = [
                "text_length",
                "language_complexity",
                "punctuation_density",
                "word_frequency",
                "sentence_count",
                "avg_word_length",
            ]

    def extract_text_features(self, text: str, language: str) -> Dict[str, float]:
        """Extract features from text for quality prediction"""
        features = {}

        # Basic text features
        features["text_length"] = len(text)
        features["word_count"] = len(text.split())
        features["sentence_count"] = text.count(".") + text.count("!") + text.count("?")
        features["avg_word_length"] = features["text_length"] / max(
            1, features["word_count"]
        )

        # Language complexity (simple heuristic)
        features["language_complexity"] = self._get_language_complexity(language)

        # Punctuation density
        punctuation_count = sum(1 for c in text if c in ".,!?;:")
        features["punctuation_density"] = punctuation_count / max(
            1, features["text_length"]
        )

        # Word frequency (simple heuristic based on common words)
        common_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        words = text.lower().split()
        common_word_count = sum(1 for word in words if word in common_words)
        features["word_frequency"] = common_word_count / max(1, len(words))

        return features

    def _get_language_complexity(self, language: str) -> float:
        """Get language complexity score (0-1)"""
        complexity_scores = {
            "en": 0.5,
            "es": 0.6,
            "fr": 0.6,
            "de": 0.7,
            "it": 0.6,
            "pt": 0.6,
            "zh": 0.8,
            "ja": 0.8,
            "ko": 0.8,
            "ru": 0.7,
            "ar": 0.8,
        }
        return complexity_scores.get(language, 0.5)

    def predict_quality(
        self, engine_id: str, text: str, language: str, quality_tier: str
    ) -> float:
        """Predict quality score for an engine"""
        with self._lock:
            if not SKLEARN_AVAILABLE:
                return self._simple_quality_prediction(
                    engine_id, text, language, quality_tier
                )

            model_key = f"{engine_id}_quality"
            if model_key not in self.models:
                return self._simple_quality_prediction(
                    engine_id, text, language, quality_tier
                )

            # Extract features
            features = self.extract_text_features(text, language)
            feature_vector = np.array(
                [
                    features["text_length"],
                    features["language_complexity"],
                    features["punctuation_density"],
                    features["word_frequency"],
                    features["sentence_count"],
                    features["avg_word_length"],
                ]
            ).reshape(1, -1)

            try:
                prediction = self.models[model_key].predict(feature_vector)[0]
                return max(0.0, min(1.0, prediction))  # Clamp to [0, 1]
            except Exception as e:
                print(f"Quality prediction failed for {engine_id}: {e}")
                return self._simple_quality_prediction(
                    engine_id, text, language, quality_tier
                )

    def _simple_quality_prediction(
        self, engine_id: str, text: str, language: str, quality_tier: str
    ) -> float:
        """Simple heuristic-based quality prediction"""
        # Base quality scores by engine
        base_scores = {
            "xtts": 0.85,
            "openvoice": 0.80,
            "coqui": 0.75,
            "tortoise": 0.90,
        }

        base_score = base_scores.get(engine_id, 0.7)

        # Adjust for quality tier
        tier_multipliers = {
            "fast": 0.9,
            "balanced": 1.0,
            "quality": 1.1,
        }
        base_score *= tier_multipliers.get(quality_tier, 1.0)

        # Adjust for text length (very short or very long texts are harder)
        text_length = len(text)
        if text_length < 10:
            base_score *= 0.8
        elif text_length > 500:
            base_score *= 0.9

        # Adjust for language complexity
        complexity = self._get_language_complexity(language)
        base_score *= 1.0 - (complexity - 0.5) * 0.2

        return max(0.0, min(1.0, base_score))

    def train_model(self, engine_id: str, training_data: List[Dict[str, Any]]):
        """Train quality prediction model with historical data"""
        if not SKLEARN_AVAILABLE or not training_data:
            return

        with self._lock:
            model_key = f"{engine_id}_quality"
            if model_key not in self.models:
                return

            # Prepare training data
            X = []
            y = []

            for record in training_data:
                features = record["text_features"]
                feature_vector = [
                    features["text_length"],
                    features["language_complexity"],
                    features["punctuation_density"],
                    features["word_frequency"],
                    features["sentence_count"],
                    features["avg_word_length"],
                ]
                X.append(feature_vector)
                y.append(record["actual_score"])

            if len(X) < 10:  # Need minimum samples
                return

            X = np.array(X)
            y = np.array(y)

            try:
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )

                # Train model
                self.models[model_key].fit(X_train, y_train)

                # Evaluate
                y_pred = self.models[model_key].predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                self.model_accuracy[model_key] = r2

                print(
                    f"Trained {engine_id} quality model: R² = {r2:.3f}, MSE = {mse:.3f}"
                )

            except Exception as e:
                print(f"Failed to train model for {engine_id}: {e}")

    def get_model_info(self, engine_id: str) -> Dict[str, Any]:
        """Get model information"""
        model_key = f"{engine_id}_quality"

        return {
            "engine_id": engine_id,
            "model_type": "RandomForestRegressor" if SKLEARN_AVAILABLE else "Heuristic",
            "accuracy": self.model_accuracy.get(model_key, 0.0),
            "feature_importance": self.feature_importance.get(engine_id, []),
            "trained": model_key in self.models
            and hasattr(self.models[model_key], "feature_importances_"),
        }


class ABTestManager:
    """A/B testing manager for engine comparison"""

    def __init__(self):
        self.active_tests: Dict[str, ABTestConfig] = {}
        self.test_results: Dict[str, List[ABTestResult]] = {}
        self._lock = threading.Lock()

    def create_test(self, config: ABTestConfig) -> str:
        """Create a new A/B test"""
        with self._lock:
            self.active_tests[config.test_id] = config
            self.test_results[config.test_id] = []
            return config.test_id

    def get_test_assignment(self, test_id: str, user_id: str) -> Optional[str]:
        """Get engine assignment for a user in an A/B test"""
        with self._lock:
            if test_id not in self.active_tests:
                return None

            test = self.active_tests[test_id]

            # Check if test is still active
            if test.status != "active":
                return None

            # Check duration
            if datetime.now() - test.created_at > timedelta(
                days=test.max_duration_days
            ):
                test.status = "completed"
                return None

            # Deterministic assignment based on user_id hash
            user_hash = hash(user_id) % 100
            cumulative = 0

            for engine_id, percentage in test.traffic_split.items():
                cumulative += percentage
                if user_hash < cumulative:
                    return engine_id

            # Fallback to first engine
            return list(test.traffic_split.keys())[0]

    def record_result(
        self,
        test_id: str,
        engine_id: str,
        user_id: str,
        job_id: str,
        metric_value: float,
    ):
        """Record A/B test result"""
        with self._lock:
            if test_id not in self.test_results:
                return

            result = ABTestResult(
                test_id=test_id,
                engine_id=engine_id,
                user_id=user_id,
                job_id=job_id,
                metric_value=metric_value,
            )

            self.test_results[test_id].append(result)

    def get_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get A/B test results"""
        with self._lock:
            if test_id not in self.test_results:
                return {}

            results = self.test_results[test_id]
            if not results:
                return {"test_id": test_id, "engines": {}, "summary": {}}

            # Group by engine
            engine_results = {}
            for result in results:
                if result.engine_id not in engine_results:
                    engine_results[result.engine_id] = []
                engine_results[result.engine_id].append(result.metric_value)

            # Calculate statistics
            engine_stats = {}
            for engine_id, values in engine_results.items():
                engine_stats[engine_id] = {
                    "sample_count": len(values),
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "median": np.median(values),
                }

            # Overall summary
            all_values = [r.metric_value for r in results]
            summary = {
                "total_samples": len(results),
                "engines_tested": len(engine_stats),
                "overall_mean": np.mean(all_values),
                "overall_std": np.std(all_values),
            }

            return {
                "test_id": test_id,
                "engines": engine_stats,
                "summary": summary,
                "status": (
                    self.active_tests.get(test_id, {}).status
                    if test_id in self.active_tests
                    else "unknown"
                ),
            }

    def get_significance_test(
        self, test_id: str, engine_a: str, engine_b: str
    ) -> Dict[str, Any]:
        """Perform statistical significance test between two engines"""
        with self._lock:
            if test_id not in self.test_results:
                return {}

            results = self.test_results[test_id]

            # Get results for both engines
            values_a = [r.metric_value for r in results if r.engine_id == engine_a]
            values_b = [r.metric_value for r in results if r.engine_id == engine_b]

            if len(values_a) < 5 or len(values_b) < 5:
                return {"error": "Insufficient samples for significance test"}

            # Simple t-test approximation
            mean_a = np.mean(values_a)
            mean_b = np.mean(values_b)
            std_a = np.std(values_a)
            std_b = np.std(values_b)

            # Pooled standard error
            se = math.sqrt((std_a**2 / len(values_a)) + (std_b**2 / len(values_b)))

            # T-statistic
            t_stat = (mean_a - mean_b) / se if se > 0 else 0

            # Simple significance threshold (t > 2 is roughly p < 0.05)
            significant = abs(t_stat) > 2.0

            return {
                "engine_a": engine_a,
                "engine_b": engine_b,
                "mean_a": mean_a,
                "mean_b": mean_b,
                "std_a": std_a,
                "std_b": std_b,
                "t_statistic": t_stat,
                "significant": significant,
                "sample_size_a": len(values_a),
                "sample_size_b": len(values_b),
            }

    def list_active_tests(self) -> List[Dict[str, Any]]:
        """List all active A/B tests"""
        with self._lock:
            tests = []
            for test_id, test in self.active_tests.items():
                if test.status == "active":
                    result_count = len(self.test_results.get(test_id, []))
                    tests.append(
                        {
                            "test_id": test_id,
                            "name": test.name,
                            "description": test.description,
                            "engines": list(test.traffic_split.keys()),
                            "traffic_split": test.traffic_split,
                            "language": test.language,
                            "quality_tier": test.quality_tier,
                            "result_count": result_count,
                            "created_at": test.created_at.isoformat(),
                        }
                    )
            return tests


# Global instances
_quality_predictor: Optional[QualityPredictor] = None
_ab_test_manager: Optional[ABTestManager] = None


def get_quality_predictor() -> QualityPredictor:
    """Get the global quality predictor instance"""
    global _quality_predictor

    if _quality_predictor is None:
        _quality_predictor = QualityPredictor()

    return _quality_predictor


def get_ab_test_manager() -> ABTestManager:
    """Get the global A/B test manager instance"""
    global _ab_test_manager

    if _ab_test_manager is None:
        _ab_test_manager = ABTestManager()

    return _ab_test_manager


def predict_engine_quality(
    engine_id: str, text: str, language: str, quality_tier: str
) -> float:
    """Predict quality score for an engine"""
    return get_quality_predictor().predict_quality(
        engine_id, text, language, quality_tier
    )


def create_ab_test(
    name: str,
    description: str,
    engines: List[str],
    traffic_split: Dict[str, float],
    language: str,
    quality_tier: str,
) -> str:
    """Create a new A/B test"""
    test_id = f"test_{int(time.time())}"
    config = ABTestConfig(
        test_id=test_id,
        name=name,
        description=description,
        engines=engines,
        traffic_split=traffic_split,
        language=language,
        quality_tier=quality_tier,
    )
    return get_ab_test_manager().create_test(config)


if __name__ == "__main__":
    # Test quality prediction
    predictor = get_quality_predictor()

    # Test prediction
    quality = predictor.predict_quality("xtts", "Hello world", "en", "balanced")
    print(f"Predicted quality for XTTS: {quality}")

    # Test A/B testing
    ab_manager = get_ab_test_manager()

    # Create test
    test_id = create_ab_test(
        name="XTTS vs OpenVoice",
        description="Compare XTTS and OpenVoice for English balanced quality",
        engines=["xtts", "openvoice"],
        traffic_split={"xtts": 50.0, "openvoice": 50.0},
        language="en",
        quality_tier="balanced",
    )

    print(f"Created A/B test: {test_id}")

    # Simulate some results
    for i in range(20):
        engine = "xtts" if i % 2 == 0 else "openvoice"
        ab_manager.record_result(
            test_id,
            engine,
            f"user_{i}",
            f"job_{i}",
            random.uniform(0.7, 0.9) if engine == "xtts" else random.uniform(0.6, 0.8),
        )

    # Get results
    results = ab_manager.get_test_results(test_id)
    print(f"A/B test results: {results}")

    # Significance test
    sig_test = ab_manager.get_significance_test(test_id, "xtts", "openvoice")
    print(f"Significance test: {sig_test}")
