# -*- coding: utf-8 -*-
"""id6012 go!go!vanillas の発売時刻を実ページに合わせる（10:00 → 13:00）。
実ページの窓＝sd 2026-09-26 st 13:00 / ed 2026-10-23（tmp/eplus_blocks.py で確認済み）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
hit = 0
for e in EV:
    if e.get('id') != 6012:
        continue
    t = e['tickets'][0]
    old = t['type']
    new = old.replace('9/26 10:00発売', '9/26 13:00発売')
    if new != old:
        t['type'] = new
        hit = 1
        print('old:', old)
        print('new:', new)
if hit:
    open('index.html.bak_0902_6012', 'w', encoding='utf-8').write(h)
    out = h[:m.start()] + m.group(1) + json.dumps(EV, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
    open('index.html', 'w', encoding='utf-8').write(out)
    print('applied')
else:
    print('該当なし＝書き換えていない')
