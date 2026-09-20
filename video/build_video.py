"""Cut the raw AI Studio screen recordings into the demo video, with captions.

Outputs in video/out/:
  memorybridge_demo_captioned.mp4  - captions burned in, silent audio track
  memorybridge_demo_clean.mp4      - same cut, no captions (for re-timing after voice-over)
  memorybridge_demo.srt            - captions for YouTube
  narration_script.md              - the captions as a read-aloud script with timestamps
"""
import glob
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(ROOT, "out")
WORK = os.path.join(OUT, "_work")
os.makedirs(WORK, exist_ok=True)

def clip(stamp):
    return glob.glob(os.path.join(RAW, f"*{stamp}.mp4"))[0]

TURBO = clip("21-39-04")      # TurboPrep process + Auto Model results
OVERVIEW = clip("21-46-02")   # model process overview
MODEL = clip("21-48-12")      # model process operator by operator
SCORES = clip("21-56-44")     # grid scoring results
APP = clip("22-08-32")        # the Streamlit app in Chrome
HOLDOUT = clip("22-27-51")    # holdout Performance (2) results
HOLDOUT_AUC = os.path.join(WORK, "holdout_auc_still.png")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "28.4", "-i", HOLDOUT, "-frames:v", "1",
                "-vf", "scale=1920:992,pad=1920:1080:0:0:color=black", HOLDOUT_AUC], check=True)

PAPER, INK, RED, GREY = "#f7f6f1", "#1f1b16", "#cc2018", "#6b645a"
FONT = "C:/Windows/Fonts/arial.ttf"
FONT_B = "C:/Windows/Fonts/arialbd.ttf"


def card(name, title, lines, kicker=None):
    img = Image.new("RGB", (1920, 1080), PAPER)
    d = ImageDraw.Draw(img)
    y = 150
    if kicker:
        d.text((140, y), kicker.upper(), font=ImageFont.truetype(FONT_B, 34), fill=RED)
        y += 70
    d.text((140, y), title, font=ImageFont.truetype(FONT_B, 76), fill=INK)
    y += 130
    d.rectangle([140, y, 340, y + 8], fill=RED)
    y += 60
    body = ImageFont.truetype(FONT, 42)
    for line in lines:
        if line == "":
            y += 30
            continue
        bold = line.startswith("*")
        d.text((140, y), line.lstrip("*"), font=ImageFont.truetype(FONT_B, 42) if bold else body,
               fill=INK if bold else GREY if line.startswith("(") else INK)
        y += 62
    path = os.path.join(WORK, f"{name}.png")
    img.save(path)
    return path


