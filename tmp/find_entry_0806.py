# -*- coding: utf-8 -*-
"""登録済みindex.htmlから名前部分一致でエントリを探す。"""
import json, re, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src = open("index.html", "rb").read().decode("utf-8")
m = re.search(r"  const EVENTS = (\[.*?\]);", src, re.S)
data = json.loads(m.group(1))
key = sys.argv[1]
for e in data:
    blob = (e.get("artist") or "") + (e.get("name") or "")
    if key in blob:
        print("id%-5s %-14s %s | %s | %s" % (
            e["id"], e.get("genre"), (e.get("artist") or "")[:44],
            e.get("date"), (e.get("dateLabel") or "")[:40]))
