#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""削除候補の確認用URLを機械抽出して出す（捏造禁止・実データのみ）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
sys.stdout.reconfigure(encoding="utf-8")
from heal_stale_deadlines import load_events, pia_urls  # noqa: E402

IDS = [134, 274, 435, 883, 932, 954, 961, 1268, 1275, 1916, 2282, 2457,
       2783, 3080, 3242, 3279, 3467, 3670, 4010, 4076, 2605, 187]

with open("index.html", "rb") as f:
    h = f.read().decode("utf-8")
_m, EVENTS = load_events(h)
evs = {e.get("id"): e for e in EVENTS}
for i in IDS:
    e = evs.get(i)
    if not e:
        print(f"id={i} NOT FOUND")
        continue
    urls = pia_urls(e)
    links = e.get("links") or {}
    other = {k: v for k, v in links.items() if k != "pia" and v}
    print(f"id={i}\t{e.get('name')}\t{e.get('venue')}\t公演日={e.get('date')}\tsoldout={e.get('soldout')}")
    print(f"\tpia={urls[0] if urls else '(なし)'}\tother={other if other else '-'}")
