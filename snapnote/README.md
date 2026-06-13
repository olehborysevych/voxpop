A background capture tool, but the real point is the local triage agent behind it. Cross-platform (Windows/Linux first).

### The gesture stays the same

Configurable global hotkey (triple-tap space, or a safer modifier combo). On trigger:

1. Screenshot of the active window / region.
2. Start recording from the mic.
3. You say what this is: "auth bug, add to the payments investigation", "new thing, customer keeps getting logged out", "ticket: dropdown is broken on mobile".
4. Recording stops on silence or a second key press.

### What changes: there's a local agent in the loop

The capture doesn't just get filed — it gets *understood*, immediately, on-device.

A small local model (something Gemma-class, edge-sized, runs on a work laptop without a GPU farm) gets the screenshot + transcribed audio and does the first pass:

- OCR / read the screenshot — is this a code editor, a browser, an email, a chat, a Jira board, a log file?
- Transcribe + parse the voice note — what's the intent? A note? An action item? A new investigation? An append to an existing one?
- Match against existing investigations by keywords/context/recent activity, or decide this is the start of a new one.
- Produce a small structured record: `{ investigation_id (existing | new), summary, action_items[], source_type, tags }`.

This is the "agent that captures what I see and think" — it's not trying to be smart, it's trying to be a fast, private, always-on triage layer that turns a screenshot + a sentence into a filed, categorized note.

### Investigations as the organizing unit

- Each investigation = a folder/local DB entry with a running log of captures (screenshot, transcript, structured record, timestamp, source app/window/URL).
- New capture either appends to an existing investigation (matched by the local model) or starts a new one.
- Investigations can be marked private — excluded from any escalation/export, stays local only.
- Quick review/merge UI: rename investigations, re-file a capture that got misclassified, merge two investigations the local model split by mistake.

### Escalation: when the local agent isn't enough

The local model is for triage, not for doing the work. When an investigation needs real reasoning — debugging, drafting a fix, writing up a ticket — the tool hands off to a heavier agent:

- Launches a **Claude Code CLI** session (or hits an API) scoped to that investigation's context — its captures, transcripts, summaries.
- Model selection is deliberate: local Gemma for triage (free, private, instant), Claude Code for anything that needs real reasoning, with model choice (Haiku/Sonnet/Opus) picked based on task complexity to manage token cost.
- This can be manual ("escalate this investigation") or automatic (the local agent flags an investigation as "ready" — enough context gathered, clear action items — and kicks off a session).

### Output: tickets, not just notes

- A skill/command that takes an investigation and drafts a Jira ticket (title, description, screenshots, action items) via the corporate AI account's CLI/API — so a quick voice dump during the day becomes a filed ticket without manually writing it up later.
- Same pattern could extend to other corporate tools (Confluence page, Slack message to a channel) as additional "skills" the escalation agent can call.

### Privacy / on-prem constraints (this is a work tool)

- Screenshots and audio never leave the machine for the triage step — local model only.
- Private investigations stay fully local, never escalated, never exported.
- Escalation to Claude Code / corporate AI is opt-in per investigation (or auto, but only for non-private ones), and only the relevant text/summaries get sent — not raw screenshots/audio unless needed.
- Token usage for Claude Code sessions should be visible/budgeted, since this could be invoked often throughout the day.

### Rough stack

- Tray app / background service: Tauri or a lightweight Python service + native global-hotkey hook (cross-platform).
- Screenshot + mic capture: OS-native APIs.
- Local model runtime: Ollama or llama.cpp running a Gemma-class model (vision + text) for OCR/classification/matching.
- Local storage: SQLite + flat files for screenshots/audio per investigation.
- Escalation: shell out to `claude` CLI (Claude Code) with investigation context piped in; ticket-creation skill calls corporate Jira CLI/API.
- Simple local UI (web view or native) for browsing investigations, reviewing/merging, and triggering escalation manually.

### Open questions

- How good does a small local model need to be to reliably tell "new investigation" vs "append to existing"? Probably needs a fallback: if confidence is low, ask (a quick popup) rather than guess.
- What's the trigger for auto-escalation — capture count? explicit "investigate this" keyword in the voice note? time since last update?
- How much history/context gets passed to Claude Code per session — full transcript log, or a rolling summary to keep token usage sane?
- Corporate AI CLI integration: what auth/skill model does it expose, and can it be scripted the same way as Claude Code?
