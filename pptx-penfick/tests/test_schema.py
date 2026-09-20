import pytest

from pptskill.schema import SchemaError, parse_outline


def _minimal_slide():
    return {"type": "cover", "title": "Hello"}


def test_parse_valid_minimal():
    outline = parse_outline({"meta": {"title": "T"}, "slides": [_minimal_slide()]})
    assert outline.slide_count() == 1
    assert outline.meta.theme == "dark-keynote"


def test_missing_title():
    with pytest.raises(SchemaError):
        parse_outline({"meta": {}, "slides": [_minimal_slide()]})


def test_unknown_type():
    with pytest.raises(SchemaError):
        parse_outline({
            "meta": {"title": "T"},
            "slides": [{"type": "nope", "title": "x"}],
        })


def test_empty_slides():
    with pytest.raises(SchemaError):
        parse_outline({"meta": {"title": "T"}, "slides": []})


def test_title_body_requires_title():
    with pytest.raises(SchemaError):
        parse_outline({
            "meta": {"title": "T"},
            "slides": [{"type": "title_body", "bullets": ["a"]}],
        })


def test_layout_registry_matches_schema():
    from pptskill.layouts import LAYOUT_TYPES
    from pptskill.schema import _known_types

    assert set(LAYOUT_TYPES) == set(_known_types())


def test_unknown_theme():
    with pytest.raises(SchemaError):
        parse_outline({"meta": {"title": "T", "theme": "nope"}, "slides": [_minimal_slide()]})


def test_chart_kind_invalid():
    with pytest.raises(SchemaError):
        parse_outline({
            "meta": {"title": "T"},
            "slides": [{
                "type": "chart",
                "title": "C",
                "chart": {
                    "kind": "radar",
                    "categories": ["A"],
                    "series": [{"name": "s", "values": [1]}],
                },
            }],
        })


def test_chart_series_length_mismatch():
    with pytest.raises(SchemaError):
        parse_outline({
            "meta": {"title": "T"},
            "slides": [{
                "type": "chart",
                "title": "C",
                "chart": {
                    "kind": "bar",
                    "categories": ["A", "B"],
                    "series": [{"name": "s", "values": [1]}],
                },
            }],
        })


def test_compare_requires_sides():
    with pytest.raises(SchemaError):
        parse_outline({
            "meta": {"title": "T"},
            "slides": [{
                "type": "compare",
                "title": "C",
                "left": {"title": "L"},
                "right": {"items": ["x"]},
            }],
        })
