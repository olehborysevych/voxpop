## Ant Lab

So we have a kitchen table. Ordinary. Crumbs, occasional stains, the usual.

Every night ants come to explore it. Looking for food. They have their routes, their scouts, their logistics. All of this is happening quietly at 2am while I sleep.

Tonight I left a jar of honey on the table. Two or three ants got stuck and drowned in it. I fished them out with a spoon, left them on a small plate. Now the rest are eating their fallen comrades and some still run around doing their thing.

And I thought: what if I just... watched. Properly.

---

### The Setup

A camera above the table. Fixed angle, good night vision or IR. Running all night.

A neural net behind it. Trained to detect and track individual ants. Their positions, velocities, directions. Timestamps on everything.

Data goes somewhere. A database. Time series of movement. Heatmaps by hour. Trails.

That's already interesting on its own.

---

### The Experiment Part

But here's where it gets better: I co-design experiments with an AI.

Put out different food sources at different positions. See how long it takes a scout to find each. See how the trail forms. How many ants switch once a second source is discovered.

Build small obstacles. A ring of tape. A gap they have to cross. A maze made of matchboxes. See how they solve it, or don't.

Vary the lighting. Temperature. Humidity. Log all of it.

The AI suggests next experiments based on what the data showed last night. I set them up before going to bed. Wake up to results.

---

### What This Actually Is

It's a citizen science rig for collective intelligence research that costs maybe €30 in hardware and runs on a Raspberry Pi.

Ant colonies are one of the best-studied models for emergent intelligence, stigmergy, distributed decision-making. There's serious academic work here. But also: it's just fascinating to watch.

The kitchen table is already the lab. I just need to add the cameras and start recording.

---

### What's Needed

- Camera (Raspberry Pi HQ cam + IR LEDs, or a cheap USB cam with decent low-light)
- Small compute (Pi 4 or Pi 5 is fine)
- Object detection model — something like YOLOv8 or a small custom model fine-tuned on ant images
- Tracking algorithm — ByteTrack or SORT for multi-object tracking between frames
- Storage + simple visualization (SQLite + a web dashboard or even just CSVs + matplotlib)
- A way to log experiment conditions (what food, where, what obstacles)

The AI co-pilot part can just be Claude or GPT getting the nightly summary and suggesting what to try next.

---

### Why This Is Interesting Beyond Ants

The same rig — camera, neural net, tracking, AI-suggested experiments — works on any tabletop biology. Slime mould. Beetles. Termites. Seeds germinating. You build it once.

And the loop of: *observe → data → AI analyzes → suggests experiment → observe again* is a general framework for low-cost autonomous science. The ants are just a great first subject because they show up for free and need no care.

---

*This is either a fun weekend project or the beginning of something genuinely useful. Probably both.*
