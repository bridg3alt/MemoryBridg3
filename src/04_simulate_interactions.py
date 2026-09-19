"""Create SIMULATED listeners and their song reactions for the RapidMiner model.

!!! Everything produced here is SYNTHETIC. Labels come from rules written below, so any model trained on
!!! them can only rediscover these rules. Results prove the pipeline works, NOT that the idea works for real people.
Rules and limitations are documented in docs/simulation_assumptions.md.

Outputs (data/processed/):
  users_synthetic.csv          300 synthetic listeners (profile only)
  interactions_train.csv       240 listeners x 40 songs  -> RapidMiner training + cross-validation
  interactions_holdout.csv      60 listeners x 40 songs  -> never used for training; final comparison vs baseline
  demo_candidates.csv          5 demo profiles x all songs (no label) -> RapidMiner Apply Model -> app
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memorybridge.profile import UserProfile  # noqa: E402
from memorybridge.recommender import load_songs, score_songs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"
SEED = 2026
N_USERS, N_HOLDOUT, SONGS_PER_USER = 300, 60, 40

USER_LANGUAGES = {"English": 0.40, "Hindi": 0.30, "Malayalam": 0.30}
WESTERN_GENRES = ["Rock", "Pop", "Jazz", "RnB", "Country", "Blues", "Folk", "Electronic"]

# ---- Hidden generating rule (NOT written to any output file) ------------------------------------
INTERCEPT = -2.9
W_BUMP, W_LANGUAGE, W_GENRE, W_ARTIST, W_POPULARITY = 2.8, 1.4, 0.6, 1.2, 1.0
BUMP_PEAK_AGE, BUMP_WIDTH = 20, 7          # "reminiscence bump" shape: strongest around age 20
USER_TASTE_SD = 0.7                        # some people respond to music more than others
RECOGNITION_BOOST = 1.5

# ---- Columns RapidMiner may use as features (all known BEFORE the reaction happens) --------------
FEATURES = ["age_at_release", "in_age_10_30", "years_outside_10_30", "language_match",
            "genre_match", "artist_match", "popularity"]


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def make_users(songs: pd.DataFrame, rng: np.random.Generator) -> list[dict]:
    users = []
    for i in range(N_USERS):
        language = rng.choice(list(USER_LANGUAGES), p=list(USER_LANGUAGES.values()))
        birth_year = int(rng.integers(1940, 1976))
        if language == "English":
            genres = list(rng.choice(WESTERN_GENRES, size=int(rng.integers(1, 3)), replace=False))
        else:
            genres = ["Film"] + ([str(rng.choice(WESTERN_GENRES))] if rng.random() < 0.3 else [])

        artists = []
        youth = songs[(songs.language == language) & songs.year.between(birth_year + 10, birth_year + 30)
                      & songs.artist.notna()]
        if len(youth) and rng.random() < 0.4:
            artists = [youth.artist.iloc[int(rng.integers(len(youth)))].split(",")[0].strip()]

        users.append({"user_id": f"U{i + 1:03d}", "birth_year": birth_year, "language": language,
                      "genres": "|".join(genres), "artists": "|".join(artists),
                      "taste": rng.normal(0, USER_TASTE_SD)})
    return users


def profile_of(user: dict) -> UserProfile:
    split = lambda s: [x for x in s.split("|") if x]  # noqa: E731
    return UserProfile(user["birth_year"], user["language"], split(user["genres"]), split(user["artists"]))


def features_for(songs: pd.DataFrame, profile: UserProfile) -> pd.DataFrame:
    scored = score_songs(songs, profile, period=None)
    age = scored["age_at_release"]
    return pd.DataFrame({
        "song_id": scored["song_id"],
        "title": scored["title"],
        "artist": scored["artist"],
        "source": scored["source"],
        "song_language": scored["language"],
        "year": scored["year"].astype(int),
        "age_at_release": age.astype(int),
        "in_age_10_30": age.between(10, 30).astype(int),
        "years_outside_10_30": ((10 - age).clip(lower=0) + (age - 30).clip(lower=0)).astype(int),
        "language_match": scored["language_score"].astype(int),
        "genre_match": scored["genre_score"].astype(int),
        "artist_match": scored["artist_score"].astype(int),
        "popularity": scored["popularity"],
        "baseline_score": scored["score"].round(2),
    })


def simulate_reactions(rows: pd.DataFrame, taste: float, rng: np.random.Generator) -> pd.DataFrame:
    bump = np.exp(-((rows.age_at_release - BUMP_PEAK_AGE) / BUMP_WIDTH) ** 2)
    popularity = (rows.popularity / 100).fillna(0.5)
    z = (INTERCEPT + W_BUMP * bump + W_LANGUAGE * rows.language_match + W_GENRE * rows.genre_match
         + W_ARTIST * rows.artist_match + W_POPULARITY * (popularity - 0.5) + taste)

    p_recognized, p_memory = sigmoid(z + RECOGNITION_BOOST), sigmoid(z)
    recognized = rng.random(len(rows)) < p_recognized
    memory = recognized & (rng.random(len(rows)) < p_memory / p_recognized)  # P(memory) = sigmoid(z)
    liked = np.where(memory, rng.random(len(rows)) < 0.9, recognized & (rng.random(len(rows)) < 0.5))
    story = memory & (rng.random(len(rows)) < 0.6)
    saved = story & (rng.random(len(rows)) < 0.85)

    out = rows.copy()
    out["recognized"], out["liked"] = recognized.astype(int), liked.astype(int)
    out["memory_triggered"] = np.where(memory, "yes", "no")
    out["story_recorded"], out["saved"] = story.astype(int), saved.astype(int)
    return out


def safe_for_ai_studio(frame: pd.DataFrame) -> pd.DataFrame:
    """AI Studio's CSV import treats '#' as a comment and '"' as a quote, which silently breaks rows."""
    frame = frame.copy()
    for column in ["title", "artist"]:
        frame[column] = frame[column].str.replace("#", "No.", regex=False).str.replace('"', "'", regex=False)
    return frame


