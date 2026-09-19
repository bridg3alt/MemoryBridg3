# To-do

Owner tags: **[USER-TP]** means work in TurboPrep, **[USER-RM]** means work in RapidMiner/AI Studio, **[PY]** means work in Python, **[BOTH]** means both.

Each checkpoint ends with a report back, and the next one starts only after the user says so.

## Priority 1: Must have

### Checkpoint 2: Data subset
- [ ] [PY] `pip install h5py`, download `msd_summary_file.h5` (316 MB), and inspect its real fields
- [ ] [PY] Build an 8k-song subset (1950–2010, has year and genre, spread evenly across decades) with audio fields and artist_mbid: `data/interim/msd_subset.csv`
- [ ] [PY] Report the unique artist count, MusicBrainz request estimate and runtime, and **wait for approval**
- [ ] [PY] Write `docs/dataset_notes.md` (row counts at each step)

### Checkpoint 3: MusicBrainz enrichment (only after approval)
- [ ] [PY] `src/musicbrainz_enrich.py`: 1 request/s, User-Agent, cache, retry, resume, logging
- [ ] [PY] Output `data/interim/mb_artists.csv` (country, area, language, genre) and report real coverage

### Checkpoint 4: TurboPrep
- [ ] [PY] Write `docs/turboprep_checklist.md` with exact steps, reasons, expected results and screenshots to take
- [ ] [USER-TP] Import the subset and inspect it: missing values, duplicates, text cleanup
- [ ] [USER-TP] Join the MusicBrainz data, standardize genre and language, create the needed fields
- [ ] [USER-TP] Export `data/processed/songs_master.csv`
- [ ] [PY] Check the export (row count, columns, missing values)

### Checkpoint 5: Baseline recommender = Milestone 1
- [ ] [PY] Transparent score: era 40%, language 20%, genre 15%, artist 10%, popularity 15% (prototype assumptions, not validated)
- [ ] [PY] CLI: birth year + language gives 10 songs with reasons
- [ ] [BOTH] Review what worked, what data was used, what RapidMiner and Python each did, and what remains

### Checkpoint 6: RapidMiner model
- [ ] [PY] Synthetic interactions, clearly labelled **SIMULATED**, plus `docs/simulation_assumptions.md`
- [ ] [PY] Write `docs/rapidminer_steps.md` (includes a lesson on data leakage and splitting by user)
- [ ] [USER-RM] Read Data, Set Role, Generate/Select Attributes, Cross Validation (split by user), Logistic Regression / Random Forest / Gradient Boosted Trees, Performance
- [ ] [USER-RM] Compare the models and record real AUC, accuracy, precision, recall and F1 in `results/`
- [ ] [USER-RM] Apply Model, export predictions, save `rapidminer/MemoryBridge.rmp`
- [ ] [PY] Top-10 from RapidMiner predictions, with hit rate compared to the baseline

### Checkpoint 7: App + memory
- [x] [PY] SQLite database with `users`, `memories` and `interactions`
- [x] [PY] Streamlit screens: Profile, Memory Journey, Music Cue, Capture Memory, Timeline
- [ ] [BOTH] Save one memory, restart the app, and get it back

## Priority 2: Nice to have
- [ ] MusicBrainz enrichment expansion
- [ ] Photos attached to memories
- [ ] Timeline improvements
- [ ] Multiple life periods
- [ ] Interaction logging improvements

## Priority 3: Only if time remains
- [ ] Speech-to-text
- [ ] Billboard enrichment (`charted` flag)
- [ ] Advanced visualizations
- [ ] Larger dataset (80k+)
- [ ] More sophisticated personalization

## Checkpoint 8: Wrap-up
- [ ] [PY] `docs/demo_script.md` (5 minutes)
- [ ] [USER] Slides, screenshots, demo recording
