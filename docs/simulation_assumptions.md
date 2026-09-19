# Simulation Assumptions: ⚠ SIMULATED DATA

**Everything in `users_synthetic.csv`, `interactions_train.csv` and `interactions_holdout.csv` is synthetic.** No real person was involved.

## Why we simulated
The prototype has no real users yet. A model can't be built or tested without examples, so we made up realistic-looking examples to prove the **pipeline** works: TurboPrep data → RapidMiner model → predictions → app.

## The big limitation (read this before looking at any score)
The "reactions" come from **rules we wrote** (below). A model trained on them can, at best, **rediscover those rules**. So:
- A high AUC or accuracy is **not evidence** that music triggers memories in real people, or that MemoryBridge works.
- It only shows that RapidMiner can learn a pattern that exists in the data, and that the pipeline runs end to end.
- Every model result from this data must be labelled **SIMULATED**.
- Real evidence needs real (consented) user feedback. The app will log real interactions in the same format.

## How the data was made (`src/04_simulate_interactions.py`, seed 2026)

### Listeners (300)
- **Language:** English 40%, Hindi 30%, Malayalam 30%. Actual counts: English 104, Malayalam 99, Hindi 97.
- **Birth year:** uniformly random between 1940 and 1975.
- **Favourite genres:** English listeners get 1–2 of Rock, Pop, Jazz, RnB, Country, Blues, Folk, Electronic. Hindi and Malayalam listeners get "Film", plus a Western genre 30% of the time.
- **Favourite artist:** 40% of listeners get one artist taken from songs in their language released when they were aged 10–30.
- **Hidden "taste":** each listener gets a random number (normal, sd 0.7) meaning "responds to music more or less than average". It is **not** in any output file.

### Which songs each listener reacts to (40 each)
- 20 from the listener's top 200 by the baseline formula (songs the app would plausibly show)
- 20 picked at random from all 9,840 songs, so there are also clearly unsuitable songs
- Duplicates are removed, so a few listeners have fewer than 40 songs.

### The hidden reaction rule
For each listener and song:

```
bump  = exp(-((age_at_release - 20) / 7)^2)          # peaks at age 20, fades by ~age 5 and ~35
z     = -2.9 + 2.8*bump + 1.4*language_match + 0.6*genre_match
        + 1.2*artist_match + 1.0*(popularity/100 - 0.5) + taste
P(memory_triggered = yes) = 1 / (1 + e^-z)
```
Missing popularity counts as 0.5.

- **Where these choices come from:** the bump around age 20 reflects the "reminiscence bump" described in autobiographical memory research, where music from adolescence and early adulthood is often more memorable. The size of each weight is **our assumption**, not a measured value.
- **Deliberate mismatch with the features:** the rule uses a *smooth curve* around age 20, but RapidMiner only receives `age_at_release`, `in_age_10_30` and `years_outside_10_30`. The model has to approximate the curve; it isn't handed it.
- **Other reaction fields:**
  - `recognized` happens more easily than a memory.
  - `memory_triggered` can only be yes if the song was recognized.
  - `liked`: 90% if there was a memory, otherwise 50% of recognized songs.
  - `story_recorded`: 60% of memories.
  - `saved`: 85% of stories.

## Result (measured)

| File | Rows | Listeners | memory_triggered = yes |
|---|---|---|---|
| interactions_train.csv | 9,589 | 240 (U001–U240) | 43.0% |
| interactions_holdout.csv | 2,400 | 60 (U241–U300) | 40.2% |
| demo_candidates.csv | 49,200 | 5 demo profiles × 9,840 songs | no label |

Checks on the training file:
- Yes-rate when age at release is 10–30: 58.5%. Outside that range: 13.9%.
- Yes-rate with a language match: 58.3%. Without: 13.4%.
- No listener sees the same song twice.

## Rules for using this data in RapidMiner (leakage)
- **Label:** `memory_triggered`
- **Allowed features** (known *before* the reaction): `age_at_release, in_age_10_30, years_outside_10_30, language_match, genre_match, artist_match, popularity`
- **Never use as features:**
  - `recognized, liked, story_recorded, saved`: these happen at the same time as or after the answer. `story_recorded = 1` is only possible when the answer is yes, so using it would be cheating.
  - `baseline_score`: kept only for comparing against the baseline afterwards.
  - `user_id`, `song_id`, `title`, `artist`: identifiers, not general patterns.
- **Split by listener** (`user_id` as the batch attribute) in cross-validation, so a listener's songs are never in both training and testing.
- **The holdout listeners (U241–U300) are never used for training or tuning**, only for the final comparison against the baseline.

## Text cleanup for AI Studio
In `title` and `artist`, `#` was replaced by `No.` and `"` by `'`, because the AI Studio CSV import treats `#` as a comment and `"` as a quote.
