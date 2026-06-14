import numpy as np
from PIL import Image

from riverbeta.colormap import build_fingerprints, save_colormap_image


def _write_solid_image(path, color, size=(32, 32)):
    Image.new("RGB", size, color).save(path)


def test_build_fingerprints_shape(tmp_path):
    paths = []
    for i, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
        p = tmp_path / f"frame_{i}.jpg"
        _write_solid_image(p, color)
        paths.append(p)

    fingerprints = build_fingerprints(paths, grid=(4, 4))
    assert fingerprints.shape == (3, 4, 4, 3)


def test_fingerprint_matches_solid_color(tmp_path):
    p = tmp_path / "red.jpg"
    _write_solid_image(p, (200, 10, 10))

    fingerprints = build_fingerprints([p], grid=(2, 2))
    # every cell should be close to the source color
    assert np.allclose(fingerprints[0], [200, 10, 10], atol=2)


def test_save_colormap_image_writes_file(tmp_path):
    paths = []
    for i, color in enumerate([(255, 0, 0), (0, 255, 0)]):
        p = tmp_path / f"frame_{i}.jpg"
        _write_solid_image(p, color)
        paths.append(p)

    fingerprints = build_fingerprints(paths, grid=(4, 4))
    out_path = tmp_path / "colormap.png"
    save_colormap_image(fingerprints, out_path, scale=2)

    assert out_path.exists()
    img = Image.open(out_path)
    assert img.size == (2 * 2, 4 * 4 * 2)  # n_frames*scale, (grid_h*grid_w)*scale
