# RapidMiner Steps: MemoryBridge Model (⚠ SIMULATED data)

You build this yourself in **AI Studio → Design view**.
- **Operator** = a box that does one step.
- **Port** = a small half-circle on a box's edge.
- **Connecting** = dragging a line from an output port (right side) to an input port (left side).

What we predict: **memory_triggered (yes/no)**, meaning "will this listener say this song reminds them of something meaningful".

---

## Part 1: Import the data (Turbo Prep not needed)

For each of `interactions_train.csv`, `interactions_holdout.csv` and `demo_candidates.csv` (in `data/processed`):
1. Repository panel → **Import Data** → **My Computer** → choose the file → **Next**
2. Encoding **UTF-8**, separator **Comma**, first row as names ✔ → **Next**
3. Column types screen:
   - `popularity` should be **real**
   - `memory_triggered` should be **binominal** (two values). If it says polynominal, change it to **binominal**.
   - (demo_candidates has no memory_triggered column)
4. Store in **Local Repository** with names `interactions_train`, `interactions_holdout`, `demo_candidates`

✅ Rows: 9,589 · 2,400 · 49,200

---

## Part 2: Build the cross-validation process (compare 3 models)

Start a new, empty process: **File → New Process → Blank**.

### Operator 1: Retrieve
- Drag **interactions_train** from the Repository panel onto the white canvas. A **Retrieve** box appears.

### Operator 2: Set Role
- Operators panel → search **Set Role** → drag it onto the canvas. Connect **Retrieve out → Set Role exa**.
- Parameters panel (right):
  - attribute name: **memory_triggered**, target role: **label**
  - click **set additional roles → Edit List**, and add:
    - `user_id` → **batch**
    - `song_id` → **id**
- **Why:** the *label* is what we predict. The *batch* tells cross-validation which rows belong to the same listener. The *id* is kept for identifying rows, but never used for learning.

### Operator 3: Select Attributes
- Search **Select Attributes** → drag → connect **Set Role exa → Select Attributes exa**.
- attribute filter type: **subset** → **Select Attributes…** → move these 7 to the right side:
  `age_at_release, in_age_10_30, years_outside_10_30, language_match, genre_match, artist_match, popularity`
- **Why:** this keeps out columns that would leak the answer (`recognized, liked, story_recorded, saved`) and unhelpful ones (`title, baseline_score`…). The label, batch and id roles are kept automatically.

### Operator 4: Replace Missing Values
- Search **Replace Missing Values** → drag → connect **Select Attributes exa → Replace Missing Values exa**.
- attribute filter type: **single** → attribute **popularity** → default: **average**
- **Why:** 48% of rows have no popularity, and Logistic Regression can't handle missing values. The average is a neutral guess.

### Operator 5: Cross Validation
- Search **Cross Validation** → drag → connect **Replace Missing Values exa → Cross Validation exa**.
- Parameters:
  - number of folds: **5**
  - ✔ **split on batch attribute**. **This is the data-leakage protection:** every listener's songs stay together, either all in training or all in testing.
- **Double-click** the Cross Validation box. You now see two halves: **Training** (left) and **Testing** (right).

**Inside Training (left half):**
- Search **Logistic Regression** → drag into the left half
- Connect the left edge **tra** → **Logistic Regression tra**
- Connect **Logistic Regression mod** → the right edge **mod** of the Training half

**Inside Testing (right half):**
- Search **Apply Model** → drag into the right half
- Connect the left edge **mod → Apply Model mod**, and **tes → Apply Model unl**
- Search **Performance (Binominal Classification)** → drag → connect **Apply Model lab → Performance lab**
- In Performance's parameters, tick: **accuracy, AUC, precision, recall, f_measure**
  - positive class: **yes**
- Connect **Performance per** → the right edge **per**

Click the **up arrow / "Process"** link at the top to go back out.

### Connect the results
- Connect **Cross Validation per** → the right edge of the canvas **res**

### Run
- Click the blue **▶ Run** button. Results appear in the **Results** view.
- 📸 Screenshot of the performance table
- Write the numbers into the table below.

