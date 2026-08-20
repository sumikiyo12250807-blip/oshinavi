#!/usr/bin/env python3
"""統合対象の実データを正確に取得（野球・みなとみらいフェス）"""
import json
import re
import sys
sys.path.insert(0, 'tools')
import build_pia_entries  # noqa
from check_expired import extract_events_array

EVENTS = extract_events_array('index.html')
by = {e['id']: e for e in EVENTS}

for i in [2696, 2697, 2698, 2699, 2729, 2728, 2726, 2727]:
    e = by.get(i)
    if not e:
        print(f'id={i} 無し'); continue
    print(f"id={i} | {e.get('name')} | genre={e.get('genre')} | {e.get('prefecture')}/{e.get('venue')} | date={e.get('date')}")
    for t in e.get('tickets', []):
        print(f"    type={t.get('type')} | date={t.get('date')} start={t.get('startDate')} url={t.get('url','')}")
    print(f"    links.pia={(e.get('links') or {}).get('pia')}")
