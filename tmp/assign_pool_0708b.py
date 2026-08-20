# -*- coding: utf-8 -*-
import re, json, io, sys
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
# 空_piaSubフォールバックengeki→実態音楽のもの
override = {2206: 'jpop', 2216: 'jpop', 2218: 'jpop'}
# バレエ=classic+engeki両方
extra = {2243: ['engeki']}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
tally = Counter(); n = 0; report = []
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    i = e['id']
    g = override.get(i, e.get('_genre'))
    if not g or g == 'new':
        print('!! unresolved', i, e.get('_genre')); continue
    e['genre'] = g
    if i in extra:
        e['extraGenres'] = extra[i]
    elif e.get('_extraGenres'):
        e['extraGenres'] = e['_extraGenres']
    for k in ('_genre', '_piaSub', '_extraGenres'):
        e.pop(k, None)
    tally[g] += 1; n += 1
    report.append((i, g, e['artist']))

no = re.search(r'(const NEW_ORDER = )\[[^\]]*\](;)', h)
newh = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
if no:
    newh = re.sub(r'(const NEW_ORDER = )\[[^\]]*\](;)', r'\g<1>[]\2', newh, count=1)

print('=== assigned %d 件 ===' % n)
for k, v in sorted(tally.items(), key=lambda x: -x[1]):
    print('   %s: %d' % (k, v))
if DRY:
    print('(DRY)')
else:
    open('index.html.bak_0708_assign2', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(newh)
    print('written (backup: index.html.bak_0708_assign2) / NEW_ORDER cleared')
