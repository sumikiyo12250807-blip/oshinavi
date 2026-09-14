# -*- coding: utf-8 -*-
"""9/14夜に新着へ入れた「X投稿のライブの取りこぼし」24件（id9859〜9903・飛び番あり）を .claude/state/last_batch.json に記録する。
翌朝の「前夜の新着の再チェック」で使う（inject 後に必ず更新する決まり）。
使い方: python tmp/x0914/lastbatch_add.py [--apply]
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = '.claude/state/last_batch.json'
IDS = [9859, 9861, 9862, 9863, 9864, 9865, 9868, 9869, 9870, 9875, 9879, 9880, 9881, 9885, 9887, 9890, 9891,
       9892, 9894, 9895, 9896, 9897, 9902, 9903]
raw = io.open(P, encoding='utf-8').read()
d = json.loads(raw)
rec = {
    'date': '2026-09-14',
    'slot': 'evening',
    'id_from': min(IDS),
    'id_to': max(IDS),
    'count': len(IDS),
    'ids': IDS,
    'source': 'ぴあ・X投稿（9/15発売）に出したアーティスト名での総ざらい（tmp/x0914/audit_posts.py・audit_posts2.py）→公演名・公演日で絞った本当の抜け',
    'assigned': False,
    'rechecked': False,
    'note': '新規49件のうち24件（25件は買える枠0＝載せない）。ほかに既存4件へ1枠ずつ足した（5732・4118・2500・915）。'
            '9/14夜に reconcile --ids と別エージェントの独立の読み直しをかける予定。飛び番＝組み上がらなかった分',
}
if any(b.get('ids') == IDS for b in d.get('batches', [])):
    print('もう記録してある')
    sys.exit(0)
d['batches'].append(rec)
print('足す: %s %s id%s〜%s %d件' % (rec['date'], rec['slot'], rec['id_from'], rec['id_to'], rec['count']))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in raw else '\n'
io.open(P, 'w', encoding='utf-8', newline='').write(json.dumps(d, ensure_ascii=False, indent=2).replace('\n', nl) + nl)
print('書き込み完了')