# (source, start_s, end_s, captions) - source is a video path or a card image path.
# Order follows the workflow as it was done: TurboPrep -> process setup -> manual model
# comparison -> Auto Model cross-check -> Random Forest chosen -> holdout test -> scoring.
SEGMENTS = [
    (card("title", "MemoryBridge", [
        "Music as a cue for autobiographical memory",
        "",
        "*Data science workflow in Altair AI Studio (RapidMiner)",
        "IEDC Summit 2026 - Data Science Contest",
        "",
        "(Not a medical product. Training data is SIMULATED.)",
    ]), 0, 9, [
        "This is MemoryBridge. It suggests songs from the years of a person's life that are most likely to bring back a memory.",
        "This video walks through the data science workflow built in Altair AI Studio.",
    ]),

    # --- Step 1: cleaning and preparation in TurboPrep ---
    (TURBO, 0, 22, [
        "Step 1: cleaning and preparation in TurboPrep. This process builds one master song table from three sources.",
        "Retrieve loads the Hindi, Malayalam and Million Song Dataset extracts.",
        "Generate Attributes adds tempo, loudness, key and popularity as missing where a source has no audio fields.",
    ]),
    (TURBO, 28, 34, [
        "Each Subprocess unifies column types: nominal to text, text to nominal, numbers to real.",
    ]),
    (TURBO, 62, 102, [
        "Append stacks the three sources into one table.",
        "Generate Attributes turns language codes into language names. Rare languages become 'Other'.",
        "Select, Rename and Reorder Attributes give the final 14 columns.",
        "Result: songs_master, 9,840 songs from 1950 to 2010. MSD 6,491, Hindi 2,000, Malayalam 1,349.",
        "Problems found by counting rows: '#' read as a comment broke 5 rows, and the export turned Malayalam into '???' until set to UTF-8.",
    ]),

    # --- Step 2: training data ---
    (card("data", "Training data", [
        "*No real listener reactions exist yet, so they are SIMULATED.",
        "300 synthetic listeners (English / Hindi / Malayalam), 40 songs each",
        "Train: 9,589 rows, 240 listeners, 43.0% yes",
        "Holdout: 2,400 rows, 60 listeners never used in training",
        "",
        "*Label: memory_triggered (yes / no)",
        "Features: age_at_release, in_age_10_30, years_outside_10_30,",
        "language_match, genre_match, artist_match, popularity",
    ], kicker="Step 2"), 0, 14, [
        "Step 2: training data. There are no real listener reactions yet, so a Python script simulates them for 300 listeners.",
        "The label is memory_triggered. The model gets seven features. A high score here proves the pipeline works, not that the idea works on real people.",
    ]),

    # --- Step 3: the RapidMiner process ---
    (OVERVIEW, 0, 25, [
        "Step 3: the RapidMiner process.",
        "Four rows: train with cross validation, test on unseen listeners, score demo profiles, score the full profile grid.",
    ]),
    (MODEL, 5, 42, [
        "Set Role: memory_triggered is the label, user_id is the batch attribute, one listener per batch.",
        "Select Attributes keeps only the 7 features.",
        "Replace Missing Values fills missing popularity with the training average, 63.633.",
        "The same value is used in every row of the process, so training and scoring see identical inputs.",
    ]),
    (MODEL, 88, 100, [
        "Cross Validation uses 'split on batch attribute': each listener is tested on a model that never saw them.",
        "A random row split would put the same listener on both sides and inflate every score.",
    ]),
    (MODEL, 48, 80, [
        "Inside Cross Validation: the learner on the training side, Apply Model and Performance on the testing side.",
        "Performance uses 'yes' as the positive class: accuracy, AUC, precision, recall, F-measure.",
        "Multiply sends one trained model to every Apply Model.",
        "So cross validation, the holdout test and the scores the app reads all come from the same model.",
    ]),

    # --- Step 4: model comparison ---
    (card("compare", "Comparing models", [
        "*Same process, learner swapped inside Cross Validation",
        "(split by listener, 240 listeners)",
        "",
        "Logistic Regression   AUC 0.790   accuracy 71.9%   recall 64.7%",
        "Random Forest           AUC 0.831   accuracy 74.1%   recall 80.5%",
        "Gradient Boosted       AUC 0.835   accuracy 73.8%   recall 58.3%",
        "(Always predicting 'no' gives 57.0% accuracy)",
    ], kicker="Step 4"), 0, 14, [
        "Step 4: comparing models. The same process was run with Logistic Regression, Random Forest and Gradient Boosted Trees inside Cross Validation.",
        "Random Forest AUC 0.831, Gradient Boosted Trees 0.835, Logistic Regression 0.790.",
    ]),
    (TURBO, 200, 210, [
        "The models were trained from TurboPrep: the Model button hands the prepared table to Auto Model.",
    ]),
    (TURBO, 210, 230, [
        "Auto Model trained 8 algorithm types on the same 7 features, 168 models in total.",
        "Classification error: Gradient Boosted Trees 23.9%, Random Forest 24.9%, Deep Learning 25.3%, the others 26.6 to 27.2%.",
        "ROC comparison of all eight model types.",
    ]),
    (TURBO, 272, 279, [
        "Random Forest weights and simulator: years_outside_10_30 matters most, then age_at_release and popularity.",
        "Auto Model score for Random Forest: accuracy 75.1%, AUC 82.8%, recall 78.7%.",
    ]),
    (TURBO, 316, 328, [
        "Statistics and correlations between the features and the label.",
        "Auto Model splits rows at random, so one listener can land in both train and test. It is a check, not the final test.",
    ]),
    (card("choice", "Why Random Forest", [
        "*Gradient Boosted Trees and Random Forest are close in both checks.",
        "AUC 0.835 vs 0.831: inside the +/- 0.073 spread across listeners",
        "",
        "*Recall for 'yes': Random Forest 80.5%  vs  GBT 58.3%",
        "Missing a song that would trigger a memory is the costly error.",
        "Showing one extra song that does not work costs a scroll.",
        "",
        "*Random Forest chosen: 100 trees, gain ratio, maximal depth 10",
    ], kicker="Decision"), 0, 13, [
        "Both checks put Gradient Boosted Trees and Random Forest close together. The AUC difference is inside the spread across listeners.",
        "Random Forest is chosen for recall: 80.5% against 58.3%. Missing a song that would trigger a memory is the costly error.",
    ]),

    # --- Step 5: holdout test ---
    (HOLDOUT, 0, 8, [
        "Step 5: holdout test on 60 listeners never used in training, 2,400 rows. Accuracy 72.1%.",
        "Class recall for 'yes': 74.8%, 722 of 965 real memory songs found.",
    ]),
    # The ROC screen is on for about a second in a variable-frame-rate clip, so hold a still of it.
    (HOLDOUT_AUC, 0, 8, [
        "AUC 0.804. AI Studio shows it with 'no' as the positive class; the ROC AUC is the same either way.",
        "Ranked by the model, each listener's top 10 songs hit 74.2%, against 63.2% for the formula and 40.2% at random.",
    ]),

    # --- Step 6: scoring ---
    (MODEL, 240, 272, [
        "Step 6: scoring. Rows 3 and 4 apply the same model to new data.",
        "Retrieve grid_candidates: 27 stand-in profiles (3 languages x birth years 1935 to 1975) x 9,840 songs = 265,680 rows.",
        "Write CSV saves predictions_grid, predictions_demo and predictions_holdout.",
        "The app reads predictions_grid to rank songs for a real listener.",
    ]),
    (MODEL, 290, 298, [
        "Running the process.",
    ]),
    (SCORES, 45, 60, [
        "265,680 scored rows. Each gets prediction(memory_triggered) and confidence(yes).",
    ]),
    (SCORES, 121, 137, [
        "confidence(yes) runs from 0.024 to 0.854.",
        "23,809 rows are predicted yes and 241,871 no.",
    ]),
    (SCORES, 158, 168, [
        "Malayalam profile: songs released before the listener was born get confidence(yes) near 0.09.",
    ]),
    # --- Step 7: the app using the scores ---
    (APP, 30, 43, [
        "Step 7: the app. The listener picks a period of their life.",
        "Childhood, college, early adulthood, family and career.",
    ]),
    (APP, 52, 64, [
        "Music Cue ranks songs for that period, here Malayalam film songs from a listener born in 1960.",
        "Each song says why it was chosen: the year, the age it fits, the language and the genre.",
    ]),
    (APP, 98, 110, [
        "The listener records what the song brings back, by speaking it in Malayalam, Hindi or English.",
        "Nothing is saved until they keep it, and the app never writes the memory for them.",
    ]),
    (APP, 355, 365, [
        "My Life in Music: the memories they kept, in the order they happened.",
    ]),
    (card("design", "What the output changed", [
        "Ranking all 9,840 songs, the model put 1-2 wrong-language songs",
        "into some top-10 lists.",
        "(A Malayalam profile got an English song at 0.705, above Malayalam songs at 0.685.)",
        "",
        "*Fix: a two-stage recommender",
        "1. The baseline formula picks 200 candidates (era, language, genre, artist, popularity)",
        "2. The Random Forest ranks those 200 by confidence(yes)",
        "",
        "*Result: 100% language match in the top 10 for all 5 test profiles",
    ], kicker="Finding"), 0, 16, [
        "Looking at the output, not just the metric, found a problem: some top-10 lists had songs in the wrong language.",
        "The fix is two stages. The formula picks 200 candidates, and the Random Forest ranks them. Language match in the top 10 went to 100%.",
    ]),
    (card("end", "Limits and next steps", [
        "Trained on SIMULATED reactions: this proves the pipeline, not the idea.",
        "The grid matches language and birth year only.",
        "Scoring is a batch step in AI Studio, not a live service.",
        "",
        "*Next: collect real reactions from real listeners and retrain.",
        "The app already stores them in the training format.",
        "",
        "(Not a medical product. It never invents a memory.)",
    ]), 0, 12, [
        "Limits: the model learned from simulated reactions, and scoring is a batch step.",
        "Next: collect real reactions from real listeners and retrain. Thank you.",
    ]),
]


