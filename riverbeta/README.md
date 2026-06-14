## Riverbeta

I have a kayak trip video. Mine, or someone else's — doesn't matter. There's a guy on camera (sometimes me) paddling down a river, talking. "Watch out, there's a weir after this bend." "Big rock river-left, stay right." "Portage coming up, take out before the bridge."

All of that is gold. It's *beta* — the kayaking term for route intel: where the obstacles are, how to read them, what to avoid. And it's buried inside a 40-minute video that nobody is going to scrub through before they put in on the same stretch of river.

I want to pull it out and turn it into a map.

---

### The Pipeline

**1. Get the video.** Download it (yt-dlp). Keep the video and split out the audio track.

**2. Transcribe and translate.** Run the audio through speech-to-text with word/segment-level timestamps (Whisper or similar). My commentary is a mix of Ukrainian, Russian, and English depending on the day — so translate to a common language for analysis, but keep the original text alongside it. Every line of transcript now has a `[start, end]` timestamp.

**3. Find the obstacles.** Scan the transcript for the vocabulary of river hazards: weir, rapid, eddy, strainer, portage, "river-left/river-right", grade mentions, hole, sieve, undercut. Keyword spotting gets the candidates; an LLM pass over each candidate sentence (plus a bit of surrounding context) pulls out a structured note: `{ timestamp, hazard_type, side, severity, note }`. This is the core "comment" layer.

**4. Watch the video without watching it.** Sample frames at a fixed rate (1 fps, say) and reduce each one to a color fingerprint — a small histogram or downsampled pixel grid. Stack these over time and you get a "pixel color map": a compressed visual timeline of the whole trip. Green/brown river, gray rock, white foam at a rapid, dark under a bridge — the map shows where the *visual character* of the trip changes, cheaply, without running anything heavy frame-by-frame.

**5. Find plan changes.** Diff consecutive frames (or their histograms) to detect cuts and big shifts in framing — camera angle changes, a new shot setup, "and now here's the weir" moments. These often cluster right around the hazard mentions found in step 3, which is itself a useful signal: narration + a visual change at the same timestamp is a strong "this matters" marker.

**6. Pick the pictures.** For each hazard/comment from step 3, look at the frames near its timestamp (especially near a detected plan change) and pick the best one or two to illustrate it — sharpest, least motion-blurred, most representative of the color map's "interesting" segment. Now every comment on the map has a thumbnail.

**7. Build the map.** Output: a timeline/storyboard — thumbnail, timestamp (linking back to the source video), original-language quote, translated note, hazard tag. If the river/put-in/take-out can be identified (from the title, description, or just named landmarks in the narration), pin the same points on an actual geographic map. Even without geocoding, the timeline storyboard alone is the useful artifact — a scannable "beta sheet" for the run.

---

### Rough Stack

- **Download:** `yt-dlp`
- **Audio/frame extraction:** `ffmpeg`
- **Transcription + translation:** `faster-whisper` (timestamps come for free; translate task or a separate MT pass for uk/ru → en)
- **Hazard extraction:** keyword spotting over the transcript, then an LLM pass (Claude) for structured extraction per candidate sentence
- **Frame fingerprinting / color map:** `ffmpeg` frame sampling + numpy/PIL histograms
- **Scene/plan-change detection:** histogram-delta thresholding, or `PySceneDetect` if it needs to be more robust than a quick diff
- **Output:** a static HTML report — timeline of cards (thumbnail + timestamp + quote + note), maybe with an embedded color-map strip as a visual scrollbar; geographic map view as a stretch goal

---

### Implementation

A first working version lives in this folder as a Python CLI, `riverbeta`. Everything runs locally — no cloud APIs:

- **Download:** `yt-dlp` + `ffmpeg` (external binaries, must be installed separately)
- **Transcription + translation:** `faster-whisper` running a local model (CPU by default, `--device cuda` if you have a GPU)
- **Hazard extraction:** pure regex/keyword matching over the transcript (English/Ukrainian/Russian terms for weirs, rapids, strainers, portages, eddies, sieves, undercuts, holes)
- **Color map + scene changes:** `numpy`/`Pillow` only

Install:

```bash
cd riverbeta
pip install -e .
```

Run the whole pipeline:

```bash
riverbeta run "https://www.youtube.com/watch?v=XXXX" --out output/my-trip
```

Or run each step on its own (useful for iterating, e.g. re-running `hazards` after tweaking the keyword list without re-transcribing):

```bash
riverbeta fetch "https://www.youtube.com/watch?v=XXXX" --out output/my-trip
riverbeta transcribe --out output/my-trip --model small
riverbeta frames --out output/my-trip --fps 1
riverbeta colormap --out output/my-trip
riverbeta hazards --out output/my-trip
riverbeta report --out output/my-trip
```

This writes `output/my-trip/report.html` — a timeline of cards, each with a thumbnail, a link back to the video at the right timestamp, the original-language quote, and its English translation, plus a `colormap.png` showing the visual fingerprint of the whole video.

Run the test suite (covers hazard extraction, color map, scene detection, report rendering — the parts that don't need a real video):

```bash
pip install pytest
pytest
```

---

### Open Questions

- **Geocoding.** Most paddling videos have zero GPS data. The title/description usually names the river and put-in/take-out — that plus named landmarks in the narration ("after the old mill", "the bridge at X") might be enough for rough pins, but it's manual-ish.
- **"Plan change" vs. just a cut.** Need to tell apart a deliberate new shot ("now watch this rapid") from an incidental jump cut (skipped boring paddling). The narration timestamps probably do more disambiguating work than the video diff alone.
- **Language handling.** Want to keep the original-language quote (the actual warning as spoken) next to the translation, not just the translation — the original phrasing sometimes carries info ("полий" vs "завал" are different hazard types that a generic translation might flatten).
- **Beyond kayaking.** Same pipeline — narrated POV video → transcript with timestamps → hazard/landmark extraction → illustrated timeline — works for hiking trail reports, climbing route descriptions, road trip vlogs with "don't take this turn" warnings. The kayak trip is just the first, most concrete case.

---

*The video already has all the information. This is just making it skimmable.*
