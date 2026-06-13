A small background tool. Cross-platform (Windows/Linux first, maybe macOS later).

The idea: you're deep in something — debugging, research, reading — and you hit a moment worth keeping. A weird error, a suspicious line of code, a page that might matter later. You don't want to stop and write it up. You just want to grab it and say what it is, out loud, in two seconds, and get back to work.

So: a global hotkey. Configurable, but the natural default is something dumb and fast — triple-tap spacebar, or similar. On trigger:

1. Screenshot of the active window (or full screen, configurable).
2. Immediately start recording from the microphone.
3. You say a short voice note: "this is the auth bug", "save this for the investigation", "found it, line 42 in parser.py".
4. Recording stops on silence, or another key press, or after a max duration.

The screenshot + audio clip (+ maybe active window title / URL if it's a browser) get bundled as one "capture" and pushed into a session — a running collection of evidence for whatever you're currently researching or building. Optionally the voice note gets transcribed (local whisper or similar) so the session ends up as a searchable timeline: screenshot, transcript, timestamp, source app/URL.

Later you open the session and have a chronological trail of "what I was looking at and why I cared", instead of fifty random screenshots in a folder with no context.

---

### Why

Developers (and researchers in general) already do half of this manually — alt+tab, snip, paste into Notion/Obsidian, then try to remember why it mattered. This collapses that into one gesture and offloads the "why" to your own voice, which is faster than typing and easier to do without breaking flow.

### Rough shape

- Background agent / tray app, cross-platform (Electron, Tauri, or a Python service + native hotkey hook).
- Global hotkey listener (configurable trigger, not just triple-spacebar).
- Screenshot capture (active window / region / full screen).
- Mic capture, short clips, local-first storage.
- Optional speech-to-text (local model for privacy, or pluggable to an API).
- Browser extension or OS-level hook to grab the current URL/page title when relevant.
- "Sessions" as the organizing unit — each capture appends to the active session (a folder, a local DB, or synced to a note-taking tool).
- Export/share a session as a simple report: list of captures with screenshot + transcript + timestamp + source.

### Open questions

- How much should run locally vs. sync somewhere? Privacy matters since screenshots/audio can contain sensitive stuff.
- Session lifecycle: how do you start/stop/switch sessions without breaking the "no friction" promise?
- Hotkey conflicts across OSes/apps — triple-tap on a key like space is risky (typing while thinking). Maybe a modifier combo is safer, but the "no hands off keyboard" feel is the point.
