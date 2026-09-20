"""Export PPTX slides to PNG via PowerPoint COM (Windows)."""
from __future__ import annotations

import json
import re
from pathlib import Path


class ExportError(RuntimeError):
    """PNG export failed."""


def parse_slide_spec(spec: str | None, total: int) -> list[int]:
    if not spec or not str(spec).strip():
        return list(range(1, total + 1))
    out: list[int] = []
    for part in str(spec).split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    seen: list[int] = []
    for i in out:
        if 1 <= i <= total and i not in seen:
            seen.append(i)
    return seen


def export_png(
    pptx_path: str | Path,
    out_dir: str | Path,
    *,
    slides: str | None = None,
    width: int = 1280,
    height: int = 720,
) -> list[Path]:
    pptx_path = Path(pptx_path).resolve()
    out_dir = Path(out_dir).resolve()
    if not pptx_path.exists():
        raise ExportError(f"pptx not found: {pptx_path}")
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        import win32com.client  # type: ignore
    except Exception:
        win32com = None
    # Use comtypes-free dynamic dispatch via win32com if available;
    # otherwise fall back to PowerShell COM bridge.

    pngs: list[Path] = []
    try:
        pngs = _export_via_powershell(pptx_path, out_dir, slides, width, height)
    except Exception as e:
        raise ExportError(f"PowerPoint PNG export failed: {e}") from e

    manifest = {
        "pptx": str(pptx_path),
        "pngs": [str(p) for p in pngs],
        "width": width,
        "height": height,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return pngs


def _export_via_powershell(pptx_path: Path, out_dir: Path, slides: str | None, width: int, height: int) -> list[Path]:
    import subprocess
    import tempfile

    # First get slide count via python-pptx
    from pptx import Presentation

    prs = Presentation(str(pptx_path))
    total = len(prs.slides)
    if total == 0:
        raise ExportError("presentation has no slides")
    indices = parse_slide_spec(slides, total)

    # Build a small PowerShell script
    ps = r"""
$ErrorActionPreference = 'Stop'
$pptx = $env:PPTX_PATH
$outDir = $env:OUT_DIR
$w = [int]$env:OUT_W
$h = [int]$env:OUT_H
$indices = $env:SLIDE_INDICES -split ',' | Where-Object { $_ } | ForEach-Object { [int]$_ }
$pp = New-Object -ComObject PowerPoint.Application
try {
  $pres = $pp.Presentations.Open($pptx, $true, $false, $false)
  foreach ($i in $indices) {
    $path = Join-Path $outDir ("slide-{0}.png" -f $i)
    $pres.Slides.Item($i).Export($path, "PNG", $w, $h)
    Write-Output $path
  }
  $pres.Close()
} finally {
  $pp.Quit()
}
"""
    env = {
        **__import__("os").environ,
        "PPTX_PATH": str(pptx_path),
        "OUT_DIR": str(out_dir),
        "OUT_W": str(width),
        "OUT_H": str(height),
        "SLIDE_INDICES": ",".join(str(i) for i in indices),
    }
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as f:
        f.write(ps)
        script = f.name
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script],
        capture_output=True,
        text=True,
        env=env,
        timeout=180,
    )
    if proc.returncode != 0:
        raise ExportError(proc.stderr or proc.stdout or f"exit {proc.returncode}")
    pngs = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.lower().endswith(".png") and Path(line).exists():
            pngs.append(Path(line))
    if not pngs:
        raise ExportError("export produced no PNG files")
    return pngs
