# -*- coding: utf-8 -*-
"""明日(引数の日付)に発売開始する枠を、X投稿のネタ選び用に一覧する。"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from check_expired import extract_events_array

TARGET = sys.argv[1] if len(sys.argv) > 1 else '2026-07-21'

events = extract_events_array('index.html')
rows = []
for e in events:
    hits = [t for t in (e.get('tickets') or []) if t.get('startDate') == TARGET]
    if hits:
        rows.append((e, hits))

print(f'=== {TARGET} に発売開始する枠を持つエントリ {len(rows)}件 ===\n')
by_genre = {}
for e, hits in rows:
    by_genre.setdefault(e.get('genre'), []).append((e, hits))

for g in sorted(by_genre, key=lambda x: -len(by_genre[x])):
    lst = by_genre[g]
    print(f'--- {g} ({len(lst)}件) ---')
    for e, hits in lst:
        print(f'  id={e["id"]} {e.get("name")}')
        print(f'      {e.get("prefecture")} / {e.get("venue")} / 公演 {e.get("date")}')
        for t in hits:
            print(f'      枠: {t.get("type")}')
    print()
