import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from memorybridge.profile import UserProfile  # noqa: E402
from memorybridge.recommender import recommend, score_songs  # noqa: E402


def make_songs():
    return pd.DataFrame({
        "song_id": ["A", "B", "C", "D"],
        "title": ["In period", "Far away", "Two years out", "No popularity"],
        "artist": ["X", "Y", "Z", "W"],
        "year": [1978, 2008, 1982, 1978],
        "genre": ["Film", "Rock", "Film", "Film"],
        "language": ["Malayalam", "English", "Malayalam", "Malayalam"],
        "popularity": [80.0, 100.0, 80.0, None],
        "source": ["Malayalam"] * 4,
    })


def test_example_from_explanation_scores_82_5():
    profile = UserProfile(1958, "Malayalam", genres=["Film"])
    scored = score_songs(make_songs(), profile, "College").set_index("song_id")
    assert scored.loc["D", "score"] == pytest.approx(82.5)  # 40 + 20 + 15 + 0 + 7.5


def test_era_decays_outside_period():
    profile = UserProfile(1958, "Malayalam")
    scored = score_songs(make_songs(), profile, "College").set_index("song_id")
    assert scored.loc["A", "era_score"] == 1.0
    assert scored.loc["C", "era_score"] == pytest.approx(0.6)  # 1982 is 2 years after 1980
    assert scored.loc["B", "era_score"] == 0.0


def test_recommend_orders_by_score_and_explains():
    profile = UserProfile(1958, "Malayalam", genres=["Film"])
    top = recommend(make_songs(), profile, "College", top_n=2)
    assert list(top["song_id"]) == ["A", "D"]
    assert "college years" in top.iloc[0]["reasons"]