def main() -> None:
    rng = np.random.default_rng(SEED)
    songs = load_songs()
    users = make_users(songs, rng)

    parts = []
    for user in users:
        features = features_for(songs, profile_of(user))
        top_candidates = features.nlargest(200, "baseline_score")
        shown = pd.concat([top_candidates.sample(SONGS_PER_USER // 2, random_state=int(rng.integers(1e9))),
                           features.sample(SONGS_PER_USER // 2, random_state=int(rng.integers(1e9)))])
        shown = shown.drop_duplicates("song_id")
        reactions = simulate_reactions(shown, user["taste"], rng)
        reactions.insert(0, "user_id", user["user_id"])
        reactions.insert(1, "user_language", user["language"])
        reactions.insert(2, "birth_year", user["birth_year"])
        parts.append(reactions)
    interactions = safe_for_ai_studio(pd.concat(parts, ignore_index=True))

    holdout_ids = {u["user_id"] for u in users[-N_HOLDOUT:]}
    is_holdout = interactions.user_id.isin(holdout_ids)
    interactions[~is_holdout].to_csv(OUT / "interactions_train.csv", index=False, encoding="utf-8-sig")
    interactions[is_holdout].to_csv(OUT / "interactions_holdout.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(users).drop(columns="taste").to_csv(OUT / "users_synthetic.csv", index=False, encoding="utf-8-sig")

    demo_profiles = [("D1", UserProfile(1958, "Malayalam", ["Film"])), ("D2", UserProfile(1952, "Hindi", ["Film"])),
                     ("D3", UserProfile(1960, "Hindi", ["Film"])), ("D4", UserProfile(1950, "English", ["Rock", "Pop"])),
                     ("D5", UserProfile(1965, "English", ["Jazz"]))]
    demo = []
    for demo_id, profile in demo_profiles:
        rows = features_for(songs, profile)
        rows.insert(0, "user_id", demo_id)
        rows.insert(1, "user_language", profile.language)
        rows.insert(2, "birth_year", profile.birth_year)
        demo.append(rows)
    # The demo file only needs IDs and features for RapidMiner; text columns (titles/artists with commas) are left out
    # because AI Studio failed to parse them. The app looks titles up from songs_master.csv by song_id.
    demo_columns = ["user_id", "user_language", "birth_year", "song_id", "year"] + FEATURES + ["baseline_score"]
    pd.concat(demo)[demo_columns].to_csv(OUT / "demo_candidates.csv", index=False, encoding="utf-8-sig")

    for name, frame in [("train", interactions[~is_holdout]), ("holdout", interactions[is_holdout])]:
        print(f"{name}: {len(frame):,} rows, {frame.user_id.nunique()} users, "
              f"memory_triggered=yes {(frame.memory_triggered == 'yes').mean():.1%}")
    print(f"demo_candidates: {sum(len(d) for d in demo):,} rows")


if __name__ == "__main__":
    main()
