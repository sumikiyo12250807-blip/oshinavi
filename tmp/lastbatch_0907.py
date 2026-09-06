# -*- coding: utf-8 -*-
"""今朝投入したバッチを .claude/state/last_batch.json に記録する（翌朝の再チェックで使う）。"""
import io, json

P = ".claude/state/last_batch.json"
st = json.load(io.open(P, encoding="utf-8"))

st["batches"].append({
    "date": "2026-09-07",
    "slot": "morning",
    "id_from": 7098,
    "id_to": 7161,
    "count": 61,
    "source": "ぴあ 発売前スイープ 7ジャンル×rlsStatus=0102/0202（全ジャンルで最終ページまで到達）",
    "assigned": False,
    "rechecked": False,
    "note": "候補64件のうち 7129/7141 は売切でskip、7152 は[貸切公演]で枠0のため除外。"
            "投入後ゲート＝check_badges OK / reconcile --new は OK62・MISSING/DROP/STALE/FETCH/QC 全0・照合枠98/102"
})

# 7097（ゴールデンステージ第12回）も同じ朝の投入なので併記
st["batches"].append({
    "date": "2026-09-07",
    "slot": "morning-split",
    "id_from": 7097,
    "id_to": 7097,
    "count": 1,
    "source": "e+（id6983に別公演が2つ混ざっていたので第12回を分割）",
    "assigned": False,
    "rechecked": False,
    "note": "gate_eplus_slots PASS（実ページの枠数と一致）"
})

json.dump(st, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("記録した: %d バッチ" % len(st["batches"]))
