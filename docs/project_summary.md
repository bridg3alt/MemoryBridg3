# MemoryBridge — complete project summary

Everything built, measured and decided, from the first download to the submission package.
Written 2026-09-18. Numbers here are measured, not estimated; each one can be traced to a file
in this repository.

---

## 1. The idea

MemoryBridge uses music as a cue for autobiographical memory. A person enters their birth year,
language and favourite genres. The app suggests songs that plausibly belong to periods of their
life, the person writes down what a song reminds them of, and later revisits those memories by
life period.

The loop is: **cue → memory → storage → retrieval by life period.**

Life periods (`src/memorybridge/profile.py`) are product categories, not medical facts:
Childhood 10–15, College 16–22, Early adulthood 23–30, Family/Career 31–45. Default window when
no period is chosen: ages 10–30.

**Disclaimer carried through every document:** not a medical product. Does not diagnose, treat,
cure or slow any condition including dementia. Makes no claim to restore memory. Never invents a
memory — the user's own recorded story is the only source of truth.

**Research basis:** Cuddy, Sikka et al., "A Focus on the Reminiscence Bump to Personalize Music
Playlists for Dementia", Journal of Multidisciplinary Healthcare, 2021. Recollection of popular
music peaks around the teenage years. That is where the age 10–30 window and the age-20 peak come
from. That literature is about dementia care; MemoryBridge makes no medical claim.

## 2. Where it sits among existing products (`docs/related_work.md`)

Two groups of products exist and MemoryBridge sits between them.

- **Group A, personalised music for memory loss** — Music & Memory, Music for My Mind, generic
  decade playlists. They all require someone to already know the person's songs, and they stop at
  the playlist.
- **Group B, life-story apps** — StoryWorth, LifeBio Memory, My House of Memories, Memoir. They
  start at the story and use written prompts, not music, as the cue.

What is new here: it closes the loop from cue to retrieval, it covers Hindi and Malayalam rather
than English only, and the cues are 9,840 songs ranked per person by a model rather than a
curated list.

## 3. Division of work

| Tool | Responsible for |
|---|---|
| **TurboPrep** (Altair AI Studio) | Cleaning, joining, standardising, producing the master song table |
| **RapidMiner / AI Studio** | Feature selection, model training, cross validation, model comparison, holdout evaluation, batch scoring |
| **Python** | Downloads, MusicBrainz API, sampling, the simulator, the SQLite database, the Streamlit app, tests, connecting RapidMiner output to the app |

## 4. Data sources and licences (`docs/dataset_notes.md`)

| Dataset | Source | Licence | Used for |
|---|---|---|---|
| Million Song Dataset (summary file, unique_tracks, tracks_per_year) | millionsongdataset.com, Bertin-Mahieux et al. 2011 | Free for research | Western songs, years, audio fields |
| tagtraum genre labels CD2 | tagtraum.com, Schreiber 2015 | Free for research, credit required | MSD genres |
| Bollywood Songs & Albums Metadata 1931–2025 | github.com/MrAsacker/bollywood-songs-metadata | MIT, scraped from MySwar | Hindi film songs |
| Malayalam song dataset | github.com/Abhinav-ark/Mal_lyrics_analysis | MIT, scraped from a Malayalam song site | Malayalam film songs |
| Billboard Hot 100 | utdata/rwd-billboard-data | Public GitHub | Downloaded, not used in the final model |
| MusicBrainz | API | Live API, 1 request/second | Artist country and language |

Raw file sizes and counts, all measured:
- `unique_tracks.txt` — 1,000,000 rows, 72,665 distinct artist names, 74,065 rows repeat an
  artist+title pair already seen.
- `tracks_per_year.txt` — 515,576 rows, 1922–2011. **First download was truncated at 78,570 rows,
  cut off in 1989; caught by a row count and downloaded again.**
- `msd_tagtraum_cd2.cls` — 280,831 rows, 15 genres.
- `msd_summary_file.h5` — 316 MB, 1,000,000 rows, three tables.
- `hot-100-current.csv` — 1958-08-04 to 2026-09-19, 32,752 unique title+performer pairs.
- Hindi — 57,005 songs, 12,673 albums (one album_uuid duplicated), 68.2% unrated.
- Malayalam — 26,232 songs, 1938–2022.

