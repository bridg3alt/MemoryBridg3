"""MemoryBridge web app (Streamlit).

Run from the project folder:
    python -m streamlit run app/streamlit_app.py

The app never writes memories for the user; stories are the user's own words.
"""
from pathlib import Path
import sys

import pandas as pd
import streamlit as st
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

from memorybridge import audio, db  # noqa: E402
from memorybridge.profile import LIFE_PERIODS, UserProfile, period_for_age  # noqa: E402
from memorybridge.ranking import load_grid_predictions, recommend_songs  # noqa: E402
from memorybridge.recommender import load_songs  # noqa: E402
from style import (apply_theme, dots, hero, icon_img,  # noqa: E402
                   nav_icon, player, scene, small_label, vinyl)

PHOTOS = ROOT / "data" / "photos"
PAGES = ["My Profile", "Memory Journey", "Music Cue", "Capture a Memory", "My Life in Music"]
PAGE_ICONS = ["profile", "journey", "cue", "capture", "timeline"]
PERIOD_WORDS = {
    "Childhood": "the songs around the house",
    "College": "the years of friends and freedom",
    "Early adulthood": "finding your own way",
    "Family/Career": "busy years, full house",
}
# Speech recognition codes for the languages the app collects memories in.
SPEECH_CODES = {"Malayalam": "ml-IN", "Hindi": "hi-IN", "Tamil": "ta-IN", "Telugu": "te-IN",
                "Kannada": "kn-IN", "English": "en-IN"}

st.set_page_config(page_title="MemoryBridge", layout="wide", initial_sidebar_state="collapsed")
apply_theme()


@st.cache_data
def songs() -> pd.DataFrame:
    return load_songs()


@st.cache_data
def grid_predictions() -> pd.DataFrame:
    return load_grid_predictions()


@st.cache_resource
def preview_cache() -> dict:
    """Preview lookups are kept for the whole session, and on disk, so a demo never waits twice."""
    return audio.load_cache()


def play_here(song, key: str) -> None:
    """Play the song inside the app: your own file first, then a 30-second preview, else a link.

    On the Capture and Timeline pages the song comes from a frame indexed by song_id, so the id
    is the row's name rather than a column.
    """
    song_id = str(song["song_id"] if "song_id" in song.index else song.name)
    cache = preview_cache()
    source, value = audio.playable(song_id, song["title"],
                                   song["artist"] if isinstance(song["artist"], str) else "", cache)
    if source == "file":
        st.audio(value)
    elif source == "preview":
        st.audio(value, format="audio/m4a")
        st.caption("30-second preview, from the free iTunes Search service.")
    else:
        st.link_button("Find it on YouTube", song["play_url"], key=key)
        st.caption("No preview exists for this one. Put an audio file at "
                   f"`data/audio/{song_id}.mp3` to play it here.")


def go_to(page: str, remember: bool = True) -> None:
    """Change page on the next run, keeping a trail so Back can walk it in reverse."""
    if remember and page != st.session_state.get("page"):
        st.session_state.setdefault("history", []).append(st.session_state.get("page", PAGES[0]))
    st.session_state.pending_page = page


def go_back() -> None:
    """Step back to the page you came from."""
    history = st.session_state.get("history") or []
    if history:
        st.session_state.pending_page = history.pop()


def can_go_back() -> bool:
    return bool(st.session_state.get("history"))


def text_or(value, fallback: str) -> str:
    return value if isinstance(value, str) and value.strip() else fallback


def song_line(song) -> str:
    return (f"### {icon_img('record', 26)} {song['title']}\n"
            f"**{text_or(song['artist'], 'Unknown artist')}**  ·  "
            f"<span class='mb-year'>{int(song['year'])}</span>  ·  {song['language']}")


def current_user() -> dict | None:
    user_id = st.session_state.get("user_id")
    return db.get_user(user_id) if user_id else None


def profile_of(user: dict) -> UserProfile:
    return UserProfile(user["birth_year"], user["language"], [g for g in user["genres"].split("|") if g])


# ---------------------------------------------------------------- top navigation
st.session_state.setdefault("page", PAGES[0])
if "pending_page" in st.session_state:
    st.session_state.page = st.session_state.pop("pending_page")

with st.container(key="mb_nav"):
    nav_columns = st.columns(len(PAGES))
    for tab, (page_name, page_icon) in enumerate(zip(PAGES, PAGE_ICONS)):
        with nav_columns[tab]:
            here = page_name == st.session_state.page
            nav_icon(page_icon, here)
            if st.button(page_name, key=f"nav_{tab}", use_container_width=True,
                         type="primary" if here else "secondary"):
                go_to(page_name)
                st.rerun()

