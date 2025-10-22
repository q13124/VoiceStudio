from services.models.audio_metrics import AudioMetrics
from pydantic import ValidationError

def test_metrics_accepts_none_and_numbers():
    m = AudioMetrics(lufs=-23.1, clip_pct=0.0, dc_offset=0.12, head_ms=100, tail_ms=50)
    assert m.lufs == -23.1
    assert m.clip_pct == 0.0
    assert m.head_ms == 100

def test_metrics_rejects_bad_types():
    try:
        AudioMetrics(lufs="nope")  # type: ignore
        assert False, "Should have raised"
    except ValidationError:
        pass
