# -*- coding: utf-8 -*-
"""新着プールのe+由来49件を、下書きジャンルつきで棚卸しする（振り分け前の確認）。"""
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))


def src(e):
    blob = json.dumps(e, ensure_ascii=False)
    if "t.pia.jp" in blob or "ticket.pia.jp" in blob:
        return "pia"
    if "eplus.jp" in blob:
        return "eplus"
    return "other"


pool = sorted([e for e in EVENTS if e.get("genre") == "new" and src(e) == "eplus"],
              key=lambda e: e["id"])
print("e+由来の新着 = %d件" % len(pool))

cnt = collections.Counter(e.get("_genre") or "（下書き無し）" for e in pool)
print("下書きジャンルの内訳: %s" % dict(cnt))
print("")

for e in pool:
    g = e.get("_genre") or "🚨下書き無し"
    print("id=%-5d %-10s %-34s @%-24s 公演%s"
          % (e["id"], g, (e.get("artist") or "")[:34],
             (e.get("venue") or "")[:24], e.get("date")))
