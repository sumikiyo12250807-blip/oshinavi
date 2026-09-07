# -*- coding: utf-8 -*-
"""夜に投入した御園座の3件を last_batch.json に記録する（翌朝の再チェックで使う）。"""
import io, json

P = ".claude/state/last_batch.json"
st = json.load(io.open(P, encoding="utf-8"))
st["batches"].append({
    "date": "2026-09-07",
    "slot": "night",
    "id_from": 7162,
    "id_to": 7164,
    "count": 3,
    "source": "ぴあ（X投稿に出す御園座をアーティスト名で総ざらいして見つけた別公演）",
    "assigned": False,
    "rechecked": False,
    "note": "トータルテンボス漫才ツアー(owarai・6枠)／映画「国宝」特別上映(engeki)／坂東玉三郎 衣裳の魅力(dento)。"
            "舟木一夫 御園座特別コンサートは売切でskip。"
            "🚨このバッチのidは 7160 でなく 7162 から＝朝に消した 7160/7161 を再利用しないため"
})
json.dump(st, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("記録した: %d バッチ" % len(st["batches"]))
