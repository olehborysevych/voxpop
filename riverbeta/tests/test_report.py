from pathlib import Path

from riverbeta.report import build_report, pick_illustration


FRAMES = [
    {"path": "frames/frame_000000.jpg", "timestamp": 0.0},
    {"path": "frames/frame_000005.jpg", "timestamp": 5.0},
    {"path": "frames/frame_000010.jpg", "timestamp": 10.0},
    {"path": "frames/frame_000020.jpg", "timestamp": 20.0},
]


def test_pick_illustration_prefers_nearby_scene_change():
    scene_changes = [{"timestamp": 10.0, "score": 50.0}]
    frame = pick_illustration(hazard_start=9.0, frames=FRAMES, scene_changes=scene_changes, window=5.0)
    assert frame["timestamp"] == 10.0


def test_pick_illustration_falls_back_to_nearest_frame():
    frame = pick_illustration(hazard_start=21.0, frames=FRAMES, scene_changes=[], window=5.0)
    assert frame["timestamp"] == 20.0


def test_build_report_creates_html(tmp_path):
    transcript = {
        "language": "uk",
        "original": [{"start": 9.0, "end": 11.0, "text": "Обережно, гребля!"}],
        "english": [{"start": 9.0, "end": 11.0, "text": "Careful, a weir!"}],
    }
    hazards = [{
        "start": 9.0, "end": 11.0,
        "hazard_type": "weir", "side": None, "severity": "high",
        "text": "Обережно, гребля!",
    }]
    scene_changes = [{"timestamp": 10.0, "score": 50.0}]
    metadata = {"title": "Test Trip", "webpage_url": "https://youtu.be/abc123"}

    out_path = build_report(tmp_path, hazards, FRAMES, scene_changes, transcript, metadata)

    assert out_path == tmp_path / "report.html"
    html = out_path.read_text()
    assert "Test Trip" in html
    assert "weir" in html
    assert "Careful, a weir!" in html
    assert "frames/frame_000010.jpg" in html
    assert "https://youtu.be/abc123?t=9" in html


def test_build_report_handles_no_hazards(tmp_path):
    transcript = {"language": "en", "original": [], "english": []}
    out_path = build_report(tmp_path, [], FRAMES, [], transcript, {"title": "Empty"})
    html = out_path.read_text()
    assert "No hazard mentions found" in html
