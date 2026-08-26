# -*- coding: utf-8 -*-
"""投入しないものを built から外す。
 - 5309 / 5311 … eventCd が既存と一致＝同じ興行なので統合に回す（投入すると分裂する）
 - 5323 …………… 最終締切が2日後＝もうじき終わる枠は載せない
   （feedback_harvest_source_order_and_far_deadline）"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

DROP = {5309, 5311, 5323}
rows = json.load(open("tmp/built_0826.json", encoding="utf-8"))
keep = [e for e in rows if e["id"] not in DROP]
json.dump(keep, open("tmp/built_final_0826.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("投入 %d件（除外 %s）" % (len(keep), sorted(DROP)))
print("id: %s" % ",".join(str(e["id"]) for e in keep))
