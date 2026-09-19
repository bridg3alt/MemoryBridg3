"""Find something playable for a song, so listening happens inside the app.

Three sources, best first:

1. A local file  `data/audio/<song_id>.mp3` (or .m4a/.ogg/.wav). Always right, works offline,
   any language. You put these there yourself for the songs used in a demo.
2. A 30-second preview from the iTunes Search API (free, no key, no sign-up). Found by searching
   the artist and title as text, so it only works when those are in Latin script -- English yes,
   Hindi often, Malayalam script no.
3. Nothing, in which case the app keeps the YouTube search link.

Preview lookups are cached in `data/processed/preview_cache.csv` so a demo never depends on the
network being up, and so the same song is never looked up twice.
"""
from pathlib import Path
import json
import urllib.parse
import urllib.request

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AUDIO = ROOT / "data" / "audio"
CACHE = ROOT / "data" / "processed" / "preview_cache.csv"
EXTENSIONS = (".mp3", ".m4a", ".ogg", ".wav")
ITUNES = "https://itunes.apple.com/search"
TIMEOUT = 8


def local_audio(song_id: str) -> Path | None:
    """A file you placed yourself, named after the song id."""
    for extension in EXTENSIONS:
        candidate = AUDIO / f"{song_id}{extension}"
        if candidate.exists():
            return candidate
    return None


def load_cache(path: Path = CACHE) -> dict[str, str]:
    """song_id -> preview url. An empty string means 'looked for it, found nothing'."""
    if not path.exists():
        return {}
    frame = pd.read_csv(path, encoding="utf-8-sig").fillna("")
    return dict(zip(frame.song_id.astype(str), frame.preview_url.astype(str)))


def save_cache(cache: dict[str, str], path: Path = CACHE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame({"song_id": list(cache), "preview_url": list(cache.values())})
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def _is_latin(text: str) -> bool:
    """iTunes searches text, so a title written in Malayalam or Devanagari will not be found."""
    letters = [character for character in str(text) if character.isalpha()]
    return bool(letters) and sum(character.isascii() for character in letters) / len(letters) > 0.6


def fetch_preview(title: str, artist: str) -> str:
    """Ask iTunes for a 30-second preview. Returns '' when there is nothing to play."""
    if not _is_latin(title) and not _is_latin(artist):
        return ""
    terms = urllib.parse.quote(f"{artist} {title}".strip()[:180])
    url = f"{ITUNES}?term={terms}&entity=song&limit=1"
    request = urllib.request.Request(url, headers={"User-Agent": "MemoryBridge/0.1 (student project)"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            results = json.load(response).get("results", [])
    except Exception:                                    # offline, rate limited, malformed reply
        return ""
    return results[0].get("previewUrl", "") if results else ""


def playable(song_id: str, title: str, artist: str, cache: dict[str, str] | None = None,
             allow_lookup: bool = True) -> tuple[str, str]:
    """What to play for this song, and where it came from.

    Returns (source, value): ("file", path) | ("preview", url) | ("", "").
    """
    file = local_audio(song_id)
    if file:
        return "file", str(file)

    cache = {} if cache is None else cache
    if song_id in cache:
        return ("preview", cache[song_id]) if cache[song_id] else ("", "")
    if not allow_lookup:
        return "", ""

    url = fetch_preview(title, artist)
    cache[song_id] = url
    return ("preview", url) if url else ("", "")
