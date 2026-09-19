# Demo video script — IEDC Summit 2026 Data Science Contest

Required: 5–15 minutes, uploaded to YouTube, public or unlisted.
Target length: **9–10 minutes** (safe middle of the window).

Record in this order. Each block says what is on screen and what to say.

---

## Block 0 — Title card (0:00–0:30)

On screen: slide 1 of the PPT (project title, your name, college).

> "Hi, I'm <name> from <college>. This is MemoryBridge — a music-based reminiscence
> prototype. I'll walk through the problem, the data, the RapidMiner workflow, the model
> comparison, and a live demo of the app."

---

## Block 1 — Problem statement (0:30–1:30)

On screen: PPT problem slides.

Say:
- People remember their lives through the music of their youth. A song from when someone
  was 15–25 is a strong cue for autobiographical memory.
- MemoryBridge asks for birth year, language and favourite genres, suggests songs that
  plausibly belong to periods of that person's life, and lets them write down what the song
  reminds them of, then revisit it by life period.
- Say the disclaimer out loud: **not a medical product, does not diagnose or treat anything,
  never invents a memory — the user's own recorded story is the only source of truth.**

---

## Block 2 — Data (1:30–3:00)

On screen: `docs/data_dictionary.md` / `docs/dataset_notes.md`, then `data/processed/songs_master.csv`.

Say the real numbers:
- Sources: Million Song Dataset (1,000,000 tracks) + tagtraum genre labels + Billboard Hot 100
  + a Bollywood/Hindi metadata set (57,005 songs) + a Malayalam set (26,232 songs).
- MusicBrainz API enrichment for artist country and language: 3,502 of 3,525 artists found,
  language coverage 99.8%.
- Final master table: **`songs_master.csv`, 9,840 rows × 14 columns**, years 1950–2010,
  MSD 6,491 · Bollywood 2,000 · Malayalam 1,349, 0 duplicate song_ids.
- Name two real problems you hit: genre+year tracks are heavily skewed to the 2000s, so the
  subset is spread evenly across decades (928 per decade); and the Indian datasets have no
  audio fields, so tempo/loudness/key are missing for 3,349 rows.

---

## Block 3 — TurboPrep (3:00–4:15)

On screen: AI Studio, open `rapidminer/turboprep_songs_master.rmp`.

Walk through Parts A–D:
- A: Hindi clean → 2,000 rows.
- B: Malayalam clean → 1,349 rows (1,500 sampled, 151 placeholder/"." titles removed).
- C: MSD + MusicBrainz join → 6,491 rows.
- D: append the three, standardize 15 ISO language codes → the language field.

Worth mentioning because it shows real data-cleaning judgement:
- AI Studio's CSV import treats `#` as a comment character — that broke 5 rows, found and fixed.
- The export used the system encoding and turned Malayalam into `???` — fixed by setting
  Preferences → Encoding to UTF-8.

---

## Block 4 — Features and the honest caveat (4:15–5:15)

On screen: `docs/simulation_assumptions.md`.

Say clearly and early:
- There is no real listening-reaction data for this prototype, so interactions are
  **SIMULATED** by `src/04_simulate_interactions.py` (seed 2026): 300 synthetic listeners,
  train 9,589 rows / 240 listeners / 43.0% yes, holdout 2,400 rows / 60 listeners.
- Label: `memory_triggered`. 7 features: `age_at_release`, `in_age_10_30`,
  `years_outside_10_30`, `language_match`, `genre_match`, `artist_match`, `popularity`.
- State the limit: this shows the pipeline works end to end, it does not show the idea works
  on real people. Judges reward this, they do not punish it.

---

## Block 5 — The RapidMiner process (5:15–7:15)

On screen: AI Studio, open `rapidminer/MemoryBridge_model.rmp`. Zoom so operators are readable.

Row by row:
1. **Cross Validation with split on batch attribute**, batch = `user_id`. Explain why:
   each listener's rows are tested on a model that never saw that listener
   (leave-one-listener-out). A random split would leak the same listener into train and test.
2. Three models compared. Read the table:

