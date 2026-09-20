from pathlib import Path

import pytest

from pptskill.schema import SchemaError, parse_outline
from pptskill.theme import ThemeError, list_themes, resolve_theme, theme_from_dict
from pptskill.render import render_outline


def test_list_themes_has_seven():
    names = list_themes()
    for n in [
        "dark-keynote",
        "light-corporate",
        "education-blue",
        "pitch-green",
        "minimal-mono",
        "finance-navy",
        "warm-editorial",
    ]:
        assert n in names
    assert len(names) >= 7


def test_custom_theme_from_dict_extends():
    t = theme_from_dict({
        "name": "x",
        "extends": "light-corporate",
        "accent": "#E11D48",
    })
    assert t.name == "x"
    assert (t.accent[0], t.accent[1], t.accent[2]) == (0xE1, 0x1D, 0x48)


def test_resolve_theme_file(tmp_path: Path):
    p = tmp_path / "brand.json"
    p.write_text('{"name":"b","extends":"dark-keynote","accent":"#FF0000"}', encoding="utf-8")
    t = resolve_theme("brand.json", base_dir=tmp_path)
    assert t.name == "b"
    assert t.accent[0] == 0xFF


def test_schema_accepts_json_theme_ref():
    outline = parse_outline({
        "meta": {"title": "T", "theme": "brand.json"},
        "slides": [{"type": "cover", "title": "C"}],
    })
    assert outline.meta.theme == "brand.json"


def test_schema_rejects_bad_theme():
    with pytest.raises(SchemaError):
        parse_outline({
            "meta": {"title": "T", "theme": "not-a-theme"},
            "slides": [{"type": "cover", "title": "C"}],
        })


def test_load_outline_missing_theme_file(tmp_path: Path):
    from pptskill.schema import load_outline

    o = tmp_path / "o.json"
    o.write_text(
        '{"meta":{"title":"T","theme":"missing.json"},"slides":[{"type":"cover","title":"C"}]}',
        encoding="utf-8",
    )
    with pytest.raises(SchemaError):
        load_outline(o)


def test_render_with_custom_theme_file(tmp_path: Path):
    theme = tmp_path / "t.json"
    theme.write_text('{"name":"c","extends":"light-corporate","accent":"#00FF00"}', encoding="utf-8")
    outline = parse_outline({
        "meta": {"title": "T", "theme": "t.json"},
        "slides": [{"type": "cover", "title": "Hi", "notes": "n"}],
    })
    out = tmp_path / "d.pptx"
    render_outline(outline, out, base_dir=tmp_path)
    assert out.exists()


def test_bad_color_raises():
    with pytest.raises(ThemeError):
        theme_from_dict({"name": "b", "accent": "red"})
