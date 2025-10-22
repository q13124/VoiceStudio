"""
Tests for AudioMetrics model validation
"""
from services.api.voice_engine_router import AudioMetrics
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

def test_metrics_accepts_none_values():
    m = AudioMetrics()
    assert m.lufs is None
    assert m.clip_pct is None
    assert m.dc_offset is None
    assert m.head_ms is None
    assert m.tail_ms is None
    assert m.lra is None
    assert m.true_peak is None

def test_metrics_validates_clip_pct_range():
    # Valid range
    m = AudioMetrics(clip_pct=50.0)
    assert m.clip_pct == 50.0
    
    # Edge cases
    m = AudioMetrics(clip_pct=0.0)
    assert m.clip_pct == 0.0
    
    m = AudioMetrics(clip_pct=100.0)
    assert m.clip_pct == 100.0
    
    # Invalid range - should raise
    try:
        AudioMetrics(clip_pct=101.0)
        assert False, "Should have raised for clip_pct > 100"
    except ValidationError:
        pass
    
    try:
        AudioMetrics(clip_pct=-1.0)
        assert False, "Should have raised for clip_pct < 0"
    except ValidationError:
        pass

def test_metrics_validates_dc_offset_range():
    # Valid range
    m = AudioMetrics(dc_offset=0.5)
    assert m.dc_offset == 0.5
    
    # Edge case
    m = AudioMetrics(dc_offset=0.0)
    assert m.dc_offset == 0.0
    
    # Invalid range - should raise
    try:
        AudioMetrics(dc_offset=-0.1)
        assert False, "Should have raised for dc_offset < 0"
    except ValidationError:
        pass

def test_metrics_validates_head_tail_ms_range():
    # Valid range
    m = AudioMetrics(head_ms=100, tail_ms=200)
    assert m.head_ms == 100
    assert m.tail_ms == 200
    
    # Edge case
    m = AudioMetrics(head_ms=0, tail_ms=0)
    assert m.head_ms == 0
    assert m.tail_ms == 0
    
    # Invalid range - should raise
    try:
        AudioMetrics(head_ms=-1)
        assert False, "Should have raised for head_ms < 0"
    except ValidationError:
        pass
    
    try:
        AudioMetrics(tail_ms=-1)
        assert False, "Should have raised for tail_ms < 0"
    except ValidationError:
        pass

def test_metrics_strict_mode_rejects_extra_fields():
    try:
        AudioMetrics(lufs=-23.0, extra_field="not_allowed")
        assert False, "Should have raised for extra field"
    except ValidationError:
        pass

def test_metrics_serialization():
    m = AudioMetrics(lufs=-23.1, clip_pct=0.5, head_ms=100)
    data = m.dict()
    assert data["lufs"] == -23.1
    assert data["clip_pct"] == 0.5
    assert data["head_ms"] == 100
    assert data["lra"] is None

def test_metrics_deserialization():
    data = {"lufs": -23.1, "clip_pct": 0.5, "head_ms": 100, "lra": None}
    m = AudioMetrics(**data)
    assert m.lufs == -23.1
    assert m.clip_pct == 0.5
    assert m.head_ms == 100
    assert m.lra is None
