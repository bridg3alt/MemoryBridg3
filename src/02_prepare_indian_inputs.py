"""Prepare the Hindi and Malayalam raw inputs for TurboPrep.

This script does NOT clean, filter, join or deduplicate. Those are TurboPrep steps.
It only:
  - Hindi: stacks the per-decade songs and albums CSVs into one songs file and one albums file.
  - Malayalam: renames Malayalam-script headers to English, and replaces the full lyrics
    with their first line (the conventional song title). Full lyrics are copyrighted and not needed.
Outputs are UTF-8 with BOM so AI Studio / Excel show Indian scripts correctly.
"""
from pathlib import Path
import glob

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

MALAYALAM_COLUMNS = ["row_index", "actors", "lyricist", "singers", "lyrics",
                     "year", "music_director", "film", "raga", "category"]


def stack(pattern: str) -> pd.DataFrame:
    files = sorted(glob.glob(str(pattern)))
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


def prepare_hindi() -> None:
    songs = stack(RAW / "bollywood" / "songs" / "*.csv")
    albums = stack(RAW / "bollywood" / "albums" / "*.csv")
    songs.to_csv(INTERIM / "bollywood_songs_raw.csv", index=False, encoding="utf-8-sig")
    albums.to_csv(INTERIM / "bollywood_albums_raw.csv", index=False, encoding="utf-8-sig")
    print(f"Hindi songs: {len(songs):,} rows | albums: {len(albums):,} rows")


def prepare_malayalam() -> None:
    df = pd.read_csv(RAW / "malayalam" / "dataset.csv")
    df.columns = MALAYALAM_COLUMNS
    df["title_first_line"] = df["lyrics"].fillna("").str.split("\n").str[0].str.strip()
    df = df.drop(columns=["lyrics", "row_index"])
    df.insert(0, "ml_song_id", [f"ML{i:05d}" for i in range(len(df))])
    # Some text fields contain line breaks or double quotes, which break rows when AI Studio imports the CSV.
    text_columns = df.select_dtypes(include=["object", "str"]).columns
    df[text_columns] = (df[text_columns]
                        .replace(r"[\r\n]+", " ", regex=True)
                        .replace('"', "'", regex=True)
                        .apply(lambda s: s.str.strip()))
    df.to_csv(INTERIM / "malayalam_songs_raw.csv", index=False, encoding="utf-8-sig")
    print(f"Malayalam songs: {len(df):,} rows | blank titles: {(df.title_first_line == '').sum():,}")


if __name__ == "__main__":
    prepare_hindi()
    prepare_malayalam()
