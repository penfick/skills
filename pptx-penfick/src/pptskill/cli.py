"""pptskill CLI."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pptskill import __version__
from pptskill.assets import check_assets, import_asset
from pptskill.export_png import ExportError, export_png
from pptskill.images import ImageError
from pptskill.qa import diagnose, write_report
from pptskill.render import render_outline
from pptskill.schema import SchemaError, load_outline
from pptskill.update import load_json, save_json, update_slide

EXIT_OK = 0
EXIT_SCHEMA = 2
EXIT_RENDER = 3
EXIT_QA = 4


def _cmd_content_check(args: argparse.Namespace) -> int:
    from pptskill.content_check import content_check, load_outline_dict

    try:
        raw = load_outline_dict(args.outline)
    except Exception as e:
        print(f"content-check error: {e}", file=sys.stderr)
        return EXIT_SCHEMA
    allow = [t for t in (args.allow or "").split(",") if t.strip()]
    extra = [t for t in (args.deny or "").split(",") if t.strip()]
    from pptskill.content_check import DEFAULT_DENY

    deny = list(DEFAULT_DENY) + extra
    report = content_check(
        raw,
        deny=deny,
        allow=allow,
        expect_pages=args.expect_pages,
        page_tolerance=args.page_tolerance,
        strict_notes=bool(args.strict_notes),
    )
    if args.json:
        Path(args.json).write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return EXIT_OK if report.ok else EXIT_QA


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        outline = load_outline(args.outline)
    except SchemaError as e:
        print(f"schema error: {e}", file=sys.stderr)
        return EXIT_SCHEMA
    print(f"OK: {outline.slide_count()} slides, theme={outline.meta.theme}, title={outline.meta.title}")
    return EXIT_OK


def _cmd_render(args: argparse.Namespace) -> int:
    try:
        outline = load_outline(args.outline)
    except SchemaError as e:
        print(f"schema error: {e}", file=sys.stderr)
        return EXIT_SCHEMA
    try:
        base_dir = Path(args.outline).resolve().parent
        theme = args.theme
        if theme and str(theme).lower().endswith(".json"):
            cand = Path(theme)
            if cand.is_absolute():
                theme = str(cand)
            elif cand.exists():
                theme = str(cand.resolve())
            else:
                alt = base_dir / cand
                if alt.exists():
                    theme = str(alt.resolve())
                else:
                    theme = str(base_dir / cand)  # error message will show outline-relative path
        out = render_outline(
            outline,
            args.output,
            theme_name=theme,
            base_dir=base_dir,
            ensure_contrast=bool(args.ensure_contrast),
        )
    except Exception as e:
        print(f"render error: {e}", file=sys.stderr)
        return EXIT_RENDER
    print(f"rendered: {out} ({outline.slide_count()} slides)")
    return EXIT_OK


def _cmd_qa(args: argparse.Namespace) -> int:
    report = diagnose(args.pptx, visual=bool(args.visual), png_dir=args.png_dir)
    if args.json:
        write_report(report, args.json)
        print(f"report: {args.json}")
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return EXIT_OK if report.ok else EXIT_QA


def _cmd_export_png(args: argparse.Namespace) -> int:
    try:
        pngs = export_png(
            args.pptx,
            args.out_dir,
            slides=args.slides,
            width=args.width,
            height=args.height,
        )
    except ExportError as e:
        print(f"export error: {e}", file=sys.stderr)
        return EXIT_RENDER
    print(f"exported {len(pngs)} png(s) -> {args.out_dir}")
    for p in pngs:
        print(p)
    return EXIT_OK


def _cmd_update_slide(args: argparse.Namespace) -> int:
    try:
        outline = load_json(args.outline)
        patch = load_json(args.patch)
        new_outline = update_slide(outline, args.index, patch)
    except (SchemaError, OSError, json.JSONDecodeError) as e:
        print(f"update error: {e}", file=sys.stderr)
        return EXIT_SCHEMA
    if args.inplace:
        out = save_json(new_outline, args.outline)
    else:
        if not args.output:
            print("update error: require --output or --inplace", file=sys.stderr)
            return EXIT_SCHEMA
        out = save_json(new_outline, args.output)
    print(f"updated slide {args.index} -> {out}")
    return EXIT_OK


def _cmd_assets_check(args: argparse.Namespace) -> int:
    outline = load_json(args.outline)
    base = Path(args.outline).resolve().parent
    results = check_assets(outline, base)
    print(json.dumps({"ok": all(r.get("ok") for r in results) if results else True, "assets": results},
                     ensure_ascii=False, indent=2))
    return EXIT_OK if all(r.get("ok") for r in results) else EXIT_SCHEMA


def _cmd_assets_import(args: argparse.Namespace) -> int:
    try:
        dest = import_asset(args.file, args.to, name=args.name, max_side=args.max_side)
    except ImageError as e:
        print(f"import error: {e}", file=sys.stderr)
        return EXIT_RENDER
    print(f"imported: {dest}")
    return EXIT_OK


def _cmd_theme_fix(args: argparse.Namespace) -> int:
    from pptskill.contrast import ensure_contrast, format_reports
    from pptskill.theme import COLOR_KEYS, resolve_theme

    try:
        theme = resolve_theme(str(args.theme))
        fixed, reports = ensure_contrast(
            theme,
            min_body=args.min_contrast,
            min_muted=max(3.0, args.min_contrast - 1.5),
        )
        data = {"name": fixed.name, "extends": theme.name if theme.name != fixed.name else "light-corporate"}
        for key in COLOR_KEYS:
            c = getattr(fixed, key)
            data[key] = f"#{c[0]:02X}{c[1]:02X}{c[2]:02X}"
        data["series"] = [f"#{c[0]:02X}{c[1]:02X}{c[2]:02X}" for c in fixed.series]
        data["font_latin"] = fixed.font_latin
        data["font_cjk"] = fixed.font_cjk
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception as e:
        print(f"fix error: {e}", file=sys.stderr)
        return EXIT_RENDER
    print(format_reports(reports))
    print(f"theme written: {out}")
    if args.strict and not all(r.ok for r in reports):
        return EXIT_QA
    return EXIT_OK


def _cmd_themes(args: argparse.Namespace) -> int:
    from pptskill.theme import list_themes

    print(json.dumps({"themes": list_themes()}, ensure_ascii=False, indent=2))
    return EXIT_OK


def _cmd_theme_extract(args: argparse.Namespace) -> int:
    from pptskill.brand_extract import BrandExtractError, theme_from_logo, write_theme_json

    try:
        data = theme_from_logo(
            args.logo,
            name=args.name or "brand-extracted",
            extends=args.extends,
            mode=args.mode,
            max_colors=args.max_colors,
        )
        out = write_theme_json(data, args.output)
    except BrandExtractError as e:
        print(f"extract error: {e}", file=sys.stderr)
        return EXIT_RENDER
    except Exception as e:
        print(f"extract error: {e}", file=sys.stderr)
        return EXIT_RENDER
    print(f"theme written: {out}")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pptskill", description="JSON outline → PPTX renderer")
    p.add_argument("--version", action="version", version=f"pptskill {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate", help="validate outline JSON schema")
    v.add_argument("outline", type=Path)
    v.set_defaults(func=_cmd_validate)

    r = sub.add_parser("render", help="render outline to .pptx")
    r.add_argument("outline", type=Path)
    r.add_argument("-o", "--output", type=Path, required=True)
    r.add_argument("--theme", default=None,
                   help="override theme (builtin name or path to .json; see `pptskill themes`)")
    r.add_argument("--ensure-contrast", action="store_true",
                   help="auto-adjust ink/muted tokens for WCAG contrast before render")
    r.set_defaults(func=_cmd_render)

    q = sub.add_parser("qa", help="structural / visual QA on a .pptx")
    q.add_argument("pptx", type=Path)
    q.add_argument("--json", type=Path, default=None, help="write QA report JSON")
    q.add_argument("--visual", action="store_true", help="add geometric overflow/aspect checks")
    q.add_argument("--png-dir", type=Path, default=None, help="attach exported PNG paths to report")
    q.set_defaults(func=_cmd_qa)

    cc = sub.add_parser("content-check", help="heuristic outline integrity (deny entities, page count)")
    cc.add_argument("outline", type=Path)
    cc.add_argument("--expect-pages", type=int, default=None)
    cc.add_argument("--page-tolerance", type=int, default=2)
    cc.add_argument("--allow", default=None, help="comma-separated terms to allow")
    cc.add_argument("--deny", default=None, help="extra deny terms, comma-separated")
    cc.add_argument("--strict-notes", action="store_true")
    cc.add_argument("--json", type=Path, default=None)
    cc.set_defaults(func=_cmd_content_check)

    e = sub.add_parser("export-png", help="export slides to PNG via PowerPoint COM")
    e.add_argument("pptx", type=Path)
    e.add_argument("--out-dir", type=Path, required=True)
    e.add_argument("--slides", default=None, help="e.g. 1,3-5")
    e.add_argument("--width", type=int, default=1280)
    e.add_argument("--height", type=int, default=720)
    e.set_defaults(func=_cmd_export_png)

    u = sub.add_parser("update-slide", help="patch one slide in an outline JSON")
    u.add_argument("outline", type=Path)
    u.add_argument("--index", type=int, required=True, help="1-based slide index")
    u.add_argument("--patch", type=Path, required=True, help="JSON patch object")
    u.add_argument("-o", "--output", type=Path, default=None)
    u.add_argument("--inplace", action="store_true")
    u.set_defaults(func=_cmd_update_slide)

    a = sub.add_parser("assets", help="local image asset helpers")
    asub = a.add_subparsers(dest="assets_cmd", required=True)
    ac = asub.add_parser("check", help="check image paths in outline")
    ac.add_argument("outline", type=Path)
    ac.set_defaults(func=_cmd_assets_check)
    ai = asub.add_parser("import", help="copy/normalize image into assets dir")
    ai.add_argument("file", type=Path)
    ai.add_argument("--to", type=Path, required=True)
    ai.add_argument("--name", default=None)
    ai.add_argument("--max-side", type=int, default=1600)
    ai.set_defaults(func=_cmd_assets_import)

    th = sub.add_parser("themes", help="list builtin theme names")
    th.set_defaults(func=_cmd_themes)

    tsub = sub.add_parser("theme", help="theme utilities")
    tcmds = tsub.add_subparsers(dest="theme_cmd", required=True)
    te = tcmds.add_parser("extract", help="extract theme JSON from a local logo image")
    te.add_argument("logo", type=Path)
    te.add_argument("-o", "--output", type=Path, required=True)
    te.add_argument("--name", default="brand-extracted")
    te.add_argument("--extends", default=None, help="base builtin theme name")
    te.add_argument("--mode", default="auto", choices=["auto", "light", "dark"])
    te.add_argument("--max-colors", type=int, default=5)
    te.set_defaults(func=_cmd_theme_extract)

    tf = tcmds.add_parser("fix", help="auto-adjust theme tokens for contrast")
    tf.add_argument("theme", type=Path)
    tf.add_argument("-o", "--output", type=Path, required=True)
    tf.add_argument("--min-contrast", type=float, default=4.5)
    tf.add_argument("--strict", action="store_true", help="exit 4 if any pair still low")
    tf.set_defaults(func=_cmd_theme_fix)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