### Swap the model and run again
1. Double-click **Cross Validation** → in the Training half, click **Logistic Regression** → press **Delete**
2. Drag in **Random Forest** → reconnect **tra → Random Forest tra** and **mod → mod** → **▶ Run** → record the results
3. Do the same with **Gradient Boosted Trees** → **▶ Run** → record the results

(If a model complains about the label type, check that `memory_triggered` is **binominal**.)

Save the process: **File → Save Process As… → MemoryBridge_model_comparison**

---

## Results table (fill in with real numbers only, all ⚠ SIMULATED)

| Model | AUC | Accuracy | Precision (yes) | Recall (yes) | F1 |
|---|---|---|---|---|---|
| Logistic Regression | | | | | |
| Random Forest | | | | | |
| Gradient Boosted Trees | | | | | |

**How to read them:**
- **AUC:** 0.5 = coin flip, 1.0 = perfect ranking. It shows how well "yes" songs are ranked above "no" songs. This is the most relevant score for a recommender.
- **Accuracy:** % of correct yes/no guesses. About 57% is possible just by always saying "no", so compare against that.
- **Precision:** of the songs predicted yes, the % that really were yes. High precision means few disappointing suggestions.
- **Recall:** of all real yes-songs, the % the model found.
- **F1:** a balance of precision and recall.
- The "±" after a number shows how much it varied across the 5 folds. Small is good.

**Pick the best model by AUC.** If the models are within about 0.01 of each other, prefer the simpler one (Logistic Regression), because it's easier to explain.

---

## Part 3: Final model → holdout + demo predictions (after Part 2)

*(Detailed click steps will be given at that checkpoint.)*

1. The **mod** output of Cross Validation is the chosen model retrained on **all** 240 training listeners.
2. Apply it to **interactions_holdout** (the 60 listeners never seen before) with the same Set Role → Select Attributes → Replace Missing Values steps, then **Write CSV** → `data/processed/predictions_holdout.csv`.
3. Apply it to **demo_candidates** in the same way → `data/processed/predictions_demo.csv`.
4. Save the process as `rapidminer/MemoryBridge_model.rmp`.
5. The Python side then compares **top-10 hit rate: model vs baseline formula vs random** on the holdout listeners, and connects the demo predictions to the app.

**Honest-reporting rule:** write the numbers down exactly as RapidMiner shows them, even if they're disappointing. Label every result ⚠ SIMULATED.

## Part 4 — Make the model live for every listener (full walkthrough)

### What this part does, and why it is needed

Open the app today, pick a listener, go to Music Cue, and the grey line at the bottom says
**"Chosen for you by: Baseline formula"**. That is the weighted formula in
`src/memorybridge/recommender.py` (era 40 / language 20 / genre 15 / artist 10 / popularity 15) —
not the Random Forest you trained.

The reason: AI Studio scores data in a batch and writes a file. It is not a service the running app
can call. So the app can only use scores that already exist on disk. The five demo profiles had
such a file (`predictions_demo.csv`); they have now been removed from the project, because a demo
that only works for five hard-coded people is not worth showing.

The fix is the **profile grid**: 27 stand-in listeners (3 languages x 9 birth years, 1935-1975 in
5-year steps) that cover the range of people this app is for. Score those 27 once, and every real
listener is served from the nearest cell — same language, closest birth year.
`data/processed/grid_candidates.csv` is exactly that: 265,680 rows (27 profiles x 9,840 songs),
21.7 MB, already written by `python src/06_make_profile_grid.py`.

**Your part:** steps 2 and 3, in Altair AI Studio.
**Already done:** the candidates file, and the lookup in `grid_cell()` (`src/memorybridge/ranking.py`).

### Step 1 — Look at the problem first (2 minutes, and it gives you a "before" screenshot)

    python -m streamlit run app/streamlit_app.py

Pick Thomas in the listener box, open **Memory Journey**, pick a life period, and read the grey line
at the bottom of **Music Cue**. It says `Baseline formula`. Screenshot it. Stop the app with Ctrl+C.

