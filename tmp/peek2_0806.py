# -*- coding: utf-8 -*-
"""構築結果のサマリを出す（ファイル指定）。"""
import json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
built = json.load(open(sys.argv[1], encoding="utf-8-sig"))
for e in built:
    print("id%s [%s] %s" % (e["id"], e.get("_genre"), (e.get("artist") or "")[:44]))
    print("    %s | %s | 千秋楽 %s | 枠%d" % (
        (e.get("venue") or "")[:44], e.get("prefecture"), e.get("date"),
        len(e.get("tickets") or [])))
print("計", len(built), "件")
