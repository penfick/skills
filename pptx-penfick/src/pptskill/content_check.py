"""Heuristic content integrity checks on outline JSON."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

DEFAULT_DENY = (
    "NVIDIA",
    "NVDA",
    "GeForce",
    "Jensen Huang",
    "Jensen",
    "黄仁勋",
    "CUDA",
    "DGX",
    "Blackwell",
    "Hopper",
    "Omniverse",
    "Mellanox",
)


@dataclass
class Finding:
    level: str  # error | warn
    code: str
    msg: str
    slide: int | None = None


@dataclass
class ContentReport:
    ok: bool
    findings: list[Finding] = field(default_factory=list)
    slide_count: int = 0

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "slide_count": self.slide_count,
            "findings": [asdict(f) for f in self.findings],
        }


def _iter_strings(obj: Any, prefix: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(obj, str):
        yield prefix, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _iter_strings(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _iter_strings(v, f"{prefix}[{i}]")


def _slide_index_from_path(path: str) -> int | None:
    m = re.match(r"slides\[(\d+)\]", path)
    return int(m.group(1)) + 1 if m else None


def content_check(
    outline: dict[str, Any],
    *,
    deny: Iterable[str] | None = None,
    allow: Iterable[str] | None = None,
    expect_pages: int | None = None,
    page_tolerance: int = 2,
    strict_notes: bool = False,
) -> ContentReport:
    findings: list[Finding] = []
    slides = outline.get("slides") or []
    slide_count = len(slides) if isinstance(slides, list) else 0

    deny_terms = [t for t in (deny if deny is not None else DEFAULT_DENY) if t]
    allow_set = {t.lower() for t in (allow or []) if t}
    deny_lower = [(t, t.lower()) for t in deny_terms if t.lower() not in allow_set]

    # full-text scan
    text_blob_parts: list[str] = []
    for path, s in _iter_strings(outline):
        text_blob_parts.append(s)
        low = s.lower()
        for term, term_low in deny_lower:
            if term_low in low:
                findings.append(Finding(
                    level="error",
                    code="deny_entity",
                    msg=f"forbidden entity {term!r} at {path}",
                    slide=_slide_index_from_path(path),
                ))
    blob = "\n".join(text_blob_parts).lower()
    # catch a few segment phrases from sample decks when they appear as chart categories
    sample_segments = ("专业可视化", "data center gaming", "geforce rtx")
    for seg in sample_segments:
        if seg.lower() in blob and seg.lower() not in allow_set:
            findings.append(Finding(
                level="error",
                code="sample_segment",
                msg=f"looks like sample-deck segment language: {seg!r}",
            ))

    if expect_pages is not None:
        if abs(slide_count - int(expect_pages)) > int(page_tolerance):
            findings.append(Finding(
                level="error",
                code="page_count",
                msg=f"slide_count={slide_count} expect={expect_pages} tolerance={page_tolerance}",
            ))

    if isinstance(slides, list):
        for i, sl in enumerate(slides, start=1):
            if not isinstance(sl, dict):
                continue
            notes = sl.get("notes")
            if not isinstance(notes, str) or not notes.strip():
                findings.append(Finding(
                    level="error" if strict_notes else "warn",
                    code="missing_notes",
                    msg=f"slide {i} missing notes",
                    slide=i,
                ))

    ok = not any(f.level == "error" for f in findings)
    return ContentReport(ok=ok, findings=findings, slide_count=slide_count)


def load_outline_dict(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))
