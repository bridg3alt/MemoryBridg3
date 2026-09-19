"""Compare top-10 ranking quality on the 60 holdout listeners (SIMULATED data).

For each listener, rank their ~40 songs three ways and count how many of the top 10 were real "yes" answers:
  - RapidMiner Random Forest: confidence(yes) from predictions_holdout.csv
  - Baseline formula: baseline_score (era 40 / language 20 / genre 15 / artist 10 / popularity 15)
  - Random order (averaged over 200 shuffles)
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TOP_K = 10


def find_predictions() -> Path:
    for path in [ROOT / "data" / "processed" / "predictions_holdout.csv", ROOT / "data" / "predictions_holdout.csv"]:
        if path.exists():
            return path
    raise FileNotFoundError("predictions_holdout.csv not found in data/processed or data")


def precision_at_k(frame: pd.DataFrame, score_column: str) -> float:
    top = frame.sort_values(score_column, ascending=False).groupby("user_id").head(TOP_K)
    return top.groupby("user_id")["is_yes"].mean().mean()


def main() -> None:
    predictions = pd.read_csv(find_predictions(), sep=None, engine="python")
    holdout = pd.read_csv(ROOT / "data" / "processed" / "interactions_holdout.csv", encoding="utf-8-sig")
    data = holdout.merge(predictions[["user_id", "song_id", "confidence(yes)"]], on=["user_id", "song_id"])
    data["is_yes"] = (data["memory_triggered"] == "yes").astype(float)
    assert len(data) == len(holdout), "every holdout row should have a prediction"

    rng = np.random.default_rng(0)
    random_scores = []
    for _ in range(200):
        data["random"] = rng.random(len(data))
        random_scores.append(precision_at_k(data, "random"))

    results = {
        "RapidMiner Random Forest": precision_at_k(data, "confidence(yes)"),
        "Baseline formula": precision_at_k(data, "baseline_score"),
        "Random order": float(np.mean(random_scores)),
    }
    print(f"SIMULATED | holdout listeners: {data.user_id.nunique()} | rows: {len(data):,} | "
          f"overall yes-rate: {data.is_yes.mean():.1%}")
    for name, value in results.items():
        print(f"  top-{TOP_K} hit rate  {name:<26} {value:.1%}")


if __name__ == "__main__":
    main()
