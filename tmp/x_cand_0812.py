# -*- coding: utf-8 -*-
"""8/12 10:00以降発売＋8/13発売の枠を抽出してX投稿候補リストを作る。"""
import os
import sys
import json
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from check_expired import extract_events_array

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'x_cand_0812.json')

events = extract_events_array('index.html')

rows = []
for e in events:
    for t in (e.get('tickets') or []):
        sd = t.get('startDate') or ''
        if sd not in ('2026-08-12', '2026-08-13'):
            continue
        rows.append({
            'id': e.get('id'),
            'name': e.get('name'),
            'artist': e.get('artist'),
            'genre': e.get('genre'),
            'extraGenres': e.get('extraGenres'),
            'pref': e.get('prefecture'),
            'venue': (e.get('venue') or '').replace('\xa0', ' '),
            'showDate': e.get('date'),
            'startDate': sd,
            'startTime': t.get('startTime'),
            'ticketType': t.get('type'),
            'dateLabel': t.get('dateLabel'),
            'endDate': t.get('date'),
        })

rows.sort(key=lambda r: (r['startDate'], r['startTime'] or '', r['id']))
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)

print('total %d' % len(rows))
for r in rows:
    print('%s %s | id=%s %s | %s %s | %s' % (
        r['startDate'], r['startTime'] or '--:--', r['id'], r['name'],
        r['pref'], r['venue'], r['ticketType']))
