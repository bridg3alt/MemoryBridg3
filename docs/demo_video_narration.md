# What to say in the demo video — word for word

Read this out loud. Simple sentences on purpose. Pause at every full stop.

Total speaking time: about 11 minutes at a normal pace. Do not rush.

`[SCREEN: ...]` tells you what should be visible. `[DO: ...]` is an action, not something you say.

---

## 1. Opening — 30 seconds

`[SCREEN: first PPT slide — project title, your name, your college]`

> Hello. My name is ____ and I am from ____ college.
>
> My project is called MemoryBridge.
>
> MemoryBridge is a music app that helps a person remember their own life.
>
> In this video I will show you four things. The problem I wanted to solve. The data I used.
> The machine learning workflow I built in RapidMiner. And the working app at the end.

---

## 2. The problem — 1 minute

`[SCREEN: PPT problem slide]`

> Here is the idea behind the project.
>
> Most people have very strong memories attached to music. The songs you heard when you were
> a teenager, or in your twenties, stay with you for the rest of your life. You hear one of
> those songs today and suddenly you remember a place, or a person, or a day.
>
> So my question was this. If I know a person's birth year, their language, and the kind of
> music they like, can I pick songs that will bring back their memories?
>
> And once a song brings back a memory, can the app help them write that memory down and
> keep it?
>
> One important thing before I continue. This is not a medical product. It does not diagnose
> any illness. It does not treat anything. It does not claim to bring back lost memory. And
> it never invents a memory. The only story in the app is the story the user writes
> themselves.

---

## 3. The data — 1 minute 30 seconds

`[SCREEN: docs/dataset_notes.md, then scroll data/processed/songs_master.csv]`

> Now let me show you the data.
>
> I used five sources. The Million Song Dataset, which has one million songs. A genre label
> file for those songs. The Billboard Hot 100 charts, for popularity. A Hindi film music
> dataset with fifty seven thousand songs. And a Malayalam song dataset with twenty six
> thousand songs.
>
> I added two Indian datasets on purpose. The Million Song Dataset is mostly English music.
> If I want this app to work for a person in Kerala who was young in the nineteen sixties,
> English songs alone are useless to them.
>
> I also used the MusicBrainz API to find the country and the language of each artist. I
> found three thousand five hundred and two artists out of three thousand five hundred and
> twenty five. Language coverage was almost one hundred percent.
>
> `[DO: point at the file]`
>
> After cleaning and joining everything, this is my final table. Nine thousand eight hundred
> and forty songs. Fourteen columns. Years from nineteen fifty to two thousand and ten.
>
> I had two problems with this data and I want to be honest about both.
>
> First, songs with both a year and a genre are mostly from the two thousands. Very few from
> the nineteen fifties. So I did not take a random sample. I took the same number of songs
> from every decade, so old listeners are not ignored.
>
> Second, the Hindi and Malayalam datasets have no audio measurements. No tempo, no loudness.
> So those columns are empty for about three thousand rows, and I could not build features
> from them.

---

## 4. Data preparation in TurboPrep — 1 minute

`[SCREEN: AI Studio, open rapidminer/turboprep_songs_master.rmp]`

> This is my data preparation, built in TurboPrep inside Altair AI Studio.
>
> It has four parts.
>
> Part A cleans the Hindi songs. Two thousand rows at the end.
>
> Part B cleans the Malayalam songs. One thousand three hundred and forty nine rows. I had to
> remove one hundred and fifty one rows because the title was a website placeholder, not a
> real song name.
>
> Part C joins the Million Song Dataset with the MusicBrainz artist information. Six thousand
> four hundred and ninety one rows.
>
> Part D puts all three together and makes the language column consistent, because the
> sources used fifteen different language codes.
>
> Two things went wrong here and I want to mention them, because fixing them is part of the
> work.
>
> The CSV import treats the hash symbol as a comment. That silently broke five rows, and I
> only found it by counting the rows after every step.
>
> And my first export turned all the Malayalam text into question marks, because it used the
> system encoding. I fixed it by setting the encoding to UTF-8 in preferences.

