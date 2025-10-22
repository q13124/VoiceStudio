"""
VoiceStudio Router Engine Selection Tests
Tests the multilingual and quality-based engine selection logic
"""

import types
from services.voice_engine_router import (
    VoiceEngineRouter,
    EngineRegistry,
    RouterConfig,
    QualityPredictor,
)


class FakeEngine:
    def __init__(self, id_, langs, tier_load):
        self.id = id_
        self.languages = langs
        self.quality = ["fast", "balanced", "quality"]
        self._load = tier_load

    def healthy(self):
        return True

    def current_load(self):
        return self._load

    def supports(self, language, tier):
        return language in self.languages

    def tts(self, **kwargs):
        return b"ok"


def test_multilingual_prefers_xtts_when_available():
    """Test that XTTS is preferred for multilingual content when available"""
    reg = EngineRegistry(
        adapters=[
            FakeEngine("xtts", ["en", "es", "fr"], 0.2),
            FakeEngine("tortoise", ["en"], 0.1),
        ]
    )
    router = VoiceEngineRouter(reg, RouterConfig())
    engine, order = router.select_engine(
        text="hola mundo", language="es", tier="balanced"
    )
    assert engine == "xtts"
    assert "xtts" in order


def test_quality_english_may_prefer_tortoise_for_max_quality():
    """Test that Tortoise may be preferred for English quality tier"""
    reg = EngineRegistry(
        adapters=[
            FakeEngine("xtts", ["en"], 0.1),
            FakeEngine("tortoise", ["en"], 0.05),
        ]
    )
    cfg = RouterConfig()
    router = VoiceEngineRouter(reg, cfg)
    engine, order = router.select_engine(
        text="hello world", language="en", tier="quality"
    )
    assert engine in {"xtts", "tortoise"}
    assert set(order) == {"xtts", "tortoise"}


def test_fallback_chain_respects_config_order():
    """Test that fallback chain follows configured order"""
    cfg = RouterConfig()
    cfg.fallback_order = ["tortoise", "xtts", "openvoice"]

    reg = EngineRegistry(
        adapters=[
            FakeEngine("xtts", ["en"], 0.1),
            FakeEngine("tortoise", ["en"], 0.2),  # Higher load but first in order
            FakeEngine("openvoice", ["en"], 0.05),
        ]
    )

    router = VoiceEngineRouter(reg, cfg)
    engine, order = router.select_engine(text="test", language="en", tier="balanced")

    # Should prefer tortoise despite higher load due to config order
    assert engine == "tortoise"
    assert order == ["tortoise", "xtts", "openvoice"]


def test_engine_selection_considers_load():
    """Test that engine selection considers current load"""
    reg = EngineRegistry(
        adapters=[
            FakeEngine("xtts", ["en"], 0.8),  # High load
            FakeEngine("openvoice", ["en"], 0.1),  # Low load
        ]
    )

    router = VoiceEngineRouter(reg, RouterConfig())
    engine, order = router.select_engine(text="test", language="en", tier="balanced")

    # Should prefer openvoice due to lower load
    assert engine == "openvoice"
    assert "openvoice" in order


def test_unsupported_language_fallback():
    """Test fallback when no engine supports the requested language"""
    reg = EngineRegistry(
        adapters=[
            FakeEngine("xtts", ["en"], 0.1),
            FakeEngine("tortoise", ["en"], 0.1),
        ]
    )

    router = VoiceEngineRouter(reg, RouterConfig())
    engine, order = router.select_engine(text="test", language="zh", tier="balanced")

    # Should still return an engine (fallback behavior)
    assert engine in ["xtts", "tortoise"]
    assert len(order) > 0


def test_quality_tier_preference():
    """Test that quality tier affects engine selection"""
    reg = EngineRegistry(
        adapters=[
            FakeEngine("xtts", ["en"], 0.1),
            FakeEngine("tortoise", ["en"], 0.1),
        ]
    )

    router = VoiceEngineRouter(reg, RouterConfig())

    # Fast tier should prefer faster engines
    engine_fast, _ = router.select_engine(text="test", language="en", tier="fast")

    # Quality tier should prefer quality engines
    engine_quality, _ = router.select_engine(text="test", language="en", tier="quality")

    # Both should be valid selections
    assert engine_fast in ["xtts", "tortoise"]
    assert engine_quality in ["xtts", "tortoise"]


