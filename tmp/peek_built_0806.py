# -*- coding: utf-8 -*-
"""構築済みエントリの中身を確認する（id指定 or 名前部分一致）。"""
import json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
built = json.load(open("tmp/built_0806.json", encoding="utf-8-sig"))
key = sys.argv[1] if len(sys.argv) > 1 else "阪神"
for e in built:
    if key not in (e.get("artist") or ""):
        continue
    print("== id%s %s" % (e["id"], e.get("artist")))
    print("   venue=%s / pref=%s / date=%s / _genre=%s" % (
        e.get("venue"), e.get("prefecture"), e.get("date"), e.get("_genre")))
    print("   dateLabel=%s" % e.get("dateLabel"))
    print("   pia=%s" % (e.get("links") or {}).get("pia"))
    for t in e.get("tickets") or []:
        print("     -", json.dumps(t, ensure_ascii=False))
