# -*- coding: utf-8 -*-
"""受付中・スポーツの組み立て207件（tmp/built_uk03_0914.json）＋混雑で落ちて組み直した 8833（tmp/built_8833_0914.json）を
「既存に畳む」「新規投入」に分ける（読むだけ・2026-09-14）。split_built_0914.py の結果と、相手の既存の会期・形を見て決めた:
  畳む＝完全一致37（アイスリボン×5→4928・大日本プロレス×8→1265・東京女子プロレス×6→2564・PURE-J×2→2828・
        BASARA→3335・FREEDOMS→2738・ボートピア梅田→5586・マリーゴールド×10→1273・みちのくプロレス×3→1274）
        ＋同じ試合＝コンサドーレ×大分 9/19→3710／パシフィックネーションズカップ 9/19 秩父宮→3397（3位決定戦・決勝）
        ＋複数会場をまとめた既存へ＝センダイガールズ 須賀川・仙台×2→2626／プロレスリング・ノア 高知・高松→3635
  新規＝残り全部。SHOOT BOXING 10/24 後楽園（既存7932は ACT.6 11/8 愛知＝別大会）／BOAT RACE 尼崎 9/1〜9/29（既存は10月の期間）／
        ホークスの試合×11（既存446は「ぴあ特別シート」の商品）／大阪プロレス・OZ×3・ガンバレ☆×2（1大会＝1エントリの形）／
        8833 いわて盛岡シティマラソン 会場・盛岡駅間送迎バス（混雑ページで落ちたのを単独で組み直した）
中止・延期・販売を終了致しましたを弾く直しの後に組んだ分。
使い方: python tmp/prep_uk03_0914.py
出力: tmp/inject_uk03_0914.json ／ tmp/merge_uk03_built_0914.json ＋ tmp/merge_uk03_cands_0914.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_uk03_0914.json', encoding='utf-8'))}
# 8833 の組み直しは PowerShell の「>」で保存した＝頭に BOM が付いている → utf-8-sig で読む（BOM が無くても読める）
extra = json.load(io.open('tmp/built_8833_0914.json', encoding='utf-8-sig'))
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_uk03_0914.json', encoding='utf-8'))}
assert len(extra) == 1 and extra[0]['id'] == 8833, '8833 の組み直しが1件でない'
assert 8833 not in built, '8833 が本体の組み立てにも居る＝二重になる'
extra[0]['artist'] = extra[0]['name'] = cands[8833]['artist'] if extra[0]['artist'] == 'retry' else extra[0]['artist']
built[8833] = extra[0]

MERGE = {}
for ids, t in (((8755, 8756, 8757, 8758, 8759), 4928),
               ((8886, 8887, 8888, 8889, 8890, 8891, 8892, 8893), 1265),
               ((8901, 8902, 8903, 8904, 8905, 8906), 2564),
               ((8944, 8945), 2828), ((8980,), 3335), ((8982,), 2738), ((8987,), 5586),
               ((8989, 8990, 8991, 8992, 8993, 8994, 8995, 8996, 8997, 8998), 1273),
               ((9000, 9001, 9002), 1274),
               ((8984,), 3710), ((8764,), 3397),
               ((8872, 8874, 8875), 2626), ((8978, 8979), 3635)):
    for i in ids:
        MERGE[i] = t
missing = [i for i in MERGE if i not in built]
assert not missing, '組み立てに無い id を指している %s' % missing
new_ids = sorted(set(built) - set(MERGE))
json.dump([built[i] for i in new_ids], io.open('tmp/inject_uk03_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([built[i] for i in MERGE], io.open('tmp/merge_uk03_built_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([dict(cands[i], target=t) for i, t in MERGE.items()],
          io.open('tmp/merge_uk03_cands_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('組み立て %d件（8833 を含む）＝ 新規投入 %d / 既存に畳む %d' % (len(built), len(new_ids), len(MERGE)))
print('新規のid範囲 %s〜%s' % (new_ids[0], new_ids[-1]))