def run(cmd):
    subprocess.run(cmd, check=True)


def fmt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# Sources differ in height (992 vs 1020), so scale by width and pad to 1080.
VF = "fps=30,scale=1920:-2,pad=1920:1080:0:0:color=black,format=yuv420p"
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-an"]

parts, subs, script = [], [], []
t = 0.0
for i, (src, a, b, caps) in enumerate(SEGMENTS):
    dur = b - a
    part = os.path.join(WORK, f"seg{i:02}.mp4")
    if src.endswith(".png"):
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(dur), "-i", src,
             "-vf", "fps=30,format=yuv420p", *ENC, part])
    else:
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(dur), "-i", src,
             "-vf", VF, *ENC, part])
    parts.append(part)
    # Encoded length can differ slightly from the request; time captions from the real length.
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", part],
        capture_output=True, text=True, check=True).stdout)

    # Split the segment's time across its captions by word count.
    words = [len(c.split()) for c in caps]
    total = sum(words)
    ct = t
    for c, w in zip(caps, words):
        span = dur * w / total
        subs.append((ct, ct + span - 0.05, c))
        ct += span
    script.append((t, caps))
    t += dur

concat = os.path.join(WORK, "list.txt")
with open(concat, "w") as f:
    f.writelines(f"file '{p.replace(os.sep, '/')}'\n" for p in parts)

