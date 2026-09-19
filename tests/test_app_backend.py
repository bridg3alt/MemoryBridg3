import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from memorybridge import db  # noqa: E402
from memorybridge.profile import UserProfile, period_for_age  # noqa: E402
from memorybridge.ranking import RANKED_BY_BASELINE, RANKED_BY_MODEL, recommend_songs  # noqa: E402


def test_memory_survives_reconnect_and_filters_by_period(tmp_path):
    path = tmp_path / "test.db"
    user_id = db.create_user("Meera", 1958, "Malayalam", ["Film"], path=path)
    db.save_memory(user_id, "ML00016", "We sang this on the college bus.", "College", "Friends", "Kochi", 1978, None,
                   path=path)
    db.save_memory(user_id, "ML00032", "My father hummed this.", "Childhood", "Father", "", 1970, None, path=path)

    college = db.get_memories(user_id, "College", path=path)  # each call opens a fresh connection
    assert [m["story"] for m in college] == ["We sang this on the college bus."]
    assert [m["year"] for m in db.get_memories(user_id, path=path)] == [1970, 1978]


def test_empty_story_is_rejected(tmp_path):
    user_id = db.create_user("A", 1960, "Hindi", [], path=tmp_path / "t.db")
    with pytest.raises(ValueError):
        db.save_memory(user_id, "S1", "   ", "College", "", "", 1980, None, path=tmp_path / "t.db")


def test_dismissed_and_saved_songs_are_not_suggested_again(tmp_path):
    path = tmp_path / "t.db"
    user_id = db.create_user("A", 1960, "Hindi", [], path=path)
    db.log_interaction(user_id, "S1", False, False, False, False, "baseline", path=path)
    db.log_interaction(user_id, "S2", True, False, False, False, "baseline", path=path)
    db.log_interaction(user_id, "S3", True, True, True, True, "baseline", path=path)
    assert db.dismissed_song_ids(user_id, path=path) == {"S1", "S3"}


def make_songs():
    return pd.DataFrame({
        "song_id": ["A", "B", "C"], "title": ["a", "b", "c"], "artist": ["x", "y", "z"],
        "year": [1978, 1979, 2005], "genre": ["Film"] * 3, "language": ["Malayalam"] * 3,
        "popularity": [None, None, None], "source": ["Malayalam"] * 3, "play_url": ["u"] * 3,
    })


def test_model_reorders_candidates_for_demo_profile():
    predictions = pd.DataFrame({"user_id": ["D1", "D1", "D1"], "song_id": ["A", "B", "C"],
                                "confidence(yes)": [0.2, 0.9, 0.99]})
    top, ranked_by = recommend_songs(make_songs(), UserProfile(1958, "Malayalam", ["Film"]), "College", "D1",
                                     predictions, top_n=2)
    assert ranked_by == RANKED_BY_MODEL
    assert list(top.song_id) == ["C", "B"]  # C has the highest model confidence among the candidate pool


def test_new_profile_falls_back_to_baseline():
    empty = pd.DataFrame(columns=["user_id", "song_id", "confidence(yes)"])
    top, ranked_by = recommend_songs(make_songs(), UserProfile(1958, "Malayalam", ["Film"]), "College", None,
                                     empty, exclude={"A"}, top_n=1)
    assert ranked_by == RANKED_BY_BASELINE
    assert list(top.song_id) == ["B"]


def test_period_for_age():
    assert period_for_age(12) == "Childhood"
    assert period_for_age(20) == "College"
    assert period_for_age(60) == "Other"


def test_deleting_a_listener_removes_their_memories_and_reactions(tmp_path):
    path = tmp_path / "t.db"
    keep = db.create_user("Keep", 1955, "Hindi", [], path=path)
    drop = db.create_user("Drop", 1960, "Malayalam", [], path=path)
    db.save_memory(keep, "S1", "kept story", "College", "", "", 1975, None, path=path)
    db.save_memory(drop, "S2", "removed story", "College", "", "", 1980, "data/photos/2.jpg", path=path)
    db.log_interaction(drop, "S2", True, True, True, True, "baseline", path=path)

    photos = db.delete_user(drop, path=path)

    assert photos == ["data/photos/2.jpg"]                      # so the caller can delete the file
    assert [u["user_id"] for u in db.list_users(path=path)] == [keep]
    assert db.get_memories(drop, path=path) == []
    assert db.dismissed_song_ids(drop, path=path) == set()
    assert db.count_memories(keep, path=path) == 1              # the other listener is untouched
