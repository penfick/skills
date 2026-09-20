"""CJK-safe font helpers for python-pptx runs."""
from __future__ import annotations

from pptx.oxml.ns import qn


def set_cjk_font(run, font_name: str = "Microsoft YaHei", latin_name: str | None = None) -> None:
    """Set a:latin, a:ea, a:cs so mixed CJK/Latin text renders correctly."""
    latin = latin_name or font_name
    run.font.name = latin
    rPr = run._r.get_or_add_rPr()
    successors = {
        "a:ea": ("a:cs", "a:sym", "a:hlinkClick", "a:hlinkMouseOver", "a:rtl", "a:extLst"),
        "a:cs": ("a:sym", "a:hlinkClick", "a:hlinkMouseOver", "a:rtl", "a:extLst"),
    }
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            rPr.insert_element_before(el, *successors[tag])
        el.set("typeface", font_name)
    latin_el = rPr.find(qn("a:latin"))
    if latin_el is None:
        latin_el = rPr.makeelement(qn("a:latin"), {})
        rPr.insert_element_before(
            latin_el,
            "a:ea",
            "a:cs",
            "a:sym",
            "a:hlinkClick",
            "a:hlinkMouseOver",
            "a:rtl",
            "a:extLst",
        )
    latin_el.set("typeface", latin)


def style_run(run, *, size=16, bold=False, color=None, font_cjk="Microsoft YaHei", font_latin="Segoe UI") -> None:
    from pptx.util import Pt

    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    set_cjk_font(run, font_cjk, font_latin)
