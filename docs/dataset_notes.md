# Dataset Notes

All numbers below come from real runs on 2026-09-17.

## Sources and licenses

| Dataset | Source | License / terms | Used for |
|---|---|---|---|
| Million Song Dataset: summary file, unique_tracks, tracks_per_year | millionsongdataset.com (Bertin-Mahieux et al., 2011) | Free for research | Western songs, years, audio fields |
| tagtraum genre labels CD2 | tagtraum.com (Schreiber, 2015) | Free for research, credit required | MSD genres |
| Bollywood Songs & Albums Metadata 1931–2025 | github.com/MrAsacker/bollywood-songs-metadata | MIT (repo). Scraped from MySwar, so credit both | Hindi film songs |
| Malayalam song dataset | github.com/Abhinav-ark/Mal_lyrics_analysis (`dataset.csv`) | MIT (repo). Appears to be scraped from a Malayalam song website (likely malayalasangeetham.info) | Malayalam film songs |
| Billboard Hot 100 | utdata/rwd-billboard-data | Public GitHub | Not used yet (Priority 3) |

## MSD summary file (`data/raw/msd_summary_file.h5`, 316,104,481 bytes)
- Three tables, each with 1,000,000 rows: `metadata/songs`, `analysis/songs`, `musicbrainz/songs`.
- Fields confirmed from the file: title, artist_name, artist_mbid, artist_location, artist_familiarity, artist_hotttnesss, song_hotttnesss, release, tempo, loudness, key, mode, duration, time_signature, energy, danceability, year.
- **`energy` is 0 for all 1,000,000 songs** (measured), so it is unusable.

## MSD subset (`src/01_make_msd_subset.py` → `data/interim/msd_subset.csv`)

| Step | Rows |
|---|---|
| Summary file | 1,000,000 |
| With a year **and** a tagtraum genre | 223,140 |
| Sample: 1950–2010, 928 per decade, seed 42 | **6,496** |

Quality of the subset:
- 0 duplicate title+artist pairs.
- 3,608 artist names and 3,525 unique MusicBrainz artist IDs. The ID is missing for 0.7%.
- `song_hotttnesss` is missing (NaN) for 38.1% and equal to 0 for 2.4%.
- `tempo` = 0 for 0.1%. `loudness` is never missing.
- `artist_location` is blank for 28.2%, and is free text (not a country).

Genres: Rock 2,626 · Jazz 749 · Pop 661 · Electronic 448 · RnB 437 · Blues 324 · Country 279 · Folk 198 · Metal 184 · Rap 138 · Reggae 116 · Latin 111 · Punk 110 · World 73 · New Age 42.

Caveat: the "2010" group contains only songs from the year 2010, because the MSD ends in 2011.

## Hindi (`src/02_prepare_indian_inputs.py` → `data/interim/bollywood_*_raw.csv`)
- 57,005 songs (all song_uuids unique) and 12,673 albums. **One album_uuid is duplicated** (12,672 unique).
- Every song links to an album.
- Album categories: "Hindi, Film" 8,916 · "Hindi, Non Film" 3,644 · English and instrumental about 113. 99.1% of albums contain "Hindi".
- Hindi songs from 1950–2010: 39,271. By decade: 1950s 7,685 · 60s 5,253 · 70s 5,720 · 80s 6,669 · 90s 6,292 · 2000s 6,887 · 2010 765.
- `song_rating`: **68.2% are 0, meaning unrated**. The median is 0 and the maximum is 5.
- Singers are missing for 2.3%. `youtube_url` is present for all songs.
- 333 rows repeat a song_title + song_singers pair.

## Malayalam (`src/02_prepare_indian_inputs.py` → `data/interim/malayalam_songs_raw.csv`)
- 26,232 songs from 1938 to 2022. Year is missing for 80.
- Headers were renamed from Malayalam script to English.
- **Full lyrics were removed.** Only their first line is kept, as `title_first_line` (derived title).
- 2,499 songs have a blank title. 6,297 rows repeat a film + title pair already seen.
- Missing: actors 67.6%, raga 86%, category 91%, singers 4.8%.
- Names are in Malayalam script.

## MusicBrainz enrichment (`src/03_musicbrainz_enrich.py` → `data/interim/mb_artists.csv`), run 2026-09-17
- 3,525 unique artist_mbids, one request each at about 1.1 s. There were many HTTP 503 "busy" replies, which the script retried automatically. Wall-clock time was 02:49–14:57 (about 12 h, much longer than the 65 min estimate; the cause of the extra time was not investigated). 12 artists failed on the first run and succeeded on a second run.
- Result: 3,502 found, 23 not found (404).
- Coverage among the found artists: country 3,445 (98.4%), release language 3,495 (99.8%), MusicBrainz genre 2,983 (85.2%).
- Most common artist languages: English 3,144 · Spanish 104 · French 49 · German 37 · Italian 33 · Portuguese 31.
- Most common countries: US 1,765 · GB 721 · DE 143 · CA 113 · SE 80 · FR 73 · JM 55.
- At song level (6,496 MSD songs): 97.3% have a country and 98.2% have a language. English 5,900 · Spanish 140 · French 88 · German 54.
- Caveat: language is the **most common language across up to 25 of the artist's releases**. It describes the artist, not each individual song.

## Prototype total (planned, after TurboPrep)
About 6,500 MSD + 2,000 Hindi + 1,500 Malayalam ≈ **10,000 songs**. This is prototype scale; the full 1M-song MSD is not processed.
