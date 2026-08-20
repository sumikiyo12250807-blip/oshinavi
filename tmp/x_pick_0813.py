# -*- coding: utf-8 -*-
"""8/13夜に出すX投稿6本ぶんのエントリ全体をUTF-8 JSONで書き出す（Fableに渡す素材）。"""
import os, sys, json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from check_expired import extract_events_array

sys.stdout.reconfigure(encoding='utf-8')

IDS = [3153, 4020, 3316, 4045, 2815, 3397, 3398]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'x_pick_0813.json')

events = extract_events_array('index.html')
picked = [e for e in events if e.get('id') in IDS]
order = {i: n for n, i in enumerate(IDS)}
picked.sort(key=lambda e: order.get(e.get('id'), 99))

with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(picked, f, ensure_ascii=False, indent=1)
print('wrote n=%d' % len(picked))
for e in picked:
    print('--- id=%d %s @%s (%s)' % (e['id'], e.get('name'), e.get('venue'), e.get('date')))
    print('    artist=%s / dateLabel=%s' % (e.get('artist'), e.get('dateLabel')))
    print('    links=%s' % json.dumps({k: v for k, v in (e.get('links') or {}).items() if v}, ensure_ascii=False))
    for t in e.get('tickets') or []:
        print('    枠| %s | start=%s end=%s' % (t.get('type'), t.get('startDate'), t.get('date')))
