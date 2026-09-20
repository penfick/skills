from pathlib import Path

from PIL import Image, ImageDraw

from pptskill.brand_extract import extract_palette, pick_accent, theme_from_logo, write_theme_json
from pptskill.render import render_outline
from pptskill.schema import parse_outline


def _solid_logo(path: Path, color: tuple[int, int, int], size=(120, 80)) -> Path:
    img = Image.new("RGB", size, (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, size[0] - 10, size[1] - 10], fill=color)
    img.save(path, format="PNG")
    return path


def _two_tone_logo(path: Path) -> Path:
    img = Image.new("RGB", (160, 100), (250, 250, 250))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 80, 100], fill=(0x76, 0xB9, 0x00))
    d.rectangle([80, 0, 160, 100], fill=(0x1F, 0x3A, 0x5F))
    img.save(path, format="PNG")
    return path


def test_extract_green_logo(tmp_path: Path):
    logo = _solid_logo(tmp_path / "logo.png", (0x76, 0xB9, 0x00))
    palette = extract_palette(logo)
    assert palette
    accent = pick_accent(palette)
    # should be close to NVIDIA green
    assert abs(accent[1] - 0xB9) < 40
    assert accent[1] > accent[0] and accent[1] > accent[2]


def test_theme_from_logo_json_roundtrip(tmp_path: Path):
    logo = _solid_logo(tmp_path / "logo.png", (0xE1, 0x1D, 0x48))
    data = theme_from_logo(logo, name="acme", mode="light")
    assert data["name"] == "acme"
    assert data["accent"].startswith("#")
    assert len(data["series"]) == 5
    out = write_theme_json(data, tmp_path / "brand.json")
    assert out.exists()


def test_render_with_extracted_theme(tmp_path: Path):
    logo = _two_tone_logo(tmp_path / "logo.png")
    data = theme_from_logo(logo, name="twotone", mode="auto")
    theme_path = write_theme_json(data, tmp_path / "t.json")
    outline = parse_outline({
        "meta": {"title": "T", "theme": theme_path.name},
        "slides": [{"type": "cover", "title": "Hi", "notes": "n"}],
    })
    out = tmp_path / "d.pptx"
    render_outline(outline, out, theme_name=str(theme_path), base_dir=tmp_path)
    assert out.exists()


def test_missing_logo():
    import pytest
    from pptskill.brand_extract import BrandExtractError

    with pytest.raises(BrandExtractError):
        extract_palette("nope-missing.png")


def test_two_tone_keeps_both_colors(tmp_path: Path):
    logo = _two_tone_logo(tmp_path / "logo.png")
    data = theme_from_logo(logo, name="twotone", mode="auto")
    series = data["series"]
    # green half should remain
    assert any(int(c[3:5], 16) > int(c[1:3], 16) for c in series), series


def test_transparent_bg_not_black_accent(tmp_path: Path):
    img = Image.new("RGBA", (100, 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([10, 10, 90, 70], fill=(0xE1, 0x1D, 0x48, 255))
    logo = tmp_path / "alpha.png"
    img.save(logo)
    data = theme_from_logo(logo, name="alpha", mode="auto")
    assert data["accent"].upper() != "#000000"


def test_gray_logo_fallback(tmp_path: Path):
    img = Image.new("RGB", (80, 80), (180, 180, 180))
    logo = tmp_path / "gray.png"
    img.save(logo)
    data = theme_from_logo(logo, name="gray", mode="auto")
    assert data["accent"].upper() == "#1F3A5F"
