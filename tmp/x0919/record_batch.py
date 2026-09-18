# -*- coding: utf-8 -*-
"""今夜の投入を .claude/state/last_batch.json に足す（翌朝の再チェックで使う）。

2026-09-18 夜の便＝X投稿の素材を作る前にぴあの明日〜3日後発売と突き合わせて出た
「本当の抜け」から、既存への足し込み26件と新規7件を入れた。
新規の id 範囲＝13327〜13331（音楽）と 13332〜13333（演劇・イベント）。

  python tmp/x0919/record_batch.py
"""
import io
import json

P = '.claude/state/last_batch.json'
d = json.load(io.open(P, encoding='utf-8'))
d['batches'].append({
    'date': '2026-09-18',
    'slot': 'evening',
    'id_from': 13327,
    'id_to': 13333,
    'count': 7,
    'source': 'ぴあ 明日〜3日後発売の突き合わせ（lg=01/02/03/06/07）で出た未登録',
    'assigned': False,
    'rechecked': False,
    'note': ('X投稿の素材を作る前の突き合わせ。抜け46件のうち足し込み26件＋新規7件。'
             '🚫駐車券だけの売り場1件は入れていない（出す側／推しに会う枠でない）。'
             '足し込みで「買える枠0」が6件直った（2743秋山黄色・4038コブクロ・4820BALLISTIK BOYZ・'
             '4047山下大輝・7332ACTORS☆LEAGUE・6528さらばのこの本）'),
})
io.open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
print('記録した: %d件目 / 最後のバッチ = %s %s id%d..%d'
      % (len(d['batches']), d['batches'][-1]['date'], d['batches'][-1]['slot'],
         d['batches'][-1]['id_from'], d['batches'][-1]['id_to']))
