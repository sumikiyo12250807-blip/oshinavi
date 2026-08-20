# -*- coding: utf-8 -*-
"""7/1 第2弾50件 ジャンル振り分け(ユーザーOK「振り分けてプッシュ」2026-07-01)。
各エントリの_genre下書きをそのまま確定。補正=1768 ナーポオケラ(ハワイのフラ)を classic→engeki。
下書きフィールド除去・NEW_ORDER空・genre:new解消。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OVERRIDE = {1768: ('engeki', [])}  # フラ興行=classic誤り→engeki(最寄り)

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

from collections import Counter
tally = Counter()
n = 0
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    if e['id'] in OVERRIDE:
        g, extra = OVERRIDE[e['id']]
    else:
        g, extra = e.get('_genre'), e.get('_extraGenres') or []
    assert g and g != 'new', 'id%s の_genre不正: %r' % (e['id'], g)
    e['genre'] = g
    if extra:
        e['extraGenres'] = extra
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    tally[g + ('+' + '/'.join(extra) if extra else '')] += 1
    n += 1

h_new = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>[]', h, count=1)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h_new, re.S)
out = h_new[:m2.start()] + m2.group(1) + new_arr + m2.group(3) + h_new[m2.end():]
remaining = sum(1 for e in EVENTS if e.get('genre') == 'new')
open('index.html.bak_0701b_assign', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(out)
print('振り分け %d件 / genre:new 残 %d' % (n, remaining))
print('内訳:', dict(sorted(tally.items(), key=lambda x: -x[1])))