Fields checked and rejected:
- `energy` is 0 for all 1,000,000 MSD songs — unusable.
- `song_hotttnesss` missing for 38.1% of the subset.
- `artist_location` is free text, not a country — replaced by MusicBrainz country.
- Hindi `song_rating` is 0 for 68.2%.

## 5. Preparation pipeline, stage by stage

### 5.1 Python preparation

| Script | Output | Result |
|---|---|---|
| `src/01_make_msd_subset.py` | `data/interim/msd_subset.csv` | 1,000,000 → 223,140 with year **and** genre → **6,496** sampled, 928 per decade 1950–2010, seed 42 |
| `src/02_prepare_indian_inputs.py` | `bollywood_songs_raw.csv`, `bollywood_albums_raw.csv`, `malayalam_songs_raw.csv` | Raw extracts, headers translated from Malayalam script |
| `src/03_musicbrainz_enrich.py` | `data/interim/mb_artists.csv` | **3,502 of 3,525 artists found.** Country 98.4%, language 99.8%. 1 request/second, User-Agent, cache, retry, resume, logging |

Why the subset is stratified: songs with both year and genre are heavily skewed to the 2000s
(1950s 1,210 vs 2000s 128,641). A random sample would have almost no music for an older listener,
so the sample takes 928 songs per decade.

### 5.2 TurboPrep in AI Studio (`rapidminer/turboprep_songs_master.rmp`)

| Part | Input | Output rows |
|---|---|---|
| A | Hindi raw | `hindi_clean.csv` — 2,000 |
| B | Malayalam raw | `malayalam_clean.csv` — 1,349 (1,500 sampled, 151 placeholder/"." titles removed) |
| C | MSD subset + MusicBrainz join | `msd_clean.csv` — 6,491 (5 rows broken by `#` removed) |
| D | Append all three, standardise 15 ISO language codes | **`data/processed/songs_master.csv` — 9,840 rows × 14 columns** |

Master table composition: MSD 6,491 · Bollywood 2,000 · Malayalam 1,349. Years 1950–2010. Zero
duplicate song_ids.

By language: English 5,921 · Hindi 2,000 · Malayalam 1,349 · Spanish 140 · Unknown 93 · French 88
· German 54 · Italian 48 · Portuguese 45 · Multiple 35 · Swedish 19 · Other 17 · Finnish 12 ·
Norwegian 11 · Danish 4 · Japanese 3 · Dutch 1.

Missing values carried forward: popularity 5,238 · tempo/loudness/key 3,349 (the Indian datasets
have no audio fields) · country 152 · artist 44.

### 5.3 Data-cleaning problems found and fixed

These are worth naming in the report; each was found by counting rows or reading output, not by
assuming the tool was right.

- AI Studio's CSV import treats `#` as a comment by default — silently broke 5 MSD rows and 4
  Malayalam film names.
- TurboPrep's CSV export used the **system encoding**, turning Malayalam text into `???`. Fixed by
  setting Preferences → Encoding to UTF-8.
- Malayalam import broke on line breaks and double quotes inside text fields — fixed in `src/02`.
- 149 of 1,500 sampled Malayalam titles were the website placeholder "ഇവിടെ ക്ലിക്ക് ചെയ്തു ചേര്‍ക്കാം"
  ("click here to add") and 2 were "." — removed.
- Hidden trailing spaces in field names typed into Generate/Rename (`popularity `, `country `) —
  found and renamed.
- Turbo Prep's Sample has no seed, so samples are not exactly reproducible; the saved exports are
  the fixed record.
- Turbo Prep's Remove Duplicates treats missing values as different from each other (Hindi: removed
  30, not 92).

## 6. Baseline recommender — Milestone 1

`src/memorybridge/recommender.py`, `profile.py`, `recommend.py`.

Transparent weighted score, stated as a prototype assumption and not a validated formula:

| Component | Weight |
|---|---|
| Era (age at release inside the chosen life period) | 40% |
| Language match | 20% |
| Genre match | 15% |
| Artist match | 10% |
| Popularity | 15% |

Missing popularity counts as a neutral 0.5. At most 2 songs per exact artist string. CLI takes a
birth year and language and returns 10 songs with a written reason for each. 3 unit tests pass.
Checked on 3 profiles: Malayalam 1958 College, Hindi 1952 with Lata Mangeshkar, English 1950
Rock/Pop College — all returned in-period, same-language songs.

