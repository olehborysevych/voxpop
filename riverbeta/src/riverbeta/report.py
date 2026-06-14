"""Build the illustrated, timestamped HTML report."""

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import transcribe as transcribe_mod

TEMPLATES_DIR = Path(__file__).parent / "templates"


def _nearest_frame(timestamp: float, frames: list[dict]) -> dict:
    return min(frames, key=lambda f: abs(f["timestamp"] - timestamp))


def pick_illustration(
    hazard_start: float,
    frames: list[dict],
    scene_changes: list[dict],
    window: float = 5.0,
) -> dict:
    """Pick the frame that best illustrates a hazard mention.

    Prefer a frame near a detected scene change close to the hazard's
    timestamp (the narration usually lines up with "and now look at this"
    cuts); otherwise just use the closest sampled frame.
    """
    nearby_changes = [
        sc for sc in scene_changes if abs(sc["timestamp"] - hazard_start) <= window
    ]
    target_ts = nearby_changes[0]["timestamp"] if nearby_changes else hazard_start
    return _nearest_frame(target_ts, frames)


def _format_timestamp(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"


def _video_link(webpage_url: str | None, start: float) -> str | None:
    if not webpage_url:
        return None
    sep = "&" if "?" in webpage_url else "?"
    return f"{webpage_url}{sep}t={int(start)}"


def build_report(
    out_dir: Path,
    hazards: list[dict],
    frames: list[dict],
    scene_changes: list[dict],
    transcript: dict,
    metadata: dict,
) -> Path:
    """Render ``report.html`` into ``out_dir`` and return its path."""
    cards = []
    for hazard in sorted(hazards, key=lambda h: h["start"]):
        frame = pick_illustration(hazard["start"], frames, scene_changes)
        english = transcribe_mod.english_text_at(transcript, hazard["start"], hazard["end"])
        cards.append({
            "timestamp": _format_timestamp(hazard["start"]),
            "video_link": _video_link(metadata.get("webpage_url"), hazard["start"]),
            "hazard_type": hazard["hazard_type"],
            "side": hazard["side"],
            "severity": hazard["severity"],
            "text_original": hazard["text"],
            "text_english": english,
            "thumbnail": Path(frame["path"]).name,
        })

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("report.html.j2")
    html = template.render(
        title=metadata.get("title") or "Riverbeta",
        description=metadata.get("description"),
        language=transcript.get("language"),
        cards=cards,
        colormap_image="colormap.png" if (out_dir / "colormap.png").exists() else None,
    )

    out_path = out_dir / "report.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def load_json(path: Path):
    return json.loads(path.read_text())
