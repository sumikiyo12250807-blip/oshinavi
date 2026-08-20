# -*- coding: utf-8 -*-
"""2026-08-12 朝バッチ：投入する50件を確定する。
- built_0812.json(40件) から 4126 吉川晃司を外す＝ぴあが発売日も締切も出しておらず
  公演日表記も過去(8/1)で信用できない（[[feedback_no_placeholder_dates]]）。
- built_0812b.json(12件) は先頭11件だけ採用＝1バッチ50件上限を守る。
- 4151 ITAMI GREENJAM’26 は _piaSub「音楽/フェスティバル」が対応表に無く engeki に
  倒れていた。屋外・複数組なので fes に直す（[[feedback_fes_definition]]）。
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DROP = {4126}
GENRE_FIX = {4151: "fes"}
LIMIT_B = 11

a = [e for e in json.load(open("tmp/built_0812.json", encoding="utf-8-sig")) if e["id"] not in DROP]
b = json.load(open("tmp/built_0812b.json", encoding="utf-8-sig"))[:LIMIT_B]
out = a + b
for e in out:
    if e["id"] in GENRE_FIX:
        print("  ジャンル下書き修正 id=%d %s → %s" % (e["id"], e["_genre"], GENRE_FIX[e["id"]]))
        e["_genre"] = GENRE_FIX[e["id"]]
    assert e.get("tickets"), "id=%d の枠が空" % e["id"]
    assert e.get("_genre"), "id=%d の下書きジャンルが空" % e["id"]

json.dump(out, open("tmp/all_new_0812.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import collections
print("投入対象 %d件 / id %d〜%d" % (len(out), out[0]["id"], out[-1]["id"]))
print("下書き内訳:", dict(collections.Counter(e["_genre"] for e in out)))
