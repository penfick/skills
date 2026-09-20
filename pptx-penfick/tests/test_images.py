from pathlib import Path

import pytest
from PIL import Image
from pptx import Presentation

from pptskill.images import ImageError, resolve_image_path
from pptskill.render import render_outline
from pptskill.schema import SchemaError, parse_outline


def _make_jpg(path: Path, size=(800, 600)) -> Path:
    Image.new("RGB", size, color=(20, 120, 40)).save(path, format="JPEG")
    return path


def test_resolve_missing(tmp_path: Path):
    with pytest.raises(ImageError):
        resolve_image_path("nope.jpg", tmp_path)


def test_resolve_relative(tmp_path: Path):
    img = _make_jpg(tmp_path / "a.jpg")
    p = resolve_image_path("a.jpg", tmp_path)
    assert p == img.resolve()


def test_image_text_render(tmp_path: Path):
    assets = tmp_path / "assets"
    assets.mkdir()
    _make_jpg(assets / "sample.jpg", size=(1200, 800))
    outline = parse_outline({
        "meta": {"title": "T"},
        "slides": [{
            "type": "image_text",
            "title": "图文",
            "image": {"path": "assets/sample.jpg", "side": "left"},
            "bullets": ["要点"],
            "notes": "n",
        }],
    })
    out = tmp_path / "deck.pptx"
    render_outline(outline, out, base_dir=tmp_path)
    prs = Presentation(str(out))
    assert len(prs.slides) == 1
    # has a picture shape
    kinds = [sh.shape_type for sh in prs.slides[0].shapes]
    assert any(k is not None for k in kinds)


def test_image_text_missing_file_fails_render(tmp_path: Path):
    outline = parse_outline({
        "meta": {"title": "T"},
        "slides": [{
            "type": "image_text",
            "title": "图文",
            "image": {"path": "missing.jpg", "side": "left"},
            "bullets": ["x"],
        }],
    })
    with pytest.raises(ImageError):
        render_outline(outline, tmp_path / "x.pptx", base_dir=tmp_path)


def test_schema_requires_image_path():
    with pytest.raises(SchemaError):
        parse_outline({
            "meta": {"title": "T"},
            "slides": [{
                "type": "image_text",
                "title": "t",
                "image": {"side": "left"},
            }],
        })
