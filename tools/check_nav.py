#!/usr/bin/env python3
"""Regression test: every sidebar shows the full titles of all 28 lectures."""
from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "manuscripts"
SITE = ROOT / "site"

expected = {}
for n, path in enumerate(sorted(SRC.glob("Lecture_*.md")), 1):
    assert re.search(rf"Lecture_{n:02}_", path.name), path.name
    source = path.read_text(encoding="utf-8-sig")
    match = re.search(r"^# (.+)$", source, flags=re.MULTILINE)
    assert match, path
    title = match.group(1).strip().replace("*", "")
    expected[n] = title.split("｜", 1)[-1]
assert len(expected) == 28, len(expected)

pattern = re.compile(
    r'<a class="nav-item [^"]*" href="lecture-(\d{2})\.html">(\d{2}) · ([^<]*)</a>'
)
pages = sorted(SITE.glob("*.html"))
assert len(pages) == 33, len(pages)
for page in pages:
    text = page.read_text(encoding="utf-8")
    links = pattern.findall(text)
    assert len(links) == 28, f"{page.name}: expected 28 sidebar links, got {len(links)}"
    for n, (path_num, label_num, actual_html) in enumerate(links, 1):
        assert path_num == label_num == f"{n:02}", (page.name, n, path_num, label_num)
        actual = html.unescape(actual_html)
        assert actual == expected[n], (
            f"{page.name}: lecture {n:02} title mismatch: {actual!r} != {expected[n]!r}"
        )
assert "[:26]" not in (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
print(f"Navigation PASS: {len(pages)} pages × {len(expected)} complete chapter titles")
