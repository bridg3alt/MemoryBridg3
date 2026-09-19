# Related Work: what already exists (checked 2026-09-18)

Two separate groups of products exist. **MemoryBridge sits between them.**

## Group A: personalized music for people with memory loss

| Product | What it does | How MemoryBridge differs |
|---|---|---|
| **Music & Memory** (US non-profit, app released 2026) | Caregivers build personal playlists for someone in their care; the classic programme of this field | The caregiver must already **know** the person's songs. We **suggest** songs from birth year, language and era, then **capture the memory** the song brings back |
| **Music for My Mind** (UK charity, free Playlist Maker) | Builds playlists for people with dementia and researches their effect | Same starting point, but they stop at the playlist. We add the story, photo and retrieval loop |
| **Spotify / YouTube "songs of your youth" playlists** | Generic decade playlists | Ours is per person (birth year → life period), covers Hindi and Malayalam, and needs no streaming account |

**Research basis (worth citing on a slide):** Cuddy, Sikka et al., *"A Focus on the Reminiscence Bump to Personalize Music Playlists for Dementia"*, Journal of Multidisciplinary Healthcare, 2021 — recollection of popular music peaks around the teenage years. This is the published idea behind our age-10–30 window and the age-20 peak in the simulation. Note: that literature is about dementia care; **MemoryBridge makes no medical claim**.

## Group B: life-story and memory-keeping apps

| Product | What it does | How MemoryBridge differs |
|---|---|---|
| **StoryWorth** | Emails a question a week, then prints a keepsake book (1M+ books) | Their cue is a **written question**; ours is a **song from the person's own era** |
| **LifeBio Memory** | Life-story app with guided prompts, used in care settings | Same: text prompts, no music cue, no ML ranking |
| **My House of Memories** (National Museums Liverpool) | Browse museum objects with sound and images, save to a memory box or timeline | Closest in spirit. Cues are **museum objects** picked by curators; ours are **9,840 songs ranked per person by a model** |
| **Memoir, MemLife, Memoriz** | Journal and family-memory apps | Storage only, no cue and no personalization |

## What is actually new in MemoryBridge
1. **It closes the loop:** cue → memory → storage → retrieval by life period. Group A stops at the cue; Group B starts at the story.
2. **A learned ranking, not a fixed rule.** The RapidMiner Random Forest ranks candidate songs, and every "this reminds me of something" answer becomes training data for the next version. (Currently trained on ⚠ SIMULATED data.)
3. **Indian-language coverage.** 2,000 Hindi and 1,349 Malayalam film songs beside 6,491 Western songs, with explicit language matching. Both product groups are almost entirely Western-catalogue.
4. **No account and no streaming service needed.** It cold-starts from open datasets (MSD, MusicBrainz, tagtraum, two open Indian-music datasets) and works offline except for the Play link.
5. **It never invents a memory**, unlike AI-storytelling projects such as [EDCare](https://github.com/Joeljaison391/EDCare) (2024), which asks a language model to write a "non-fictional" story about a person's past.

## Honest gaps versus those products
- They have **real users and real music libraries**; we have a prototype with simulated feedback.
- Music & Memory and Music for My Mind come with **care-setting protocols and evidence**; we make no clinical claim.
- StoryWorth and LifeBio offer **printed books, family sharing and accounts**; ours stores everything locally on one computer.