back_column, who_column = st.columns([1, 2.4])
with back_column:
    if st.button("Back", key="nav_back", disabled=not can_go_back(), use_container_width=True):
        go_back()
        st.rerun()
with who_column:
    users = db.list_users()
    if users:
        labels = {u["user_id"]: f"{u['name']}  ·  {u['birth_year']}" for u in users}
        ids = list(labels)
        current = st.session_state.get("user_id", ids[0])
        st.session_state.user_id = st.selectbox("Who is listening?", ids, label_visibility="collapsed",
                                                index=ids.index(current) if current in ids else 0,
                                                format_func=labels.get)
st.markdown("<hr class='mb-rule'/>", unsafe_allow_html=True)

user = current_user()
page = st.session_state.page

# ---------------------------------------------------------------- 1. profile
if page == PAGES[0]:
    words, turntable = st.columns([1.1, 1], vertical_alignment="center")
    with words:
        hero("Memory Bridge", "A song can open a door you thought was closed.")
    with turntable:
        kept_songs = db.get_memories(user["user_id"]) if user else []
        if kept_songs:                   # the record shows the last song this person kept
            last = songs().set_index("song_id").loc[kept_songs[-1]["song_id"]]
            scene(last["title"], text_or(last["artist"], ""), str(int(last["year"])), size=330)
        else:
            scene("Memory Bridge", "the songs that remember with you", "", size=330)
    if user:
        st.markdown(f"#### Welcome back, {user['name'].split('—')[0].strip()}")
        st.markdown(f"Born **{user['birth_year']}** · listens in **{user['language']}** · "
                    f"loves **{user['genres'].replace('|', ', ') or 'all kinds of music'}**")
        st.button("Choose a time in your life →", on_click=go_to, args=(PAGES[1],), type="primary")

        # Removing a listener throws away their memories for good, so it asks twice: the tick box
        # has to be ticked before the button does anything.
        kept = db.count_memories(user["user_id"])
        with st.expander("Remove this listener"):
            st.warning(f"This deletes **{user['name']}**, their **{kept}** saved "
                       f"{'memory' if kept == 1 else 'memories'}, their photos and every reaction "
                       f"they left. It cannot be undone.")
            sure = st.checkbox(f"Yes, delete {user['name']} and everything they saved",
                               key=f"sure_{user['user_id']}")
            if st.button("Delete for good", type="primary", disabled=not sure):
                for photo in db.delete_user(user["user_id"]):
                    file = ROOT / photo
                    if file.exists():
                        file.unlink()
                remaining = db.list_users()
                st.session_state.user_id = remaining[0]["user_id"] if remaining else None
                st.session_state.history = []
                st.session_state.capture_song_id = None
                st.rerun()
        st.divider()

    languages = sorted(songs().language.dropna().unique())
    genres = sorted(songs().genre.dropna().unique())
    with st.form("new_profile"):
        st.markdown("#### Tell us a little about you")
        name = st.text_input("Your name")
        birth_year = st.number_input("The year you were born", min_value=1930, max_value=2000, value=1958, step=1)
        language = st.selectbox("The language your favourite songs are in", languages,
                                index=languages.index("English"))
        favourite = st.multiselect("Music you have always liked", genres)
        if st.form_submit_button("Save and begin", type="primary") and name.strip():
            st.session_state.user_id = db.create_user(name.strip(), int(birth_year), language, favourite)
            st.rerun()

elif not user:
    hero("Memory Bridge", "A song can open a door you thought was closed.")
    st.info("Let's start with your name and the year you were born.")
    st.button("Create my profile", on_click=go_to, args=(PAGES[0],), type="primary")

