# -*- coding: utf-8 -*-
"""X投稿ドラフト用に、指定idのエントリ全体をUTF-8 JSONで書き出す。"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from check_expired import extract_events_array

IDS = [int(x) for x in sys.argv[1:]] or [2151]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'x_pick_0801.json')

events = extract_events_array('index.html')
picked = [e for e in events if e.get('id') in IDS]

with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(picked, f, ensure_ascii=False, indent=1)
print(f'wrote {OUT} n={len(picked)}')
