# Architecture

Decisions for v1, with the reasoning so future-us remembers why.

## Shape: thin clients around one always-on daemon

```
Capture clients (thin, swappable)
  • Desktop tray app: global hotkey → screenshot + mic + active window/URL
  • (later) ESP32 device: button → mic (+ optional cam frame), LAN POST
  • (later) browser extension, phone
        │
        │  capture = { image?: bytes, audio?: bytes, text?: string,
        │              source_meta: { app, window_title, url?, device_id } }
        │
        │  HTTP to localhost (desktop) / LAN (device)
        ▼
snapnoted — core daemon, the actual product
  • POST /capture — ingest, persist raw capture
  • STT (whisper.cpp) on audio
  • triage: local vision+text model reads image + transcript →
      { investigation_id (existing|new), summary, action_items[],
        source_type, tags, status }
  • investigations + status/staleness tracking — SQLite + flat files
  • escalation orchestrator → shells out to `claude` CLI / corp AI CLI
  • GET /investigations, /events (stale, needs-input, done)
        │
        ├── local model backend (Ollama, if present, else embedded llama.cpp)
        └── whisper.cpp for STT
```

**Why a daemon, not one app:** the core promise is "always-on, nothing gets lost, nags me if stale." That has to survive the UI window being closed and start on login. The daemon is the persistent core; the tray/hotkey/capture piece and the browse/review UI are both just clients of its local HTTP API.

**Why the `/capture` contract matters:** every client — desktop hotkey, ESP32 button, future browser extension — POSTs the same shape, with fields optional. `image` absent + `audio` present + `source_meta.device_id` = "esp32-01" is a complete, valid capture. This is what makes the hardware device a client addition later, not a redesign.

## Stack: Electron (UI + daemon, one language)

Electron for the desktop tray app and the investigation-browse UI — one JS/TS codebase for both, fastest to a usable v1, richest UI for the review/merge screens.

Two known costs, both worth calling out now:

- **Idle footprint.** An always-running Electron tray process is heavier than ideal for "snappy and free." Mitigation: the *daemon* (`snapnoted`) should be a separate lightweight Node process (no Electron/Chromium) that runs persistently; Electron is only the UI surface, launched on demand from the tray and closeable without killing the daemon. The daemon is the thing that's always-on; the Electron window is not.
- **Global hotkey + screenshot on Linux/Wayland and macOS permissions.** Electron's `globalShortcut` and `desktopCapturer` cover X11/Windows reasonably; Wayland needs portal-based screenshot (`org.freedesktop.portal.Screenshot`) and may not support arbitrary global hotkeys without compositor-specific extensions. macOS needs Screen Recording + Accessibility + Microphone permission grants — unavoidable, just needs a first-run setup flow.

Fallback if Electron's hotkey/portal story proves too unreliable on a given platform: a tiny native helper binary (per-OS) that only does hotkey-listen + screenshot + mic-capture and POSTs to the daemon — Electron then becomes pure UI. Worth prototyping the native-helper path early on Linux specifically, since that's the likely daily-driver OS and Wayland is the riskiest piece.

## Local model: interface with two backends

Triage (vision+text classification, OCR-ish reading of screenshots, matching to investigations) goes through a small internal interface — `classify(image?, transcript) -> TriageResult` — with two implementations:

- **Ollama backend** — if Ollama is installed/reachable on `localhost:11434`, use it. Simplest, handles model management, easy to swap models (Gemma 3 vision-capable variants).
- **Embedded backend** — bundled `llama.cpp` (or `llama.cpp` server spawned as a child process) with a packaged model file, for locked-down corporate machines where installing Ollama isn't possible. Same interface, daemon doesn't care which is active.

Daemon probes for Ollama at startup; falls back to embedded. This is config, not a fork — same `TriageResult` shape either way, so the rest of the system (investigation matching, status logic, escalation) is identical regardless of backend.

STT (whisper.cpp) is bundled either way — small, fast, no reason to make it pluggable.

## v1 scope: desktop-first, device-ready

v1 = desktop tray client + daemon + browse/review UI + escalation to Claude Code CLI. No ESP32 firmware work yet.

But the `/capture` API is designed against the device's constraints from day one (small payloads, audio-first, fields optional, LAN-reachable) so that adding the ESP32 later is: point it at `http://<laptop-ip>:<port>/capture`, send `{ audio, source_meta: { device_id } }`. No daemon changes expected.

## Open questions carried forward

- Auth/trust for `/capture` when it's LAN-reachable (device case) vs localhost-only (desktop case) — needs at least a shared token once the device is in play, even on a "trusted" home/work LAN.
- Packaging: daemon as a system service (systemd / Windows service / launchd) vs. "starts when Electron tray starts" — service is more correct for "always-on," but more install complexity. Probably: Electron installer registers the daemon as an autostart service per-OS.
- Escalation context size and the `claude` CLI invocation shape — still open from the README, doesn't block daemon/client architecture.
