from pathlib import Path

from pptx import Presentation

from pptskill.render import render_outline
from pptskill.schema import parse_outline


def test_compare_kpi_quote_render(tmp_path: Path):
    outline = parse_outline({
        "meta": {"title": "T"},
        "slides": [
            {
                "type": "compare",
                "title": "对比",
                "left": {"title": "A", "items": ["a1"]},
                "right": {"title": "B", "items": ["b1"], "highlight": True},
                "notes": "n1",
            },
            {
                "type": "kpi",
                "title": "指标",
                "cards": [
                    {"number": "1", "label": "one", "hint": "h"},
                    {"number": "2", "label": "two"},
                ],
                "notes": "n2",
            },
            {"type": "quote", "text": "引用内容", "cite": "某人", "notes": "n3"},
        ],
    })
    out = tmp_path / "deck.pptx"
    render_outline(outline, out)
    prs = Presentation(str(out))
    assert len(prs.slides) == 3
