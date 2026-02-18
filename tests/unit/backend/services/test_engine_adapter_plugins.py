"""Unit tests for engine adapter wrappers."""

import numpy as np

from plugins.engine_bark.adapter import BarkEngineAdapter
from plugins.engine_piper.adapter import PiperEngineAdapter
from plugins.engine_xtts_v2.adapter import XttsEngineAdapter


class _FakeEngine:
    def __init__(self, *args, **kwargs):
        self.cleaned = False

    def initialize(self):
        return True

    def cleanup(self):
        self.cleaned = True

    def synthesize(self, *args, **kwargs):
        return np.array([0.0, 0.1, -0.1], dtype=np.float32)

    def health_check(self):
        return {"status": "ok"}


def test_xtts_adapter_synthesize_and_health():
    adapter = XttsEngineAdapter(engine_cls=_FakeEngine)
    assert adapter.initialize() is True
    out = adapter.synthesize("hello", reference_audio="ref.wav")
    assert out is not None
    assert len(out) == 3
    assert adapter.health()["status"] == "ok"
    adapter.cleanup()


def test_piper_adapter_synthesize_and_health():
    adapter = PiperEngineAdapter(engine_cls=_FakeEngine)
    assert adapter.initialize() is True
    out = adapter.synthesize("hello")
    assert out is not None
    assert len(out) == 3
    assert adapter.health()["status"] == "ok"
    adapter.cleanup()


def test_bark_adapter_synthesize_and_health():
    adapter = BarkEngineAdapter(engine_cls=_FakeEngine)
    assert adapter.initialize() is True
    out = adapter.synthesize("hello")
    assert out is not None
    assert len(out) == 3
    assert adapter.health()["status"] == "ok"
    adapter.cleanup()
