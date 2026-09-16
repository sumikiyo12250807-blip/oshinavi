# -*- coding: utf-8 -*-
"""ズレが出たidについて、登録の枠とエージェントが読んだ枠を並べて見せる（読むだけ）。
使い方: python tmp/show_recheck_0914.py <id,id,...>
出力: tmp/show_recheck_0914.txt
"""
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\ada2db76-3770-4399-ab5a-9e566d50214d\scratchpad'
IDS = [int(x) for x in sys.argv[1].split(',') if x.strip()]

src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
res = {}
for p in glob.glob(os.path.join(SP, 'recheck_*_result.json')):
    for r in json.load(io.open(p, encoding='utf-8')):
        res[r['id']] = r

out = []
for i in IDS:
    e = by.get(i) or {}
    out.append('==== id%s %s ／ date=%s ／ 県=%s' % (i, e.get('name'), e.get('date'), e.get('prefecture')))
    out.append('  [登録]')
    for t in e.get('tickets') or []:
        out.append('    %s | start=%s date=%s soldout=%s | %s' % (
            t.get('type'), t.get('startDate'), t.get('date'), t.get('soldout'), t.get('url') or ''))
    r = res.get(i) or {}
    out.append('  [エージェント] shows=%s' % [(s.get('date'), s.get('pref')) for s in r.get('shows') or []])
    for s in r.get('slots') or []:
        out.append('    %s | %s %s | %s | %s〜%s' % (
            s.get('name'), s.get('show_date'), s.get('pref'), s.get('state'), s.get('start'), s.get('end')))
    if r.get('note'):
        out.append('  note: %s' % r['note'])
io.open('tmp/show_recheck_0914.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('→ tmp/show_recheck_0914.txt')