# ---------------------------------------------------------------- 2. memory journey
elif page == PAGES[1]:
    st.markdown("## Where shall we go back to?")
    st.markdown("<span class='mb-tag'>Pick a time in your life, and we will bring its music back.</span>",
                unsafe_allow_html=True)
    st.write("")
    profile = profile_of(user)
    st.markdown("<div class='period-grid'>", unsafe_allow_html=True)
    columns = st.columns(2)
    for i, name in enumerate(LIFE_PERIODS):
        first, last = profile.year_range(name)
        with columns[i % 2]:
            if st.button(f"{name}\n{first} – {last}\n{PERIOD_WORDS[name]}",
                         use_container_width=True, key=name):
                st.session_state.period = name
                go_to(PAGES[2])
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------- 3. music cue
elif page == PAGES[2]:
    period = st.session_state.get("period")
    profile = profile_of(user)
    st.markdown(f"## Songs from your {period.lower() if period else 'younger'} years",
                unsafe_allow_html=True)

    top, ranked_by = recommend_songs(songs(), profile, period,
                                     exclude=db.dismissed_song_ids(user["user_id"]),
                                     grid_predictions=grid_predictions())
    # Words on the left, the record playing on the right.
    words, turntable = st.columns([1.1, 1], vertical_alignment="center")
    with words:
        small_label("Currently playing.",
                    f"{text_or(top.iloc[0]['artist'], 'Unknown artist')} - {top.iloc[0]['title']}"
                    if len(top) else "Nothing yet.")
        first, last = profile.year_range(period) if period else ("", "")
        st.markdown(f"<span class='mb-micro'>{PERIOD_WORDS.get(period, '')} &nbsp;·&nbsp; "
                    f"{first} - {last}</span><br/>"
                    f"<span class='mb-label' style='margin-top:.6rem'>{len(top)} songs</span>",
                    unsafe_allow_html=True)
        dots(min(len(top), 6), 1)
    with turntable:
        if len(top):
            leading = top.iloc[0]
            scene(leading["title"], text_or(leading["artist"], ""), str(int(leading["year"])), size=330)

    st.write("")
    for _, song in top.iterrows():
        with st.container(border=True):
            st.markdown(song_line(song), unsafe_allow_html=True)
            st.markdown(f"<span class='mb-why'>{icon_img('sparkle', 17)}{' · '.join(song['reasons'])}</span>", unsafe_allow_html=True)
            st.write("")
            play_here(song, key=f"yt_{song['song_id']}")
            knows, no_bell, capture = st.columns([1, 1.2, 1.4])
            if knows.button("I know it", key=f"rec_{song['song_id']}", use_container_width=True):
                db.log_interaction(user["user_id"], song["song_id"], True, False, False, False, ranked_by)
                st.toast("Noted.")
            if no_bell.button("Not for me", key=f"no_{song['song_id']}", use_container_width=True):
                db.log_interaction(user["user_id"], song["song_id"], False, False, False, False, ranked_by)
                st.rerun()
            if capture.button("It reminds me…", key=f"cap_{song['song_id']}", use_container_width=True,
                              type="primary"):
                st.session_state.capture_song_id = song["song_id"]
                st.session_state.capture_ranked_by = ranked_by
                go_to(PAGES[3])
                st.rerun()

    if len(top):
        leading = top.iloc[0]
        player(leading["title"], text_or(leading["artist"], "Unknown artist"))
    st.markdown(f"<span class='mb-ranked'>Chosen for you by: {ranked_by}</span>", unsafe_allow_html=True)

