# -*- coding: utf-8 -*-
"""いまの新着プール（genre:"new"）の中身を、前夜(9/11)投入分とそれ以外に分けて出す（読むだけ）。
使い方: python tmp/pool_ids_0912.py
"""
import collections
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
LO, HI = 7840, 8157
src = open('index.html', encoding='utf-8').read()
m = re.search(r'  const EVENTS = (\[.*?\]);', src, re.S)
events = json.loads(m.group(1))
pool = [e for e in events if e.get('genre') == 'new']
last = [e for e in pool if LO <= e['id'] <= HI]
other = [e for e in pool if not (LO <= e['id'] <= HI)]
print('新着プール %d件 = 前夜分 %d件 + それ以外 %d件' % (len(pool), len(last), len(other)))
for e in other:
    L = e.get('links') or {}
    src_ = [k for k in ('pia', 'eplus', 'rakuten', 'lawson') if L.get(k)]
    print('  それ以外 id%s %s [%s] _genre=%s' % (e['id'], (e.get('name') or '')[:40], ','.join(src_), e.get('_genre')))
nog = [e['id'] for e in last if not e.get('_genre')]
print('前夜分で _genre が無いもの: %s' % nog)
print('前夜分の _genre 内訳: %s' % dict(collections.Counter(e.get('_genre') for e in last)))
open('tmp/pool_other_0912.txt', 'w', encoding='utf-8').write(','.join(str(e['id']) for e in other))
