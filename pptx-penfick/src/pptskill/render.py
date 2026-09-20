"""Render Outline → Presentation."""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation

from pptskill.layouts import render_slide
from pptskill.layouts.base import SLIDE_H, SLIDE_W
from pptskill.schema import Outline
from pptskill.theme import Theme, apply_theme_tokens, resolve_theme


def _slide_theme(deck_theme: Theme, slide_cfg: dict, base_dir) -> Theme:
    theme_ref = slide_cfg.get("theme")
    tokens = slide_cfg.get("theme_tokens")
    theme = deck_theme
    if isinstance(theme_ref, str) and theme_ref.strip():
        theme = resolve_theme(theme_ref, base_dir=base_dir)
    if isinstance(tokens, dict) and tokens:
        theme = apply_theme_tokens(theme, tokens)
    return theme


def render_outline(
    outline: Outline,
    out_path: str | Path,
    theme_name: str | None = None,
    base_dir: str | Path | None = None,
    ensure_contrast: bool = False,
) -> Path:
    theme = resolve_theme(theme_name or outline.meta.theme, base_dir=base_dir)
    if ensure_contrast:
        from pptskill.contrast import ensure_contrast

        theme, _ = ensure_contrast(theme)
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    prs.core_properties.title = outline.meta.title
    prs.core_properties.author = outline.meta.author or "pptskill"
    prs.core_properties.subject = outline.meta.subtitle or outline.meta.title

    total = outline.slide_count()
    for i, slide_cfg in enumerate(outline.slides, start=1):
        st = _slide_theme(theme, slide_cfg, base_dir)
        if ensure_contrast:
            from pptskill.contrast import ensure_contrast

            st, _ = ensure_contrast(st)
        render_slide(prs, slide_cfg, st, page=i, total=total, base_dir=base_dir)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return out
