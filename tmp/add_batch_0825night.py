# -*- coding: utf-8 -*-
"""8/25夜に投入した新着88件(id5201-5300)の記録が last_batch.json から漏れていたので後追いで追記する。"""
import json
import io

P = ".claude/state/last_batch.json"
data = json.load(open(P, encoding="utf-8"))

if any(b.get("date") == "2026-08-25" and b.get("slot") == "night" for b in data["batches"]):
    print("既に記録あり。何もしない。")
else:
    data["batches"].append({
        "date": "2026-08-25",
        "slot": "night",
        "id_from": 5201,
        "id_to": 5300,
        "count": 88,
        "source": "ぴあ 発売前rlsIn=03(51件)＋受付中(49件)を100件ビルド→売切/混雑12件を除いて88件を投入",
        "assigned": False,
        "rechecked": False,
        "note": "🚨last_batch への記録が漏れていたので 8/26 朝に後追いで書いた（plan.md 8/25セクションが一次情報）。同日に presale_harvest の終端判定バグを再修正（現在位置が進まなくなったら終端）＋ tools/pia_sweep_all.py を新設（sg×rg でぴあ一覧の1000件頭打ちを割る）＋ build_pia_entries に genreCd フォールバックを追加。翌朝(8/26)に①独立再照合②別エージェントの客観チェック→振り分け。50件ずつ2本に分けて回す。"
    })
    with open(P, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("追記した: 2026-08-25 night id5201-5300 count=88")
