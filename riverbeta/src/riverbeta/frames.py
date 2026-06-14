"""Sample frames from the video at a fixed rate, all done locally via ffmpeg."""

import subprocess
from pathlib import Path


def sample_frames(video_path: Path, out_dir: Path, fps: float = 1.0) -> list[dict]:
    """Extract frames at ``fps`` frames per second into ``out_dir``.

    Returns a list of ``{"path": str, "timestamp": float}`` in order.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(out_dir / "frame_%06d.jpg")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", f"fps={fps}",
            "-q:v", "2",
            pattern,
        ],
        check=True,
        capture_output=True,
    )

    frame_paths = sorted(out_dir.glob("frame_*.jpg"))
    return [
        {"path": str(path), "timestamp": i / fps}
        for i, path in enumerate(frame_paths)
    ]
