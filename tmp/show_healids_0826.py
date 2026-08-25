# -*- coding: utf-8 -*-
"""tmp/heal_ids.json から指定idの再構築結果だけを取り出して見る。"""
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

IDS = set(int(x) for x in sys.argv[1].split(","))
rows = json.load(open("tmp/heal_ids.json", encoding="utf-8"))
for r in rows:
    if r.get("id") in IDS:
        print("id=%s status=%s %s" % (r.get("id"), r.get("status"), r.get("artist")))
        for t in r.get("tickets") or []:
            print("   - %s | date=%s | startDate=%s | url=%s" % (
                t.get("type"), t.get("date"), t.get("startDate"), t.get("url")))
        print("")
