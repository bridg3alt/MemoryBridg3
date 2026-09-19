# Progress

Last updated: 2026-09-17 (Checkpoint 2)

## Completed
- Project folders created: data/raw, data/processed, docs, src, rapidminer, results, presentation.
- Raw files downloaded and checked (row counts measured with `wc -l` and pandas):
  - `unique_tracks.txt`: 1,000,000 tracks, 72,665 distinct artist names.
  - `tracks_per_year.txt`: 515,576 tracks with a release year (1922–2011).
  - `msd_tagtraum_cd2.cls`: 280,831 tracks with a genre label (15 genres), unzipped.
  - `hot-100-current.csv`: Billboard weekly charts, 1958-08-04 to 2026-09-19, 32,752 unique title+performer pairs.
- Tools confirmed: Altair AI Studio 2026.1.1 installed; Python 3.13.7 with pandas, numpy, requests, scikit-learn, matplotlib.
- Measured the tracks that have both a year and a genre: 223,140 in total, 222,766 of them from 1950–2010.
- Checkpoint 1 docs written: README.md, progress.md, todo.md, docs/data_dictionary.md.
- Checkpoint 2: h5py installed; `msd_summary_file.h5` downloaded (316 MB, 1,000,000 rows, fields confirmed).
- Hindi dataset (Bollywood metadata, MIT) downloaded: 57,005 songs, 12,673 albums.
- Malayalam dataset (Mal_lyrics_analysis, MIT) downloaded: 26,232 songs. Lyrics dropped, first line kept as title.
- `data/interim/msd_subset.csv`: 6,496 songs, 928 per decade 1950–2010, seed 42.
- `data/interim/bollywood_songs_raw.csv`, `bollywood_albums_raw.csv`, `malayalam_songs_raw.csv` created (raw, uncleaned).
- docs/dataset_notes.md and docs/turboprep_checklist.md written.
- MusicBrainz enrichment done: 3,502 of 3,525 artists found; country 98.4%, language 99.8%. Output: `data/interim/mb_artists.csv`.
- TurboPrep Part A (Hindi) done: `hindi_clean.csv`, 2,000 rows (verified).
- TurboPrep Part B (Malayalam) done: `malayalam_clean.csv`, 1,349 rows (1,500 sampled, then 151 placeholder/"." titles removed; verified).
- TurboPrep Part C (MSD + MusicBrainz join) done: `msd_clean.csv`, 6,491 rows (5 rows broken by the '#' comment character were removed; verified).
- TurboPrep Part D done: appended the three tables and standardized language (15 ISO codes → Norwegian/Danish/Other). **`data/processed/songs_master.csv`: 9,840 rows × 14 columns (verified 2026-09-17 19:44).**
  - By source: MSD 6,491 · Bollywood 2,000 · Malayalam 1,349. 0 duplicate song_ids. Years 1950–2010.
  - Language: English 5,921 · Hindi 2,000 · Malayalam 1,349 · Spanish 140 · Unknown 93 · French 88 · German 54 · Italian 48 · Portuguese 45 · Multiple languages 35 · Swedish 19 · Other 17 · Finnish 12 · Norwegian 11 · Danish 4 · Japanese 3 · Dutch 1.
  - Missing: popularity 5,238 · tempo/loudness/key 3,349 (the Indian datasets have no audio fields) · country 152 · artist 44.

- TurboPrep process saved: `rapidminer/turboprep_songs_master.rmp`.
- **Milestone 1 reached (Checkpoint 5):** baseline recommender `src/memorybridge/` (profile.py, recommender.py, recommend.py). Weights: era 40 / language 20 / genre 15 / artist 10 / popularity 15. Missing popularity = neutral 0.5 (user decision). At most 2 songs per exact artist string. 3 unit tests pass (`tests/test_recommender.py`). Checked on 3 profiles (Malayalam 1958 College, Hindi 1952 + Lata Mangeshkar, English 1950 Rock/Pop College); all returned in-period, same-language songs with reasons.

