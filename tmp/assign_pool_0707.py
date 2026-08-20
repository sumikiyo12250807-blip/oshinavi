# -*- coding: utf-8 -*-
"""新着プール(genre:new)44件のジャンル本振り分け。
_genre下書き→genre、_extraGenres→extraGenres(非空のみ)、下書きフィールド除去、NEW_ORDER空に。
直し: 合唱団るふらん=fes下書き→classic(合唱・fes定義に非該当)。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
mo = re.search(r'(NEW_ORDER\s*=\s*)(\[[^\]]*\])', h)
order = set(json.loads(mo.group(2)))
from collections import Counter
c = Counter()
changed = 0
for e in EVENTS:
    if e.get('id') not in order or e.get('genre') != 'new':
        continue
    g = e.get('_genre') or 'jpop'
    if '合唱団るふらん' in e.get('name',''):
        g = 'classic'
    ex = e.get('_extraGenres') or []
    e['genre'] = g
    if ex:
        e['extraGenres'] = ex
        c[g+'+'+'/'.join(ex)] += 1
    else:
        c[g] += 1
    for k in ('_genre','_extraGenres','_piaSub'):
        e.pop(k, None)
    changed += 1
print(f"assigned {changed}件")
print("集計:", dict(c))
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    h2 = h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():]
    mo2 = re.search(r'(NEW_ORDER\s*=\s*)(\[[^\]]*\])', h2)
    h2 = h2[:mo2.start()]+mo2.group(1)+'[]'+h2[mo2.end():]
    open('index.html.bak_0707_assign','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h2)
    print("written (backup: index.html.bak_0707_assign) / NEW_ORDER=[]")
