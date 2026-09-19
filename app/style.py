"""Monochrome record-sleeve styling for MemoryBridge.

Editorial black and white: near-white paper, one heavy condensed display face, small
letter-spaced labels, a spinning vinyl, and cards that read as record sleeves. No colour --
emphasis comes from weight and size, the way a printed sleeve does.

Public API: apply_theme(), hero(), doodle(), icon_uri(), icon_img(), nav_icon(),
vinyl(), small_label(), dots().
"""
from base64 import b64encode
from functools import lru_cache
from pathlib import Path
import html

import streamlit as st

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Allura&family=Just+Another+Hand&family=Permanent+Marker&family=Caveat:wght@500;700"
         "&family=Special+Elite&display=swap")

ASSETS = Path(__file__).resolve().parent / "assets"
DOODLES = ASSETS / "doodles"
ICONS = ASSETS / "icons"
PATTERN = ASSETS / "pattern-music.svg"
WORDMARK = ASSETS / "wordmark.png"
PAPER_BG = ASSETS / "paper-bg.jpg"
EDGE_LEFT = ASSETS / "edge-left.png"
EDGE_RIGHT = ASSETS / "edge-right.png"


def _pattern_uri() -> str:
    """Scattered music doodles, tiled behind the page."""
    if not PATTERN.exists():
        return ""
    return "data:image/svg+xml;base64," + b64encode(PATTERN.read_bytes()).decode("ascii")


def _paper_uri() -> str:
    """The aged graph paper, used lightly under the content."""
    if not PAPER_BG.exists():
        return ""
    return "data:image/jpeg;base64," + b64encode(PAPER_BG.read_bytes()).decode("ascii")


def _edge_uri(path: Path) -> str:
    """One torn edge, for the side of the page."""
    if not path.exists():
        return ""
    return "data:image/png;base64," + b64encode(path.read_bytes()).decode("ascii")


PATTERN_URI = _pattern_uri()
PAPER_URI = _paper_uri()
EDGE_LEFT_URI = _edge_uri(EDGE_LEFT)
EDGE_RIGHT_URI = _edge_uri(EDGE_RIGHT)

# Paper fibre: a noise tile, so the page is never a flat colour.
FIBRE = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'>"
         "<filter id='f'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='4'/>"
         "<feColorMatrix type='saturate' values='0'/></filter>"
         "<rect width='180' height='180' filter='url(%23f)' opacity='.06'/></svg>")

# The ragged edge every sheet in the app is torn along. Fixed, so it never flickers between runs.
TORN = "polygon(0.0% 0.94%, 3.8% 0.01%, 7.7% 0.06%, 11.5% 1.02%, 15.4% 0.89%, 19.2% 0.41%, 23.1% 0.32%, 26.9% 0.63%, 30.8% 0.59%, 34.6% 1.03%, 38.5% 1.08%, 42.3% 1.00%, 46.2% 0.89%, 50.0% 0.24%, 53.8% 0.70%, 57.7% 0.32%, 61.5% 0.77%, 65.4% 0.32%, 69.2% 0.19%, 73.1% 0.56%, 76.9% 1.07%, 80.8% 0.84%, 84.6% 0.98%, 88.5% 0.00%, 92.3% 0.28%, 96.2% 0.66%, 100.0% 0.50%, 100.0% 99.30%, 96.2% 99.48%, 92.3% 99.08%, 88.5% 99.24%, 84.6% 99.45%, 80.8% 99.45%, 76.9% 98.97%, 73.1% 99.18%, 69.2% 99.13%, 65.4% 99.83%, 61.5% 99.26%, 57.7% 99.88%, 53.8% 99.39%, 50.0% 99.03%, 46.2% 99.17%, 42.3% 98.98%, 38.5% 99.94%, 34.6% 99.56%, 30.8% 99.17%, 26.9% 99.22%, 23.1% 99.83%, 19.2% 99.71%, 15.4% 98.91%, 11.5% 99.23%, 7.7% 99.59%, 3.8% 99.21%, 0.0% 99.37%)"

