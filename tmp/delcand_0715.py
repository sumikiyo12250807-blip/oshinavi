#!/usr/bin/env python3
"""削除候補の links / tickets を index.html から機械抽出（URL捏造禁止・実データのみ）"""
import io
import sys
sys.path.insert(0, 'tools')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from check_expired import extract_events_array

IDS = [1481, 1532, 2186, 2199, 2221, 2278, 2319, 2331]

EVENTS = extract_events_array('index.html')
by_id = {e.get('id'): e for e in EVENTS}

for i in IDS:
    e = by_id.get(i)
    if not e:
        print(f'id={i} 見つからない')
        continue
    links = e.get('links') or {}
    vendors = ','.join(sorted(links.keys()))
    print(f"\nid={i} | {e.get('title')} | {e.get('venue')} | 公演{e.get('date')} | genre={e.get('genre')}")
    print(f"  販売サイト: {vendors if vendors else '★links無し'}")
    for k, v in links.items():
        print(f"    {k}: {v}")
    for t in (e.get('tickets') or []):
        print(f"    枠: {t.get('type')} | date={t.get('date')} | startDate={t.get('startDate')}")
