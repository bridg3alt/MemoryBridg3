"""Enrich MSD subset artists with MusicBrainz data (country, area, language, genres).

One API call per unique artist_mbid:
    GET https://musicbrainz.org/ws/2/artist/{mbid}?inc=releases+genres+tags&fmt=json

Safe by design:
  - rate limit: at most 1 request per ~1.1 s (MusicBrainz rule is 1/s)
  - identifying User-Agent
  - cache: every response saved to data/raw/musicbrainz_cache/{mbid}.json
  - resumable: cached artists are skipped, so it can be stopped and restarted
  - retries with back-off on 503/429/network errors; 404 is cached as "not found"
  - log: results/logs/musicbrainz.log

Output: data/interim/mb_artists.csv (one row per artist_mbid). Joined to songs later in TurboPrep.
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import logging
import time

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
SUBSET = ROOT / "data" / "interim" / "msd_subset.csv"
CACHE = ROOT / "data" / "raw" / "musicbrainz_cache"
OUTPUT = ROOT / "data" / "interim" / "mb_artists.csv"
LOG = ROOT / "results" / "logs" / "musicbrainz.log"

API = "https://musicbrainz.org/ws/2/artist/{mbid}?inc=releases+genres+tags&fmt=json"
USER_AGENT = "MemoryBridgePrototype/0.1 (student research prototype)"
DELAY_SECONDS = 1.1
MAX_RETRIES = 5

LANGUAGE_NAMES = {"eng": "English", "spa": "Spanish", "fra": "French", "deu": "German",
                  "ita": "Italian", "por": "Portuguese", "jpn": "Japanese", "swe": "Swedish",
                  "fin": "Finnish", "nld": "Dutch", "hin": "Hindi", "mal": "Malayalam",
                  "zxx": "No linguistic content", "mul": "Multiple languages"}


def fetch(session: requests.Session, mbid: str) -> dict:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(API.format(mbid=mbid), timeout=30)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 404:
                return {"error": 404}
            logging.warning("mbid=%s status=%s attempt=%s", mbid, response.status_code, attempt)
        except requests.RequestException as exc:
            logging.warning("mbid=%s network error=%s attempt=%s", mbid, exc, attempt)
        time.sleep(DELAY_SECONDS * 2 ** attempt)
    return {"error": "failed"}


def download(mbids: list[str]) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    todo = [m for m in mbids if not (CACHE / f"{m}.json").exists()]
    logging.info("unique mbids=%s already cached=%s to fetch=%s", len(mbids), len(mbids) - len(todo), len(todo))

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    for i, mbid in enumerate(todo, 1):
        started = time.monotonic()
        data = fetch(session, mbid)
        if data.get("error") != "failed":  # failures are not cached, so a re-run retries them
            (CACHE / f"{mbid}.json").write_text(json.dumps(data), encoding="utf-8")
        if i % 100 == 0 or i == len(todo):
            logging.info("progress %s/%s", i, len(todo))
        time.sleep(max(0.0, DELAY_SECONDS - (time.monotonic() - started)))


def summarize(mbid: str) -> dict:
    path = CACHE / f"{mbid}.json"
    if not path.exists():
        return {"artist_mbid": mbid, "mb_status": "not_fetched"}
    data = json.loads(path.read_text(encoding="utf-8"))
    if "error" in data:
        return {"artist_mbid": mbid, "mb_status": f"error_{data['error']}"}

    languages = Counter((r.get("text-representation") or {}).get("language")
                        for r in data.get("releases", []))
    languages.pop(None, None)
    top_language = languages.most_common(1)[0][0] if languages else None
    genres = sorted(data.get("genres", []), key=lambda g: -g.get("count", 0))

    return {
        "artist_mbid": mbid,
        "mb_status": "ok",
        "mb_artist_name": data.get("name"),
        "mb_type": data.get("type"),
        "mb_country": data.get("country"),
        "mb_area": (data.get("area") or {}).get("name"),
        "mb_language_code": top_language,
        "mb_language": LANGUAGE_NAMES.get(top_language, top_language),
        "mb_release_count_sampled": len(data.get("releases", [])),
        "mb_top_genre": genres[0]["name"] if genres else None,
        "mb_genres": "|".join(g["name"] for g in genres[:5]) or None,
    }


def build_table(mbids: list[str]) -> None:
    table = pd.DataFrame([summarize(m) for m in mbids])
    table.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    ok = table[table.mb_status == "ok"]
    logging.info("wrote %s rows | ok=%s | country=%s | language=%s | genre=%s",
                 len(table), len(ok), ok.mb_country.notna().sum(),
                 ok.mb_language.notna().sum(), ok.mb_top_genre.notna().sum())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-only", action="store_true", help="skip API calls, rebuild CSV from cache")
    args = parser.parse_args()

    LOG.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(LOG, encoding="utf-8"), logging.StreamHandler()])

    mbids = sorted(pd.read_csv(SUBSET).artist_mbid.dropna().loc[lambda s: s.str.len() > 0].unique())
    if not args.build_only:
        download(mbids)
    build_table(mbids)


if __name__ == "__main__":
    main()