CSS = f"""
<style>
@import url('{FONTS}');

:root {{
  --paper: #efe6d4;
  --paper-card: #f8f1e0;
  --paper-soft: #e4d7bb;
  --ink: #231a12;
  --ink-80: #33251a;
  --ink-55: #54402d;
  --ink-35: #7a6349;
  --ink-15: #bfad8c;
  --red: #7a2b3a;            /* deep wine */
  --wine-soft: #9d4f5c;
  --wood: #6b4a2f;
  --parchment: #efe4cd;
  --script: 'Allura', 'Caveat', cursive;   /* the signature wordmark */
  --display: 'Permanent Marker', cursive;
  --hand: 'Caveat', 'Comic Sans MS', cursive;
  --ui: 'Special Elite', 'Courier New', monospace;
  --tall: 'Just Another Hand', 'Caveat', cursive;
  --pixel: 'Special Elite', 'Courier New', monospace;
  --type: 'Special Elite', 'Courier New', monospace;
}}

.block-container {{
  max-width: 1340px !important;
  padding-top: 1.4rem !important;
  padding-bottom: 2.4rem !important;
  padding-left: 2.4rem !important;
  padding-right: 2.4rem !important;
  background: transparent;
}}

.stApp {{
  background-color: var(--paper);
  background-image:
    radial-gradient(ellipse at 50% 0%, rgba(255,250,236,.9) 0%, rgba(255,252,244,0) 55%),
    radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 52%, rgba(74,55,35,.14) 100%),
    linear-gradient(180deg, rgba(178,146,96,.10), rgba(178,146,96,.04)),
    url("{PATTERN_URI}");
  background-size: auto, auto, auto, 560px 560px;
  background-position: center, center, center, center;
  background-repeat: no-repeat, no-repeat, no-repeat, repeat;
  background-attachment: fixed, fixed, fixed, fixed;
}}
[data-testid="stHeader"] {{ background: transparent; }}

/* the torn edges of an old sheet, down the left and right of the window */
.stApp::before, .stApp::after {{
  content: "";
  position: fixed;
  top: 0;
  bottom: 0;
  width: 108px;
  z-index: 0;
  pointer-events: none;
  background-repeat: repeat-y;
  background-size: 100% auto;
  opacity: .85;
}}
.stApp::before {{
  left: 0;
  background-image: url("{EDGE_LEFT_URI}");
}}
.stApp::after {{
  right: 0;
  background-image: url("{EDGE_RIGHT_URI}");
}}
/* the content sits above the edges */
[data-testid="stAppViewContainer"] {{ position: relative; z-index: 1; }}

@media (max-width: 1100px) {{
  .stApp::before, .stApp::after {{ width: 54px; }}
}}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {{ display: none !important; }}

/* ---------- type ---------- */
html, body, [class*="css"], .stMarkdown, .stMarkdown p, label, input, textarea,
.stSelectbox div, .stMultiSelect div, .stRadio label, .stCaption, .stAlert p {{
  font-family: var(--ui);
  color: var(--ink-80);
  -webkit-font-smoothing: antialiased;
}}
.stMarkdown p, label, .stRadio label, .stAlert p {{ font-size: 1.12rem; line-height: 1.6; }}

h1, h2 {{
  text-shadow: 0 1px 0 rgba(255,251,240,.9);
  font-family: var(--display) !important;
  font-weight: 400 !important;
  letter-spacing: 0;
  color: var(--ink) !important;
  line-height: 1.02 !important;
}}
h1 {{ font-size: 3.6rem !important; }}
h2 {{ font-size: 2.5rem !important; }}
h3 {{
  font-family: var(--hand) !important;
  font-weight: 700 !important;
  font-size: 2rem !important;
  letter-spacing: 0;
  color: var(--ink) !important;
}}
h4 {{
  font-family: var(--hand) !important;
  font-weight: 700 !important;
  font-size: 1.4rem !important;
  color: var(--ink) !important;
}}

[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{
  color: var(--ink-55) !important;
  font-size: .92rem !important;
  letter-spacing: .2px;
}}

/* ---------- the small labels with a full stop, as on the sleeve ---------- */
.mb-label {{
  font-family: var(--hand);
  font-weight: 700;
  font-size: 1.75rem;
  color: var(--ink);
  display: block;
  margin: .1rem 0 .15rem;
}}
.mb-sub {{ font-family: var(--ui); font-size: 1rem; color: var(--ink-55); }}
.mb-micro {{
  font-family: var(--type);
  font-size: .68rem;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--ink-35);
}}
.mb-right {{ text-align: right; }}

/* ---------- navigation ---------- */
.st-key-mb_nav {{
  border: none;
  background: transparent;
  padding: .4rem 0 0 !important;
  margin-bottom: .2rem;
  box-shadow: none;
}}
.mb-navicon {{ display: flex; justify-content: center; align-items: flex-end; height: 44px; }}
.mb-navicon img {{
  height: 38px;
  opacity: .8;
  transition: opacity .15s ease, transform .15s ease;
}}
.mb-navicon.mb-on img {{ opacity: 1; transform: translateY(-2px) scale(1.06); }}
.st-key-mb_nav .stButton > button {{
  width: 100%;
  min-height: 3.4rem;
  height: auto;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: var(--red) !important;
  font-family: var(--ui) !important;
  font-size: 1rem !important;
  font-weight: 700;
  letter-spacing: 0;
  text-shadow: 0 1px 0 rgba(255,250,238,.75);
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
  padding: .05rem .05rem .45rem !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  word-break: normal;
  hyphens: none;
}}
.st-key-mb_nav .stButton > button:hover {{
  color: var(--ink) !important;
  background: transparent !important;
  transform: none !important;
  border-bottom-color: var(--ink-15) !important;
  background: transparent !important;
}}
.st-key-mb_nav .stButton > button[kind="primary"] {{
  background: transparent !important;
  color: var(--red) !important;
  font-weight: 700;
  border-bottom: 2px solid var(--red) !important;
}}

/* ---------- the record ---------- */
.mb-turntable {{ display: flex; justify-content: center; margin: .2rem 0 1rem; }}
.mb-stage {{
  position: relative;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  margin: .1rem 0 1.2rem;
}}
.mb-stage .mb-sleeve {{        /* the envelope the record slides out of */
  position: absolute;
  left: 50%;
  bottom: -6%;
  transform: translateX(-46%) rotate(-2deg);
  width: 82%;
  height: 62%;
  background:
    url("{FIBRE}"),
    linear-gradient(160deg, #f6ead2 0%, #e9dabd 60%, #dfcdab 100%);
  background-size: 180px 180px, auto;
  box-shadow: 0 16px 34px rgba(74,55,35,.24);
  clip-path: {TORN};
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0 0 0 12%;
}}
.mb-stage .mb-sleeve .mb-sleeve-text {{
  font-family: var(--ui);
  font-size: .95rem;
  line-height: 1.5;
  color: var(--ink-55);
}}
/* the postmark in the corner of the envelope */
.mb-stamp {{
  position: absolute;
  right: 4%;
  bottom: 2%;
  z-index: 3;
  width: 92px;
  padding: 8px 5px;
  text-align: center;
  background: #efdfc4;
  border: 1px dashed rgba(122,43,58,.45);
  box-shadow: 0 4px 10px rgba(74,55,35,.18);
  transform: rotate(4deg);
  font-family: var(--ui);
  font-size: .6rem;
  letter-spacing: .5px;
  color: var(--red);
  text-transform: uppercase;
}}
.mb-stamp img {{ height: 20px; opacity: .8; display: block; margin: 0 auto 3px; }}
.mb-stage .mb-vinyl {{ z-index: 1; }}
.mb-vinyl {{
  position: relative;
  width: var(--disc, 240px);
  height: var(--disc, 240px);
  border-radius: 50%;
  background:
    repeating-radial-gradient(circle at 50% 50%, #241a13 0 2px, #140e09 2px 4px);
  box-shadow: 0 18px 36px rgba(0,0,0,.28), inset 0 0 40px rgba(255,255,255,.05);
  animation: mb-spin 4.5s linear infinite;
}}
.mb-vinyl.mb-still {{ animation-play-state: paused; }}
.mb-vinyl .mb-disc-label {{
  position: absolute;
  inset: 0;
  margin: auto;
  width: 40%;
  height: 40%;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 6px;
  background: #f6eedd;
  font-family: var(--pixel);
  font-size: .5rem;
  line-height: 1.35;
  letter-spacing: .3px;
  color: var(--ink-55);
  text-transform: uppercase;
  overflow: hidden;
}}
.mb-vinyl .mb-disc-year {{ font-family: var(--tall); font-size: 1.4rem; color: var(--red); }}
.mb-vinyl .mb-spindle {{
  position: absolute;
  inset: 0;
  margin: auto;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--paper);
  z-index: 2;
}}
@keyframes mb-spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}

.mb-dots {{ display: flex; gap: 7px; justify-content: center; margin: .5rem 0 .2rem; }}
.mb-dots span {{ width: 7px; height: 7px; border-radius: 50%; background: var(--ink-35); }}
.mb-dots span.mb-off {{ background: var(--ink-15); }}

/* ---------- cards read as sleeves ---------- */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > [data-testid="stVerticalBlock"]) {{
  position: relative;
  background:
    url("{FIBRE}"),
    linear-gradient(180deg, #fbf6ea, #f5eeda);
  background-size: 180px 180px, auto;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: 0 10px 26px rgba(17,17,17,.07);
  padding: 1.6rem 1.7rem !important;
  margin-bottom: 1.15rem;
  clip-path: {TORN};              /* torn along the top and bottom edges */
}}
.st-key-mb_nav [data-testid="stVerticalBlockBorderWrapper"] {{
  box-shadow: none;
  border: none !important;
}}

/* ---------- buttons ---------- */
.stButton > button, .stLinkButton > a, .stFormSubmitButton > button, .stDownloadButton > button {{
  font-family: var(--ui) !important;
  font-size: 1rem !important;
  font-weight: 500;
  letter-spacing: .2px;
  border-radius: 999px !important;
  border: 1px solid var(--ink-15) !important;
  background: var(--paper-card);
  color: var(--ink-80) !important;
  padding: .55rem 1.5rem !important;
  box-shadow: none;
  transition: background .15s ease, color .15s ease, border-color .15s ease;
}}
.stButton > button:hover, .stLinkButton > a:hover,
.stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{
  background: var(--ink);
  color: #ffffff !important;
  border-color: var(--ink) !important;
  transform: none;
}}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
  background: var(--red);
  color: #ffffff !important;
  border-color: var(--ink) !important;
  font-weight: 700;
}}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{
  background: var(--ink);
}}
.period-grid + div .stButton > button, .period-grid ~ div .stButton > button {{
  min-height: 140px;
  border-radius: 3px !important;
  font-family: var(--hand) !important;
  font-size: 1.85rem !important;
  font-weight: 700;
  letter-spacing: 0;
  white-space: pre-line;
  background: var(--paper-soft);
}}

/* ---------- inputs ---------- */
textarea, input, .stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div, .stNumberInput input {{
  background: var(--paper-card) !important;
  border-radius: 3px !important;
  border: 1px solid var(--ink-15) !important;
  font-family: var(--ui) !important;
  font-size: 1.08rem !important;
  color: var(--ink) !important;
}}
textarea:focus, input:focus {{ border-color: var(--ink) !important; box-shadow: none !important; }}
[data-testid="stFileUploaderDropzone"] {{
  background: var(--paper-soft) !important;
  border: 1px dashed var(--ink-35) !important;
  border-radius: 3px !important;
}}
audio {{ width: 100%; filter: sepia(.35) saturate(.7); }}

/* ---------- the story ---------- */
blockquote {{
  border-left: 3px solid var(--red) !important;
  background: transparent;
  border-radius: 0 !important;
  padding: .3rem 0 .3rem 1rem !important;
  font-family: var(--hand) !important;
  font-size: 1.8rem !important;
  line-height: 1.4;
  color: var(--ink) !important;
}}
blockquote p {{ font-family: var(--hand) !important; font-size: 1.8rem !important; }}

hr {{ border: none; border-top: 1px solid var(--ink-15); }}
a {{ color: var(--ink) !important; text-underline-offset: 3px; }}

/* ---------- masthead ---------- */
.mb-hero {{
  padding: 1rem 0 1rem;
  margin-bottom: 1rem;
  border-bottom: none;
  position: relative;
}}
/* a torn strip instead of a ruled line */
.mb-hero::after {{
  content: "";
  position: absolute;
  left: 0;
  width: 62%;
  bottom: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--red), rgba(122,43,58,.15));
}}
.mb-wordmark {{
  display: block;
  width: 100%;
  max-width: 560px;
  height: auto;
  margin: .2rem 0 .6rem;
}}
.mb-hero h1 {{
  font-family: var(--script) !important;
  margin: 0 !important;
  font-size: 5rem !important;
  line-height: 1.05 !important;
  letter-spacing: 0;
  color: var(--red) !important;
  padding-bottom: .1em;          /* the descenders of the script need the room */
}}
.mb-hero .mb-record {{
  font-family: Georgia, 'Times New Roman', serif;
  font-style: italic;
  font-weight: 700;
  font-size: 1.75rem;
  color: var(--ink);
  display: block;
  margin-top: .3rem;
}}
.mb-hero .mb-tag {{ font-family: var(--ui); font-size: 1.08rem; color: var(--ink-80); display: block; margin: .45rem 0 1rem; }}

/* ---------- marks ---------- */
.mb-tag {{ font-family: var(--hand); font-size: 1.5rem; color: var(--ink-55); }}
.mb-why {{
  font-family: var(--ui);
  font-size: .95rem;
  color: var(--ink-55);
  background: var(--paper-soft);
  border: none;
  border-radius: 999px;
  padding: .28rem .8rem;
  display: inline-block;
}}
.mb-why img.mb-ic, .mb-tag img.mb-ic {{
  height: 14px;
  vertical-align: -2px;
  margin-right: 5px;
  opacity: .45;
}}
.mb-year {{
  font-family: var(--tall);
  font-size: 2.1rem;
  color: var(--red);
  letter-spacing: .5px;
}}
.mb-ranked {{
  font-family: var(--type);
  color: var(--ink-55);
  font-size: .68rem;
  letter-spacing: 2.5px;
  text-transform: uppercase;
}}
.mb-sleeve-title {{
  font-family: var(--display);
  font-size: 1.5rem;
  line-height: 1.35;
  color: var(--ink);
  text-transform: uppercase;
  margin: .2rem 0 .4rem;
}}

/* ---------- ticket stub ---------- */
.mb-ticket {{
  position: absolute;
  left: 2%;
  bottom: -4%;
  z-index: 3;
  padding: 7px 10px;
  background: #f1dfc2;
  border-left: 3px dotted rgba(122,43,58,.5);
  box-shadow: 0 6px 14px rgba(74,55,35,.2);
  transform: rotate(-4deg);
  font-family: var(--ui);
  font-size: .6rem;
  letter-spacing: .6px;
  color: var(--ink-55);
  text-transform: uppercase;
}}

/* ---------- the player bar along the bottom of the page ---------- */
.mb-player {{
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1.4rem 0 .6rem;
  padding: .7rem 1.1rem;
  background: linear-gradient(180deg, #f8f1e0, #ece0c6);
  border: 1px solid rgba(122,43,58,.18);
  border-radius: 999px;
  box-shadow: 0 10px 26px rgba(74,55,35,.16);
}}
.mb-player .mb-cover {{
  width: 76px;
  height: 60px;
  flex: none;
  background: linear-gradient(170deg, #c7a878, #8a6a4a 55%, #46331f);
  border-radius: 4px;
}}
.mb-player .mb-cover img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 4px; }}
.mb-player .mb-now {{ flex: 1; min-width: 0; }}
.mb-player .mb-now .mb-song {{
  font-family: var(--ui);
  font-size: 1.15rem;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.mb-player .mb-now .mb-by {{ font-family: var(--ui); font-size: .92rem; color: var(--ink-55); }}
.mb-player .mb-line {{
  height: 3px;
  background: rgba(122,43,58,.18);
  border-radius: 2px;
  margin: .45rem 0 .25rem;
  position: relative;
}}
.mb-player .mb-line span {{
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 38%;
  background: var(--red);
  border-radius: 2px;
}}
.mb-player .mb-line span::after {{
  content: "";
  position: absolute;
  right: -5px;
  top: -3px;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--red);
}}
.mb-player .mb-times {{
  display: flex;
  justify-content: space-between;
  font-family: var(--ui);
  font-size: .7rem;
  color: var(--ink-55);
}}
.mb-player .mb-remembers {{
  font-family: var(--script);
  font-size: 1.7rem;
  color: var(--red);
  flex: none;
  padding-left: .9rem;
  border-left: 1px solid rgba(122,43,58,.2);
  transform: rotate(-3deg);
}}

/* ---------- doodles ---------- */
.mb-doodle-wrap {{ display: flex; justify-content: center; margin: .2rem 0 1rem; }}
.mb-doodle {{
  opacity: .5;
  filter: sepia(.5) contrast(1.02);
  -webkit-mask-image: linear-gradient(to bottom, #000 60%, rgba(0,0,0,.15) 100%);
  mask-image: linear-gradient(to bottom, #000 60%, rgba(0,0,0,.15) 100%);
}}
.mb-doodle-wrap.mb-doodle-right {{ justify-content: flex-end; margin-top: -1.2rem; }}
</style>
"""


