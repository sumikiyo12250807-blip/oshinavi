# -*- coding: utf-8 -*-
"""新着プールの下書きジャンルを一覧し、人の判断が要るものを抜き出す（2026-08-05）。

ぴあカテゴリ(_piaSub)がそのまま使える子は触らない約束（[[project_vendor_genre_autoassign]]）。
人が見るのは _piaSub が空／「その他」系＝名前fallbackで決まった子だけ。
おまけで「締切が目前の枠」も出す（載せた翌日に消えるものを把握するため）。
"""
import datetime
import io
import json
import os
import re
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"
TODAY = datetime.date(2026, 8, 5)

h = io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
EVENTS = json.loads(re.search(r"const EVENTS\s*=\s*(\[.*?\]);", h, re.S).group(1))
pool = [e for e in EVENTS if e.get("genre") == "new"]

c = Counter()
for e in pool:
    g = e.get("_genre") or "?"
    ex = e.get("_extraGenres") or []
    c[g + ("+" + ",".join(ex) if ex else "")] += 1
print("=== 下書きジャンルの内訳（%d件）===" % len(pool))
for k, v in c.most_common():
    print("   %-18s %d件" % (k, v))

print("\n=== 人の判断が要る子（_piaSubが空 or その他系）===")
n = 0
for e in sorted(pool, key=lambda x: x["id"]):
    sub = e.get("_piaSub") or ""
    if sub and "その他" not in sub:
        continue
    n += 1
    print("   id%-5d _genre=%-9s _piaSub=%-22s %s" % (
        e["id"], e.get("_genre"), sub or "(空)", (e.get("artist") or "")[:44]))
print("   → %d件" % n)

print("\n=== 締切が目前の枠（〜8/8）===")
rows = []
for e in pool:
    for t in e.get("tickets") or []:
        try:
            d = datetime.date(*map(int, (t.get("date") or "").split("-")))
        except Exception:
            continue
        if TODAY <= d <= TODAY + datetime.timedelta(days=3) and not t.get("startDate"):
            rows.append((d, e["id"], (e.get("artist") or "")[:40], (t.get("type") or "")[:52]))
for d, eid, art, ty in sorted(rows):
    print("   %s id%-5d %-40s %s" % (d, eid, art, ty))
print("   → %d枠" % len(rows))
