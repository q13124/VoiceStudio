import pytest
from fastapi.testclient import TestClient
from app.core.models.ab import ABRating, ABSummaryRequest, AudioMetrics
from app.core.ab.summary import summarize_ratings
from services.main import app

client = TestClient(app)

def test_summarize_basic():
    """Test basic summarize_ratings functionality"""
    rs = [
        ABRating(itemId="a1", engine="xtts", score=4.5, winner=True),
        ABRating(itemId="a2", engine="xtts", score=4.0, winner=False),
        ABRating(itemId="b1", engine="openvoice", score=4.2, winner=False),
        ABRating(itemId="b2", engine="openvoice", score=4.8, winner=True),
        ABRating(itemId="b3", engine="openvoice", score=4.6, winner=True),
    ]
    stats = summarize_ratings(rs)
    by_engine = {s.engine: s for s in stats}
    assert by_engine["xtts"].n_items == 2
    assert by_engine["openvoice"].n_items == 3
    assert 0.0 <= by_engine["xtts"].win_rate <= 1.0
    assert 0.0 <= by_engine["openvoice"].win_rate <= 1.0

def test_ab_summary_basic():
    """Test basic A/B summary functionality"""
    ratings = [
        ABRating(
            itemId="item1",
            engine="xtts",
            score=4.5,
            winner=True,
            metrics=AudioMetrics(lufs=-23.1, clip_pct=0.0)
        ),
        ABRating(
            itemId="item2", 
            engine="openvoice",
            score=3.8,
            winner=False,
            metrics=AudioMetrics(lufs=-21.5, clip_pct=0.1)
        ),
        ABRating(
            itemId="item3",
            engine="xtts", 
            score=4.2,
            winner=True,
            metrics=AudioMetrics(lufs=-22.8, clip_pct=0.0)
        )
    ]
    
    request = ABSummaryRequest(
        sessionId="test_session_123",
        ratings=ratings
    )
    
    response = client.post("/v1/ab/summary", json=request.model_dump())
    assert response.status_code == 200
    
    data = response.json()
    assert data["sessionId"] == "test_session_123"
    assert data["total_items"] == 3
    assert len(data["engines"]) == 2
    
    # Check engine stats
    engines = {e["engine"]: e for e in data["engines"]}
    
    # XTTS should have 2 items, 2 wins
    xtts_stats = engines["xtts"]
    assert xtts_stats["n_items"] == 2
    assert xtts_stats["wins"] == 2
    assert xtts_stats["win_rate"] == 1.0
    assert xtts_stats["mean_score"] == 4.35  # (4.5 + 4.2) / 2
    assert xtts_stats["median_lufs"] == -22.95  # median of -23.1, -22.8
    assert xtts_stats["clip_hit_rate"] == 0.0  # no clips
    
    # OpenVoice should have 1 item, 0 wins
    ov_stats = engines["openvoice"]
    assert ov_stats["n_items"] == 1
    assert ov_stats["wins"] == 0
    assert ov_stats["win_rate"] == 0.0
    assert ov_stats["mean_score"] == 3.8
    assert ov_stats["median_lufs"] == -21.5
    assert ov_stats["clip_hit_rate"] == 1.0  # 1 clip hit

def test_ab_summary_empty_ratings():
    """Test that empty ratings list is rejected"""
    request = ABSummaryRequest(
        sessionId="test_session",
        ratings=[]
    )
    
    response = client.post("/v1/ab/summary", json=request.model_dump())
    assert response.status_code == 422  # Validation error

def test_ab_summary_confidence_intervals():
    """Test that confidence intervals are calculated correctly"""
    # Create many ratings to test CI calculation
    ratings = []
    for i in range(100):
        ratings.append(ABRating(
            itemId=f"item{i}",
            engine="engine_a",
            winner=i < 60,  # 60% win rate
            score=4.0
        ))
    
    request = ABSummaryRequest(
        sessionId="ci_test",
        ratings=ratings
    )
    
    response = client.post("/v1/ab/summary", json=request.model_dump())
    assert response.status_code == 200
    
    data = response.json()
    engine_stats = data["engines"][0]
    
    assert engine_stats["win_rate"] == 0.6
    assert engine_stats["win_rate_ci95_low"] is not None
    assert engine_stats["win_rate_ci95_high"] is not None
    assert engine_stats["win_rate_ci95_low"] < engine_stats["win_rate"]
    assert engine_stats["win_rate_ci95_high"] > engine_stats["win_rate"]

def test_ab_summary_route_ok():
    """Test basic route functionality"""
    payload = {
        "sessionId": "sess-123",
        "ratings": [
            {"itemId":"1","engine":"xtts","score":4.6,"winner":True,"metrics":{"lufs":-23.4,"clip_pct":0.0}},
            {"itemId":"2","engine":"xtts","score":4.2,"winner":False,"metrics":{"lufs":-21.9,"clip_pct":0.0}},
            {"itemId":"3","engine":"openvoice","score":4.7,"winner":True,"metrics":{"lufs":-24.0,"clip_pct":0.1}}
        ]
    }
    r = client.post("/v1/ab/summary", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["sessionId"] == "sess-123"
    assert "engines" in data and isinstance(data["engines"], list)
    assert data["total_items"] == 3

def test_ab_summary_example_payload():
    """Test with the provided example payload"""
    payload = {
        "sessionId": "ab-2025-10-21T13:05Z-xyz",
        "ratings": [
            { "itemId": "cand-01", "engine": "hidden-A", "score": 4.6, "winner": True,  "metrics": { "lufs": -23.1, "clip_pct": 0.0 } },
            { "itemId": "cand-02", "engine": "hidden-B", "score": 4.2, "winner": False, "metrics": { "lufs": -21.9, "clip_pct": 0.2 } }
        ]
    }
    
    response = client.post("/v1/ab/summary", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["sessionId"] == "ab-2025-10-21T13:05Z-xyz"
    assert data["total_items"] == 2
    assert len(data["engines"]) == 2
    
    # Check engine stats
    engines = {e["engine"]: e for e in data["engines"]}
    
    # hidden-A should have 1 item, 1 win
    engine_a = engines["hidden-A"]
    assert engine_a["n_items"] == 1
    assert engine_a["wins"] == 1
    assert engine_a["win_rate"] == 1.0
    assert engine_a["mean_score"] == 4.6
    assert engine_a["median_lufs"] == -23.1
    assert engine_a["clip_hit_rate"] == 0.0  # no clips
    
    # hidden-B should have 1 item, 0 wins
    engine_b = engines["hidden-B"]
    assert engine_b["n_items"] == 1
    assert engine_b["wins"] == 0
    assert engine_b["win_rate"] == 0.0
    assert engine_b["mean_score"] == 4.2
    assert engine_b["median_lufs"] == -21.9
    assert engine_b["clip_hit_rate"] == 1.0  # 1 clip hit
