"""Detect "plan changes" (cuts / new shots) from frame color fingerprints."""

import numpy as np


def detect_scene_changes(
    fingerprints: np.ndarray,
    timestamps: list[float],
    threshold: float = 18.0,
) -> list[dict]:
    """Flag timestamps where the color fingerprint jumps by more than ``threshold``.

    Returns a list of ``{"timestamp": float, "score": float}``, one entry
    per detected change, ordered by time.
    """
    flat = fingerprints.reshape(fingerprints.shape[0], -1)
    if len(flat) < 2:
        return []

    diffs = np.sqrt(((flat[1:] - flat[:-1]) ** 2).mean(axis=1))
    return [
        {"timestamp": timestamps[i + 1], "score": float(d)}
        for i, d in enumerate(diffs)
        if d > threshold
    ]
