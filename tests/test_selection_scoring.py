import types
from services.voice_engine_router import VoiceEngineRouter, EngineRegistry, RouterConfig


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
    assert engine == "xtts" and "xtts" in order


def test_quality_english_may_prefer_tortoise_for_max_quality():
    reg = EngineRegistry(
        adapters=[FakeEngine("xtts", ["en"], 0.1), FakeEngine("tortoise", ["en"], 0.05)]
    )
    cfg = RouterConfig()
    router = VoiceEngineRouter(reg, cfg)
    engine, order = router.select_engine(
        text="hello world", language="en", tier="quality"
    )
    assert engine in {"xtts", "tortoise"}
    assert set(order) == {"xtts", "tortoise"}
