# -*- coding: utf-8 -*-
"""7/6 新着プール(genre:new・_genre下書き持ち)を本ジャンルへ振り分け。
_genre->genre、_extraGenres->extraGenres、下書き除去、NEW_ORDERから外す。
自分の音楽知識で再分類しない([[project_vendor_genre_autoassign]])。"""
import re, json, sys, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

cnt, done = Counter(), []
for e in EVENTS:
    if e.get('genre') == 'new' and '_genre' in e:
        g = e['_genre']
        e['genre'] = g
        ex = [x for x in (e.get('_extraGenres') or []) if x]
        if ex:
            e['extraGenres'] = ex
        for k in ('_genre', '_extraGenres', '_piaSub'):
            e.pop(k, None)
        cnt[g] += 1
        done.append(e['id'])

print('振り分け', len(done), '件')
for g, c in cnt.most_common():
    print(f'  {g}: {c}')

mo = re.search(r'const NEW_ORDER = (\[[0-9,\s]*\]);', h)
cur = json.loads(mo.group(1))
rest = [i for i in cur if i not in set(done)]
no = '[' + ', '.join(str(i) for i in rest) + ']'
h2 = h[:mo.start()] + 'const NEW_ORDER = ' + no + ';' + h[mo.end():]
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
print('NEW_ORDER残り', len(rest), '件:', rest)

if DRY:
    print('(DRY)')
else:
    open('index.html.bak_0706_assign', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h2[:m.start()] + m.group(1) + new_arr + m.group(3) + h2[m.end():])
    print('written (backup: index.html.bak_0706_assign)')
