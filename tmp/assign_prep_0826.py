# -*- coding: utf-8 -*-
"""振り分けの下ごしらえ。
project_vendor_genre_autoassign＝ジャンルはharvest時のぴあカテゴリで決まっている（再分類しない）。
人が判断するのは _piaSub が「〜その他」または空のものだけ。そこだけを抜き出す。"""
import json
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
pool = [e for e in json.loads(m.group(1)) if e.get("genre") == "new"]

need = []
auto = []
for e in pool:
    sub = e.get("_piaSub") or ""
    if (not sub) or ("その他" in sub):
        need.append(e)
    else:
        auto.append(e)

print("新着プール %d件 → 自動でジャンルが決まる %d件 / 人が決める %d件" % (len(pool), len(auto), len(need)))
print("")
print("=== 自動割り当ての内訳（_piaSub → _genre）===")
for k, v in Counter("%s → %s" % (e.get("_piaSub"), e.get("_genre")) for e in auto).most_common():
    print("  %-42s %d" % (k, v))

print("")
print("=== 🤔人が決める %d件（ぴあが「その他」に入れた子）===" % len(need))
for e in sorted(need, key=lambda x: x["id"]):
    print("")
    print("id=%-5d [下書き %s] %s" % (e["id"], e.get("_genre") or "-", e.get("artist")))
    print("      %s / %s / 公演%s / _piaSub=%s" % (
        e.get("venue"), e.get("prefecture"), e.get("date"), e.get("_piaSub") or "(なし)"))
    print("      %s" % ((e.get("links") or {}).get("pia")))