def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


@lru_cache(maxsize=2)
def _wordmark_uri() -> str:
    if not WORDMARK.exists():
        return ""
    return "data:image/png;base64," + b64encode(WORDMARK.read_bytes()).decode("ascii")


def hero(title: str, tagline: str) -> None:
    """The masthead. Uses the wordmark image when one is present, otherwise sets the name in type."""
    uri = _wordmark_uri()
    if uri:
        mark = (f"<img class='mb-wordmark' src='{uri}' alt='{html.escape(title)}'/>")
    else:
        mark = f"<h1>{html.escape(title)}</h1>"
    st.markdown(
        f"<div class='mb-hero'>{mark}"
        f"<span class='mb-record'>A record of a life.</span>"
        f"<span class='mb-tag'>{html.escape(tagline)}</span></div>",
        unsafe_allow_html=True)


def small_label(text: str, sub: str = "") -> None:
    """The sleeve's little headings: 'Currently playing.' with a quieter line under it."""
    extra = f"<span class='mb-sub'>{html.escape(sub)}</span>" if sub else ""
    st.markdown(f"<span class='mb-label'>{html.escape(text)}</span>{extra}", unsafe_allow_html=True)


def dots(total: int, filled: int) -> None:
    """The row of dots that shows where you are in the list."""
    marks = "".join(f"<span class='{'' if i < filled else 'mb-off'}'></span>" for i in range(total))
    st.markdown(f"<div class='mb-dots'>{marks}</div>", unsafe_allow_html=True)


