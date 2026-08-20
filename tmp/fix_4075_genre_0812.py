# -*- coding: utf-8 -*-
"""2026-08-12：4075 昭和・平成歌謡ナイト Vol.3 のジャンル下書きを
ユーザー判断（Jpopと演歌）に合わせる＝_genre:"jpop" + _extraGenres:["enka"]。
genre は "new" のまま（振り分けはユーザーの合図待ち）。
"""
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0812_genre4075"


def entry_span(src, eid):
    m = re.search(r'\n\s*\{\s*"id": %d,' % eid, src)
    if not m:
        raise SystemExit("id=%d が見つからない" % eid)
    i = src.index("{", m.start())
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return i, j + 1


shutil.copyfile(P, BAK)
src = open(P, "rb").read().decode("utf-8")
i, j = entry_span(src, 4075)
body = src[i:j]
assert '"_genre": "enka"' in body, "_genre が enka でない：" + body[:400]
new = body.replace('"_genre": "enka"', '"_genre": "jpop"')
new = new.replace('"_extraGenres": [],', '"_extraGenres": [\r\n      "enka"\r\n    ],')
assert '"_extraGenres": [\r\n      "enka"' in new, "_extraGenres の置換に失敗"
src = src[:i] + new + src[j:]
out = src.encode("utf-8")
assert len(re.findall(rb"(?<!\r)\n", out)) == 0, "単独LFが混ざった"
open(P, "wb").write(out)
print("id=4075 _genre=jpop / _extraGenres=[enka] に更新 (backup: %s)" % BAK)
