# -*- coding: utf-8 -*-
"""8/2 X投稿の主役6組ぶん、エントリ全体をUTF-8 JSONで書き出す（Fableに渡す素材）。"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from check_expired import extract_events_array

IDS = [2525, 2665, 2885, 2425, 2664, 2192]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'x_pick_0802.json')

events = extract_events_array('index.html')
picked = [e for e in events if e.get('id') in IDS]
order = {i: n for n, i in enumerate(IDS)}
picked.sort(key=lambda e: order.get(e.get('id'), 99))

with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(picked, f, ensure_ascii=False, indent=1)

print('wrote %s n=%d' % (OUT, len(picked)))
for e in picked:
    print('--- id=%s %s' % (e.get('id'), e.get('name')))
    print('    %s / %s / 公演 %s' % (e.get('prefecture'), (e.get('venue') or '').replace('\xa0', ' '), e.get('date')))
    for t in (e.get('tickets') or []):
        if t.get('startDate') == '2026-08-02':
            print('    ★8/2発売枠: %s' % t.get('type'))
    print('    links: %s' % ','.join(sorted((e.get('links') or {}).keys())))
