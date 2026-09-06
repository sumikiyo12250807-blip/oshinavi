# -*- coding: utf-8 -*-
"""ピックアップのタイル差し替え候補を、index.html から機械で抜く。
🚨名前とidを手で写さない（取り違え防止）。9/7〜9/13に発売が始まる枠を持つことも同時に確かめる。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

FROM, TO = "2026-09-07", "2026-09-13"
CAND = [3118, 3422, 3053, 4103, 1109, 4538, 177, 5664, 5050, 710, 4230, 6141,
        2317, 3406, 696, 4496, 799, 615, 3471, 4690, 2254, 4741]

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
byid = {e["id"]: e for e in json.loads(m.group(2))}

for eid in CAND:
    e = byid.get(eid)
    if not e:
        print("🚨 id=%d が無い" % eid)
        continue
    days = sorted({t.get("startDate") for t in (e.get("tickets") or [])
                   if t.get("startDate") and FROM <= t.get("startDate") <= TO})
    mark = "OK " if days else "🚨 "
    print('%s("%s", %d),   # 発売 %s / %s'
          % (mark, e.get("artist") or e.get("name"), eid,
             ",".join(d[5:] for d in days), (e.get("venue") or "")[:34]))