Known limitation: Malayalam songs have no popularity or audio fields, so many tie at exactly 82.5,
and their order among ties is file order, not meaning. This is one of the reasons a model was
worth adding.

## 7. Training data — SIMULATED (`docs/simulation_assumptions.md`)

No real listener reactions exist yet, so `src/04_simulate_interactions.py` (seed 2026) generates
them.

**300 synthetic listeners:** language English 40% / Hindi 30% / Malayalam 30% (actual 104 / 97 /
99). Birth year uniform 1940–1975. Favourite genres drawn per language. 40% get a favourite artist
from their own language and era. Each has a hidden "taste" value (normal, sd 0.7) that is in no
output file.

**40 songs each:** 20 from that listener's baseline top 200, 20 drawn at random from all 9,840, so
clearly unsuitable songs are present too. Duplicates removed.

**The hidden reaction rule:**

```
bump = exp(-((age_at_release - 20) / 7)^2)
z    = -2.9 + 2.8*bump + 1.4*language_match + 0.6*genre_match
       + 1.2*artist_match + 1.0*(popularity/100 - 0.5) + taste
P(memory_triggered = yes) = 1 / (1 + e^-z)
```

Deliberate design choice: the rule uses a smooth curve around age 20, but the model only receives
`age_at_release`, `in_age_10_30` and `years_outside_10_30`. The model has to approximate the curve;
it is not handed it.

Chain of reactions: `recognized` happens more easily than a memory; `memory_triggered` requires
recognition; `liked` 90% after a memory, otherwise 50% of recognised songs; `story_recorded` 60%
of memories; `saved` 85% of stories.

**Outputs:** `users_synthetic.csv`, `interactions_train.csv` (9,589 rows, 240 listeners, 43.0%
yes), `interactions_holdout.csv` (2,400 rows, 60 listeners, 40.2% yes), `demo_candidates.csv`
(49,200 rows).

**The limitation, stated everywhere it appears:** a model trained on these labels can at best
rediscover the rules that made them. A high AUC is not evidence that music triggers memories in
real people. It shows the pipeline runs end to end and that RapidMiner learns a pattern that is
present. Every result is labelled SIMULATED.

## 8. Modelling in RapidMiner (`rapidminer/MemoryBridge_model.rmp`)

Label `memory_triggered`. Seven features: `age_at_release`, `in_age_10_30`,
`years_outside_10_30`, `language_match`, `genre_match`, `artist_match`, `popularity`. Missing
popularity replaced with the training average, 63.633, applied identically to training, holdout,
demo and grid data.

**Validation: Cross Validation with split on batch attribute, batch = `user_id`** —
leave-one-listener-out. Each listener's rows are tested on a model that never saw that listener. A
random row split would leak the same listener into both sides and inflate every score.

| Model | AUC | Accuracy | Precision (yes) | Recall (yes) | F1 |
|---|---|---|---|---|---|
| Logistic Regression | 0.790 ± 0.081 | 71.87% ± 8.79% | 68.69% micro | 64.73% ± 25.25% | 66.07% |
| **Random Forest** | **0.831 ± 0.073** | **74.08% ± 7.86%** | 66.58% ± 16.76% | **80.52% ± 10.81%** | 71.25% ± 11.26% |
| Gradient Boosted Trees | 0.835 ± 0.073 | 73.77% ± 8.47% | 75.92% ± 16.50% | 58.28% ± 14.98% | 64.00% ± 11.81% |

Reference point: always predicting "no" gives 57.0% accuracy.

Pooled confusion matrices: LogReg TP 2,626 / FP 1,197 / FN 1,500 / TN 4,266 · Random Forest TP
3,274 / FP 1,633 / FN 852 / TN 3,830 · GBT TP 2,350 / FP 739 / FN 1,776 / TN 4,724.

Independent check outside RapidMiner (Python, scikit-learn logistic regression, 5 listener-grouped
folds): accuracy 0.730, AUC 0.786 — close to RapidMiner's 0.7187 / 0.790, so the RapidMiner setup
is not producing an inflated number.

**Random Forest chosen**, and the reason matters more than the number: its AUC ties with Gradient
Boosted Trees well inside the ±0.073 spread, but its recall is 80.5% against 58.3%. For a
reminiscence app, missing a song that would have triggered a memory is the expensive error;
showing one extra song that does not work costs the user a scroll. It is also the easier model to
explain.

## 9. Evaluation on unseen listeners

Holdout: 60 listeners (U241–U300) never used in training.

