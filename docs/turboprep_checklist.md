# TurboPrep Checklist: MemoryBridge

You do these steps yourself in **AI Studio 2026.1.1 → Turbo Prep view**.

In AI Studio, a **table** is called an **ExampleSet**, and a **column** is called an **attribute**.

Menu names can be slightly different in your version. If you can't find one, look for the nearest equivalent.

**Order of work:**
- **Part A:** Hindi (ready now)
- **Part B:** Malayalam (ready now)
- **Part C:** MSD (starts once `msd_subset.csv` exists)
- **Part D:** Append all three and export the master table

**After every part:**
- Click **Commit Transformation** to save your work.
- Take the screenshots marked 📸, and save them in `results/screenshots/`.
- Write the row counts in the table at the bottom.

---

## Part 0: Setup (once)

1. Open AI Studio. Top right, open the **Turbo Prep** view.
2. In the Repository panel, create a folder: `Local Repository/MemoryBridge/data`.
   - **Why:** everything you save stays in one place. Later, the RapidMiner process reads from this folder.

### How to load a CSV (used in every part)
1. In Turbo Prep, click **Load Data**, then **Import Data**, then **My Computer**, and pick the file.
2. On the format screen, set:
   - **Encoding:** `UTF-8` (important, otherwise Malayalam script turns into ??? marks)
   - **Column separator:** comma
   - **First row as names:** on
3. On the column types screen, check the numbers (year, tempo and so on) are **integer** or **real**, not polynominal.
   - Polynominal means text categories.
4. Store the data in `MemoryBridge/data`, using the name given in each step.

---

## Part A: Hindi songs (Bollywood metadata)

**Files:** `data/interim/bollywood_songs_raw.csv` (57,005 rows) and `data/interim/bollywood_albums_raw.csv` (12,673 rows)

**Goal:** one clean table of about 2,000 Hindi film songs from 1950 to 2010.

### A1. Load both files
- Store them as `hindi_songs_raw` and `hindi_albums_raw`.
- **Expect:** 57,005 rows × 10 columns, and 12,673 rows × 8 columns.
- 📸 The data view of each table.

### A2. Remove the duplicate album ID (albums table)
- Select `hindi_albums_raw`. Go to **Cleanse → Remove Duplicates** and compare only `album_uuid`.
- **Why:** one album ID appears twice. If you join with a duplicate key, every song on that album gets copied twice.
- **Expect:** 12,673 → 12,672 rows.

### A3. Join songs to albums
- Go to **Merge → Join**. Left = `hindi_songs_raw`, right = albums (from A2). Key = `album_uuid` on both sides. Type = **Left join**.
- **What a join is:** every song row has an `album_uuid`. The join looks up that ID in the albums table and copies the album's information onto the song row. This gives each song its year, film name, music director and label.
- **Why a left join:** it keeps every song, even if its album can't be found. We checked that all 57,005 songs have an album.
- **Expect:** 57,005 rows, now with album columns added.
- 📸 The join setup screen and the result.

### A4. Filter to 1950–2010 and Hindi only
- **Transform → Filter:** `album_year` ≥ 1950 **and** `album_year` ≤ 2010.
- **Transform → Filter:** `album_category` **contains** `Hindi`.
- **Why:** our target users grew up roughly between 1950 and 2010. A few albums are English or instrumental.
- **Expect:** about **39,271** rows.

### A5. Remove duplicate songs
- **Cleanse → Remove Duplicates** on `song_title` + `song_singers` + `album_year`.
- **Why:** the same song can appear on several albums (re-releases). Without this step, the recommender could suggest the same song twice.
- 📸 The row count before and after.

### A6. Fix the rating (this is an important lesson)
- **Transform → Replace:** in `song_rating`, replace `0` with **missing**.
- **Why:** 68% of songs have a rating of 0. That means **nobody rated them**, not that they are bad. If we left 0, the model would treat unrated songs as disliked, which is wrong information.
- **Generate:** new column `popularity` = `song_rating * 20`. This turns the 0–5 scale into 0–100, matching the MSD.
- **Note:** this is a user rating from the MySwar website, not chart popularity. Say this in the presentation.

