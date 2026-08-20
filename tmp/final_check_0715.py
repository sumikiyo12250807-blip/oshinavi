#!/usr/bin/env python3
"""今回直した箇所の最終確認"""
import sys
sys.path.insert(0, 'tools')
from check_expired import extract_events_array
import build_pia_entries  # noqa stdout UTF-8

EVENTS = extract_events_array('index.html')
by = {e['id']: e for e in EVENTS}

for i in (2656, 2657, 2658, 2661, 2678, 2679, 2683, 2692, 2693, 2694):
    e = by[i]
    print(f"id={i} | {e.get('name')}")
    print(f"   dateLabel: {e.get('dateLabel')}")
    for t in e.get('tickets', []):
        print(f"   枠: {t.get('type')}")
    print()