- AI Studio Performance: **AUC 0.804** (displayed with positive class "no"; ROC AUC is identical
  either way, and a Python check using `confidence(yes)` gives 0.804 as well).
- Top-10 hit rate (`src/05_evaluate_ranking.py`) — of each listener's top 10 songs, the share that
  were real "yes" answers, averaged over listeners:

| Ranking method | Top-10 hit rate |
|---|---|
| **RapidMiner Random Forest** | **74.2%** |
| Baseline formula | 63.2% |
| Random order | 40.2% |

## 10. The finding that changed the design

Scoring all 9,840 songs for 5 demo profiles (`predictions_demo.csv`, 49,200 rows) exposed a real
failure: when the Random Forest ranked every song on its own, 1–2 of the top 10 for some profiles
were in the wrong language. Demo D1 (Malayalam) received "The Ghost Of Al Capone" — English,
popularity 19 — at confidence 0.705, above in-period Malayalam film songs at 0.685. Language match
in the top 10: D1 80%, D2 90%, D3 80%, D4 100%, D5 100%.

Diagnosis: in training, half of each listener's songs came from the baseline top 200, so the model
saw few wrong-language, low-popularity songs inside the age bump. Its predictions in that rarely
seen region are unreliable. Many Malayalam songs also share identical feature values and tie at
the same confidence.

**Decision — a two-stage recommender:**
1. The baseline formula picks the top 200 candidates (era, language, genre, artist, popularity).
2. The RapidMiner Random Forest ranks those 200 by `confidence(yes)`.

This matches how the training data was collected and is a standard recommender design. Result:
100% language match in the top 10 for all 5 demo profiles, with ages at release between 14 and 26.

**This is the strongest evidence of real data-science work in the project** — a metric looked fine,
the output did not, and looking at the output changed the architecture.

## 11. Batch scoring for every listener

`src/06_make_profile_grid.py` builds `data/processed/grid_candidates.csv`: 27 stand-in profiles
(3 languages × birth years 1935–1975 in steps of 5) × 9,840 songs = **265,680 rows, 21.7 MB**.

Row 4 of the RapidMiner process scores it: Retrieve → Set Role (`song_id` = id, `user_id` = batch)
→ Select Attributes (the 7 features) → Replace Missing Values (popularity = 63.633) → Apply Model
← Multiply → Write CSV.

The Multiply operator sends **one** trained model to every Apply Model in the process, so cross
validation, the holdout test and the file the app reads all use the identical model.

Output `data/processed/predictions_grid.csv`: **265,680 rows, 27 profiles, 9,840 songs,
`confidence(yes)` from 0.024 to 0.854, no nulls, 5,938 distinct values.**

At runtime `ranking.py` maps a real listener to their grid cell — same language, closest birth
year — via `grid_cell()`, and reads that cell's scores. Scoring is a batch step run by hand in AI
Studio, not a live service, which is how AI Studio is used in practice.

## 12. The application

`app/streamlit_app.py`, five pages: **My Profile · Memory Journey · Music Cue · Capture a Memory ·
My Life in Music.** Top folder-tab navigation with a Back button backed by a page history in
`st.session_state.history`.

- `src/memorybridge/ranking.py` — the two-stage ranking, the grid lookup, and the label shown to
  the user: "RapidMiner Random Forest (nearest profile in the grid): G_Malayalam_1960", or
  "Baseline formula" when no scores are available. The app always tells the user which one ranked
  their songs.
- `src/memorybridge/db.py` — SQLite with three tables: `users`, `memories` (story, life period,
  people, place, year, photo path), `interactions` (recognized, memory_triggered, story_recorded,
  saved, ranked_by). The `interactions` table has the same shape as the simulated training data, so
  real reactions can replace the simulation without changing the model.
- **Speech to text** in Capture a Memory via `streamlit-mic-recorder`, with the language taken from
  the listener's profile (ml-IN / hi-IN / en-IN). The transcript is editable and nothing saves until
  "Keep this memory".
