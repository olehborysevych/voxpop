"""Download a video and pull out its audio track, all locally via yt-dlp + ffmpeg."""

import json
import subprocess
from pathlib import Path


def fetch_video(url: str, out_dir: Path) -> Path:
    """Download the video as ``video.mp4`` and write ``metadata.json``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    video_path = out_dir / "video.mp4"
    meta_path = out_dir / "metadata.json"

    subprocess.run(
        [
            "yt-dlp",
            "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
            "--merge-output-format", "mp4",
            "--write-info-json",
            "--no-write-playlist-metafiles",
            "-o", str(video_path),
            url,
        ],
        check=True,
    )

    info_path = video_path.with_suffix(".info.json")
    if info_path.exists():
        info = json.loads(info_path.read_text())
        meta_path.write_text(json.dumps({
            "id": info.get("id"),
            "title": info.get("title"),
            "description": info.get("description"),
            "webpage_url": info.get("webpage_url", url),
            "duration": info.get("duration"),
        }, ensure_ascii=False, indent=2))
        info_path.unlink()

    return video_path


def extract_audio(video_path: Path, out_dir: Path) -> Path:
    """Extract a mono 16kHz WAV track suitable for speech-to-text."""
    audio_path = out_dir / "audio.wav"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn", "-ac", "1", "-ar", "16000",
            str(audio_path),
        ],
        check=True,
        capture_output=True,
    )
    return audio_path
