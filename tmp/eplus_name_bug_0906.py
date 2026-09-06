# -*- coding: utf-8 -*-
"""e+由来の新着で「artist が name の先頭1語だけ」になっている壊れた名前を数える。

🚨2026-09-06発見＝a flood of circle が「a」、Bunkamura Production… が「Bunkamura」、
YOU SOCK FESTIVAL が「YOU」になっていた。このまま振り分けるとサイトに
「a」「YOU」「Project」というカードが並ぶ＝探しに来た人が見つけられない。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))


def is_eplus(e):
    return "eplus.jp" in json.dumps(e, ensure_ascii=False)


pool = sorted([e for e in EVENTS if e.get("genre") == "new" and is_eplus(e)],
              key=lambda e: e["id"])

bad, ok = [], []
for e in pool:
    a = (e.get("artist") or "").strip()
    n = (e.get("name") or "").strip()
    # artist が name の先頭にあり、かつ name のほうが明らかに長い＝切り出しの疑い
    if a and n and n != a and n.startswith(a) and len(n) > len(a) + 2:
        bad.append((e, a, n))
    else:
        ok.append(e)

print("e+の新着 %d件 中" % len(pool))
print("  🚨 artist が name の先頭を切り出しただけ = %d件" % len(bad))
print("  ✅ そのままでよさそう              = %d件" % len(ok))
print("")
for e, a, n in bad:
    print("id=%-5d 「%s」 → 本当は「%s」" % (e["id"], a, n[:60]))
print("")
print("--- そのままでよさそうな %d件 ---" % len(ok))
for e in ok:
    print("id=%-5d %-12s %s" % (e["id"], e.get("_genre") or "下書き無し",
                                (e.get("artist") or "")[:40]))
