# -*- coding: utf-8 -*-
"""e+検索で「噛み合った」候補を、登録エントリと並べて読める形に出す（2026-08-07）。"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

rows = json.load(open(r"C:\Users\user\oshinavi\tmp\eplus_newpool_0807.json", encoding="utf-8"))
n = 0
for r in rows:
    if not r["hits"]:
        continue
    n += 1
    print("=" * 78)
    print("id%d %s" % (r["id"], r["artist"]))
    print("   登録: %s %s / 千秋楽 %s" % (r["pref"], (r["venue"] or "")[:52], r["date"]))
    for h in r["hits"]:
        print("   e+ : %s | sub=%s | %s(%s) | %s | 受付〜%s" % (
            h["koenbi"] or "日付なし", h["sub"][:28], h["venue"][:24], h["pref"],
            h["status"][:16], h["end"] or "-"))
        print("        %s" % h["url"])
print("\n=== 候補のあるエントリ %d件 ===" % n)
