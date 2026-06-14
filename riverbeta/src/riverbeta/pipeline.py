"""Glue code: each step reads/writes files in a working directory.

Working directory layout::

    out/
      metadata.json     - title, description, webpage_url, ... (from yt-dlp)
      video.mp4
      audio.wav
      transcript.json   - {"language", "original": [...], "english": [...]}
      frames/frame_*.jpg
      frames.json       - [{"path", "timestamp"}, ...]
      fingerprints.npy  - (n_frames, grid_h, grid_w, 3)
      colormap.png
      scenes.json       - [{"timestamp", "score"}, ...]
      hazards.json      - [{"start", "end", "hazard_type", "side", "severity", "text"}, ...]
      report.html
"""

import json
from pathlib import Path

from . import colormap, download, frames as frames_mod, hazards as hazards_mod, report, scenes, transcribe


def step_fetch(url: str, out_dir: Path) -> None:
    video_path = download.fetch_video(url, out_dir)
    download.extract_audio(video_path, out_dir)


def step_transcribe(out_dir: Path, model_size: str = "small", device: str = "cpu") -> None:
    audio_path = out_dir / "audio.wav"
    transcript = transcribe.transcribe(audio_path, model_size=model_size, device=device)
    transcribe.save_transcript(transcript, out_dir / "transcript.json")


def step_frames(out_dir: Path, fps: float = 1.0) -> None:
    video_path = out_dir / "video.mp4"
    sampled = frames_mod.sample_frames(video_path, out_dir / "frames", fps=fps)
    (out_dir / "frames.json").write_text(json.dumps(sampled, indent=2))


def step_colormap(out_dir: Path, grid: tuple[int, int] = (8, 8), threshold: float = 18.0) -> None:
    sampled = json.loads((out_dir / "frames.json").read_text())
    frame_paths = [Path(f["path"]) for f in sampled]
    timestamps = [f["timestamp"] for f in sampled]

    fingerprints = colormap.build_fingerprints(frame_paths, grid=grid)
    colormap.save_fingerprints(fingerprints, out_dir / "fingerprints.npy")
    colormap.save_colormap_image(fingerprints, out_dir / "colormap.png")

    changes = scenes.detect_scene_changes(fingerprints, timestamps, threshold=threshold)
    (out_dir / "scenes.json").write_text(json.dumps(changes, indent=2))


def step_hazards(out_dir: Path) -> None:
    transcript = transcribe.load_transcript(out_dir / "transcript.json")
    found = hazards_mod.extract_hazards(transcript["original"])
    (out_dir / "hazards.json").write_text(json.dumps(found, ensure_ascii=False, indent=2))


def step_report(out_dir: Path) -> Path:
    hazards = json.loads((out_dir / "hazards.json").read_text())
    sampled = json.loads((out_dir / "frames.json").read_text())
    scene_changes = json.loads((out_dir / "scenes.json").read_text())
    transcript = transcribe.load_transcript(out_dir / "transcript.json")
    metadata = json.loads((out_dir / "metadata.json").read_text()) if (out_dir / "metadata.json").exists() else {}

    return report.build_report(out_dir, hazards, sampled, scene_changes, transcript, metadata)


def run_all(
    url: str,
    out_dir: Path,
    model_size: str = "small",
    device: str = "cpu",
    fps: float = 1.0,
) -> Path:
    step_fetch(url, out_dir)
    step_transcribe(out_dir, model_size=model_size, device=device)
    step_frames(out_dir, fps=fps)
    step_colormap(out_dir)
    step_hazards(out_dir)
    return step_report(out_dir)