clean = os.path.join(OUT, "memorybridge_demo_clean.mp4")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", concat,
     "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
     "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", clean])

srt = os.path.join(OUT, "memorybridge_demo.srt")
with open(srt, "w", encoding="utf-8") as f:
    for n, (a, b, c) in enumerate(subs, 1):
        f.write(f"{n}\n{fmt(a)} --> {fmt(b)}\n{c}\n\n")

style = ("FontName=Arial,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00161B1F,"
         "BackColour=&H40161B1F,BorderStyle=4,Outline=1,Shadow=0,MarginV=8,MarginL=40,MarginR=40")
# The subtitles filter needs a path without drive-letter colons, so run from OUT.
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-i", "memorybridge_demo_clean.mp4",
     "-vf", f"subtitles=memorybridge_demo.srt:force_style='{style}'",
     "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "copy",
     "memorybridge_demo_captioned.mp4"], check=True, cwd=OUT)

with open(os.path.join(OUT, "narration_script.md"), "w", encoding="utf-8") as f:
    f.write("# Voice-over script\n\nRead each line when its caption appears. "
            f"Total length {int(t // 60)}:{int(t % 60):02}.\n\n")
    for start, caps in script:
        f.write(f"**{int(start // 60)}:{int(start % 60):02}**\n\n")
        f.writelines(f"- {c}\n" for c in caps)
        f.write("\n")

print(f"done: {len(SEGMENTS)} segments, {t:.0f} s ({int(t // 60)}:{int(t % 60):02})")
