# -*- coding: utf-8 -*-
"""今日発売(startDate==today)の枠を持つエントリをジャンル別に出す（X投稿の候補出し用）"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TODAY = "2026-08-01"
raw = open(r"C:\Users\user\oshinavi\index.html", "rb").read().decode("utf-8")
m = re.search(r"const EVENTS = (\[.*?\]);", raw, re.S)
evs = json.loads(m.group(1))

hits = []
for e in evs:
    if e.get("genre") == "new":
        continue
    sale = []
    for t in e.get("tickets") or []:
        sd = t.get("startDate")
        if sd == TODAY:
            sale.append(t)
    if sale:
        hits.append((e, sale))

print("今日(%s)発売の枠を持つエントリ: %d件" % (TODAY, len(hits)))
by_genre = {}
for e, sale in hits:
    g = e.get("genre") or "?"
    by_genre.setdefault(g, []).append((e, sale))

for g in sorted(by_genre, key=lambda x: -len(by_genre[x])):
    print("\n===== %s (%d件) =====" % (g, len(by_genre[g])))
    for e, sale in by_genre[g]:
        ex = ",".join(e.get("extraGenres") or [])
        print("  id=%s | %s | %s | %s | %s%s" % (
            e["id"], e.get("artist"), e.get("name"),
            e.get("prefecture"), e.get("dateLabel"),
            (" [+%s]" % ex) if ex else ""))
        for t in sale:
            print("        枠: %s" % t.get("type"))
