# -*- coding: utf-8 -*-
"""3508 のバッジに残った全角／を半角化（ビルダー側は恒久修正済・こちらは現物の追随）。"""
import json
import re

h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

e = byid[3508]
n = 0
log = []
for t in e['tickets']:
    if '／' in (t.get('type') or ''):
        old = t['type']
        t['type'] = t['type'].replace('／', '/')
        n += 1
        log.append(f'  {old}')
        log.append(f'   → {t["type"]}')
assert n == 1, f'対象 {n} 件（1件のはず）'

open('index.html.bak_0730_slash', 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
log.insert(0, 'id=3508 THE AWAODORI バッジの全角／を半角化')
open('tmp/fix_slash_3508_0730.txt', 'w', encoding='utf-8').write('\n'.join(log))
