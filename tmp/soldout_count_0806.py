# -*- coding: utf-8 -*-
"""soldout:true の枠が今どれくらい使われているか数える。"""
import json, re, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src = open("index.html", "rb").read().decode("utf-8")
m = re.search(r"  const EVENTS = (\[.*?\]);", src, re.S)
data = json.loads(m.group(1))
n = 0
for e in data:
    for t in e.get("tickets") or []:
        if t.get("soldout"):
            n += 1
            print(e["id"], (e.get("artist") or "")[:26], "|", t.get("type", "")[:52], "|", t.get("date"))
print("soldout枠 計", n)