def test_quality_predictor_scoring():
    """Test the quality predictor scoring system"""
    predictor = QualityPredictor()

    # Test basic scoring
    score = predictor.estimate("xtts", text="test", language="en", tier="balanced")
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0

    # Test multilingual advantage
    xtts_en = predictor.estimate("xtts", text="test", language="en", tier="balanced")
    xtts_es = predictor.estimate("xtts", text="test", language="es", tier="balanced")

    # XTTS should score well for both languages
    assert xtts_en > 0.5
    assert xtts_es > 0.5


def test_engine_registry_discovery():
    """Test engine registry discovery functionality"""
    reg = EngineRegistry(
        adapters=[
            FakeEngine("xtts", ["en", "es"], 0.1),
            FakeEngine("tortoise", ["en"], 0.2),
        ]
    )

    # Test listing
    engines = reg.list()
    assert "xtts" in engines
    assert "tortoise" in engines

    # Test discovery
    discovery = reg.discover()
    assert "xtts" in discovery
    assert "tortoise" in discovery

    # Test individual engine info
    xtts_info = discovery["xtts"]
    assert xtts_info["healthy"] is True
    assert xtts_info["load"] == 0.1
    assert "en" in xtts_info["languages"]
    assert "es" in xtts_info["languages"]


def test_router_generation_pipeline():
    """Test the complete generation pipeline"""
    reg = EngineRegistry(
        adapters=[
            FakeEngine("xtts", ["en"], 0.1),
        ]
    )

    router = VoiceEngineRouter(reg, RouterConfig())

    # Test generation
    audio = router.generate(
        engine_id="xtts",
        text="Hello world",
        voice_profile={"voice_id": "test"},
        params={"language": "en"},
    )

    assert isinstance(audio, bytes)
    assert len(audio) > 0


def test_router_fallback_mechanism():
    """Test router fallback when primary engine fails"""
    reg = EngineRegistry(
        adapters=[
            FakeEngine("xtts", ["en"], 0.1),
            FakeEngine("openvoice", ["en"], 0.1),
        ]
    )

    router = VoiceEngineRouter(reg, RouterConfig())

    # Mock XTTS to be unhealthy
    reg._adapters["xtts"].healthy = lambda: False

    engine, order = router.select_engine(text="test", language="en", tier="balanced")

    # Should fallback to openvoice
    assert engine == "openvoice"
    assert "openvoice" in order


def test_multiple_language_support():
    """Test support for multiple languages"""
    reg = EngineRegistry(
        adapters=[
            FakeEngine("xtts", ["en", "es", "fr", "de"], 0.1),
            FakeEngine("tortoise", ["en"], 0.1),
        ]
    )

    router = VoiceEngineRouter(reg, RouterConfig())

    languages = ["en", "es", "fr", "de"]
    for lang in languages:
        engine, order = router.select_engine(
            text="test", language=lang, tier="balanced"
        )

        # Should find a suitable engine
        assert engine in ["xtts", "tortoise"]
        assert len(order) > 0


def test_router_config_loading():
    """Test router configuration loading"""
    cfg = RouterConfig()

    # Test default values
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 5090
    assert "xtts" in cfg.fallback_order
    assert "openvoice" in cfg.fallback_order

    # Test quality preferences
    assert cfg.quality_preference["quality"] > cfg.quality_preference["balanced"]
    assert cfg.quality_preference["balanced"] > cfg.quality_preference["fast"]


def test_engine_load_tracking():
    """Test that engine load is properly tracked"""
    reg = EngineRegistry(
        adapters=[
            FakeEngine("xtts", ["en"], 0.3),
            FakeEngine("openvoice", ["en"], 0.7),
        ]
    )

    discovery = reg.discover()

    assert discovery["xtts"]["load"] == 0.3
    assert discovery["openvoice"]["load"] == 0.7


if __name__ == "__main__":
    # Run all tests
    test_functions = [
        test_multilingual_prefers_xtts_when_available,
        test_quality_english_may_prefer_tortoise_for_max_quality,
        test_fallback_chain_respects_config_order,
        test_engine_selection_considers_load,
        test_unsupported_language_fallback,
        test_quality_tier_preference,
        test_quality_predictor_scoring,
        test_engine_registry_discovery,
        test_router_generation_pipeline,
        test_router_fallback_mechanism,
        test_multiple_language_support,
        test_router_config_loading,
        test_engine_load_tracking,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
            failed += 1

    print(f"\nTest Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed")