# ---------------------------------------------------------------- 4. capture
elif page == PAGES[3]:
    st.markdown("## What does this song bring back?")
    song_id = st.session_state.get("capture_song_id")
    if not song_id:
        st.info("Pick a song first, then tell us what it reminds you of.")
        st.button("Back to the songs", on_click=go_to, args=(PAGES[2],))
    else:
        song = songs().set_index("song_id").loc[song_id]
        vinyl(song["title"], text_or(song["artist"], ""), str(int(song["year"])), size=260)
        with st.container(border=True):
            small_label("Currently playing.",
                        f"{text_or(song['artist'], 'Unknown artist')} - {song['title']}")
            play_here(song, key=f"yt_capture_{song_id}")

        age = int(song["year"]) - user["birth_year"]
        default_period = st.session_state.get("period") or period_for_age(age)
        period_options = list(LIFE_PERIODS) + ["Other"]

        # Speak instead of type. The recording is made in the browser and sent to Google's free
        # recognition service, so this needs the internet. Errors are reported in full rather than
        # swallowed: streamlit_mic_recorder's own speech_to_text() hides every failure behind None.
        if st.session_state.pop("clear_story", False):
            st.session_state.story_input = ""      # must happen before the box below is drawn
        st.session_state.setdefault("story_input", "")
        own_language = user["language"] if user["language"] in SPEECH_CODES else "English"
        st.markdown(f"{icon_img('capture', 22)}<span class='mb-tag'>Rather say it out loud? "
                    f"Choose the language, press record, speak, then press stop.</span>",
                    unsafe_allow_html=True)

        choices = [own_language, "English"] if own_language != "English" else ["English"]
        if own_language != "English":
            choices.append(f"Try {own_language}, then English")
        spoken_language = st.radio("Speak in", choices, horizontal=True, key="speech_language")

        if spoken_language.startswith("Try "):
            attempts = [own_language, "English"]
        else:
            attempts = [spoken_language]

        mic_columns = st.columns([2, 1])
        with mic_columns[0]:
            recording = mic_recorder(start_prompt="Start speaking", stop_prompt="I have finished",
                                     just_once=True, use_container_width=True, format="wav",
                                     key="story_mic")
        with mic_columns[1]:
            if st.button("Clear", use_container_width=True, disabled=not st.session_state.story_input):
                st.session_state.story_input = ""
                st.rerun()

        if recording:
            st.audio(recording["bytes"], format="audio/wav")   # so you can hear what was captured
            audio_data = sr.AudioData(recording["bytes"], recording["sample_rate"],
                                      recording["sample_width"])
            recognizer = sr.Recognizer()
            heard, problem = "", ""
            for attempt in attempts:
                try:
                    heard = recognizer.recognize_google(audio_data, language=SPEECH_CODES[attempt])
                    problem = ""
                    break
                except sr.UnknownValueError:
                    problem = ("No words were recognised. Speak a little louder and closer to the "
                               "microphone, and leave a moment of quiet before pressing stop.")
                except sr.RequestError as error:
                    problem = (f"Could not reach the recognition service ({error}). "
                               f"Check the internet connection, then try again.")
                    break
                except Exception as error:                      # noqa: BLE001 - shown, not hidden
                    problem = f"{type(error).__name__}: {error}"
                    break
            if heard:
                st.session_state.story_input = f"{st.session_state.story_input} {heard}".strip()
                st.session_state.speech_note = f"Heard: “{heard}”"
            else:
                st.session_state.speech_problem = problem
            st.rerun()

        if note := st.session_state.pop("speech_note", None):
            st.success(note + "  Read it over and change anything that came out wrong.")
        if problem := st.session_state.pop("speech_problem", None):
            st.warning(problem)
        st.caption("The words are recognised online by Google. Allow the microphone when the browser "
                   "asks. Malayalam and Hindi work best with short, clear sentences.")

        with st.form("capture"):
            story = st.text_area("Tell it in your own words", height=190, key="story_input",
                                 placeholder="We used to sing this on the bus to college…")
            first, second = st.columns(2)
            with first:
                life_period = st.selectbox("This belongs to", period_options,
                                           index=period_options.index(default_period))
                people = st.text_input("Who was with you?", placeholder="my sister, college friends")
            with second:
                year = st.number_input("Around which year?", min_value=1930, max_value=2030,
                                       value=int(song["year"]), step=1)
                place = st.text_input("Where was it?", placeholder="Kochi")
            photo = st.file_uploader("A photo from that time (optional)", type=["jpg", "jpeg", "png"])
            if st.form_submit_button("Keep this memory", type="primary"):
                if not story.strip():
                    st.error("Write a line or two first — these are your words, and only yours.")
                else:
                    memory_id = db.save_memory(user["user_id"], song_id, story, life_period, people, place,
                                               int(year), None)
                    if photo is not None:
                        PHOTOS.mkdir(parents=True, exist_ok=True)
                        photo_path = PHOTOS / f"{memory_id}{Path(photo.name).suffix.lower()}"
                        photo_path.write_bytes(photo.getvalue())
                        db.set_photo(memory_id, str(photo_path.relative_to(ROOT)))
                    db.log_interaction(user["user_id"], song_id, True, True, True, True,
                                       st.session_state.get("capture_ranked_by", "unknown"))
                    st.session_state.capture_song_id = None
                    st.session_state.clear_story = True
                    st.session_state.saved_message = f"Kept safe in {life_period}."
                    go_to(PAGES[4])
                    st.rerun()

# ---------------------------------------------------------------- 5. timeline
elif page == PAGES[4]:
    st.markdown("## My Life in Music")
    st.markdown("<span class='mb-tag'>Everything you have kept, in the order it happened.</span>",
                unsafe_allow_html=True)
    if message := st.session_state.pop("saved_message", None):
        st.success(message)
    choice = st.selectbox("Take me back to…", ["everything"] + list(LIFE_PERIODS) + ["Other"])
    memories = db.get_memories(user["user_id"], None if choice == "everything" else choice)
    if not memories:
        st.info("Nothing kept yet. Find a song you remember, and tell it its story.")
        st.button("Find a song", on_click=go_to, args=(PAGES[1],), type="primary")
    by_id = songs().set_index("song_id")
    for memory in memories:
        song = by_id.loc[memory["song_id"]]
        with st.container(border=True):
            st.markdown(f"<span class='mb-year'>{memory['year']}</span>  "
                        f"&nbsp;&nbsp;{memory['life_period']}",
                        unsafe_allow_html=True)
            st.markdown(song_line(song), unsafe_allow_html=True)
            st.markdown(f"> {memory['story']}")
            details = [f"{icon_img('people', 18)}{memory['people']}" if memory["people"] else "",
                       f"{icon_img('place', 18)}{memory['place']}" if memory["place"] else ""]
            if any(details):
                st.markdown(f"<span class='mb-why'>{'  ·  '.join(d for d in details if d)}</span>",
                            unsafe_allow_html=True)
            if memory["photo_path"] and (ROOT / memory["photo_path"]).exists():
                st.image(str(ROOT / memory["photo_path"]), width=340)
            play_here(song, key=f"yt_timeline_{memory['memory_id']}")
