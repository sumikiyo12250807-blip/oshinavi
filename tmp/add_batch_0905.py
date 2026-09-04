# -*- coding: utf-8 -*-
"""今朝投入したバッチを .claude/state/last_batch.json に記録する（翌朝の再チェックで使う）。"""
import json, io

STATE = ".claude/state/last_batch.json"
d = json.load(io.open(STATE, encoding="utf-8"))

# 9/4分は振り分け・再チェック済みに更新
for b in d["batches"]:
    if b["date"] == "2026-09-04" and b["slot"] == "morning":
        b["assigned"] = True
        b["rechecked"] = True
        b["note"] = (b.get("note", "") +
                     " 9/5朝に再チェック＝91件を振り分け（logs/assigned_2026-09-05.md）。"
                     "id6613 ピングー展はぴあURL無効化のため保留、id6547 TMG福岡は id6546 に統合。")

d["batches"].append({
    "date": "2026-09-05",
    "slot": "morning",
    "id_from": 6904,
    "id_to": 6933,
    "count": 30,
    "source": "ぴあ 発売前 rlsStatus=0102（音楽lg=01・total904/91ページ全到達・未掲載106件のうち同名既存を除く36行→30エントリ）",
    "assigned": False,
    "rechecked": False,
    "note": "48枠のうち発売前43枠（明日以降12・本日発売31）。同名の既存エントリがある70件（44アーティスト）は"
            "統合が要るので投入せず tmp/samename_map_0905.txt に残した＝昼の便で処理する。"
})
json.dump(d, io.open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("BATCHES=%d last=%s %s id%s-%s" % (len(d["batches"]), d["batches"][-1]["date"],
                                         d["batches"][-1]["slot"], d["batches"][-1]["id_from"],
                                         d["batches"][-1]["id_to"]))
