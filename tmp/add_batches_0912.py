# -*- coding: utf-8 -*-
"""last_batch.json に 9/12 朝の投入2バッチを記録する（翌朝の再チェックで使う）。
使い方: python tmp/add_batches_0912.py
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = '.claude/state/last_batch.json'
d = json.load(io.open(P, encoding='utf-8'))
have = {(b.get('date'), b.get('id_from')) for b in d['batches']}
new = [
    {'date': '2026-09-12', 'slot': 'morning-uketsuke', 'id_from': 8163, 'id_to': 8258, 'count': 55,
     'source': 'ぴあ 受付中 rlsStatus=0101 の残りタネ（tmp/cand_uk_0912.json）から音楽100件',
     'assigned': False, 'rechecked': False,
     'note': '100件ビルド→31件は売切でskip（タネが9/9のもの）→69件→同じアーティストの既存に足した13件'
             '（水森かおり→7637・メトロノーム×2→8030・尾崎裕哉→8115・ゴホウビ×2→7684・DEATH CAB→7973・'
             'ピーター・ケーター→8005・HONEBONE→8013・bokula.→8015・REYTONS→7696・シクラメン→7698・倍賞千恵子→554）／'
             '保留1件（8178 ボロフェスタ2026＝既存6251はMETRO券だけのエントリ）→55件投入。id欠番あり。'
             '残りタネ1,931件は tmp/rest0101_0912.json。翌朝(9/13)に①独立再照合②別エージェントの客観チェック→振り分け。'},
    {'date': '2026-09-12', 'slot': 'morning', 'id_from': 8261, 'id_to': 8343, 'count': 76,
     'source': 'ぴあ 発売前スイープ rlsStatus=0102/0202（9バケツとも最終ページまで到達）＝未掲載169件→新規83/統合行き86',
     'assigned': False, 'rechecked': False,
     'note': '新規83件ビルド→売切4件skip（8266/8267/8304/8320）→79件→部分一致11件を仕分けて保留3件'
             '（8264 大江千里トリオ＝既存4741と同じ1/24／8281 蒼ノトキ2027＝既存927と同じシリーズ／'
             '8322 なにわ淀川花火＝既存2535はぴあシートだけのエントリ）→76件投入。'
             '統合行き86件＝足す先が1つの79件を43エントリに54枠で足した（同名が2つある7件＝川崎鷹也・NELKE・ガンバレ☆プロレスは保留）。'
             '同じスイープの行で「登録済みページに後から足された窓」を18エントリ40枠足した。'
             '翌朝(9/13)に①独立再照合②別エージェントの客観チェック→振り分け。'},
]
added = 0
for b in new:
    if (b['date'], b['id_from']) in have:
        continue
    d['batches'].append(b)
    added += 1
io.open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
print('last_batch に %d バッチ記録した' % added)
