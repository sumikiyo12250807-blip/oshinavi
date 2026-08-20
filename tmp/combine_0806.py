# -*- coding: utf-8 -*-
"""投入用に35件(阪神統合済)＋補充15件を1つにまとめる。"""
import json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

a = json.load(open("tmp/built_0806_merged.json", encoding="utf-8-sig"))
b = json.load(open("tmp/built_refill_0806.json", encoding="utf-8-sig"))
for e in a:
    e.pop("_mergedFrom", None)          # 作業メモはデータに残さない
out = a + b
ids = [e["id"] for e in out]
assert len(ids) == len(set(ids)), "id重複"
json.dump(out, open("tmp/all_new_0806.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("投入セット %d件 (id %d..%d) → tmp/all_new_0806.json" % (len(out), min(ids), max(ids)))
print("枠合計 %d" % sum(len(e.get("tickets") or []) for e in out))
