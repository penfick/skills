from pathlib import Path

from pptx.dml.color import RGBColor

from pptskill.contrast import adjust_for_contrast, contrast_ratio, ensure_contrast
from pptskill.render import render_outline
from pptskill.schema import parse_outline
from pptskill.theme import THEMES, apply_theme_tokens


def test_adjust_low_contrast_dark_on_dark():
    bg = RGBColor(0, 0, 0)
    fg = RGBColor(10, 10, 10)
    out = adjust_for_contrast(fg, bg, min_ratio=4.5)
    assert contrast_ratio(out, bg) >= 4.5


def test_adjust_mid_gray_bg():
    bg = RGBColor(0x80, 0x80, 0x80)
    out = adjust_for_contrast(RGBColor(0x90, 0x90, 0x90), bg, min_ratio=4.5)
    assert contrast_ratio(out, bg) >= 4.5


def test_ensure_contrast_on_bad_theme():
    from dataclasses import replace

    base = THEMES["light-corporate"]
    bad = replace(base, ink_on_light=RGBColor(0xE0, 0xE0, 0xE0), muted_on_light=RGBColor(0xF0, 0xF0, 0xF0))
    fixed, reports = ensure_contrast(bad)
    assert contrast_ratio(fixed.ink_on_light, fixed.bg_light) >= 4.5
    assert len(reports) >= 4


def test_per_slide_theme_and_tokens(tmp_path: Path):
    outline = parse_outline({
        "meta": {"title": "T", "theme": "light-corporate"},
        "slides": [
            {"type": "cover", "title": "Dark", "theme": "dark-keynote", "notes": "n"},
            {
                "type": "title_body",
                "title": "Accent",
                "bullets": ["x"],
                "theme_tokens": {"accent": "#E11D48"},
                "notes": "n",
            },
            {"type": "closing", "title": "End", "notes": "n"},
        ],
    })
    out = tmp_path / "mix.pptx"
    render_outline(outline, out, base_dir=tmp_path)
    assert out.exists()


def test_apply_theme_tokens():
    t = apply_theme_tokens(THEMES["light-corporate"], {"accent": "#E11D48"})
    assert t.accent[0] == 0xE1
    assert t.bg_light == THEMES["light-corporate"].bg_light
