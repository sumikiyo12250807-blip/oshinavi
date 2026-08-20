# -*- coding: utf-8 -*-
"""投入した50件の要約（ジャンル内訳・発売日の近さ・一覧）。"""
import collections
import datetime
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
TODAY = datetime.date(2026, 8, 7)

evs = json.load(open(r"C:\Users\user\oshinavi\tmp\built_0807.json", encoding="utf-8"))
print("投入 %d件 (id %d..%d)\n" % (len(evs), evs[0]["id"], evs[-1]["id"]))
print("下書きジャンル: %s\n" % dict(collections.Counter(e.get("_genre") for e in evs)))

rows = []
for e in evs:
    starts = []
    for t in e.get("tickets") or []:
        sd = t.get("startDate")
        if sd:
            starts.append(sd)
    s = min(starts) if starts else ""
    rows.append((s, e["id"], (e.get("artist") or "")[:34], e.get("date", ""), e.get("prefecture", "")))
rows.sort()
for s, eid, art, d, pref in rows:
    print("  %s  id%-5d %-36s 公演%s %s" % (s or "(発売中)", eid, art, d, pref))
