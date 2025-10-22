"""
Integration tests for A/B Summary endpoint
"""
import pytest
from fastapi.testclient import TestClient
from services.api.voice_engine_router import app

client = TestClient(app)

def test_ab_summary_endpoint_basic():
    """Test basic A/B summary endpoint functionality"""
    payload = {
        "ratings": [
            {"item_id": "xtts_1", "score": 4.5, "winner": True},
            {"item_id": "coqui_1", "score": 3.2, "winner": False},
            {"item_id": "xtts_2", "score": 4.8, "winner": True},
            {"item_id": "coqui_2", "score": 3.0, "winner": False}
        ],
        "test_id": "test_001"
    }
    
    response = client.post("/v1/ab/summary", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "total_ratings" in data
    assert "engines" in data
    assert "overall_stats" in data
    
    assert data["total_ratings"] == 4
    assert len(data["engines"]) == 2
    
    # Check engine-specific stats
    xtts_engine = next(e for e in data["engines"] if e["engine"] == "xtts")
    coqui_engine = next(e for e in data["engines"] if e["engine"] == "coqui")
    
    assert xtts_engine["wins"] == 2
    assert xtts_engine["total_ratings"] == 2
    assert xtts_engine["win_rate"] == 1.0
    
    assert coqui_engine["wins"] == 0
    assert coqui_engine["total_ratings"] == 2
    assert coqui_engine["win_rate"] == 0.0

def test_ab_summary_endpoint_minimal():
    """Test A/B summary endpoint with minimal payload"""
    payload = {
        "ratings": [
            {"item_id": "xtts_1", "score": 4.0}
        ]
    }
    
    response = client.post("/v1/ab/summary", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_ratings"] == 1
    assert len(data["engines"]) == 1
    assert data["engines"][0]["engine"] == "xtts"

def test_ab_summary_endpoint_invalid_score():
    """Test A/B summary endpoint with invalid score"""
    payload = {
        "ratings": [
            {"item_id": "xtts_1", "score": 6.0}  # Invalid score > 5.0
        ]
    }
    
    response = client.post("/v1/ab/summary", json=payload)
    assert response.status_code == 422  # Validation error

def test_ab_summary_endpoint_empty_ratings():
    """Test A/B summary endpoint with empty ratings"""
    payload = {
        "ratings": []
    }
    
    response = client.post("/v1/ab/summary", json=payload)
    assert response.status_code == 422  # Validation error

def test_ab_summary_endpoint_extra_fields():
    """Test A/B summary endpoint rejects extra fields"""
    payload = {
        "ratings": [
            {"item_id": "xtts_1", "score": 4.0}
        ],
        "extra_field": "not_allowed"
    }
    
    response = client.post("/v1/ab/summary", json=payload)
    assert response.status_code == 422  # Validation error

def test_ab_summary_endpoint_confidence_intervals():
    """Test A/B summary endpoint includes confidence intervals"""
    payload = {
        "ratings": [
            {"item_id": "xtts_1", "score": 3.0},
            {"item_id": "xtts_2", "score": 4.0},
            {"item_id": "xtts_3", "score": 4.5},
            {"item_id": "xtts_4", "score": 5.0},
            {"item_id": "xtts_5", "score": 4.2}
        ]
    }
    
    response = client.post("/v1/ab/summary", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    xtts_engine = next(e for e in data["engines"] if e["engine"] == "xtts")
    
    assert "score_ci_95" in xtts_engine
    assert xtts_engine["score_ci_95"] is not None
    assert "lower" in xtts_engine["score_ci_95"]
    assert "upper" in xtts_engine["score_ci_95"]
    assert "mean" in xtts_engine["score_ci_95"]

def test_ab_summary_endpoint_multiple_engines():
    """Test A/B summary endpoint with multiple engines"""
    payload = {
        "ratings": [
            {"item_id": "xtts_1", "score": 4.5, "winner": True},
            {"item_id": "coqui_1", "score": 3.2, "winner": False},
            {"item_id": "tortoise_1", "score": 4.0, "winner": False},
            {"item_id": "xtts_2", "score": 4.8, "winner": True},
            {"item_id": "coqui_2", "score": 3.5, "winner": False},
            {"item_id": "tortoise_2", "score": 4.2, "winner": False}
        ]
    }
    
    response = client.post("/v1/ab/summary", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["engines"]) == 3
    
    engines = {e["engine"]: e for e in data["engines"]}
    assert "xtts" in engines
    assert "coqui" in engines
    assert "tortoise" in engines
    
    assert engines["xtts"]["wins"] == 2
    assert engines["coqui"]["wins"] == 0
    assert engines["tortoise"]["wins"] == 0
