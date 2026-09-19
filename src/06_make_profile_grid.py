"""Build the profile grid so that real listeners, not only the 5 demo profiles, get RapidMiner scores.

The RapidMiner model is scored offline in Altair AI Studio, so the app cannot ask it about a
listener who was created after the process ran. Instead we score a GRID of stand-in profiles
once, and the app maps every real listener to the nearest cell (same language, closest birth year).

Grid: birth years 1935-1975 in 5-year steps x the three languages the collection covers.
Genres per language are the common case (Film for Hindi/Malayalam, Rock+Pop for English), so a
listener whose genres differ still gets a sensible ranking -- genre is the smallest of the five
baseline weights (15 of 100). This is an approximation, and the app says so on screen.

Output (data/processed/):
  grid_candidates.csv   one row per grid profile x song, features only, no label

Next step (Altair AI Studio, done by hand):
  Read CSV grid_candidates.csv -> Apply Model (the saved Random Forest) -> Write CSV
  as data/processed/predictions_grid.csv, keeping user_id, song_id, confidence(yes).
See docs/rapidminer_steps.md.
"""
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memorybridge.profile import UserProfile  # noqa: E402
from memorybridge.recommender import load_songs  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
simulate = __import__("04_simulate_interactions")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"

BIRTH_YEARS = list(range(1935, 1976, 5))
LANGUAGE_GENRES = {"English": ["Rock", "Pop"], "Hindi": ["Film"], "Malayalam": ["Film"]}


def grid_key(language: str, birth_year: int) -> str:
    """The id shared by this script, the scored CSV and the app."""
    return f"G_{language}_{birth_year}"


def nearest_cell(language: str, birth_year: int) -> str:
    """The grid cell a real listener is served from."""
    known = language if language in LANGUAGE_GENRES else "English"
    closest = min(BIRTH_YEARS, key=lambda year: abs(year - birth_year))
    return grid_key(known, closest)


def main() -> None:
    songs = load_songs()
    parts = []
    for language, genres in LANGUAGE_GENRES.items():
        for birth_year in BIRTH_YEARS:
            profile = UserProfile(birth_year, language, genres)
            rows = simulate.features_for(songs, profile)
            rows.insert(0, "user_id", grid_key(language, birth_year))
            rows.insert(1, "user_language", language)
            rows.insert(2, "birth_year", birth_year)
            parts.append(rows)

    columns = (["user_id", "user_language", "birth_year", "song_id", "year"]
               + simulate.FEATURES + ["baseline_score"])
    grid = pd.concat(parts)[columns]
    path = OUT / "grid_candidates.csv"
    grid.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"{path.relative_to(ROOT)}: {len(grid):,} rows, {grid.user_id.nunique()} profiles, "
          f"{grid.song_id.nunique():,} songs, {path.stat().st_size / 1e6:.1f} MB")
    print("Next: score this file in AI Studio and write data/processed/predictions_grid.csv "
          "(user_id, song_id, confidence(yes)).")


if __name__ == "__main__":
    main()
