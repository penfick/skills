"""Extract a brand theme JSON from a local logo image (Pillow only)."""
from __future__ import annotations

import colorsys
import json
from pathlib import Path
from typing import Any

from PIL import Image

from pptskill.theme import theme_from_dict


class BrandExtractError(ValueError):
    """Logo extract failed."""


def _to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def _rgb_to_hls(r: int, g: int, b: int) -> tuple[float, float, float]:
    return colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)


def _lighten(r: int, g: int, b: int, amount: float = 0.35) -> tuple[int, int, int]:
    h, l, s = _rgb_to_hls(r, g, b)
    l = min(1.0, l + amount)
    rr, gg, bb = colorsys.hls_to_rgb(h, l, s)
    return int(rr * 255), int(gg * 255), int(bb * 255)


def _saturation(r: int, g: int, b: int) -> float:
    _, _, s = _rgb_to_hls(r, g, b)
    return s


def _luminance(r: int, g: int, b: int) -> float:
    # perceptual-ish
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def extract_palette(
    image_path: str | Path,
    *,
    max_colors: int = 5,
    max_side: int = 200,
) -> list[tuple[int, int, int, float]]:
    """Return list of (r,g,b, weight) sorted by importance."""
    p = Path(image_path)
    if not p.exists():
        raise BrandExtractError(f"logo not found: {p}")
    try:
        im = Image.open(p)
        im.load()
    except Exception as e:
        raise BrandExtractError(f"cannot decode logo: {p} ({e})") from e

    im = im.convert("RGBA")
    # composite onto white so transparent pixels do not become black
    white = Image.new("RGBA", im.size, (255, 255, 255, 255))
    base = Image.alpha_composite(white, im).convert("RGB")
    w, h = base.size
    scale = max_side / max(w, h)
    if scale < 1:
        base = base.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.BILINEAR)
    quant = base.quantize(colors=16, method=Image.Quantize.MEDIANCUT)
    pal = quant.getpalette() or []
    counts = quant.getcolors(256) or []

    items: list[tuple[int, int, int, float]] = []
    total = sum(c for c, _ in counts) or 1
    for count, idx in counts:
        if idx * 3 + 2 >= len(pal):
            continue
        r, g, b = pal[idx * 3], pal[idx * 3 + 1], pal[idx * 3 + 2]
        s = _saturation(r, g, b)
        lum = _luminance(r, g, b)
        if s < 0.08 and (lum > 0.94 or lum < 0.08):
            continue
        weight = (count / total) * (0.35 + s)
        items.append((r, g, b, weight))

    if not items:
        from collections import Counter

        px = list(base.getdata())
        for (r, g, b), c in Counter(px).most_common(5):
            items.append((r, g, b, c / max(len(px), 1)))

    items.sort(key=lambda t: t[3], reverse=True)
    # dedupe similar
    picked: list[tuple[int, int, int, float]] = []
    for r, g, b, wgt in items:
        if any(abs(r - pr) + abs(g - pg) + abs(b - pb) < 40 for pr, pg, pb, _ in picked):
            continue
        picked.append((r, g, b, wgt))
        if len(picked) >= max(8, max_colors * 2):
            break
    return picked


def pick_accent(palette: list[tuple[int, int, int, float]]) -> tuple[int, int, int]:
    if not palette:
        return (0x1F, 0x3A, 0x5F)
    ranked = sorted(
        palette,
        key=lambda t: (_saturation(t[0], t[1], t[2]) * 0.7 + t[3] * 0.3),
        reverse=True,
    )
    r, g, b, _ = ranked[0]
    if _saturation(r, g, b) < 0.12:
        for rr, gg, bb, _w in palette:
            if _saturation(rr, gg, bb) >= 0.12:
                return (rr, gg, bb)
        return (0x1F, 0x3A, 0x5F)  # gray-only fallback
    return (r, g, b)


def theme_from_logo(
    logo_path: str | Path,
    *,
    name: str = "brand-extracted",
    extends: str | None = None,
    mode: str = "auto",
    max_colors: int = 5,
) -> dict[str, Any]:
    if mode not in {"auto", "light", "dark"}:
        raise BrandExtractError("mode must be auto|light|dark")
    palette = extract_palette(logo_path, max_colors=max_colors)
    accent = pick_accent(palette)
    soft = _lighten(*accent, 0.45)
    series = []
    for r, g, b, _w in palette:
        hexc = _to_hex(r, g, b)
        if hexc not in series:
            series.append(hexc)
        if len(series) >= 5:
            break
    acc_hex = _to_hex(*accent)
    if acc_hex not in series:
        series.insert(0, acc_hex)
    # diversify only when series is effectively single-color (logo is one brand color)
    if len(set(series)) < 2:
        h, l, s = _rgb_to_hls(*accent)
        extras = []
        for delta in (0.08, -0.12, 0.2, -0.25):
            nh = (h + delta) % 1.0
            rr, gg, bb = colorsys.hls_to_rgb(nh, min(0.72, max(0.35, l)), max(0.35, min(0.85, s)))
            extras.append(_to_hex(int(rr * 255), int(gg * 255), int(bb * 255)))
        series = [acc_hex] + extras
    series = series[:5]
    while len(series) < 5:
        series.append(series[-1])

    if mode == "auto":
        mode = "light" if _luminance(*accent) > 0.55 else "dark"
    if not extends:
        extends = "light-corporate" if mode == "light" else "dark-keynote"

    return {
        "name": name,
        "extends": extends,
        "accent": acc_hex,
        "accent_soft": _to_hex(*soft),
        "series": series,
    }


def write_theme_json(data: dict[str, Any], output: str | Path) -> Path:
    # validate via loader
    theme_from_dict(data)
    p = Path(output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p
