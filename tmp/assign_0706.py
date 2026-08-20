# -*- coding: utf-8 -*-
"""7/6 新着プール振り分け。_genre→genre(下書きそのまま・再分類禁止)。
_extraGenres→extraGenres。アート2件(2034/2035)は_genre空=保留。NEW_ORDERは保留2件のみに。"""
import re, json, sys, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
HOLD = {2034, 2035}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
assigned = Counter()
held = []
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    if e['id'] in HOLD or not e.get('_genre'):
        held.append(e['id']); continue
    g = e['_genre']
    e['genre'] = g
    if e.get('_extraGenres'):
        e['extraGenres'] = e['_extraGenres']
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    assigned[g] += 1

print('振り分け:', dict(assigned), '計', sum(assigned.values()))
print('保留(genre:newのまま):', held)
no = '[' + ', '.join(str(i) for i in held) + ']'
h2, n = re.subn(r'const NEW_ORDER = \[[0-9,\s]*\];', 'const NEW_ORDER = ' + no + ';', h)
assert n == 1, f'NEW_ORDER n={n}'
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
if DRY:
    print('(DRY)')
else:
    open('index.html.bak_0706_assign', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h2[:m.start()] + m.group(1) + new_arr + m.group(3) + h2[m.end():])
    print('written (backup: index.html.bak_0706_assign)')
