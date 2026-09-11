# -*- coding: utf-8 -*-
"""last_batch.json の 9/11 投入分に「再チェック済み・振り分け済み」の印を付ける（2026-09-12 朝）。
id7946 は振り分けていない（ぴあのページが消えた）ことを note に残す。
使い方: python tmp/mark_batches_0912.py
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = '.claude/state/last_batch.json'
d = json.load(io.open(P, encoding='utf-8'))
NOTE = ('9/12朝に再チェック＝別エージェント4本がぴあ実ページからゼロで再導出（232件・読めなかったのは7946のみ）。'
        '直したもの＝7882/8145会期・8149一般10/16追加・7933天皇杯6会場・7959当日券・7975/8009会期。'
        '振り分け231件（logs/assigned_2026-09-12.md）。7946はぴあのページが消えて後継なし＝新着に保留。')
n = 0
for b in d['batches']:
    if b.get('date') == '2026-09-11' and b.get('id_from') in (7840, 7950, 8049, 8149, 8154):
        b['rechecked'] = True
        b['assigned'] = True
        b['note'] = (b.get('note') or '') + ' ／' + NOTE
        n += 1
assert n == 5, '印を付けたバッチが5つでない: %d' % n
io.open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
print('9/11のバッチ %d本に 再チェック済み・振り分け済み の印を付けた' % n)
