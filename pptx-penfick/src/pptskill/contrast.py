"""WCAG-style contrast helpers and theme autofix."""
from __future__ import annotations

import colorsys
from dataclasses import dataclass, replace

from pptx.dml.color import RGBColor

from pptskill.theme import Theme


def _channel(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(color: RGBColor) -> float:
    r, g, b = color[0], color[1], color[2]
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(a: RGBColor, b: RGBColor) -> float:
    la = relative_luminance(a)
    lb = relative_luminance(b)
    lighter, darker = (la, lb) if la >= lb else (lb, la)
    return (lighter + 0.05) / (darker + 0.05)


def _rgb_to_hls(color: RGBColor) -> tuple[float, float, float]:
    return colorsys.rgb_to_hls(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)


def _hls_to_rgb(h: float, l: float, s: float) -> RGBColor:
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, l)), max(0.0, min(1.0, s)))
    return RGBColor(int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def adjust_for_contrast(
    fg: RGBColor,
    bg: RGBColor,
    *,
    min_ratio: float = 4.5,
    max_steps: int = 24,
) -> RGBColor:
    """Shift fg lightness toward contrast target, preserving hue/sat.

    Tries the preferred direction first, then the opposite; keeps the best ratio.
    """
    if contrast_ratio(fg, bg) >= min_ratio:
        return fg
    h, l, s = _rgb_to_hls(fg)
    bg_lum = relative_luminance(bg)
    directions = (0.04, -0.04) if bg_lum < 0.45 else (-0.04, 0.04)
    best = fg
    best_ratio = contrast_ratio(fg, bg)
    for direction in directions:
        ll = l
        for _ in range(max_steps):
            ll = max(0.0, min(1.0, ll + direction))
            cand = _hls_to_rgb(h, ll, s)
            ratio = contrast_ratio(cand, bg)
            if ratio > best_ratio:
                best, best_ratio = cand, ratio
            if ratio >= min_ratio:
                return cand
    return best


@dataclass
class ContrastReport:
    pair: str
    ratio: float
    target: float
    ok: bool
    before: str
    after: str


def ensure_contrast(theme: Theme, *, min_body: float = 4.5, min_muted: float = 3.0) -> tuple[Theme, list[ContrastReport]]:
    reports: list[ContrastReport] = []

    def fix_pair(name: str, fg: RGBColor, bg: RGBColor, target: float) -> RGBColor:
        before = contrast_ratio(fg, bg)
        out = adjust_for_contrast(fg, bg, min_ratio=target)
        after = contrast_ratio(out, bg)
        reports.append(ContrastReport(
            pair=name,
            ratio=round(after, 2),
            target=target,
            ok=after >= target - 0.01,
            before=f"#{fg[0]:02X}{fg[1]:02X}{fg[2]:02X}",
            after=f"#{out[0]:02X}{out[1]:02X}{out[2]:02X}",
        ))
        return out

    ink = fix_pair("ink/bg", theme.ink, theme.bg, min_body)
    ink_l = fix_pair("ink_on_light/bg_light", theme.ink_on_light, theme.bg_light, min_body)
    muted = fix_pair("muted/bg", theme.muted, theme.bg, min_muted)
    muted_l = fix_pair("muted_on_light/bg_light", theme.muted_on_light, theme.bg_light, min_muted)

    new = replace(
        theme,
        ink=ink,
        ink_on_light=ink_l,
        muted=muted,
        muted_on_light=muted_l,
    )
    return new, reports


def format_reports(reports: list[ContrastReport]) -> str:
    lines = []
    for r in reports:
        flag = "OK" if r.ok else "LOW"
        lines.append(f"[{flag}] {r.pair}: {r.ratio} (target {r.target}) {r.before} -> {r.after}")
    return "\n".join(lines)
