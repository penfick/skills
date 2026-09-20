"""Incremental slide patching for outline JSON."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from pptskill.schema import parse_outline, SchemaError


def _deep_merge(base: dict, patch: dict) -> dict:
    out = deepcopy(base)
    for k, v in patch.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = deepcopy(v)
    return out


def update_slide(outline: dict[str, Any], index: int, patch: dict[str, Any]) -> dict[str, Any]:
    """Patch slides[index-1] (1-based). Returns new outline dict; validates result."""
    if index < 1:
        raise SchemaError(f"slide index must be >= 1, got {index}")
    slides = outline.get("slides")
    if not isinstance(slides, list) or index > len(slides):
        raise SchemaError(f"slide index {index} out of range (1..{len(slides) if isinstance(slides, list) else 0})")
    if not isinstance(patch, dict) or not patch:
        raise SchemaError("patch must be a non-empty object")
    new_outline = deepcopy(outline)
    new_outline["slides"][index - 1] = _deep_merge(new_outline["slides"][index - 1], patch)
    parse_outline(new_outline)  # raise if invalid
    return new_outline


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_json(data: dict[str, Any], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p
