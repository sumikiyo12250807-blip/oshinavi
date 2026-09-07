# -*- coding: utf-8 -*-
"""明日(2026-09-09)発売の枠を機械抽出して、ジャンル別に並べる（夜のX投稿の候補出し）。"""
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

TOMORROW = "2026-09-09"

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

rows = []
for e in EVENTS:
    for t in e.get("tickets") or []:
        if t.get("startDate") != TOMORROW:
            continue
        rows.append((e, t))

bygenre = collections.defaultdict(list)
for e, t in rows:
    bygenre[e.get("genre") or "-"].append((e, t))

print("=== 明日 %s 発売の枠 %d本 / %dジャンル ===" % (TOMORROW, len(rows), len(bygenre)))
for g in sorted(bygenre, key=lambda x: -len(bygenre[x])):
    print("")
    print("--- %s : %d本 ---" % (g, len(bygenre[g])))
    for e, t in bygenre[g]:
        print("  id=%-5d %-34s @%-26s 公演%s" % (
            e["id"], (e.get("artist") or "")[:34], (e.get("venue") or "")[:26], e.get("date")))
        print("        %s" % t.get("type"))
