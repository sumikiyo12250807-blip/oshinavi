# -*- coding: utf-8 -*-
"""2026-08-12：新着50件チェックの結果をユーザー判断どおりに反映する。
- 4133 Age Factory／ENTH／Paledusk … jpop ＋extraGenres rock
- 4144 Age Factory                  … jpop ＋extraGenres rock（rock 単独から変更・2エントリで揃える）
- 4129 トップガン マーヴェリック シネマコンサート … classic ＋extraGenres yougaku
主は「ぴあカテゴリ由来のジャンル」を採る。genre は "new" のまま（振り分けは別工程）。
[[feedback_genre_both_when_unclear]]
"""
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0812_genre2"
FIX = {
    4133: ("jpop", ["rock"]),
    4144: ("jpop", ["rock"]),
    4129: ("classic", ["yougaku"]),
}


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
for eid, (g, extra) in FIX.items():
    i, j = entry_span(src, eid)
    body = src[i:j]
    old = re.search(r'"_genre": "([^"]*)"', body).group(1)
    body2 = re.sub(r'"_genre": "[^"]*"', '"_genre": "%s"' % g, body)
    items = "".join('\r\n      "%s",' % x for x in extra).rstrip(",")
    body2 = re.sub(r'"_extraGenres": \[[^\]]*\]',
                   '"_extraGenres": [%s\r\n    ]' % items, body2)
    assert '"_extraGenres": [\r\n      "%s"' % extra[0] in body2, "id=%d の extra 置換失敗" % eid
    src = src[:i] + body2 + src[j:]
    print("  id=%d _genre %s→%s / _extraGenres=[%s]" % (eid, old, g, ", ".join(extra)))

out = src.encode("utf-8")
assert len(re.findall(rb"(?<!\r)\n", out)) == 0, "単独LFが混ざった"
open(P, "wb").write(out)
print("書き込み完了 (backup: %s)" % BAK)
