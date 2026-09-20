"""Minimal stdio MCP-style JSON tool server for pptskill.

Protocol (one JSON object per line):
  {"id": "1", "tool": "render", "args": {...}}
  -> {"id": "1", "ok": true, "result": {...}} | {"id": "1", "ok": false, "error": "..."}

Run: python -m pptskill.mcp_server
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Callable

from pptskill import __version__
from pptskill.assets import check_assets, import_asset
from pptskill.export_png import export_png
from pptskill.qa import diagnose
from pptskill.render import render_outline
from pptskill.schema import SchemaError, load_outline
from pptskill.update import load_json, save_json, update_slide


def _ok(result: Any) -> dict:
    return {"ok": True, "result": result}


def _err(msg: str) -> dict:
    return {"ok": False, "error": msg}


def tool_validate(args: dict) -> dict:
    outline = load_outline(args["outline_path"])
    return _ok({"slide_count": outline.slide_count(), "theme": outline.meta.theme, "title": outline.meta.title})


def tool_render(args: dict) -> dict:
    path = args["outline_path"]
    outline = load_outline(path)
    out = render_outline(
        outline,
        args["output"],
        theme_name=args.get("theme"),
        base_dir=Path(path).resolve().parent,
    )
    return _ok({"path": str(out), "slides": outline.slide_count()})


def tool_qa(args: dict) -> dict:
    report = diagnose(
        args["pptx_path"],
        visual=bool(args.get("visual")),
        png_dir=args.get("png_dir"),
    )
    return _ok(report.to_dict())


def tool_export_png(args: dict) -> dict:
    pngs = export_png(
        args["pptx_path"],
        args["out_dir"],
        slides=args.get("slides"),
        width=int(args.get("width", 1280)),
        height=int(args.get("height", 720)),
    )
    return _ok({"pngs": [str(p) for p in pngs]})


def tool_update_slide(args: dict) -> dict:
    outline = load_json(args["outline_path"])
    new_outline = update_slide(outline, int(args["index"]), args["patch"])
    inplace = bool(args.get("inplace"))
    out_path = args.get("output")
    if not inplace and not out_path:
        return _err("update_slide requires output path or explicit inplace=true")
    target = args["outline_path"] if inplace else out_path
    saved = save_json(new_outline, target)
    return _ok({"path": str(saved), "inplace": inplace})


def tool_assets_check(args: dict) -> dict:
    path = args["outline_path"]
    outline = load_json(path)
    results = check_assets(outline, Path(path).resolve().parent)
    return _ok({"ok": all(r.get("ok") for r in results) if results else True, "assets": results})


def tool_assets_import(args: dict) -> dict:
    dest = import_asset(args["file"], args["to"], name=args.get("name"), max_side=args.get("max_side", 1600))
    return _ok({"path": str(dest)})


def tool_theme_extract(args: dict) -> dict:
    from pptskill.brand_extract import theme_from_logo, write_theme_json

    data = theme_from_logo(
        args["logo_path"],
        name=args.get("name") or "brand-extracted",
        extends=args.get("extends"),
        mode=args.get("mode") or "auto",
        max_colors=int(args.get("max_colors", 5)),
    )
    out = write_theme_json(data, args["output"])
    return _ok({"path": str(out), "theme": data})


def tool_content_check(args: dict) -> dict:
    from pptskill.content_check import DEFAULT_DENY, content_check, load_outline_dict

    raw = load_outline_dict(args["outline_path"])
    allow = args.get("allow") or []
    if isinstance(allow, str):
        allow = [t for t in allow.split(",") if t.strip()]
    extra = args.get("deny") or []
    if isinstance(extra, str):
        extra = [t for t in extra.split(",") if t.strip()]
    report = content_check(
        raw,
        deny=list(DEFAULT_DENY) + list(extra),
        allow=list(allow),
        expect_pages=args.get("expect_pages"),
        page_tolerance=int(args.get("page_tolerance", 2)),
        strict_notes=bool(args.get("strict_notes")),
    )
    return _ok(report.to_dict())


TOOLS: dict[str, Callable[[dict], dict]] = {
    "validate": tool_validate,
    "render": tool_render,
    "qa": tool_qa,
    "export_png": tool_export_png,
    "update_slide": tool_update_slide,
    "assets_check": tool_assets_check,
    "assets_import": tool_assets_import,
    "theme_extract": tool_theme_extract,
    "content_check": tool_content_check,
}


def handle_line(line: str) -> dict:
    try:
        req = json.loads(line)
    except json.JSONDecodeError as e:
        return {"id": None, **_err(f"invalid JSON: {e}")}
    rid = req.get("id")
    tool = req.get("tool")
    args = req.get("args") or {}
    if tool not in TOOLS:
        return {"id": rid, **_err(f"unknown tool: {tool!r}; available: {sorted(TOOLS)}")}
    try:
        out = TOOLS[tool](args)
        return {"id": rid, **out}
    except SchemaError as e:
        return {"id": rid, **_err(f"schema: {e}")}
    except Exception as e:
        return {"id": rid, **_err(f"{type(e).__name__}: {e}")}


def main(argv: list[str] | None = None) -> int:
    if argv and "--help" in argv:
        print(f"pptskill-mcp {__version__}")
        print("tools:", ", ".join(sorted(TOOLS)))
        print("stdin: one JSON request per line: {\"id\",\"tool\",\"args\"}")
        return 0
    if argv and "--list-tools" in argv:
        print(json.dumps(sorted(TOOLS)))
        return 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        resp = handle_line(line)
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
