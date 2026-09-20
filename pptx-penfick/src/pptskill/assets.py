"""Local asset check/import helpers (no network)."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from PIL import Image

from pptskill.images import ImageError, resolve_image_path


def collect_image_paths(outline: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for slide in outline.get("slides") or []:
        if not isinstance(slide, dict):
            continue
        img = slide.get("image")
        if isinstance(img, dict) and img.get("path"):
            paths.append(str(img["path"]))
    return paths


def check_assets(outline: dict[str, Any], base_dir: str | Path) -> list[dict[str, Any]]:
    base = Path(base_dir)
    results: list[dict[str, Any]] = []
    for rel in collect_image_paths(outline):
        item: dict[str, Any] = {"path": rel}
        try:
            p = resolve_image_path(rel, base)
            item["ok"] = True
            item["resolved"] = str(p)
            with Image.open(p) as im:
                item["size"] = list(im.size)
        except (ImageError, Exception) as e:
            item["ok"] = False
            item["error"] = str(e)
        results.append(item)
    return results


def import_asset(
    src: str | Path,
    dest_dir: str | Path,
    *,
    name: str | None = None,
    max_side: int | None = 1600,
) -> Path:
    src_p = Path(src).resolve()
    if not src_p.exists() or not src_p.is_file():
        raise ImageError(f"source not found: {src_p}")
    dest_dir_p = Path(dest_dir).resolve()
    dest_dir_p.mkdir(parents=True, exist_ok=True)
    out_name = name or src_p.name
    dest = dest_dir_p / out_name
    # validate + optional resize
    with Image.open(src_p) as im:
        im = im.convert("RGB") if im.mode not in ("RGB", "L") else im
        if max_side:
            w, h = im.size
            scale = max_side / max(w, h)
            if scale < 1:
                im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
        ext = dest.suffix.lower()
        if ext in {".jpg", ".jpeg"}:
            im.save(dest, format="JPEG", quality=88, optimize=True)
        elif ext == ".png":
            im.save(dest, format="PNG", optimize=True)
        else:
            # default jpeg
            dest = dest.with_suffix(".jpg")
            im.save(dest, format="JPEG", quality=88, optimize=True)
    return dest
