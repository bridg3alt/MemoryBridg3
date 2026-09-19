# Data Dictionary

Status labels:
- **MEASURED** means checked on the real file (2026-09-17).
- **NEEDS VERIFICATION** means not yet checked.
- **DERIVED** means calculated from other fields.
- **SIMULATED** means synthetic data that is not real.

## 1. Raw files in `data/raw/`

### unique_tracks.txt
The separator is `<SEP>`, and there is no header. **1,000,000 rows (MEASURED).**

| Field | Type | Example | Notes |
|---|---|---|---|
| track_id | text | TRMMMYQ128F932D901 | Unique per row (1,000,000 distinct). This is the join key across MSD files. |
| song_id | text | SOQMMHC12AB0180CB8 | 999,056 distinct, so a few songs have more than one track. |
| artist | text | Faster Pussy cat | 72,665 distinct names, with no cleanup yet. |
| title | text | Silent Night | 74,065 rows repeat an artist+title pair already seen. |

### tracks_per_year.txt
The separator is `<SEP>`, and there is no header. **515,576 rows (MEASURED).** Only about half of the MSD has a known year.

| Field | Type | Example | Notes |
|---|---|---|---|
| year | integer | 1989 | Ranges from 1922 to 2011. |
| track_id | text | TRWTNGR128F426A2BE | Join key. |
| artist | text | Julio Iglesias | |
| title | text | Italia | |

Tracks per decade (MEASURED): 1920s 225 · 1930s 252 · 1940s 356 · 1950s 3,104 · 1960s 11,741 · 1970s 24,748 · 1980s 41,827 · 1990s 124,808 · 2000s 299,117 · 2010–11 9,398.

### msd_tagtraum_cd2.cls
The separator is a tab, and lines starting with `#` are comments. **280,831 rows (MEASURED).**

| Field | Type | Example | Notes |
|---|---|---|---|
| track_id | text | TRAAABD128F429CF47 | Join key. |
| genre | text | Rock | The majority genre, one of 15 (see counts below). |
| genre2 | text | RnB | Optional minority genre, often empty. |

Genre counts (MEASURED): Rock 113,150 · Electronic 30,922 · Pop 27,756 · Jazz 17,541 · Rap 13,272 · RnB 13,208 · Metal 11,222 · Country 10,695 · Reggae 8,910 · Blues 8,125 · Latin 6,444 · Folk 6,377 · Punk 5,652 · World 4,770 · New Age 2,787.

Tracks with **both year and genre**: 223,140. Of those, 222,766 are from 1950–2010, broken down as 1950s 1,210 · 60s 4,984 · 70s 11,390 · 80s 19,532 · 90s 53,420 · 2000s 128,641 · 2010 3,589 (MEASURED).

### hot-100-current.csv
Comma-separated with a header. Billboard Hot 100 weekly charts from 1958-08-04 to 2026-09-19, with 32,752 unique title+performer pairs (MEASURED). **Priority 3, not used yet.**

| Field | Type | Example |
|---|---|---|
| chart_week | date | 2022-01-01 |
| current_week | integer (chart position) | 1 |
| title | text | All I Want For Christmas Is You |
| performer | text | Mariah Carey |
| last_week | integer or NA | 1 |
| peak_pos | integer | 1 |
| wks_on_chart | integer | 50 |

### msd_summary_file.h5 (NOT YET DOWNLOADED)
Size 316 MB (server-confirmed). Expected fields: tempo, loudness, key, mode, duration, time_signature, artist_familiarity, song_hotttnesss, artist_mbid, artist_location, year. **NEEDS VERIFICATION.** Missing values are likely (hotttnesss is often NaN or 0).

## 2. Planned master table: `data/processed/songs_master.csv` (made in TurboPrep)

| Column | Source | Status |
|---|---|---|
| song_id | MSD | available |
| title | MSD | available, needs text cleanup |
| artist | MSD | available, needs text cleanup |
| year | tracks_per_year | available (the subset only keeps songs that have a year) |
| genre | tagtraum | available (the subset only keeps songs that have a genre) |
| tempo | summary file | NEEDS VERIFICATION |
| loudness | summary file | NEEDS VERIFICATION |
| key | summary file | NEEDS VERIFICATION |
| popularity | summary file `song_hotttnesss` × 100 | NEEDS VERIFICATION, will have gaps |
| energy | **DERIVED** from tempo and loudness | The MSD `energy` field is always 0 and can't be used. Our value is a rough stand-in, not a measured energy. |
| language | MusicBrainz (release language) | **Not in MSD.** Coverage NEEDS VERIFICATION. Mostly English; Indian languages will be rare. |
| country | MusicBrainz (artist country) | **Not in MSD.** Coverage NEEDS VERIFICATION. |

## 3. Planned user-specific fields (calculated later, not in the song table)

| Field | Definition |
|---|---|
| age_at_release | song year − user birth year |
| life_period | Childhood 10–15 · College 16–22 · Early adulthood 23–30 · Family/Career 31–45. These are product categories, not medical facts. |

## 4. Planned interaction fields (**SIMULATED** at first)

user_id, song_id, recognized, liked, memory_triggered (model target), story_recorded, saved, era_match, language_match, genre_match, artist_match, popularity.

The first version is synthetic, made from documented rules. Model scores on it are **not** real-world evidence. Real app usage will add real rows later.
