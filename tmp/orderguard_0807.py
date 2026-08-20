# -*- coding: utf-8 -*-
"""新着50件の「最早ticket日付」が投入時点から動いていないか照合する。
動くと新着リストの並びが変わってユーザーのチェック位置が崩れる（feedback_new_list_order_lock）。"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\user\oshinavi\tools")
from check_expired import extract_events_array  # noqa: E402


def earliest(e):
    ds = [t.get("date") for t in (e.get("tickets") or []) if t.get("date")]
    return min(ds) if ds else ""


base = {e["id"]: earliest(e) for e in
        json.load(open(r"C:\Users\user\oshinavi\tmp\built_0807.json", encoding="utf-8"))}
now = {e["id"]: earliest(e) for e in extract_events_array(r"C:\Users\user\oshinavi\index.html")
       if e["id"] in base}

ng = 0
for eid in sorted(base):
    if eid not in now:
        print("🚨 id%d が消えている" % eid)
        ng += 1
    elif base[eid] != now[eid]:
        print("🚨 id%d 最早日付が %s → %s に動いた" % (eid, base[eid], now[eid]))
        ng += 1
print("=== 投入時と比べて最早日付が動いたエントリ %d件 / %d件中 ===" % (ng, len(base)))
print("OK: 並び順は動いていない" if ng == 0 else "🚨 並び順が動く変更が入っている")