- Checkpoint 6 prep: SIMULATED data made by `src/04_simulate_interactions.py` (seed 2026): 300 synthetic listeners; `interactions_train.csv` 9,589 rows / 240 listeners / 43.0% yes; `interactions_holdout.csv` 2,400 rows / 60 listeners / 40.2% yes; `demo_candidates.csv` 49,200 rows. Docs: `docs/simulation_assumptions.md`, `docs/rapidminer_steps.md`.

- Checkpoint 6 (user, AI Studio): process `MemoryBridge_model`. Cross Validation with split on batch attribute (user_id). ⚠ SIMULATED results: LR AUC 0.790 · RF 0.831 · GBT 0.835. **Random Forest chosen.** Holdout (60 unseen listeners): AUC 0.804; top-10 hit rate RF 74.2% vs baseline 63.2% vs random 40.2%. Details in results/model_comparison.md.

- Part 3c done: `data/processed/predictions_demo.csv` (49,200 rows, 5 profiles). Found that the Random Forest ranking all songs alone lets some wrong-language songs into the top 10; chose a two-stage design (baseline top 200, then RF ranking), documented in results/model_comparison.md.
- RapidMiner process `MemoryBridge_model` now has 3 rows: cross-validation, holdout scoring (predictions_holdout.csv, written to data/ with ';'), demo scoring.

- **Checkpoint 7 done: web app built.** `app/streamlit_app.py` (5 pages), `src/memorybridge/db.py` (SQLite: users, memories, interactions), `src/memorybridge/ranking.py` (two-stage: baseline top 200, then RapidMiner confidence). 9 tests pass (`tests/`). Headless end-to-end run verified: demo profile D1, College, a Malayalam song from 1976 ranked by the RapidMiner model, memory saved, timeline shows it, database rows written.
- Bug found by the tests and fixed: an all-empty popularity column made pandas treat scores as text (`pd.to_numeric` in recommender.py).

