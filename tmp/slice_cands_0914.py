# -*- coding: utf-8 -*-
"""受付中の未登録候補（tmp/cands_uketsuke_0914.json）をぴあのジャンル(lg)ごとのファイルに分ける（読むだけ）。
組む順＝①音楽(01) ②演劇(02)・クラシック(07) ③その他（memory feedback_harvest_genre_priority）。
使い方: python tmp/slice_cands_0914.py
出力: tmp/cands_uk<lg>_0914.json（lgごと）
"""
import collections
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
cands = json.load(io.open('tmp/cands_uketsuke_0914.json', encoding='utf-8'))
by = collections.defaultdict(list)
for c in cands:
    by[c.get('_lg') or '??'].append(c)
for lg, rows in sorted(by.items()):
    json.dump(rows, io.open('tmp/cands_uk%s_0914.json' % lg, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('lg=%s %d件 → tmp/cands_uk%s_0914.json（id %s〜%s）' % (lg, len(rows), lg, rows[0]['newid'], rows[-1]['newid']))
