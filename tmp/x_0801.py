# -*- coding: utf-8 -*-
"""8/1 に発売開始する枠を UTF-8 ファイルへ書き出す（X投稿のネタ選び用）。"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from check_expired import extract_events_array

TARGET = sys.argv[1] if len(sys.argv) > 1 else '2026-08-01'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'x_{TARGET.replace("-","")}.txt')

events = extract_events_array('index.html')
rows = []
for e in events:
    hits = [t for t in (e.get('tickets') or []) if t.get('startDate') == TARGET]
    if hits:
        rows.append((e, hits))

by_genre = {}
for e, hits in rows:
    by_genre.setdefault(e.get('genre'), []).append((e, hits))

lines = [f'=== {TARGET} に発売開始する枠を持つエントリ {len(rows)}件 ===', '']
for g in sorted(by_genre, key=lambda x: -len(by_genre[x])):
    lst = by_genre[g]
    lines.append(f'--- {g} ({len(lst)}件) ---')
    for e, hits in lst:
        venue = (e.get('venue') or '').replace('\xa0', ' ')
        lines.append(f'  id={e["id"]} {e.get("name")}')
        lines.append(f'      {e.get("prefecture")} / {venue} / 公演 {e.get("date")}')
        for t in hits:
            lines.append(f'      枠: {t.get("type")}')
        links = e.get('links') or {}
        lines.append(f'      links: {",".join(sorted(links.keys()))}')
    lines.append('')

with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines))
print(f'wrote {OUT} rows={len(rows)}')