- **Checkpoint 8 (UI pass, 2026-09-18):** paper-and-ink hand-drawn theme in `app/style.py`
  (Caveat / Patrick Hand / Permanent Marker + Kalam for Devanagari; palette #f7f6f1 paper,
  #1f1b16 ink, #cc2018 red). Sidebar removed; top folder-tab navigation with hand-drawn icons,
  plus a **Back** button backed by a page history in `st.session_state.history`. Illustrations:
  6 Open Doodles figures (CC0) and 14 Iconoodle icons (MIT), all recolored to the two palette
  colours, in `app/assets/doodles/` and `app/assets/icons/`. All emoji removed.
- **Speech to text in Capture a Memory:** `streamlit-mic-recorder` (installed), language chosen
  from the listener's profile (ml-IN / hi-IN / en-IN ...). Transcript lands in
  `st.session_state.story_draft`, is editable, and nothing saves until "Keep this memory".
- **Profile grid for RapidMiner (NEEDS USER ACTION):** `src/06_make_profile_grid.py` wrote
  `data/processed/grid_candidates.csv` (265,680 rows = 27 stand-in profiles x 9,840 songs, 21.7 MB).
  `ranking.py` now falls back to `predictions_grid.csv` via `grid_cell()` (same language, closest
  birth year) so real listeners get model rankings, not just D1-D5. Scoring it in AI Studio is
  Part 4 of `docs/rapidminer_steps.md` — until that runs, real profiles still say "Baseline formula".

- **2026-09-18, second UI pass:** fonts back to Anton / Special Elite / Permanent Marker (the
  hand-drawn Caveat set was rejected). Navigation tabs restyled through `st.container(key="mb_nav")`
  -> `.st-key-mb_nav` because a markdown `<div>` cannot wrap Streamlit buttons, which is why the
  first version showed an empty bordered strip and clipped labels; labels now wrap in full.
- **Demo profiles removed** from the app and the database (D1-D5 had 0 saved memories; interactions
  deleted with them, backup at `data/memorybridge.db.bak`). `predictions_demo.csv` is no longer read.
  Everything now goes through the profile grid, so scoring `grid_candidates.csv` in AI Studio is
  what makes the model live.
- **Speech to text fixed:** the transcript was written to `story_draft` and passed as `value=` to a
  text box that keeps its own state, so it never appeared. The box is now `key="story_input"` and the
  transcript is written straight into that key. Also shows what was heard, and a message when nothing was.

- **2026-09-18, model is live for every listener.** User built row 4 of `MemoryBridge_model`
  (Retrieve grid_candidates -> Set Role -> Select Attributes -> Replace Missing Values ->
  Apply Model <- Multiply -> Write CSV) and ran it. `data/processed/predictions_grid.csv`:
  **265,680 rows, 27 profiles, 9,840 songs, confidence(yes) 0.024-0.854, no nulls, 5,938 distinct
  values.** Verified in the app: Thomas (1960, Malayalam) now reads
  "RapidMiner Random Forest (nearest profile in the grid): G_Malayalam_1960".
  Loader hardened first (`_load` in ranking.py reads utf-8-sig and names any missing column),
  because AI Studio's BOM had crashed the Music Cue page with KeyError: ['user_id'] not in index.

## In Progress
- Nothing. Waiting for the user to run the app.

## Needs User Action
- Try the recommender with your own profiles (see README / Next Step).
- ~~Score the grid in AI Studio~~ DONE 2026-09-18.
- Save one real memory (with a photo) and check it survives a restart. `memories` is still 0 rows.
- Collect 30-60 real reactions from 3-5 real listeners, to replace the SIMULATED training data.

## Needs Verification
- AI Studio's CSV import treats '#' as a comment character by default. This explains the 5-row Malayalam difference (4 film names with '#', all from 2021, so removed anyway) and the 5 broken MSD rows.

## Problems
- `tracks_per_year.txt` was truncated in the first download (78,570 of 515,576 rows, cut off in 1989). **Fixed:** downloaded again, now 515,576 rows ending in a complete 2011 record.
- 74,065 rows in `unique_tracks.txt` repeat an artist+title pair already seen, so the data has duplicate songs. TurboPrep will handle this.
- Songs with a year and genre are heavily skewed to the 2000s (128,641) compared with the 1950s (1,210). The subset must be spread evenly across decades.
- No `energy` values in the MSD (always 0), and no language or country fields. See docs/data_dictionary.md.
- MSD `energy` is 0 for all 1M songs (measured), so it can't be used.
- `song_hotttnesss` is missing for 38.1% of the subset.
- Hindi `song_rating` is 0 (unrated) for 68.2%. One Hindi album_uuid is duplicated.
- Malayalam: 2,499 blank titles and 6,297 repeated film+title pairs. Names are in Malayalam script.
- streamlit is not installed (needed at Checkpoint 7).
- RapidMiner Write CSV defaulted to the `;` separator and the path `data/` (not `data/processed/`); src/05 handles both. Performance (2) shows positive class "no" on the holdout; AUC is unaffected.
- Baseline limitation: Malayalam songs have no popularity or audio fields, so many tie at exactly 82.5. Their order among ties is just file order, not meaningful.
- Artist-per-song cap uses the exact artist text, so "K J Yesudas" and "K J Yesudas, Chorus" count as different artists.
- Malayalam CSV import broke on line breaks and double quotes inside text. **Fixed** in src/02 (replaced with a space and ', respectively).
- TurboPrep CSV export used the SYSTEM encoding, which turned Malayalam into ???. **Fixed:** set AI Studio Preferences → Encoding to UTF-8.
- Hidden trailing spaces in names typed into Generate/Rename (`popularity `, `country `). **Fixed** by renaming.
- 149 of the 1,500 sampled Malayalam titles were the website placeholder "ഇവിടെ ക്ലിക്ക് ചെയ്തു ചേര്‍ക്കാം" ("click here to add"), and 2 were "." — being removed in TurboPrep.
- Turbo Prep's Sample has no seed option, so the samples cannot be reproduced exactly; the saved exports are the fixed record.
- Remove Duplicates in Turbo Prep treats missing values as different from each other (Hindi: removed 30, not 92).

## Next Step
User runs `python -m streamlit run app/streamlit_app.py`, saves one real memory with a photo, and checks the timeline. Then Checkpoint 8: slides, demo script, screenshots.