### A7. Create the master columns
Use **Generate** to create these columns:

| New column | Expression | Why |
|---|---|---|
| `language` | `"Hindi"` | Every row is a Hindi album |
| `country` | `"India"` | |
| `genre` | `"Film"` | The data has no Rock/Pop-style genre, only film or non-film |
| `source` | `"Bollywood"` | So we always know which dataset a row came from |
| `decade` | `floor(album_year/10)*10` | Needed for the life-period analysis |

Then rename columns: click the column header and choose **Rename**.
- `song_uuid` → `song_id`
- `song_title` → `title`
- `song_singers` → `artist`
- `album_year` → `year`
- `youtube_url` → `play_url`

### A8. Sample about 2,000 songs
- **Transform → Sample**, absolute number = **2,000**. Set a fixed random seed of 42 if you get the option.
- **Why:** it keeps the prototype small. The Hindi decades are already fairly even (1950s 7,685 · 60s 5,253 · 70s 5,720 · 80s 6,669 · 90s 6,292 · 2000s 6,887 · 2010 765), so a random sample stays balanced.
- **Check:** **Pivot** with group by `decade`, count `song_id`. Every decade except 2010 should have roughly 250–400 songs.
- 📸 The pivot table (good for the slides).

### A9. Keep only the master columns and save
- **Transform → Remove**: keep only `song_id, title, artist, year, decade, genre, language, country, popularity, play_url, source`.
- Leave `tempo, loudness, key` **out** here. The Hindi data doesn't have them, and the Append step will fill them in as missing.
- **Commit**, then store the result as `hindi_clean`.
- 📸 The **History** panel (shows all your steps).

---

## Part B: Malayalam songs

**File:** `data/interim/malayalam_songs_raw.csv` (26,232 rows). The names are in Malayalam script, which is normal.

**Goal:** about 1,500 clean Malayalam film songs from 1950 to 2010.

### B1. Load the file
- Remember encoding **UTF-8**. Store it as `malayalam_raw`.
- **Expect:** 26,232 rows × 10 columns. You should see Malayalam letters, not ??? marks.
- 📸 The data view.

### B2. Look at the data quality first
- Click the column headers in Turbo Prep's data view and read the quality numbers.
- **Expect:**
  - `raga` about 86% missing
  - `category` about 91% missing
  - `actors` about 68% missing
  - `singers` about 5% missing
- **Lesson:** columns that are mostly empty can't help, so we drop them.
- 📸 The quality overview.

### B3. Remove unusable rows and columns
- **Transform → Remove** the columns `raga`, `category` and `actors`.
- **Transform → Filter:** `title_first_line` is **not missing**. This removes the 2,499 songs with no title.
- **Transform → Filter:** `year` is not missing, and 1950 ≤ `year` ≤ 2010.

### B4. Remove duplicates
- **Cleanse → Remove Duplicates** on `film` + `title_first_line`.
- **Why:** the source site lists some songs more than once (6,297 repeated pairs in the full file).
- 📸 The row count before and after.

### B5. Create the master columns
- **Generate:**
  - `language` = `"Malayalam"`
  - `country` = `"India"`
  - `genre` = `"Film"`
  - `source` = `"Malayalam"`
  - `decade` = `floor(year/10)*10`
- **Rename:**
  - `ml_song_id` → `song_id`
  - `title_first_line` → `title`
  - `singers` → `artist`
- There is **no popularity** column. Don't invent one; it stays missing.
- **Note:** the title is **derived** from the first line of the lyrics, which is how Malayalam songs are usually named.

### B6. Sample about 1,500 songs and check the decades
- **Transform → Sample** 1,500 with seed 42.
- Check with **Pivot** by `decade`.
- The source has more songs from the 1980s and 2000s than the 1950s (728), so the 1950s will look smaller. That's fine, just mention it.
- 📸 The pivot table.

