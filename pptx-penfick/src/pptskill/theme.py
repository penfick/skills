"""Theme tokens for pptskill decks."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pptx.dml.color import RGBColor


def _rgb(hex_str: str) -> RGBColor:
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


@dataclass(frozen=True)
class Theme:
    name: str
    bg: RGBColor
    bg_light: RGBColor
    ink: RGBColor
    ink_on_light: RGBColor
    muted: RGBColor
    muted_on_light: RGBColor
    accent: RGBColor
    accent_soft: RGBColor
    card: RGBColor
    card_on_light: RGBColor
    border: RGBColor
    border_on_light: RGBColor
    series: tuple[RGBColor, ...] = ()
    font_latin: str = "Segoe UI"
    font_cjk: str = "Microsoft YaHei"

    def series_color(self, index: int) -> RGBColor:
        if not self.series:
            return self.accent
        return self.series[index % len(self.series)]


DARK_KEYNOTE = Theme(
    name="dark-keynote",
    bg=_rgb("#0D0D0D"),
    bg_light=_rgb("#F4F5F0"),
    ink=_rgb("#FFFFFF"),
    ink_on_light=_rgb("#1A1A1A"),
    muted=_rgb("#A0A6B0"),
    muted_on_light=_rgb("#6B7280"),
    accent=_rgb("#76B900"),
    accent_soft=_rgb("#E8F5C8"),
    card=_rgb("#1A1A1A"),
    card_on_light=_rgb("#FFFFFF"),
    border=_rgb("#2A2A2A"),
    border_on_light=_rgb("#E5E7EB"),
    series=(
        _rgb("#76B900"),
        _rgb("#3B82F6"),
        _rgb("#A855F7"),
        _rgb("#F59E0B"),
        _rgb("#64748B"),
    ),
)

LIGHT_CORPORATE = Theme(
    name="light-corporate",
    bg=_rgb("#F4F5F0"),
    bg_light=_rgb("#F4F5F0"),
    ink=_rgb("#1A1A1A"),
    ink_on_light=_rgb("#1A1A1A"),
    muted=_rgb("#6B7280"),
    muted_on_light=_rgb("#6B7280"),
    accent=_rgb("#1F3A5F"),
    accent_soft=_rgb("#E8EEF6"),
    card=_rgb("#FFFFFF"),
    card_on_light=_rgb("#FFFFFF"),
    border=_rgb("#E5E7EB"),
    border_on_light=_rgb("#E5E7EB"),
    series=(
        _rgb("#1F3A5F"),
        _rgb("#2F6FED"),
        _rgb("#0D9488"),
        _rgb("#D97706"),
        _rgb("#64748B"),
    ),
)

EDUCATION_BLUE = Theme(
    name="education-blue",
    bg=_rgb("#F7F9FC"),
    bg_light=_rgb("#F7F9FC"),
    ink=_rgb("#0F172A"),
    ink_on_light=_rgb("#0F172A"),
    muted=_rgb("#475569"),
    muted_on_light=_rgb("#475569"),
    accent=_rgb("#2563EB"),
    accent_soft=_rgb("#DBEAFE"),
    card=_rgb("#FFFFFF"),
    card_on_light=_rgb("#FFFFFF"),
    border=_rgb("#E2E8F0"),
    border_on_light=_rgb("#E2E8F0"),
    series=(
        _rgb("#2563EB"),
        _rgb("#06B6D4"),
        _rgb("#8B5CF6"),
        _rgb("#F59E0B"),
        _rgb("#64748B"),
    ),
)

PITCH_GREEN = Theme(
    name="pitch-green",
    bg=_rgb("#0B1F17"),
    bg_light=_rgb("#F3FBF6"),
    ink=_rgb("#FFFFFF"),
    ink_on_light=_rgb("#052E16"),
    muted=_rgb("#86EFAC"),
    muted_on_light=_rgb("#166534"),
    accent=_rgb("#22C55E"),
    accent_soft=_rgb("#DCFCE7"),
    card=_rgb("#123527"),
    card_on_light=_rgb("#FFFFFF"),
    border=_rgb("#1F4D38"),
    border_on_light=_rgb("#DCFCE7"),
    series=(
        _rgb("#22C55E"),
        _rgb("#14B8A6"),
        _rgb("#EAB308"),
        _rgb("#38BDF8"),
        _rgb("#94A3B8"),
    ),
)

THEMES: dict[str, Theme] = {
    "dark-keynote": DARK_KEYNOTE,
    "light-corporate": LIGHT_CORPORATE,
    "education-blue": EDUCATION_BLUE,
    "pitch-green": PITCH_GREEN,
}

# --- R4 extras + custom JSON loader ---

MINIMAL_MONO = Theme(
    name="minimal-mono",
    bg=_rgb("#FAFAFA"),
    bg_light=_rgb("#FAFAFA"),
    ink=_rgb("#111111"),
    ink_on_light=_rgb("#111111"),
    muted=_rgb("#6B7280"),
    muted_on_light=_rgb("#6B7280"),
    accent=_rgb("#111111"),
    accent_soft=_rgb("#F3F4F6"),
    card=_rgb("#FFFFFF"),
    card_on_light=_rgb("#FFFFFF"),
    border=_rgb("#E5E7EB"),
    border_on_light=_rgb("#E5E7EB"),
    series=(
        _rgb("#111111"),
        _rgb("#525252"),
        _rgb("#A3A3A3"),
        _rgb("#D4D4D4"),
        _rgb("#737373"),
    ),
)

FINANCE_NAVY = Theme(
    name="finance-navy",
    bg=_rgb("#0A1628"),
    bg_light=_rgb("#F7F8FA"),
    ink=_rgb("#FFFFFF"),
    ink_on_light=_rgb("#0F172A"),
    muted=_rgb("#94A3B8"),
    muted_on_light=_rgb("#475569"),
    accent=_rgb("#C9A227"),
    accent_soft=_rgb("#FDF6E3"),
    card=_rgb("#122036"),
    card_on_light=_rgb("#FFFFFF"),
    border=_rgb("#1E3A5F"),
    border_on_light=_rgb("#E2E8F0"),
    series=(
        _rgb("#C9A227"),
        _rgb("#1D4ED8"),
        _rgb("#0F766E"),
        _rgb("#B45309"),
        _rgb("#64748B"),
    ),
)

WARM_EDITORIAL = Theme(
    name="warm-editorial",
    bg=_rgb("#1C1410"),
    bg_light=_rgb("#FFF8F0"),
    ink=_rgb("#FFF7ED"),
    ink_on_light=_rgb("#1C1410"),
    muted=_rgb("#D6C4B0"),
    muted_on_light=_rgb("#78716C"),
    accent=_rgb("#C2410C"),
    accent_soft=_rgb("#FFEDD5"),
    card=_rgb("#2A1F18"),
    card_on_light=_rgb("#FFFFFF"),
    border=_rgb("#3D2E24"),
    border_on_light=_rgb("#F5E6D8"),
    series=(
        _rgb("#C2410C"),
        _rgb("#B45309"),
        _rgb("#0F766E"),
        _rgb("#A16207"),
        _rgb("#78716C"),
    ),
)

THEMES["minimal-mono"] = MINIMAL_MONO
THEMES["finance-navy"] = FINANCE_NAVY
THEMES["warm-editorial"] = WARM_EDITORIAL

COLOR_KEYS = (
    "bg", "bg_light", "ink", "ink_on_light", "muted", "muted_on_light",
    "accent", "accent_soft", "card", "card_on_light", "border", "border_on_light",
)


class ThemeError(ValueError):
    """Invalid theme name or theme JSON."""


def _parse_color(value: Any, key: str) -> RGBColor:
    if not isinstance(value, str):
        raise ThemeError(f"theme.{key} must be a hex string")
    h = value.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) != 6 or any(c not in "0123456789abcdefABCDEF" for c in h):
        raise ThemeError(f"theme.{key} invalid color: {value!r}")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def apply_theme_tokens(base: Theme, tokens: dict[str, Any], *, name: str | None = None) -> Theme:
    """Merge color/series/font tokens onto an existing Theme (no extends registry)."""
    if not isinstance(tokens, dict) or not tokens:
        raise ThemeError("theme_tokens must be a non-empty object")
    data = {"name": name or base.name, **tokens}
    # use base directly; ignore extends if present in tokens
    data.pop("extends", None)
    kwargs: dict[str, Any] = {"name": str(data.get("name") or base.name)}
    for key in COLOR_KEYS:
        if key in data:
            kwargs[key] = _parse_color(data[key], key)
        else:
            kwargs[key] = getattr(base, key)
    series_in = data.get("series")
    if series_in is None:
        kwargs["series"] = base.series
    else:
        if not isinstance(series_in, list) or not series_in:
            raise ThemeError("theme.series must be a non-empty array")
        kwargs["series"] = tuple(_parse_color(c, f"series[{i}]") for i, c in enumerate(series_in))
    kwargs["font_latin"] = str(data.get("font_latin") or base.font_latin)
    kwargs["font_cjk"] = str(data.get("font_cjk") or base.font_cjk)
    return Theme(**kwargs)


def theme_from_dict(data: dict, *, base: Theme | None = None, default_base: str = "light-corporate") -> Theme:
    if not isinstance(data, dict):
        raise ThemeError("theme JSON root must be an object")
    extends = data.get("extends") or default_base
    if extends not in THEMES:
        raise ThemeError(f"unknown extends theme: {extends!r}")
    base_t = base or THEMES[extends]
    kwargs: dict[str, Any] = {"name": str(data.get("name") or base_t.name)}
    for key in COLOR_KEYS:
        if key in data:
            kwargs[key] = _parse_color(data[key], key)
        else:
            kwargs[key] = getattr(base_t, key)
    series_in = data.get("series")
    if series_in is None:
        series = base_t.series
    else:
        if not isinstance(series_in, list) or not series_in:
            raise ThemeError("theme.series must be a non-empty array")
        series = tuple(_parse_color(c, f"series[{i}]") for i, c in enumerate(series_in))
    kwargs["series"] = series
    kwargs["font_latin"] = str(data.get("font_latin") or base_t.font_latin)
    kwargs["font_cjk"] = str(data.get("font_cjk") or base_t.font_cjk)
    return Theme(**kwargs)


def load_theme_file(path: str | Path, *, base_dir: str | Path | None = None) -> Theme:
    p = Path(path)
    if not p.is_absolute() and base_dir is not None:
        p = Path(base_dir) / p
    p = p.resolve()
    if not p.exists():
        raise ThemeError(f"theme file not found: {p}")
    import json

    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception as e:
        raise ThemeError(f"invalid theme JSON: {e}") from e
    return theme_from_dict(data)


def is_theme_path_ref(name: str | None) -> bool:
    return bool(name) and str(name).lower().endswith(".json")


def resolve_theme(name: str | None, *, base_dir: str | Path | None = None) -> Theme:
    if not name:
        return DARK_KEYNOTE
    if is_theme_path_ref(name):
        return load_theme_file(name, base_dir=base_dir)
    if name not in THEMES:
        raise ThemeError(f"unknown theme: {name!r}; available: {sorted(THEMES)} or a .json path")
    return THEMES[name]


def get_theme(name: str | None) -> Theme:
    # backward-compatible: builtin names only; paths need resolve_theme with base_dir
    if not name:
        return DARK_KEYNOTE
    if is_theme_path_ref(name):
        return load_theme_file(name)
    if name not in THEMES:
        raise KeyError(f"unknown theme: {name!r}; available: {sorted(THEMES)}")
    return THEMES[name]


def list_themes() -> list[str]:
    return sorted(THEMES)
