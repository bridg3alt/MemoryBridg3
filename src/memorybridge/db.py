"""SQLite memory database: users, memories, interactions.

One local file (data/memorybridge.db). The user's own story is the source of truth; nothing is generated.
The interactions table has the same fields as the simulated training data, so real usage can later replace it.
"""
from contextlib import closing
from datetime import datetime
from pathlib import Path
import os
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
# Set MEMORYBRIDGE_DB to work on a throwaway copy. Automated runs must use it, so that testing
# the delete flow can never touch the real memories again.
DB_PATH = Path(os.environ.get("MEMORYBRIDGE_DB") or ROOT / "data" / "memorybridge.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    birth_year  INTEGER NOT NULL,
    language    TEXT NOT NULL,
    genres      TEXT NOT NULL DEFAULT '',
    region      TEXT NOT NULL DEFAULT '',
    demo_id     TEXT,
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS memories (
    memory_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(user_id),
    song_id     TEXT NOT NULL,
    story       TEXT NOT NULL,
    life_period TEXT NOT NULL,
    people      TEXT NOT NULL DEFAULT '',
    place       TEXT NOT NULL DEFAULT '',
    year        INTEGER,
    photo_path  TEXT,
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS interactions (
    interaction_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(user_id),
    song_id          TEXT NOT NULL,
    recognized       INTEGER NOT NULL,
    memory_triggered INTEGER NOT NULL,
    story_recorded   INTEGER NOT NULL,
    saved            INTEGER NOT NULL,
    ranked_by        TEXT NOT NULL,
    created_at       TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def create_user(name: str, birth_year: int, language: str, genres: list[str], region: str = "",
                demo_id: str | None = None, path: Path = DB_PATH) -> int:
    with closing(connect(path)) as db, db:
        cursor = db.execute(
            "INSERT INTO users (name, birth_year, language, genres, region, demo_id, created_at) VALUES (?,?,?,?,?,?,?)",
            (name, birth_year, language, "|".join(genres), region, demo_id, _now()))
        return cursor.lastrowid


def list_users(path: Path = DB_PATH) -> list[dict]:
    with closing(connect(path)) as db:
        return [dict(row) for row in db.execute("SELECT * FROM users ORDER BY user_id")]


def get_user(user_id: int, path: Path = DB_PATH) -> dict | None:
    with closing(connect(path)) as db:
        row = db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def log_interaction(user_id: int, song_id: str, recognized: bool, memory_triggered: bool,
                    story_recorded: bool, saved: bool, ranked_by: str, path: Path = DB_PATH) -> None:
    with closing(connect(path)) as db, db:
        db.execute(
            "INSERT INTO interactions (user_id, song_id, recognized, memory_triggered, story_recorded, saved, "
            "ranked_by, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (user_id, song_id, int(recognized), int(memory_triggered), int(story_recorded), int(saved),
             ranked_by, _now()))


def save_memory(user_id: int, song_id: str, story: str, life_period: str, people: str, place: str,
                year: int | None, photo_path: str | None, path: Path = DB_PATH) -> int:
    if not story.strip():
        raise ValueError("A memory needs the user's own story.")
    with closing(connect(path)) as db, db:
        cursor = db.execute(
            "INSERT INTO memories (user_id, song_id, story, life_period, people, place, year, photo_path, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (user_id, song_id, story.strip(), life_period, people.strip(), place.strip(), year, photo_path, _now()))
        return cursor.lastrowid


def set_photo(memory_id: int, photo_path: str, path: Path = DB_PATH) -> None:
    with closing(connect(path)) as db, db:
        db.execute("UPDATE memories SET photo_path = ? WHERE memory_id = ?", (photo_path, memory_id))


def get_memories(user_id: int, life_period: str | None = None, path: Path = DB_PATH) -> list[dict]:
    query, params = "SELECT * FROM memories WHERE user_id = ?", [user_id]
    if life_period:
        query += " AND life_period = ?"
        params.append(life_period)
    with closing(connect(path)) as db:
        return [dict(row) for row in db.execute(query + " ORDER BY year, created_at", params)]


def dismissed_song_ids(user_id: int, path: Path = DB_PATH) -> set[str]:
    """Songs that did not ring a bell or already have a saved memory, so they are not suggested again."""
    with closing(connect(path)) as db:
        rows = db.execute("SELECT DISTINCT song_id FROM interactions WHERE user_id = ? AND (recognized = 0 OR saved = 1)",
                          (user_id,))
        return {row["song_id"] for row in rows}


def count_memories(user_id: int, path: Path = DB_PATH) -> int:
    with closing(connect(path)) as db:
        return db.execute("SELECT COUNT(*) FROM memories WHERE user_id = ?", (user_id,)).fetchone()[0]


def delete_user(user_id: int, path: Path = DB_PATH) -> list[str]:
    """Remove a listener with every memory and reaction they left. Cannot be undone.

    Returns the photo paths that were attached, so the caller can delete the image files too.
    """
    with closing(connect(path)) as db, db:
        photos = [row["photo_path"] for row in
                  db.execute("SELECT photo_path FROM memories WHERE user_id = ? AND photo_path IS NOT NULL",
                             (user_id,))]
        db.execute("DELETE FROM interactions WHERE user_id = ?", (user_id,))
        db.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
        db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    return photos