| Model | AUC | Accuracy | Recall (yes) |
|---|---|---|---|
| Logistic Regression | 0.790 ± 0.081 | 71.87% | 64.73% |
| Random Forest | 0.831 ± 0.073 | 74.08% | 80.52% |
| Gradient Boosted Trees | 0.835 ± 0.073 | 73.77% | 58.28% |

   Baseline for comparison: always predicting "no" gives 57.0% accuracy.
3. **Random Forest chosen**: AUC tied with GBT inside the ±0.073 spread, much higher recall
   (80.5% vs 58.3%), which is what a reminiscence app wants — missing a song that would have
   worked costs more than showing one extra song that does not. Simpler to explain, too.
4. Holdout, 60 unseen listeners: **AUC 0.804**. Top-10 hit rate: **Random Forest 74.2%,
   baseline formula 63.2%, random order 40.2%.**
5. Row 4: scoring the profile grid — `grid_candidates.csv`, 265,680 rows = 27 profiles ×
   9,840 songs → `predictions_grid.csv`. Point out the Multiply wire feeding the trained model
   to all the Apply Model operators.

---

## Block 6 — The finding that changed the design (7:15–8:00)

On screen: `results/model_comparison.md`, demo-profile section.

- When the Random Forest ranked all 9,840 songs on its own, 1–2 of the top 10 for some
  profiles were in the wrong language (a Malayalam profile got an English song at confidence
  0.705 above in-period Malayalam songs at 0.685).
- Cause: in training, half of each listener's songs came from the baseline top 200, so the
  model rarely saw wrong-language low-popularity songs — its guesses there are unreliable.
- Fix: a **two-stage recommender**. Stage 1, the transparent baseline formula
  (era 40 / language 20 / genre 15 / artist 10 / popularity 15) picks 200 candidates.
  Stage 2, the Random Forest ranks those 200. Result: 100% language match in the top 10 for
  all 5 test profiles.

This block is the strongest part of the video — it shows evaluation changing a decision.

---

## Block 7 — Live app demo (8:00–9:15)

    python -m streamlit run app/streamlit_app.py

Do this, without narrating every click:
1. Create a profile (birth year, language, genres, a favourite artist).
2. Show the song suggestions. **Read the grey line out loud:**
   `Chosen for you by: RapidMiner Random Forest (nearest profile in the grid): G_Malayalam_1960`
   — that line is the proof the model, not the formula, is ranking.
3. Capture a memory on one song (type it, or use the mic button).
4. Open the timeline, show the memory filed under its life period.

Have the profile created **before** you hit record if the app is slow to start.

---

## Block 8 — Limits and next steps (9:15–10:00)

- Trained on SIMULATED interactions; the next step is 30–60 real reactions from 3–5 real
  listeners to replace them.
- The grid matches language and birth year only; genre and artist act through the baseline stage.
- Scoring is a batch step run by hand in AI Studio, not a live service — which is how AI Studio
  is used in practice.
- Close: name, thanks, one sentence on what you would build next.

---

## Recording

- **Windows Game Bar**: `Win + G` → Capture → record. Records one window; it will not record
  File Explorer or the desktop. Free, already installed.
- **OBS Studio** if you want the whole screen plus a webcam corner.
- Record audio with the laptop mic in a quiet room; test 20 seconds and play it back first.
- Turn off notifications: `Win + A` → Do not disturb.
- Record in blocks and stitch them, rather than chasing one perfect take.

Join clips and check duration with ffmpeg:

    ffmpeg -i part1.mp4 -i part2.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1" out.mp4
    ffprobe -i out.mp4 -show_entries format=duration -v quiet -of csv=p=0

Under 5:00 or over 15:00 risks disqualification. Check before uploading.

## Uploading

1. studio.youtube.com → Create → Upload videos.
2. Title: `MemoryBridge — Music as a Memory Cue | IEDC Summit 2026 Data Science Contest`
3. Description: name, college, one-paragraph summary, tool list (Altair AI Studio / RapidMiner,
   TurboPrep, Python, Streamlit, SQLite), the datasets and their licences, and the
   "not a medical product / trained on simulated data" note.
4. "Not made for kids".
5. Visibility: **Unlisted** or **Public**. Not Private — Private breaks the judges' link.
6. Copy the link into the form. Open that link in a private browser window to confirm it plays
   for someone who is not logged in as you.
