# -*- coding: utf-8 -*-
"""last_batch.json に 9/12 朝の保留の片付けで入れた新規1件（8344 ガンバレ☆プロレス）を記録する（index.html は触らない）。
使い方: python tmp/note_8344_0912.py
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = '.claude/state/last_batch.json'
d = json.load(io.open(P, encoding='utf-8'))
if any(b.get('date') == '2026-09-12' and b.get('id_from') == 8344 for b in d['batches']):
    print('もう記録してある')
    sys.exit(0)
d['batches'].append({
    'date': '2026-09-12', 'slot': 'morning-same2', 'id_from': 8344, 'id_to': 8344, 'count': 1,
    'source': 'ぴあ 発売前スイープの統合行きのうち、同じ名前の既存が2つあって保留した7件の片付け',
    'assigned': False, 'rechecked': False,
    'note': '8344 ガンバレ☆プロレス 11/23 高島平（大会ごとに別エントリの形＝5645・5646と同じ）。'
            '残り6件は既存へ足した＝川崎鷹也 茨城4/9・東京5/29・大阪5/27→4227／NELKE 宮城6/19・愛知7/7・大阪7/9→4499'
            '（石川6/13は4499に既にあり）。4227・4499とも県は5県以上になったので「全国」。'
            '翌朝(9/13)に①独立再照合②別エージェントの客観チェック→振り分け。'})
io.open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
print('last_batch に 8344 を記録した')
