"""Build the MSD prototype subset (raw values, no cleaning) for TurboPrep.

Steps:
  1. Read the MSD summary file (1M songs): title, artist, audio fields, hotttnesss, artist_mbid.
  2. Join release year (tracks_per_year.txt) and tagtraum genre (msd_tagtraum_cd2.cls) on track_id.
  3. Keep songs from 1950-2010 that have a genre.
  4. Stratified sample: the same number of songs from each decade (fixed seed = reproducible).
Cleaning, deduplication and standardization are deliberately left for TurboPrep.
"""
from pathlib import Path
import argparse

import h5py
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"

METADATA_FIELDS = ["song_id", "title", "artist_name", "artist_mbid", "artist_location",
                   "artist_familiarity", "artist_hotttnesss", "song_hotttnesss", "release"]
ANALYSIS_FIELDS = ["track_id", "tempo", "loudness", "key", "mode", "duration", "time_signature"]


def decode(values):
    return [v.decode("utf-8", errors="replace") if isinstance(v, bytes) else v for v in values]


def read_summary() -> pd.DataFrame:
    with h5py.File(RAW / "msd_summary_file.h5", "r") as h5:
        meta = h5["metadata"]["songs"]
        analysis = h5["analysis"]["songs"]
        df = pd.DataFrame({f: decode(meta[f][:]) for f in METADATA_FIELDS})
        for f in ANALYSIS_FIELDS:
            df[f] = decode(analysis[f][:])
    return df


def main(total: int, seed: int) -> None:
    summary = read_summary()
    years = pd.read_csv(RAW / "tracks_per_year.txt", sep="<SEP>", engine="python",
                        header=None, names=["year", "track_id", "y_artist", "y_title"])
    genres = pd.read_csv(RAW / "msd_tagtraum_cd2.cls", sep="\t", comment="#",
                         header=None, names=["track_id", "genre", "genre_minor"])

    df = (summary.merge(years[["track_id", "year"]], on="track_id")
                 .merge(genres, on="track_id"))
    print(f"summary rows: {len(summary):,} | with year+genre: {len(df):,}")

    df = df[(df.year >= 1950) & (df.year <= 2010)].copy()
    df["decade"] = (df.year // 10 * 10).astype(int)
    decades = sorted(df.decade.unique())
    per_decade = total // len(decades)

    parts = []
    for decade in decades:
        group = df[df.decade == decade]
        parts.append(group.sample(n=min(per_decade, len(group)), random_state=seed))
    subset = pd.concat(parts, ignore_index=True)

    columns = ["track_id", "song_id", "title", "artist_name", "artist_mbid", "year", "decade",
               "genre", "genre_minor", "tempo", "loudness", "key", "mode", "duration",
               "time_signature", "song_hotttnesss", "artist_familiarity", "artist_hotttnesss",
               "artist_location", "release"]
    # Double quotes inside text break rows when AI Studio imports the CSV.
    text_columns = subset[columns].select_dtypes(include=["object", "str"]).columns
    subset[text_columns] = subset[text_columns].replace('"', "'", regex=True)
    subset[columns].to_csv(INTERIM / "msd_subset.csv", index=False, encoding="utf-8-sig")
    print(f"subset rows: {len(subset):,} (target {total:,}, {per_decade:,} per decade, seed {seed})")
    print(subset.decade.value_counts().sort_index().to_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--total", type=int, default=6500)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    main(args.total, args.seed)
