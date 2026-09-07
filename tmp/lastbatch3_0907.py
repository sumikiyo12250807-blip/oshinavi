# -*- coding: utf-8 -*-
"""夜に投入した落語・バレエの別公演12件を last_batch.json に記録する。"""
import io, json

P = ".claude/state/last_batch.json"
st = json.load(io.open(P, encoding="utf-8"))
st["batches"].append({
    "date": "2026-09-07",
    "slot": "night2",
    "id_from": 7165,
    "id_to": 7186,
    "count": 12,
    "source": "ぴあ（X投稿に出す26組をアーティスト名で総ざらいして見つけた別公演）",
    "assigned": False,
    "rechecked": False,
    "note": "落語10件（博多天神落語まつり/圓朝祭/落語教育委員会/深谷特選二人会/よこはま落語会 ほか）＋"
            "東京バレエ団3件。候補24件のうち8件は売切でskip、4件（大名古屋らくご祭・オネーギン・"
            "ベジャール・真夜中の音楽室）は既存と同じ公演なので投入せず翌朝に枠を足す。"
            "投入後ゲート＝check_badges OK / reconcile --new は OK54・MISSING/DROP/QC 0、"
            "FETCH1は混雑ページの巻き添えで単独再照合したら一致"
})
json.dump(st, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("記録した: %d バッチ" % len(st["batches"]))
