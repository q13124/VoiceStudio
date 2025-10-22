import pytest
from app.core.models.ab import ABRating
from app.core.services.ab_summary import summarize_ratings

def test_summarize_basic():
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