---

## 5. The features and an honest limitation — 1 minute

`[SCREEN: docs/simulation_assumptions.md]`

> Now, to train a model I need to know which songs actually brought back a memory for a real
> person. I do not have that data. Nobody has given me their reactions yet.
>
> So I simulated it, and I am being completely open about this.
>
> I wrote a script that creates three hundred imaginary listeners. Each one has a birth year,
> a language, favourite genres and favourite artists. For each song shown to them, the script
> decides yes or no using rules from memory research. The strongest rule is age. A song
> released when the listener was between ten and thirty is much more likely to trigger a
> memory.
>
> This gives me nine thousand five hundred and eighty nine training rows from two hundred and
> forty listeners, and I kept sixty listeners completely aside for testing.
>
> The model uses seven features. The listener's age when the song was released. Whether that
> age is inside the ten to thirty window. How far outside it is. Whether the language matches.
> Whether the genre matches. Whether the artist matches. And the song's popularity.
>
> So please understand what this proves and what it does not prove. It proves my whole
> pipeline works from raw data to a running app. It does not prove the idea works on real
> people. To prove that, I need real listeners, and that is my next step.

---

## 6. The architecture — 1 minute 30 seconds

`[SCREEN: the architecture slide in the PPT — the diagram below]`

Trace the boxes with your mouse as you speak. Do not read the box names out. Tell the story of
one row of data moving through them.

```text
 RAW SOURCES                 PREPARATION              MODELLING                 APPLICATION
 ┌──────────────┐
 │ Million Song │─┐
 │ Dataset      │ │        ┌──────────────┐
 ├──────────────┤ │        │  TurboPrep   │
 │ tagtraum     │ ├──────► │  clean, join │────► songs_master.csv ─┐
 │ genres       │ │        │  standardize │          9,840 songs   │
 ├──────────────┤ │        └──────────────┘                        │
 │ Billboard    │ │         (Altair AI Studio)                     │
 │ Hot 100      │ │                                                ▼
 ├──────────────┤ │                                   ┌─────────────────────────┐
 │ Hindi film   │ │                                   │ Python: simulate        │
 │ metadata     │ ├──► Python: download, sample,      │ 300 listeners, 7        │
 ├──────────────┤ │    clean, MusicBrainz API         │ features, yes/no label  │
 │ Malayalam    │─┘                                   └───────────┬─────────────┘
 │ songs        │                                                 │
 └──────────────┘                                     interactions_train.csv
                                                                  │
                                                                  ▼
                                                   ┌──────────────────────────────┐
                                                   │ RapidMiner MemoryBridge_model│
                                                   │  cross validation, split on  │
                                                   │  user_id                     │
                                                   │  LogReg · RandomForest · GBT │
                                                   │  → Random Forest chosen      │
                                                   └───────────┬──────────────────┘
                                                               │ trained model
                                                               ▼
                                                   ┌──────────────────────────────┐
                                                   │ Apply Model on the profile   │
                                                   │ grid: 27 profiles × 9,840    │
                                                   │ songs = 265,680 rows         │
                                                   └───────────┬──────────────────┘
                                                               ▼
                                                     predictions_grid.csv
                                                               │
                                                               ▼
                                              ┌────────────────────────────────────┐
                                              │ Streamlit app  (ranking.py)        │
                                              │  stage 1: baseline picks top 200   │
                                              │  stage 2: Random Forest ranks them │
                                              │  → top 10 songs shown              │
                                              └───────────┬────────────────────────┘
                                                          ▼
                                                  SQLite: the user's memory
```

