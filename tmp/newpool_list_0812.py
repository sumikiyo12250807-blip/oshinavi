#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""genre:new のプールをレビュー用にマークダウン表で出す（id昇順固定・番号はidに紐づけ）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
sys.stdout.reconfigure(encoding="utf-8")
from heal_stale_deadlines import load_events  # noqa: E402

with open("index.html", "rb") as f:
    h = f.read().decode("utf-8")
_m, EVENTS = load_events(h)
new = sorted([e for e in EVENTS if e.get("genre") == "new"], key=lambda e: e["id"])

print("| id | アーティスト/公演 | 公演日 | 会場(県) | ジャンル下書き | 枠 | URL |")
print("|---|---|---|---|---|---|---|")
for e in new:
    links = e.get("links") or {}
    url = links.get("pia") or links.get("eplus") or links.get("rakuten") or ""
    label = "ぴあ" if "pia" in url else ("e+" if "eplus" in url else ("楽天" if url else "-"))
    venue = e.get("venue") or ""
    if len(venue) > 28:
        venue = venue[:28] + "…"
    sub = e.get("_piaSub") or ""
    g = e.get("_genre") or "?"
    if not sub:
        g += "※"
    print("| %d | %s | %s | %s(%s) | %s | %d | [%s](%s) |" % (
        e["id"], e.get("name"), e.get("date"), venue, e.get("prefecture"), g,
        len(e.get("tickets") or []), label, url))
print()
print("※＝ぴあがカテゴリを返さず名前で判断したもの")
