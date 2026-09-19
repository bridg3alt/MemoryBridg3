"""Baseline recommender: a transparent weighted score (no machine learning).

Every song gets five part-scores between 0 and 1, combined with fixed weights into a score out of 100.
The weights are prototype assumptions, not scientifically validated values.
This baseline is what the RapidMiner model must beat later.
"""
from pathlib import Path

import pandas as pd

from .profile import UserProfile

ROOT = Path(__file__).resolve().parents[2]
SONGS_MASTER = ROOT / "data" / "processed" / "songs_master.csv"

WEIGHTS = {"era": 0.40, "language": 0.20, "genre": 0.15, "artist": 0.10, "popularity": 0.15}
ERA_DECAY_PER_YEAR = 0.2      # era score lost per year outside the target period
NEUTRAL_POPULARITY = 0.5      # missing popularity = "unknown", so no dataset is penalized for lacking it
MAX_SONGS_PER_ARTIST = 2      # keeps the top 10 from being one artist


def load_songs(path: Path = SONGS_MASTER) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def _contains_any(text: pd.Series, names: list[str]) -> pd.Series:
    lowered = text.fillna("").str.lower()
    matches = pd.Series(False, index=text.index)
    for name in names:
        matches |= lowered.str.contains(name.strip().lower(), regex=False)
    return matches


def score_songs(songs: pd.DataFrame, profile: UserProfile, period: str | None = None) -> pd.DataFrame:
    first_year, last_year = profile.year_range(period)
    scored = songs.copy()
    scored["age_at_release"] = scored["year"] - profile.birth_year

    years_outside = (first_year - scored["year"]).clip(lower=0) + (scored["year"] - last_year).clip(lower=0)
    scored["era_score"] = (1 - ERA_DECAY_PER_YEAR * years_outside).clip(lower=0)
    scored["language_score"] = (scored["language"].str.lower() == profile.language.lower()).astype(float)
    scored["genre_score"] = scored["genre"].str.lower().isin([g.lower() for g in profile.genres]).astype(float)
    scored["artist_score"] = _contains_any(scored["artist"], profile.artists).astype(float)
    # to_numeric guards against a popularity column that is entirely empty (pandas would treat it as text)
    popularity = pd.to_numeric(scored["popularity"], errors="coerce")
    scored["popularity_score"] = (popularity / 100).fillna(NEUTRAL_POPULARITY)

    scored["score"] = 100 * sum(weight * scored[f"{part}_score"] for part, weight in WEIGHTS.items())
    return scored


def explain(song: pd.Series, profile: UserProfile, period: str | None) -> list[str]:
    reasons = []
    age = int(song["age_at_release"])
    year = int(song["year"])
    if song["era_score"] == 1:
        when = f"your {period.lower()} years" if period else "your teens and twenties"
        reasons.append(f"From {when} ({year}, you were {age})")
    elif song["era_score"] > 0:
        reasons.append(f"Close to the period you chose ({year}, you were {age})")
    if song["language_score"] == 1:
        reasons.append(f"In {song['language']}")
    if song["genre_score"] == 1:
        reasons.append(f"{song['genre']}, a genre you like")
    if song["artist_score"] == 1:
        reasons.append(f"By an artist you like ({song['artist']})")
    if pd.notna(song["popularity"]) and song["popularity"] >= 70:
        reasons.append("Widely rated / popular")
    return reasons


def recommend(songs: pd.DataFrame, profile: UserProfile, period: str | None = None, top_n: int = 10) -> pd.DataFrame:
    scored = score_songs(songs, profile, period).sort_values("score", ascending=False)
    per_artist = scored.groupby(scored["artist"].fillna(scored["song_id"])).cumcount()
    top = scored[per_artist < MAX_SONGS_PER_ARTIST].head(top_n).copy()
    top["reasons"] = [" · ".join(explain(row, profile, period)) for _, row in top.iterrows()]
    return top
