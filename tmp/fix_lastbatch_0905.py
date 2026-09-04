# -*- coding: utf-8 -*-
"""9/4に投入した新着は50件でなく93件だった（6501-6550 / 6601-6616 / 6701-6732 / 6800 / 6901-6902）。
last_batch.json の 9/4 morning の記録を実データに合わせて直し、追加分を追記する。"""
import json, re, io

STATE = ".claude/state/last_batch.json"

html = io.open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))
new_ids = sorted(e["id"] for e in events if e.get("genre") == "new")

# 連続する id を区間にまとめる
ranges = []
for i in new_ids:
    if ranges and i == ranges[-1][1] + 1:
        ranges[-1][1] = i
    else:
        ranges.append([i, i])

d = json.load(io.open(STATE, encoding="utf-8"))
b = d["batches"][-1]
assert b["date"] == "2026-09-04" and b["slot"] == "morning", b
b["count"] = len(new_ids)
b["id_to"] = new_ids[-1]
b["id_ranges"] = ["%d-%d" % (a, z) if a != z else str(a) for a, z in ranges]
b["note"] = ("9/4は50件で切らず未掲載を全部入れた＝計%d件（%s）。"
             "reconcile --new は9/4に通過済み。9/5朝に独立再照合と振り分けを行う。"
             % (len(new_ids), " / ".join(b["id_ranges"])))
json.dump(d, io.open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("UPDATED count=%d ranges=%s" % (len(new_ids), b["id_ranges"]))
