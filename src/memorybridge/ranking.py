"""Song recommendations for the app.

Two-stage whenever RapidMiner scores can be found for the listener:
  1. baseline formula picks the top candidates for the chosen life period
  2. RapidMiner Random Forest confidence(yes) orders them

Scores are looked up in this order:
  1. predictions_demo.csv  -- the 5 demo profiles, scored exactly
  2. predictions_grid.csv  -- a grid of stand-in profiles (language x birth year), so real
     listeners are served from the nearest cell (see src/06_make_profile_grid.py)
  3. no scores at all      -- baseline formula alone, and the app says so
"""
from pathlib import Path

import pandas as pd

from .profile import UserProfile
from .recommender import explain, score_songs

ROOT = Path(__file__).resolve().parents[2]
PREDICTIONS_DEMO = ROOT / "data" / "processed" / "predictions_demo.csv"
PREDICTIONS_GRID = ROOT / "data" / "processed" / "predictions_grid.csv"
CANDIDATE_POOL = 200
RANKED_BY_MODEL = "RapidMiner Random Forest (two-stage)"
RANKED_BY_GRID = "RapidMiner Random Forest (nearest profile in the grid)"
RANKED_BY_BASELINE = "Baseline formula"

# Must match src/06_make_profile_grid.py.
GRID_BIRTH_YEARS = list(range(1935, 1976, 5))
GRID_LANGUAGES = ("English", "Hindi", "Malayalam")


def grid_cell(language: str, birth_year: int) -> str:
    """The grid profile a real listener is served from: same language, closest birth year."""
    known = language if language in GRID_LANGUAGES else "English"
    closest = min(GRID_BIRTH_YEARS, key=lambda year: abs(year - birth_year))
    return f"G_{known}_{closest}"


NEEDED = ["user_id", "song_id", "confidence(yes)"]


def _load(path: Path) -> pd.DataFrame:
    """Read a scored file. AI Studio writes CSVs with either separator, and sometimes with a
    byte-order mark that would otherwise turn the first column into '﻿user_id'."""
    if not path.exists():
        return pd.DataFrame(columns=NEEDED)
    frame = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
    frame.columns = [str(column).strip().lstrip("﻿") for column in frame.columns]
    missing = [column for column in NEEDED if column not in frame.columns]
    if missing:
        raise ValueError(f"{path.name} is missing {missing}. Columns found: {list(frame.columns)}. "
                         f"Re-export it from AI Studio (docs/rapidminer_steps.md, Part 4).")
    return frame[NEEDED]


def load_demo_predictions(path: Path = PREDICTIONS_DEMO) -> pd.DataFrame:
    return _load(path)


def load_grid_predictions(path: Path = PREDICTIONS_GRID) -> pd.DataFrame:
    """Scores for the stand-in profile grid, if it has been scored in AI Studio yet."""
    return _load(path)


def recommend_songs(songs: pd.DataFrame, profile: UserProfile, period: str | None,
                    demo_id: str | None = None, predictions: pd.DataFrame | None = None,
                    exclude: set[str] = frozenset(), top_n: int = 10,
                    grid_predictions: pd.DataFrame | None = None) -> tuple[pd.DataFrame, str]:
    scored = score_songs(songs[~songs.song_id.isin(exclude)], profile, period)
    candidates = scored.nlargest(CANDIDATE_POOL, "score")

    model_scores = (predictions[predictions.user_id == demo_id]
                    if demo_id and predictions is not None else pd.DataFrame())
    ranked_by = RANKED_BY_MODEL
    if not len(model_scores) and grid_predictions is not None and len(grid_predictions):
        cell = grid_cell(profile.language, profile.birth_year)
        model_scores = grid_predictions[grid_predictions.user_id == cell]
        ranked_by = f"{RANKED_BY_GRID}: {cell}"

    if len(model_scores):
        candidates = candidates.merge(model_scores[["song_id", "confidence(yes)"]], on="song_id", how="left")
        ranked = candidates.sort_values(["confidence(yes)", "score"], ascending=False)
    else:
        ranked = candidates
        ranked_by = RANKED_BY_BASELINE

    top = ranked.head(top_n).copy()
    top["reasons"] = [explain(row, profile, period) for _, row in top.iterrows()]
    return top, ranked_by
