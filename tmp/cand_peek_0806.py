# -*- coding: utf-8 -*-
"""ハーベスト候補jsonの中身をジャンル別に一覧する。"""
import json, io, sys, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
path = sys.argv[1] if len(sys.argv) > 1 else "tmp/cand_new.json"
cands = json.load(open(path, encoding="utf-8"))
by = collections.defaultdict(list)
for c in cands:
    by[c.get("_genre") or c.get("genre") or "?"].append(c)
for g, rows in sorted(by.items(), key=lambda kv: -len(kv[1])):
    print("== %s %d件" % (g, len(rows)))
    for c in rows:
        print("   %s %s | 発売 %s" % (c.get("newid"), (c.get("artist") or "")[:38], c.get("_rlsdate") or c.get("rlsdate") or ""))
print("計", len(cands), "件")
print("キー例:", json.dumps(cands[0], ensure_ascii=False)[:400])
