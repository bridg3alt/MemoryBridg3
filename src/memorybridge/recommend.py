"""Command line: show the top 10 songs for a profile.

Example (run from the src folder):
    python -m memorybridge.recommend --birth-year 1958 --language Malayalam --genres Film --period College
"""
import argparse
import sys

from .profile import LIFE_PERIODS, UserProfile
from .recommender import load_songs, recommend


def main() -> None:
    parser = argparse.ArgumentParser(description="MemoryBridge baseline song recommendations")
    parser.add_argument("--birth-year", type=int, required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--genres", nargs="*", default=[], help="e.g. Film Rock Jazz")
    parser.add_argument("--artists", nargs="*", default=[], help='e.g. "Lata Mangeshkar"')
    parser.add_argument("--period", choices=list(LIFE_PERIODS), default=None)
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    profile = UserProfile(args.birth_year, args.language, args.genres, args.artists)
    first, last = profile.year_range(args.period)
    print(f"\nProfile: born {args.birth_year}, {args.language}, genres={args.genres or '-'}, "
          f"period={args.period or 'default (age 10-30)'} -> songs from {first}-{last}\n")

    for rank, (_, song) in enumerate(recommend(load_songs(), profile, args.period, args.top).iterrows(), 1):
        print(f"{rank:>2}. [{song['score']:5.1f}] {song['title']} - {song['artist'] if isinstance(song['artist'], str) else 'Unknown artist'} ({int(song['year'])}, {song['source']})")
        print(f"    Why: {song['reasons']}")
    print()


if __name__ == "__main__":
    main()