- **Design:** paper-and-ink theme in `app/style.py` (Anton / Special Elite / Permanent Marker, with
  Kalam for Devanagari; palette #f7f6f1 paper, #1f1b16 ink, #cc2018 red). 6 Open Doodles figures
  (CC0) and 14 Iconoodle icons (MIT), recoloured to two palette colours. All emoji removed.

**Tests:** `tests/test_recommender.py` and `tests/test_app_backend.py`, 9 tests passing. A headless
end-to-end run was verified: profile → College → a Malayalam song from 1976 ranked by the
RapidMiner model → memory saved → timeline shows it → database rows written.

### Application bugs found and fixed

- An all-empty popularity column made pandas treat scores as text — fixed with `pd.to_numeric` in
  `recommender.py`. Found by the tests, not by hand.
- AI Studio writes a byte-order mark, which turned the first column into `﻿user_id` and crashed
  the Music Cue page with `KeyError: ['user_id'] not in index`. `_load()` now reads `utf-8-sig`,
  accepts either separator, and names any missing column in the error.
- The speech transcript was written to `story_draft` and passed as `value=` to a text box that
  keeps its own state, so it never appeared. The box is now keyed `story_input` and the transcript
  is written straight into that key.
- A markdown `<div>` cannot wrap Streamlit buttons, which is why the first navigation bar showed an
  empty bordered strip with clipped labels. Restyled through `st.container(key="mb_nav")` →
  `.st-key-mb_nav`.
- RapidMiner's Write CSV defaults to the `;` separator and the `data/` folder rather than
  `data/processed/`; `src/05` handles both.
- Demo profiles D1–D5 were removed from the app and the database once the grid went live (0 saved
  memories; backup at `data/memorybridge.db.bak`). Everything now goes through the profile grid.

## 13. Honest limitations

1. The model is trained on **simulated** interactions. It proves the pipeline, not the idea.
2. The grid matches **language and birth year only**. Genre and favourite artists act through the
   baseline stage that selects the 200 candidates.
3. Scoring is a **batch step run by hand** in AI Studio, not a live service.
4. Malayalam songs have no popularity or audio fields, so ties are broken by file order.
5. The artist-per-song cap compares exact artist text, so "K J Yesudas" and "K J Yesudas, Chorus"
   count as different artists.
6. The `memories` table still has 0 real rows. No real person has used the app yet.
7. Turbo Prep samples are not exactly reproducible (no seed); the saved exports are the record.

## 14. Next steps

- Collect 30–60 real reactions from 3–5 real listeners and retrain, replacing the simulation. The
  `interactions` table already records them in the training format.
- Save real memories with photos and confirm they survive a restart.
- Use the Billboard data, which is downloaded but not yet part of the model.
- Turn batch scoring into a service call if the app goes past prototype.

## 15. Documents in this repository

| File | Contents |
|---|---|
| `README.md` | Pipeline diagram, who does what, how to run |
| `progress.md` | Dated log of every checkpoint, with measured numbers |
| `todo.md` | Checkpoint plan with owner tags |
| `docs/data_dictionary.md` | Every field of every file, marked MEASURED / DERIVED / SIMULATED |
| `docs/dataset_notes.md` | Sources, licences, row counts at each step |
| `docs/turboprep_checklist.md` | Exact TurboPrep steps and expected results |
| `docs/simulation_assumptions.md` | The simulator, its rules and its limits |
| `docs/rapidminer_steps.md` | Operator-by-operator build of the model process |
| `docs/related_work.md` | Existing products and what is new here |
| `results/model_comparison.md` | All model scores, confusion matrices, the two-stage decision |
| `docs/demo_video_script.md` | Video plan, timings, recording and upload steps |
| `docs/demo_video_narration.md` | Word-for-word narration for the video |
| `docs/project_summary.md` | This document |

## 16. Submission status — IEDC Summit 2026, due 18/09/2026

| Item | State |
|---|---|
| YouTube demo video, 5–15 min | Script and narration written; **not recorded** |
| PPT (problem statement + workflow design) | Ready — `presentation/MemoryBridge_IEDC_Summit_2026.pptx`, 15 slides, built on the INCLUCODE template. Name, college, email, phone and the two links still to fill in |
| Dataset used | Ready — `data/processed/` (63 MB) |
| `.rmp` process files | Ready — `MemoryBridge_model.rmp`, `turboprep_songs_master.rmp` |
| Additional files | Ready — `src/`, `app/`, `tests/`, `docs/`, `results/` |
| Zip `IEDC_<name>.zip` | Not built; exclude `data/raw/` (565 MB) |
| Google Drive link, "anyone with the link" | Not done |
| Form: name, college, mail, phone, title, LinkedIn, Drive link, YouTube link | Not submitted |