### Step 2 — Import the grid into the AI Studio repository

The process uses **Retrieve** operators, not Read CSV, so the file has to be in the repository first.

1. AI Studio -> **File > Import Data** (or *Add Data* in the Repository panel).
2. Pick `C:\Users\brigi\MemoryBridge_IEDC\data\processed\grid_candidates.csv`.
3. On the **Format your columns** page, three settings matter — all three have broken this project
   before:
   - **Encoding: UTF-8** (not SYSTEM; SYSTEM turned Malayalam into `???` during TurboPrep).
   - **Comment characters: OFF** (the default `#` silently drops rows).
   - **Value separator: `,`**
4. Column types: `user_id`, `user_language`, `song_id` = **polynominal**; `birth_year`, `year`,
   `age_at_release`, `in_age_10_30`, `years_outside_10_30`, `language_match`, `genre_match`,
   `artist_match` = **integer**; `popularity`, `baseline_score` = **real**. Leave blank `popularity`
   values missing — the process fills them in step 3.
5. Store it beside the others as **`processes/grid_candidates`**.
6. **Verify:** double-click the stored data. It must show **265,680 rows** and **13 columns**.
   Fewer rows means comment characters were left on — delete it and import again.

### Step 3 — Add a fourth row to the `MemoryBridge_model` process

Row 3 (demo scoring) is the template. Select its six operators, copy, paste, then change what the
table below lists.

| Operator | Setting |
|---|---|
| **Retrieve grid_candidates** | repository entry `processes/grid_candidates` |
| **Set Role (4)** | `song_id` -> **id**, `user_id` -> **batch** |
| **Select Attributes (4)** | a subset: `age_at_release`, `in_age_10_30`, `years_outside_10_30`, `language_match`, `genre_match`, `artist_match`, `popularity` |
| **Replace Missing Values (4)** | single attribute `popularity`, default **value**, replenishment value **63.633** (same number row 3 uses, so scores stay comparable) |
| **Apply Model (4)** | `unl` <- Replace Missing Values (4); `mod` <- **a new connection from `Multiply.output 3`** |
| **Write CSV (3)** | file `C:/Users/brigi/MemoryBridge_IEDC/data/processed/predictions_grid.csv`, separator `,`, write attribute names **true**, encoding **UTF-8** |

The Multiply wire is the step that is easy to miss. The trained Random Forest leaves
**Cross Validation.model**, enters **Multiply**, and Multiply already feeds `Apply Model (2)` and
`Apply Model (3)`. Drag one more wire from Multiply's next free output port into `Apply Model (4)`'s
`mod` port.

Run the process (blue play button). 265,680 rows take longer than the demo's 49,200 — expect a few
minutes. Save the process afterwards.

**Verify:** open `data/processed/predictions_grid.csv`. It must have the columns `user_id`,
`song_id`, `confidence(yes)` and roughly 265,680 rows, with ids like `G_Malayalam_1960`,
`G_Hindi_1950`, `G_English_1935`.

### Step 4 — See it working in the app

    python -m streamlit run app/streamlit_app.py

Same walk as step 1. The grey line under the songs must now read:

    Chosen for you by: RapidMiner Random Forest (nearest profile in the grid): G_Malayalam_1960

That is your "after" screenshot. The songs should also reorder: the baseline still picks the 200
candidates, the Random Forest decides which 10 you see first.

Still says `Baseline formula`? Check in this order:
1. Does `data/processed/predictions_grid.csv` exist, with that exact name and folder?
2. Does it have a column spelled exactly `confidence(yes)`, brackets included?
3. Restart the app — the file is read once at startup (`@st.cache_data`).

### What to say about it in the demo and the report

- The model is trained on **SIMULATED** interactions (`docs/simulation_assumptions.md`). It shows
  the pipeline works end to end; it does not show the idea works on real people.
- The grid matches **language and birth year only**. Genre and favourite artists still act through
  the baseline stage that picks the 200 candidates the model ranks.
- Scoring is a **batch step run by hand in AI Studio**, not a live service — which is how AI Studio
  is used in practice too.
