# -*- coding: utf-8 -*-
"""削除候補のURLを index.html から機械抽出する（捏造禁止・実データのみ）"""
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

IDS = [int(x) for x in sys.argv[1].split(",")]

src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
events = json.loads(m.group(1))

by_id = {e["id"]: e for e in events}
for i in IDS:
    e = by_id.get(i)
    if e is None:
        print("id=%d NOT FOUND" % i)
        continue
    links = e.get("links") or {}
    print("id=%d | %s | %s | 公演日 %s | %s" % (i, e.get("artist"), e.get("venue"), e.get("date"), e.get("prefecture")))
    for k in ("pia", "rakuten", "lawson", "eplus"):
        if links.get(k):
            print("    %-7s %s" % (k, links[k]))
    for t in e.get("tickets", []):
        print("    枠: %s | date=%s | soldout=%s | url=%s" % (t.get("type"), t.get("date"), t.get("soldout"), t.get("url")))
    print("")
