# -*- coding: utf-8 -*-
"""適用後の隠れ枠(startDate==date かつ date<=today)を全件列挙し、heal_stale.json の status と突き合わせる"""
import json, re, io, sys

TODAY = "2026-08-16"

raw = open("index.html", "rb").read().decode("utf-8")
m = re.search(r"  const EVENTS = (\[.*?\]);", raw, re.S)
if not m:
    print("events 配列が見つからない"); sys.exit(1)
events = json.loads(m.group(1))

heal = json.load(open("tmp/heal_stale.json", encoding="utf-8"))
status_by_id = {}
for h in heal:
    status_by_id[str(h.get("id"))] = h.get("status", "?")

hidden = []
for e in events:
    n = 0
    for t in e.get("tickets", []) or []:
        sd, dt = t.get("startDate"), t.get("date")
        if sd and dt and sd == dt and dt <= TODAY:
            n += 1
    if n:
        hidden.append((n, len(e.get("tickets") or []), str(e.get("id")), (e.get("artist") or e.get("title") or "")[:28]))

hidden.sort(key=lambda x: -x[0])
print("=== 適用後の隠れ枠 %d エントリ / %d 枠 ===" % (len(hidden), sum(h[0] for h in hidden)))
for n, tot, i, name in hidden:
    print("  id=%-5s 隠れ%2d/全%2d  status=%-12s %s" % (i, n, tot, status_by_id.get(i, "(走査外)"), name))

from collections import Counter
print()
print("statusごと:", dict(Counter(status_by_id.get(h[2], "(走査外)") for h in hidden)))
print("heal_stale.json 全体:", dict(Counter(h.get("status", "?") for h in heal)))
