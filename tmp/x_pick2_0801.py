# -*- coding: utf-8 -*-
"""X投稿の追加ネタ用に、指定idのエントリを別ファイルへ書き出す（x_pick_0801.jsonを壊さない）。"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from check_expired import extract_events_array

IDS = [int(x) for x in sys.argv[1:]]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'x_pick2_0801.json')

events = extract_events_array('index.html')
picked = [e for e in events if e.get('id') in IDS]

with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(picked, f, ensure_ascii=False, indent=1)
print(f'wrote {OUT} n={len(picked)}')
