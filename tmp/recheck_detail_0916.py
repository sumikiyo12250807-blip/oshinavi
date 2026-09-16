# -*- coding: utf-8 -*-
"""読み直しでズレが出た id について、登録の枠とエージェントが読んだ公演・枠を並べる（読むだけ）。
使い方: python tmp/recheck_detail_0916.py 9007,9382,9516,9805
"""
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\166bfbc5-2524-465f-aba5-b0b622c14861\scratchpad'
ids = [int(x) for x in sys.argv[1].split(',')]
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
rows = {}
for p in glob.glob(os.path.join(SP, 'recheck_*_result.json')):
    for r in json.load(io.open(p, encoding='utf-8')):
        rows[r['id']] = r
for i in ids:
    e = by[i]
    print('=== id%d %s ／ 登録 県「%s」 会期 %s ／ %s' % (i, e['name'][:40], e.get('prefecture'), e.get('date'), e.get('dateLabel')))
    for t in e.get('tickets') or []:
        print('  登録:', t.get('type'), t.get('date'), '売切' if t.get('soldout') else '', (t.get('url') or '')[-30:])
    r = rows.get(i)
    if not r:
        print('  （読み直しの結果なし）')
        continue
    for s in r.get('shows') or []:
        print('  実 公演:', s.get('date'), s.get('date_end') or '', s.get('venue'), s.get('pref'))
    for s in r.get('slots') or []:
        print('  実 枠:', s.get('state'), '|', s.get('name'), '|', s.get('sale_end'), '|', s.get('show_date'), '|', s.get('pref') or '', (s.get('url') or '')[-30:])
