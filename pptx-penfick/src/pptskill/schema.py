"""Outline JSON schema: load, validate, defaults."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Single source of truth for slide types is layouts.RENDERERS/LAYOUT_TYPES.
# This alias keeps schema validation in sync (guarded by tests).

def _is_valid_theme(value: str) -> bool:
    from pptskill.theme import THEMES, is_theme_path_ref

    return value in THEMES or is_theme_path_ref(value)


def _known_types() -> frozenset[str]:
    from pptskill.layouts import LAYOUT_TYPES

    return frozenset(LAYOUT_TYPES)


class SchemaError(ValueError):
    """Invalid outline JSON."""


@dataclass
class Meta:
    title: str
    subtitle: str = ""
    author: str = ""
    lang: str = "zh-CN"
    theme: str = "dark-keynote"
    slide_size: str = "16:9"


@dataclass
class Outline:
    meta: Meta
    slides: list[dict[str, Any]] = field(default_factory=list)

    def slide_count(self) -> int:
        return len(self.slides)


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SchemaError(msg)


def load_outline(path: str | Path) -> Outline:
    p = Path(path)
    if not p.exists():
        raise SchemaError(f"outline not found: {p}")
    try:
        raw = json.loads(p.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        raise SchemaError(f"invalid JSON: {e}") from e
    outline = parse_outline(raw)
    theme = outline.meta.theme
    if theme.lower().endswith(".json"):
        theme_path = Path(theme)
        if not theme_path.is_absolute():
            theme_path = p.resolve().parent / theme_path
        if not theme_path.exists():
            raise SchemaError(f"meta.theme file not found: {theme_path}")
    return outline


def parse_outline(raw: Any) -> Outline:
    _require(isinstance(raw, dict), "outline root must be an object")
    meta_raw = raw.get("meta")
    _require(isinstance(meta_raw, dict), "meta must be an object")
    title = meta_raw.get("title")
    _require(isinstance(title, str) and bool(title.strip()), "meta.title is required")
    theme = meta_raw.get("theme", "dark-keynote")
    _require(isinstance(theme, str) and _is_valid_theme(theme),
             "meta.theme must be a builtin theme name or a .json path")
    meta = Meta(
        title=title.strip(),
        subtitle=str(meta_raw.get("subtitle", "") or ""),
        author=str(meta_raw.get("author", "") or ""),
        lang=str(meta_raw.get("lang", "zh-CN") or "zh-CN"),
        theme=theme,
        slide_size=str(meta_raw.get("slide_size", "16:9") or "16:9"),
    )
    slides_raw = raw.get("slides")
    _require(isinstance(slides_raw, list) and len(slides_raw) >= 1, "slides must be a non-empty array")
    known = _known_types()
    slides: list[dict[str, Any]] = []
    for i, item in enumerate(slides_raw, start=1):
        _require(isinstance(item, dict), f"slides[{i}] must be an object")
        stype = item.get("type")
        _require(isinstance(stype, str) and stype in known,
                 f"slides[{i}].type must be one of {sorted(known)}")
        if stype == "title_body":
            _require(isinstance(item.get("title"), str) and item["title"].strip(),
                     f"slides[{i}].title is required for title_body")
        if stype in {"cover", "section", "closing"}:
            _require(isinstance(item.get("title"), str) and item["title"].strip(),
                     f"slides[{i}].title is required for {stype}")
        if stype == "chart":
            _validate_chart(item, i)
        if stype == "image_text":
            image = item.get("image")
            _require(isinstance(image, dict), f"slides[{i}].image must be an object")
            path = image.get("path")
            _require(isinstance(path, str) and path.strip(),
                     f"slides[{i}].image.path is required")
            side = image.get("side", "left")
            _require(side in {"left", "right"},
                     f"slides[{i}].image.side must be left|right")
            _require(isinstance(item.get("title"), str) and item["title"].strip(),
                     f"slides[{i}].title is required for image_text")
        if stype == "compare":
            _require(isinstance(item.get("title"), str) and item["title"].strip(),
                     f"slides[{i}].title is required for compare")
            for side in ("left", "right"):
                block = item.get(side)
                _require(isinstance(block, dict), f"slides[{i}].{side} must be an object")
                _require(isinstance(block.get("title"), str) and block["title"].strip(),
                         f"slides[{i}].{side}.title is required")
        if stype == "kpi":
            cards = item.get("cards")
            _require(isinstance(cards, list) and cards,
                     f"slides[{i}].cards must be a non-empty array")
            for j, card in enumerate(cards):
                _require(isinstance(card, dict), f"slides[{i}].cards[{j}] must be an object")
                _require(str(card.get("number", "")).strip(),
                         f"slides[{i}].cards[{j}].number is required")
        if stype == "quote":
            text = item.get("text")
            _require(isinstance(text, str) and text.strip(),
                     f"slides[{i}].text is required for quote")
        if "theme" in item and item["theme"] is not None:
            th = item["theme"]
            _require(isinstance(th, str) and _is_valid_theme(th),
                     f"slides[{i}].theme must be a builtin name or .json path")
        if "theme_tokens" in item and item["theme_tokens"] is not None:
            _require(isinstance(item["theme_tokens"], dict) and item["theme_tokens"],
                     f"slides[{i}].theme_tokens must be a non-empty object")
        slides.append(dict(item))
    return Outline(meta=meta, slides=slides)


def _validate_chart(item: dict[str, Any], i: int) -> None:
    from pptskill.charts import CHART_KINDS

    chart = item.get("chart")
    _require(isinstance(chart, dict), f"slides[{i}].chart must be an object")
    kind = str(chart.get("kind", "")).lower()
    _require(kind in CHART_KINDS, f"slides[{i}].chart.kind must be one of {sorted(CHART_KINDS)}")
    cats = chart.get("categories")
    series = chart.get("series")
    _require(isinstance(cats, list) and cats, f"slides[{i}].chart.categories must be non-empty")
    _require(isinstance(series, list) and series, f"slides[{i}].chart.series must be non-empty")
    if kind == "pie":
        _require(len(series) == 1, f"slides[{i}].chart pie requires exactly one series")
    for j, s in enumerate(series):
        _require(isinstance(s, dict), f"slides[{i}].chart.series[{j}] must be an object")
        values = s.get("values")
        _require(isinstance(values, list) and len(values) == len(cats),
                 f"slides[{i}].chart.series[{j}].values must match categories length")
    _require(isinstance(item.get("title"), str) and item["title"].strip(),
             f"slides[{i}].title is required for chart")