> Before I run the workflow, let me show you how the whole system fits together, so you can
> see where each tool does its job.
>
> On the left are my raw sources. Python downloads them, takes the sample, and calls the
> MusicBrainz API for artist country and language.
>
> Everything then goes into TurboPrep inside AI Studio. That is where the cleaning, the
> joining and the standardising happen, and it produces one master table of nine thousand
> eight hundred and forty songs.
>
> Python then builds the training data from that table, because I have no real listener
> reactions yet.
>
> That training data goes into my RapidMiner process. This is where the machine learning
> happens. Cross validation, three models compared, and the Random Forest chosen.
>
> The trained model is then applied to a grid of profiles. Twenty seven stand-in profiles,
> every one of my nine thousand songs scored for each of them. That is two hundred and sixty
> five thousand predictions, written out as one CSV file.
>
> And the app reads that file. When a real person opens the app, it finds the closest profile
> in the grid, takes the model's confidence scores from there, and uses them to order the
> songs.
>
> So, to be exact about one thing: the model is not running live inside the app. It is trained
> and scored in AI Studio, and the app reads the scores. That is batch scoring, and it is
> the normal way AI Studio is used in production too.
>
> The last box is the user's own memory, saved in a small database on the machine.

---

## 7. The RapidMiner workflow, running live — 3 minutes

`[SCREEN: AI Studio, open rapidminer/MemoryBridge_model.rmp, zoom in]`

**Before you record this block:**
- Open AI Studio, load the process, and set the zoom so operator names are readable at 1080p.
- Run the process once beforehand so the repository is warm and the Results tabs already exist.
- Decide what you run live. Row 1 (cross validation, three models, 9,589 rows) takes a couple of
  minutes. Row 4 (the grid, 265,680 rows) takes several. **Run row 1 live, and cut the waiting
  time out in editing** — say "this takes about two minutes, I have cut the wait" over the cut.
  Do not run row 4 on camera; show its saved results instead.

> This is my main RapidMiner process. Everything you saw in the middle of that diagram is on
> this canvas.
>
> `[DO: point at the cross validation operator]`
>
> I start with cross validation, but not the normal kind. I set it to split on the batch
> attribute, and the batch is the user id.
>
> This matters a lot. Normally cross validation splits rows randomly. But my rows are grouped
> by listener. If the same listener appears in training and in testing, the model has already
> seen that person's taste and my score would be a lie. Splitting by user id means every
> listener is tested by a model that has never seen them before.
>
`[DO: press the blue Play button and let it run on camera]`

> Let me run it now so you can see it work.
>
> `[DO: while it runs, point at the operators lighting up one after another]`
>
> You can see the process moving through the operators. It reads the training data, sets the
> roles, selects the seven features, fills the missing popularity values, and then runs the
> cross validation for all three models.
>
> `[DO: cut the waiting time here in editing]`
>
> This takes about two minutes on my machine, so I have cut the waiting out of the video.

`[DO: the Results tabs open by themselves when the run finishes]`

> And here are the results.

> `[DO: open the performance tab for each model in turn]`
>
> I compared three models.
>
> Logistic regression got an AUC of zero point seven nine.
>
> Random Forest got zero point eight three.
>
> Gradient Boosted Trees got zero point eight three five.
>
> For comparison, if I simply say no to every song, I would be correct fifty seven percent of
> the time. So all three models are learning something real.
>
> I chose the Random Forest. Let me explain why, because it did not have the highest AUC.
>
> The difference between Random Forest and Gradient Boosted Trees is smaller than the error
> bars, so I treat them as tied. But look at recall. Random Forest finds eighty percent of the
> songs that would have triggered a memory. Gradient Boosted Trees finds only fifty eight
> percent.
>
> For this app, missing a song that would have worked is the expensive mistake. Showing one
> extra song that does not work costs the user nothing. They just scroll past it. So I want
> high recall, and that is the Random Forest.
>
> `[DO: show the holdout row of the process]`
>
> Then I tested it on the sixty listeners the model had never seen. AUC zero point eight
> zero four.
>
> And here is the number I care about most. For each listener I took the top ten songs and
> checked how many were real yes answers.
>
> Random Forest: seventy four percent.
>
> My simple scoring formula without machine learning: sixty three percent.
>
> Random order: forty percent.
>
> So the model is clearly adding value over the formula.
>
> `[DO: open the Random Forest model result, switch to the tree or description view, scroll one tree]`
>
> This is the model itself. You can open any tree and read the rules it learned. The first
> splits are almost always on the listener's age when the song was released, which is exactly
> what the memory research predicts. So the model is not a black box to me. I can check that
> it learned something sensible.
>
> `[DO: scroll to row 4 of the process, point at the Multiply operator and its wires]`
>
> And this last row is the scoring step. The trained model comes out of cross validation, goes
> through this Multiply operator, and the same trained model is sent to every Apply Model in
> the process. That way the holdout test, and the file the app reads, all use one identical
> model.
>
> This row writes the two hundred and sixty five thousand predictions to a CSV file. It takes
> a few minutes, so I have already run it, and that file is what the app loads.