def _disc_markup(title: str, artist: str = "", year: str = "", size: int = 240,
                 spinning: bool = True) -> str:
    """The record itself. Styled inline as well as in the stylesheet, so it survives a slow CSS load."""
    still = "" if spinning else " mb-still"
    label = html.escape(str(title)[:38])
    who = html.escape(str(artist)[:28]) if artist else ""
    hole = max(7, size // 26)
    disc_style = (f"position:relative;width:{size}px;height:{size}px;border-radius:50%;"
                  "background:repeating-radial-gradient(circle at 50% 50%,#241a13 0 2px,#140e09 2px 4px);"
                  "box-shadow:0 18px 36px rgba(0,0,0,.28);"
                  f"--disc:{size}px;")
    label_style = ("position:absolute;inset:0;margin:auto;width:40%;height:40%;border-radius:50%;"
                   "display:flex;flex-direction:column;justify-content:center;align-items:center;"
                   "text-align:center;padding:6px;background:#f6eedd;overflow:hidden;"
                   "font-size:.5rem;line-height:1.35;text-transform:uppercase;color:#6f6e6b;")
    spindle_style = (f"position:absolute;inset:0;margin:auto;width:{hole}px;height:{hole}px;"
                     "border-radius:50%;background:#efe6d4;z-index:2;")
    year_line = (f"<div class='mb-disc-year' style='font-size:1.35rem;color:#7a2b3a'>"
                 f"{html.escape(str(year))}</div>") if year else ""
    artist_line = f"<div>{who}</div>" if who else ""
    return (f"<div class='mb-vinyl{still}' style=\"{disc_style}\">"
            f"<div class='mb-disc-label' style=\"{label_style}\">"
            f"<div>{label}</div>{year_line}{artist_line}</div>"
            f"<div class='mb-spindle' style=\"{spindle_style}\"></div></div>")


def vinyl(title: str, artist: str = "", year: str = "", size: int = 240, spinning: bool = True,
          sleeve: bool = False) -> None:
    """A record, optionally half out of its sleeve."""
    disc = _disc_markup(title, artist, year, size, spinning)
    if sleeve:
        st.markdown(f"<div class='mb-stage' style='height:{int(size * 1.18)}px'>{disc}"
                    f"<div class='mb-sleeve'></div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='mb-turntable' style='display:flex;justify-content:center;"
                    f"margin:.2rem 0 1rem'>{disc}</div>", unsafe_allow_html=True)


@lru_cache(maxsize=48)
def _uri(path_str: str) -> str:
    return "data:image/svg+xml;base64," + b64encode(Path(path_str).read_bytes()).decode("ascii")


def doodle(name: str, width: int = 240, align: str = "center") -> None:
    """One Open Doodles figure (CC0), in greyscale, faded into the page."""
    path = DOODLES / f"{name}.svg"
    if not path.exists():
        return
    side = " mb-doodle-right" if align == "right" else ""
    st.markdown(f"<div class='mb-doodle-wrap{side}'>"
                f"<img class='mb-doodle' src='{_uri(str(path))}' width='{width}' alt=''/></div>",
                unsafe_allow_html=True)


def icon_uri(name: str) -> str:
    """Data URI for one hand-drawn Iconoodle icon (MIT)."""
    path = ICONS / f"{name}.svg"
    return _uri(str(path)) if path.exists() else ""


def icon_img(name: str, height: int = 20) -> str:
    """Inline <img> for an icon, to drop inside a markdown line."""
    uri = icon_uri(name)
    return f"<img class='mb-ic' src='{uri}' height='{height}' alt=''/>" if uri else ""


def nav_icon(name: str, active: bool) -> None:
    """The icon that sits above a navigation tab."""
    on = " mb-on" if active else ""
    st.markdown(f"<div class='mb-navicon{on}'><img src='{icon_uri(name)}' alt=''/></div>",
                unsafe_allow_html=True)


def scene(title: str, artist: str = "", year: str = "", size: int = 250) -> None:
    """The record sliding out of its envelope, with a stamp and a ticket stub."""
    disc = _disc_markup(title, artist, year, size)
    st.markdown(
        f"<div class='mb-stage' style='height:{int(size * 1.26)}px'>{disc}"
        f"<div class='mb-sleeve'><div class='mb-sleeve-text'>Press play<br/>on your memories.</div></div>"
        f"<div class='mb-stamp'>{icon_img('record', 20)}Good days<br/>ahead</div>"
        f"<div class='mb-ticket'>Collecting<br/>moments<br/>through music</div>"
        f"</div>",
        unsafe_allow_html=True)


def player(title: str, artist: str = "", cover: str = "", played: str = "0:00",
           left: str = "-3:00") -> None:
    """The bar along the bottom: what is playing, and the words that go with it."""
    art = f"<img src='{cover}' alt=''/>" if cover else ""
    st.markdown(
        f"<div class='mb-player'>"
        f"<div class='mb-cover'>{art}</div>"
        f"<div class='mb-now'>"
        f"<div class='mb-song'>{html.escape(str(title))}</div>"
        f"<div class='mb-by'>{html.escape(str(artist))}</div>"
        f"<div class='mb-line'><span></span></div>"
        f"<div class='mb-times'><em>{html.escape(played)}</em><em>{html.escape(left)}</em></div>"
        f"</div>"
        f"<div class='mb-remembers'>Music<br/>Remembers.</div>"
        f"</div>",
        unsafe_allow_html=True)
