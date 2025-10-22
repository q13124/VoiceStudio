"""
Unit tests for A/B Test Summary functionality
"""
import pytest
from services.api.ab_summary import (
    ABRating, ABSummaryRequest, ABSummaryResponse, 
    EngineStats, aggregate_ab_ratings, calculate_confidence_interval
)

def test_ab_rating_validation():
    """Test ABRating model validation"""
    # Valid rating
    rating = ABRating(item_id="xtts_1", score=4.5, winner=True)
    assert rating.item_id == "xtts_1"
    assert rating.score == 4.5
    assert rating.winner is True
    
    # Invalid score range
    with pytest.raises(ValueError):
        ABRating(item_id="xtts_1", score=6.0)  # > 5.0
    
    with pytest.raises(ValueError):
        ABRating(item_id="xtts_1", score=0.5)  # < 1.0

def test_ab_summary_request_validation():
    """Test ABSummaryRequest model validation"""
    ratings = [
        ABRating(item_id="xtts_1", score=4.5, winner=True),
        ABRating(item_id="coqui_1", score=3.2, winner=False)
    ]
    
    request = ABSummaryRequest(ratings=ratings, test_id="test_001")
    assert len(request.ratings) == 2
    assert request.test_id == "test_001"
    
    # Empty ratings should fail
    with pytest.raises(ValueError):
        ABSummaryRequest(ratings=[])

def test_confidence_interval_calculation():
    """Test confidence interval calculation"""
    scores = [3.0, 4.0, 4.5, 5.0, 4.2]
    ci = calculate_confidence_interval(scores)
    
    assert ci is not None
    assert "lower" in ci
    assert "upper" in ci
    assert "mean" in ci
    assert ci["lower"] < ci["mean"] < ci["upper"]
    
    # Single score should return None
    ci_single = calculate_confidence_interval([4.0])
    assert ci_single is None

def test_aggregate_ab_ratings_basic():
    """Test basic A/B rating aggregation"""
    ratings = [
        ABRating(item_id="xtts_1", score=4.5, winner=True),
        ABRating(item_id="coqui_1", score=3.2, winner=False),
        ABRating(item_id="xtts_2", score=4.8, winner=True),
        ABRating(item_id="coqui_2", score=3.0, winner=False)
    ]
    
    result = aggregate_ab_ratings(ratings)
    
    assert isinstance(result, ABSummaryResponse)
    assert result.total_ratings == 4
    assert len(result.engines) == 2  # xtts and coqui
    
    # Check engine stats
    xtts_stats = next(e for e in result.engines if e.engine == "xtts")
    coqui_stats = next(e for e in result.engines if e.engine == "coqui")
    
    assert xtts_stats.wins == 2
    assert xtts_stats.total_ratings == 2
    assert xtts_stats.win_rate == 1.0
    
    assert coqui_stats.wins == 0
    assert coqui_stats.total_ratings == 2
    assert coqui_stats.win_rate == 0.0

def test_aggregate_ab_ratings_with_metrics():
    """Test A/B rating aggregation with audio metrics"""
    ratings = [
        ABRating(item_id="xtts_1", score=4.5, winner=True),
        ABRating(item_id="coqui_1", score=3.2, winner=False)
    ]
    
    # Mock metrics data
    item_metrics = {
        "xtts": {
            "xtts_1": {"lufs": -23.0, "clip_pct": 0.0}
        },
        "coqui": {
            "coqui_1": {"lufs": -20.0, "clip_pct": 0.5}
        }
    }
    
    result = aggregate_ab_ratings(ratings, item_metrics)
    
    xtts_stats = next(e for e in result.engines if e.engine == "xtts")
    coqui_stats = next(e for e in result.engines if e.engine == "coqui")
    
    assert xtts_stats.median_lufs == -23.0
    assert xtts_stats.clip_hit_rate == 0.0
    
    assert coqui_stats.median_lufs == -20.0
    assert coqui_stats.clip_hit_rate == 1.0  # 0.5 > 0.1 threshold

def test_engine_stats_validation():
    """Test EngineStats model validation"""
    stats = EngineStats(
        engine="xtts",
        wins=5,
        total_ratings=10,
        win_rate=0.5,
        mean_score=4.2,
        median_score=4.0,
        median_lufs=-23.0,
        clip_hit_rate=0.1,
        score_ci_95={"lower": 3.8, "upper": 4.6, "mean": 4.2}
    )
    
    assert stats.engine == "xtts"
    assert stats.wins == 5
    assert stats.win_rate == 0.5
    
    # Invalid win_rate should fail
    with pytest.raises(ValueError):
        EngineStats(
            engine="xtts",
            wins=5,
            total_ratings=10,
            win_rate=1.5  # > 1.0
        )

def test_ab_summary_response_validation():
    """Test ABSummaryResponse model validation"""
    engines = [
        EngineStats(
            engine="xtts",
            wins=2,
            total_ratings=3,
            win_rate=0.67,
            mean_score=4.3
        )
    ]
    
    response = ABSummaryResponse(
        test_id="test_001",
        total_ratings=3,
        engines=engines,
        overall_stats={"mean_score": 4.3, "total_wins": 2}
    )
    
    assert response.test_id == "test_001"
    assert response.total_ratings == 3
    assert len(response.engines) == 1
    assert response.overall_stats["mean_score"] == 4.3

def test_strict_mode_rejects_extra_fields():
    """Test that strict mode rejects extra fields"""
    with pytest.raises(ValueError):
        ABRating(item_id="xtts_1", score=4.5, extra_field="not_allowed")
    
    with pytest.raises(ValueError):
        ABSummaryRequest(ratings=[], extra_field="not_allowed")
    
    with pytest.raises(ValueError):
        EngineStats(
            engine="xtts",
            wins=1,
            total_ratings=1,
            win_rate=1.0,
            extra_field="not_allowed"
        )
