# -*- coding: utf-8 -*-
import re, json, io, sys
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', src, re.S)
data = json.loads(m.group(1))

newids = sorted(e['id'] for e in data if e.get('genre') == 'new')
print('■ genre:new 件数:', len(newids))
if newids:
    print('  id範囲:', newids[0], '〜', newids[-1])
    print('  ids:', newids)

b1 = [e for e in data if 2765 <= e['id'] <= 2814]
print('■ バッチ1(2765-2814) 件数:', len(b1))
print('  genre分布:', dict(Counter(e.get('genre') for e in b1)))
print('  _genre(下書き)を残してる数:', sum(1 for e in b1 if e.get('_genre')))

rk = [e for e in data if e['id'] == 2771]
if rk:
    print('■ ラックライフ2771 → genre:', rk[0].get('genre'), '/ _genre下書き:', rk[0].get('_genre', '無し'))

mo = re.search(r'const\s+NEW_ORDER\s*=\s*(\[[^\]]*\])', src)
no = json.loads(mo.group(1))
print('■ NEW_ORDER 件数:', len(no))
if no:
    print('  範囲:', no[0], '〜', no[-1])
# NEW_ORDER と genre:new が一致するか
print('■ NEW_ORDER と genre:new id集合は一致?:', set(no) == set(newids))
