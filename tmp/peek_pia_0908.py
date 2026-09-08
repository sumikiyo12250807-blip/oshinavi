# -*- coding: utf-8 -*-
"""ぴあの公演ページの見出し（ツアー名が入っている場所）を1件だけ覗く。"""
import io, re, sys
sys.path.insert(0, 'tools')
from build_pia_entries import fetch  # noqa: E402

h = fetch("https://t.pia.jp/pia/event/event.do?eventCd=2626860")
io.open("tmp/peek_pia_0908.html", "w", encoding="utf-8").write(h)
o = io.open("tmp/peek_pia_0908.txt", "w", encoding="utf-8")
for m in re.finditer(r"<h([12345])[^>]*>(.*?)</h\1>", h, re.S):
    t = re.sub(r"<[^>]+>", " ", m.group(2))
    o.write("h%s: %s\n" % (m.group(1), re.sub(r"\s+", " ", t).strip()[:200]))
o.write("---- class に name/ttl/title を含む要素 ----\n")
for m in re.finditer(r'<(\w+)[^>]*class="([^"]*(?:name|ttl|title|Title|Name)[^"]*)"[^>]*>(.*?)</\1>', h, re.S):
    t = re.sub(r"<[^>]+>", " ", m.group(3))
    t = re.sub(r"\s+", " ", t).strip()
    if t:
        o.write("%s | %s\n" % (m.group(2)[:50], t[:160]))
o.close()
print("ok")
