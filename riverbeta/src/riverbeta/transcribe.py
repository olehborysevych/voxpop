"""Speech-to-text + translation using a local faster-whisper model.

Produces two segment lists with matching timestamps:

- ``original``: transcript in the language(s) actually spoken
- ``english``: an English translation of the same audio (skipped if the
  detected language is already English)

Keeping both lets the hazard map show the paddler's own words next to a
translation, instead of flattening everything into one language.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Segment:
    start: float
    end: float
    text: str


def _run_pass(model, audio_path: Path, task: str):
    segments, info = model.transcribe(str(audio_path), task=task, vad_filter=True)
    return [Segment(s.start, s.end, s.text.strip()) for s in segments], info


def transcribe(
    audio_path: Path,
    model_size: str = "small",
    device: str = "cpu",
    compute_type: str = "int8",
) -> dict:
    """Run local speech-to-text (and translation, if needed)."""
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    original, info = _run_pass(model, audio_path, "transcribe")
    language = info.language

    english: list[Segment] = []
    if language != "en":
        english, _ = _run_pass(model, audio_path, "translate")

    return {
        "language": language,
        "original": [asdict(s) for s in original],
        "english": [asdict(s) for s in english],
    }


def save_transcript(transcript: dict, out_path: Path) -> None:
    out_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2))


def load_transcript(path: Path) -> dict:
    return json.loads(path.read_text())


def english_text_at(transcript: dict, start: float, end: float) -> str:
    """Return the English translation overlapping a given time range, if any."""
    pieces = [
        seg["text"]
        for seg in transcript.get("english", [])
        if seg["end"] > start and seg["start"] < end
    ]
    return " ".join(pieces).strip()
