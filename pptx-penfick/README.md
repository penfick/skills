# pptx-penfick

Generate PowerPoint decks from a structured **JSON outline** (layout templates + themes + QA).  
Agent owns research and outline content; this CLI owns rendering.

**GitHub**: part of [penfick/skills](https://github.com/penfick/skills) · Skill folder: `pptx-penfick/` · CLI package: `pptx-penfick` (alias: `pptskill`)

## Install CLI

```bash
# from this skills repo
cd pptx-penfick
uv sync && uv tool install --force .
# or
pip install -e .
```

```bash
pptx-penfick --help
pptx-penfick themes
```

## Quick start

```bash
pptx-penfick validate outline.json
pptx-penfick content-check outline.json --expect-pages 15
pptx-penfick render outline.json -o out/deck.pptx
pptx-penfick qa out/deck.pptx --visual
```

Example outline: `examples/mixed_deck.json` (schema sample only — do not copy its facts into other topics).

## Agent skill

Copy this folder’s `SKILL.md` into your agent skill root (directory name must stay `pptx-penfick`):

| Host | Path |
|------|------|
| MiMo Desktop | `~/.config/mimocode/skills/pptx-penfick/SKILL.md` |
| Claude Code | `~/.claude/skills/pptx-penfick/SKILL.md` |
| Other | `~/.agents/skills/pptx-penfick/SKILL.md` |

Or install via:

```bash
npx skills add https://github.com/penfick/skills --skill pptx-penfick -g -y
```

## Features

- 13 slide layouts (cover, chart, image_text, timeline, compare, kpi, …)
- Themes: builtins + custom JSON + logo color extract + contrast fix
- Structural QA + geometric QA + PowerPoint PNG export
- `content-check` heuristic (deny sample entities, page count)
- Per-slide theme override

## License

MIT (see repo root `LICENSE`).
