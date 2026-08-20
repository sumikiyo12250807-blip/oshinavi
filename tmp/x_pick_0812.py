# -*- coding: utf-8 -*-
"""8/12 X投稿8本ぶんのエントリ全体をUTF-8 JSONで書き出す（Fableに渡す素材）。"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from check_expired import extract_events_array

IDS = [3475, 4071, 3427, 4005, 4123, 4152, 2605, 4054]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'x_pick_0812.json')

events = extract_events_array('index.html')
picked = [e for e in events if e.get('id') in IDS]
order = {i: n for n, i in enumerate(IDS)}
picked.sort(key=lambda e: order.get(e.get('id'), 99))

with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(picked, f, ensure_ascii=False, indent=1)
print('wrote n=%d' % len(picked))
