from pathlib import Path

from pptskill.content_check import content_check


def _outline(slides):
    return {"meta": {"title": "T", "theme": "light-corporate"}, "slides": slides}


def test_deny_entity_fails():
    raw = _outline([
        {"type": "cover", "title": "OpenAI", "notes": "n"},
        {"type": "title_body", "title": "业务", "bullets": ["数据中心 GPU NVIDIA"], "notes": "n"},
    ])
    r = content_check(raw)
    assert not r.ok
    assert any(f.code == "deny_entity" for f in r.findings)


def test_allow_entity_passes():
    raw = _outline([
        {"type": "cover", "title": "NVIDIA 公司介绍", "notes": "n"},
        {"type": "title_body", "title": "GPU", "bullets": ["CUDA"], "notes": "n"},
    ])
    r = content_check(raw, allow=["nvidia", "cuda"])
    assert r.ok


def test_expect_pages():
    raw = _outline([
        {"type": "cover", "title": "A", "notes": "n"},
        {"type": "closing", "title": "B", "notes": "n"},
    ])
    r = content_check(raw, expect_pages=15, page_tolerance=2)
    assert not r.ok
    assert any(f.code == "page_count" for f in r.findings)


def test_cli_content_check(tmp_path: Path):
    import json
    from pptskill.cli import main

    p = tmp_path / "o.json"
    p.write_text(json.dumps(_outline([
        {"type": "cover", "title": "GeForce", "notes": "n"},
    ])), encoding="utf-8")
    assert main(["content-check", str(p)]) == 4
    p2 = tmp_path / "ok.json"
    p2.write_text(json.dumps(_outline([
        {"type": "cover", "title": "My Deck", "notes": "n"},
    ])), encoding="utf-8")
    assert main(["content-check", str(p2)]) == 0