---

## 8. The mistake that changed my design — 45 seconds

`[SCREEN: results/model_comparison.md]`

> Now the most interesting part of the project.
>
> When I let the Random Forest rank all nine thousand songs by itself, I found something
> wrong. For a Malayalam listener, an English song appeared in the top ten, above Malayalam
> songs from the right period.
>
> I looked into why. During training, most of the songs shown to each listener were already
> good matches. So the model almost never saw a wrong language song with low popularity. In
> that area it is simply guessing.
>
> So I changed the design. Now it works in two stages.
>
> Stage one is my simple formula. It picks two hundred songs that are the right era, right
> language, right genre. Stage two is the Random Forest, which ranks those two hundred and
> decides which ten you see first.
>
> After this change, all ten songs are in the right language for every test profile. This is
> also how real recommender systems work, and I only found it because I looked at the actual
> output instead of only the accuracy number.

---

## 9. The live app — 1 minute 15 seconds

`[SCREEN: terminal, then the Streamlit app]`

> Finally, let me show you the working app. It is built in Python with Streamlit, and it
> stores everything in a small SQLite database.

`[DO: start the app, then create a profile]`

> I enter a birth year, a language and a few favourite genres.
>
> `[DO: go to the song suggestions page]`
>
> And here are the songs chosen for this person.
>
> `[DO: point at the grey line under the songs]`
>
> Look at this line here. It says: chosen for you by RapidMiner Random Forest. That means
> these songs are not coming from my formula. They are coming from the model I just showed
> you, scored in AI Studio and loaded into this app.
>
> `[DO: open one song, capture a memory]`
>
> When a song means something to the person, they write down what it reminds them of. They
> can type it, or they can speak it, because speaking is easier for an older person.
>
> `[DO: open the timeline page]`
>
> And this is the timeline. Every memory is filed under the part of their life it belongs to.
> Childhood. School. College. So they can come back later and read their own life, told
> through their own music.

---

## 10. Closing — 45 seconds

`[SCREEN: last PPT slide]`

> To finish, here are my honest limitations.
>
> The model is trained on simulated listeners, not real ones. My next step is to collect
> thirty to sixty real reactions from real people and train it again.
>
> The scoring is a batch job I run by hand in AI Studio. It is not a live service yet.
>
> And the matching uses language and birth year. Genre and artist are handled by the first
> stage, not the model.
>
> But the full pipeline works. Raw data, cleaning in TurboPrep, feature engineering, three
> models compared properly, a chosen model, a real evaluation, and a working app that a person
> can actually use.
>
> Thank you for watching.

---

## Tips for speaking

- Read this out loud once before recording. Change any sentence that feels strange in your mouth.
- Numbers are the hard part. Say them slowly. It is fine to look at the screen and read them.
- If you stumble, stop, stay silent for two seconds, and say the sentence again. Cut it later.
- Do not apologise on camera. Do not say "sorry, this is not perfect". Say what it does and
  say what its limits are. That is confidence, not apology.
- Silence while you click is fine. Do not fill it with "umm".
