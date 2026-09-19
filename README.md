# MemoryBridge

A small prototype for the Altair Global Student Contest. MemoryBridge uses music as a personal cue for revisiting and preserving autobiographical memories.

A user enters their birth year, language and favourite genres. MemoryBridge suggests songs that plausibly belong to periods of their life. The user can then write down what a song reminds them of, and look back at those memories later by life period (for example "Childhood" or "College").

> **Not a medical product.** MemoryBridge does not diagnose, treat, cure or slow any condition (including dementia or Alzheimer's), and makes no claim to restore memory. It never invents memories: the user's own recorded story is the only source of truth.

## Pipeline

```text
Million Song Dataset (MSD) + MusicBrainz
            │
            ▼
        TurboPrep            clean, join, standardize   (user, in AI Studio)
            │
            ▼
   songs_master.csv
            │
            ▼
  RapidMiner / AI Studio     features, models, evaluation, predictions   (user)
            │
            ▼
   Top-10 song suggestions
            │
            ▼
  MemoryBridge app           Streamlit + SQLite   (Python)
            │
            ▼
  User records memory → stored → revisited by life period
```

## Who does what

| Tool | Responsible for |
|---|---|
| **TurboPrep** | Cleaning, joining, standardizing, preparing the master song table |
| **RapidMiner / AI Studio** | Exploration, feature engineering, predictive models, model comparison, evaluation, predictions |
| **Python** | Downloading/inspecting data, the MusicBrainz API, small utilities, the SQLite database, the Streamlit app, tests, and connecting RapidMiner output to the app |

Python does not replace the TurboPrep or RapidMiner steps.

## Scale

| | Songs | Status |
|---|---|---|
| **Prototype** | about 8,000 (1950–2010, spread evenly across decades) | planned, Checkpoint 2 |
| Possible production scale | 80k–100k+ | not built, not claimed |

The full 1M-song MSD has **not** been processed.

## Folder layout

```text
MemoryBridge_IEDC/
├── README.md, progress.md, todo.md
├── data/
│   ├── raw/          original downloads (never edited)
│   ├── interim/      Python-prepared subset (input to TurboPrep)
│   └── processed/    TurboPrep / RapidMiner exports
├── docs/             data dictionary, checklists, assumptions, demo script
├── src/              Python utilities (download, subset, MusicBrainz, database)
├── app/              Streamlit app (later)
├── rapidminer/       exported .rmp processes
├── results/          metrics and screenshots from real runs
└── presentation/     slides
```

## Running the app

```sh
cd C:\Users\brigi\MemoryBridge_IEDC
streamlit run app/streamlit_app.py
```
It opens in the browser at http://localhost:8501. Pages: My Profile, Memory Journey, Music Cue, Capture Memory, My Life in Music.
Songs are ranked in two stages: the baseline formula picks 200 candidates, then the RapidMiner Random Forest orders them. Every listener is served from the nearest cell of the scored profile grid (same language, closest birth year; see `src/06_make_profile_grid.py`). Until the grid is scored in AI Studio the app falls back to the baseline formula alone, and always prints on screen which was used. Memories are stored in `data/memorybridge.db` (SQLite) and photos in `data/photos/`.

Tests: `python -m pytest tests`

See [progress.md](progress.md) for current status and [todo.md](todo.md) for the checkpoint plan.

## Data sources
- Million Song Dataset: Bertin-Mahieux et al., 2011, http://millionsongdataset.com
- tagtraum genre labels (CD2): Schreiber, 2015, https://www.tagtraum.com/msd_genre_datasets.html
- MusicBrainz: https://musicbrainz.org (CC0 core data)
- Billboard Hot 100: utdata/rwd-billboard-data (optional, Priority 3)
