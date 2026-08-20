# -*- coding: utf-8 -*-
"""ハーベスト在庫(tmp/presale_*.json)を名前部分一致で検索する。"""
import json, glob, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
key = sys.argv[1]
for f in sorted(glob.glob("tmp/presale_*_0806.json")):
    try:
        rows = json.load(open(f, encoding="utf-8-sig"))
    except Exception as e:
        print("skip", f, e)
        continue
    if isinstance(rows, dict):
        rows = rows.get("new") or rows.get("items") or rows.get("rows") or []
    for r in rows:
        s = json.dumps(r, ensure_ascii=False)
        if key in s:
            print(f.split("\\")[-1], "|", s[:220])
