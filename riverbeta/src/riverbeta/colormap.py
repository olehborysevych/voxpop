"""Build a compressed visual timeline ("pixel color map") from sampled frames.

Each frame is reduced to a small grid of average colors. Stacking those
grids over time gives a cheap visual fingerprint of the whole video that
also doubles as the input for scene-change detection.
"""

from pathlib import Path

import numpy as np
from PIL import Image


def frame_fingerprint(path: Path, grid: tuple[int, int] = (8, 8)) -> np.ndarray:
    """Downsample a frame to a small ``grid`` of average RGB colors."""
    img = Image.open(path).convert("RGB").resize(grid, Image.BILINEAR)
    return np.asarray(img, dtype=np.float32)  # (grid_h, grid_w, 3)


def build_fingerprints(frame_paths: list[Path], grid: tuple[int, int] = (8, 8)) -> np.ndarray:
    """Return an array of shape ``(n_frames, grid_h, grid_w, 3)``."""
    return np.stack([frame_fingerprint(p, grid) for p in frame_paths])


def save_colormap_image(fingerprints: np.ndarray, out_path: Path, scale: int = 4) -> None:
    """Render the fingerprints as a single PNG: time across, color cells down."""
    n, h, w, c = fingerprints.shape
    strip = fingerprints.reshape(n, h * w, c).transpose(1, 0, 2)  # (h*w, n, 3)
    img = Image.fromarray(np.clip(strip, 0, 255).astype(np.uint8))
    img = img.resize((max(n, 1) * scale, h * w * scale), Image.NEAREST)
    img.save(out_path)


def save_fingerprints(fingerprints: np.ndarray, out_path: Path) -> None:
    np.save(out_path, fingerprints)


def load_fingerprints(path: Path) -> np.ndarray:
    return np.load(path)
