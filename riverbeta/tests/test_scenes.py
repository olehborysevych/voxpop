import numpy as np

from riverbeta.scenes import detect_scene_changes


def test_no_changes_for_identical_frames():
    fingerprints = np.zeros((5, 2, 2, 3), dtype=np.float32)
    timestamps = [0.0, 1.0, 2.0, 3.0, 4.0]
    assert detect_scene_changes(fingerprints, timestamps) == []


def test_detects_big_jump():
    fingerprints = np.zeros((3, 2, 2, 3), dtype=np.float32)
    fingerprints[2] = 255  # last frame is completely different
    timestamps = [0.0, 1.0, 2.0]

    changes = detect_scene_changes(fingerprints, timestamps, threshold=10.0)

    assert len(changes) == 1
    assert changes[0]["timestamp"] == 2.0
    assert changes[0]["score"] > 10.0


def test_single_frame_has_no_changes():
    fingerprints = np.zeros((1, 2, 2, 3), dtype=np.float32)
    assert detect_scene_changes(fingerprints, [0.0]) == []