### B7. Keep the master columns and save
- Keep `song_id, title, artist, year, decade, genre, language, country, source`, plus `film` and `music_director` if you like.
- **Commit**, then store as `malayalam_clean`.
- 📸 The History panel.

---

## Part C: MSD (Western songs), available once `data/interim/msd_subset.csv` has been built

**File:** `msd_subset.csv` (about 6,500 rows, balanced across decades)

### C1. Load
- Store as `msd_raw`. Check that `tempo`, `loudness`, `year` and `song_hotttnesss` are numeric.

### C2. Clean the text
- **Transform → Replace / Trim** on `title` and `artist_name`: remove extra spaces.
- **Why:** "The Beatles " and "The Beatles" would count as two different artists.

### C3. Remove duplicate songs
- **Cleanse → Remove Duplicates** on `title` + `artist_name`.
- **Why:** the MSD has 74,065 repeated artist+title pairs across its 1M tracks, and some may be in our sample.

### C4. Handle "unknown" values
- `song_hotttnesss`: replace `0` with missing. In the MSD, 0 usually means not measured.
- Then **Generate** `popularity` = `song_hotttnesss * 100`.
- `tempo` = 0 means the tempo wasn't detected, so replace it with missing.
- **Lesson:** missing is honest. A fake 0 teaches the model something false.

### C5. Standardize and create columns
- **Generate:**
  - `language` = `"English"`
  - `country` = missing for now (MusicBrainz enrichment may fill it later)
  - `source` = `"MSD"`
  - `play_url` = `"https://www.youtube.com/results?search_query=" + artist_name + " " + title`
- **Rename:** `track_id` → `song_id`, `artist_name` → `artist`.
- ⚠ **Honesty note:** we label MSD songs "English" as a prototype assumption. Most MSD songs are English, but not all. MusicBrainz can check this later. Write it in the limitations.

### C6. Keep the master columns and save
- Keep `song_id, title, artist, year, decade, genre, language, country, tempo, loudness, key, popularity, play_url, source`.
- **Commit**, then store as `msd_clean`.
- 📸 The History panel.

---

## Part D: Build the master table

### D1. Append all three
- **Merge → Append:** `msd_clean` + `hindi_clean` + `malayalam_clean`.
- **What append means:** stacking tables on top of each other. It works because we gave all three the **same column names**.
- Columns a dataset doesn't have, such as tempo for Hindi songs, become **missing**.
- **Expect:** about 6,500 + 2,000 + 1,500 = **about 10,000 rows**.
- 📸 The append result.

### D2. Final checks
- **Pivot:** `source` × `decade`, count rows. This shows the mix of songs across eras. 📸 Great for the slides.
- **Pivot:** `language`, count rows.
- Check that no `year` is outside 1950–2010, and that `title` has no missing values.

### D3. Export
- **Export → CSV** to `C:\Users\brigi\MemoryBridge_IEDC\data\processed\songs_master.csv`, with UTF-8 encoding.
- Also store it in the repository as `songs_master`.
- Click **Process** (top of Turbo Prep) and save the generated process as `rapidminer/turboprep_songs_master.rmp`.
  - **Why:** this proves the whole preparation was done in TurboPrep and can be repeated.
- 📸 The generated process view.
- When it's done, check the exported file's row count and columns.

---

## Row counts to fill in (for slides and progress.md)

| Step | Hindi | Malayalam | MSD |
|---|---|---|---|
| Loaded | 57,005 | 26,232 | |
| After join / quality cleanup | | | |
| After year filter | | | |
| After removing duplicates | | | |
| After sampling | | | |
| **Final in master** | | | |

---

## Troubleshooting
- **Malayalam shows ??? marks:** re-import and set the encoding to UTF-8.
- **year is polynominal (text):** in the import wizard, change its type to integer, or use **Change Type** in Transform.
- **Append fails or columns are duplicated:** a column name is spelled differently (for example `Artist` versus `artist`). Rename it so they match exactly.
- **Can't find a menu item:** check the AI Studio docs for your version.
