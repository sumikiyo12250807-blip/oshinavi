# -*- coding: utf-8 -*-
"""新着プール（genre:"new"）の現状を数える。投入元・発売前/受付中の比率も出す。"""
import json, re, io
from collections import Counter

TODAY = "2026-09-04"
html = io.open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))
pool = [e for e in events if e.get("genre") == "new"]

src = Counter()
presale = 0
onsale = 0
nourl = 0
buf = []
for e in pool:
    links = e.get("links") or {}
    for k in ("pia", "eplus", "rakuten", "lawson"):
        if links.get(k):
            src[k] += 1
            break
    else:
        src["(なし)"] += 1
    ts = e.get("tickets", [])
    if any((t.get("startDate") or "") > TODAY for t in ts):
        presale += 1
    else:
        onsale += 1
    nourl += sum(1 for t in ts if not t.get("url"))
    buf.append("id=%-5s %-8s %s | %s | 枠%d" % (
        e.get("id"), e.get("_genre") or "-", (e.get("name") or "")[:44],
        e.get("dateLabel", "")[:40], len(ts)))

io.open("tmp/newpool_0904.txt", "w", encoding="utf-8").write("\n".join(buf))
print("POOL=%d" % len(pool))
print("SOURCE=%s" % dict(src))
print("PRESALE(これから発売)=%d  ALREADY_ONSALE=%d" % (presale, onsale))
print("SLOTS_WITHOUT_URL=%d" % nourl)
ids = sorted(e.get("id") for e in pool)
print("ID_RANGE=%s..%s" % (ids[0], ids[-1]) if ids else "EMPTY")
print("IDS=" + ",".join(str(i) for i in ids))
