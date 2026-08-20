#!/usr/bin/env python3
"""新着50件を目視レビュー用にダンプ（ジャンル下書き・会場・県・枠・URL）"""
import sys
sys.path.insert(0, 'tools')
from check_expired import extract_events_array  # noqa
import build_pia_entries  # noqa  stdoutをUTF-8ラップ

EVENTS = extract_events_array('index.html')
NEW = [e for e in EVENTS if e.get('genre') == 'new']

for e in NEW:
    g = e.get('_genre') or '(下書き無し)'
    sub = e.get('_piaSub')
    cat = e.get('_piaCat')
    print(f"id={e['id']} | {e.get('name')}")
    print(f"   会場: {e.get('venue')} ／ 県: {e.get('prefecture')} ／ 公演日: {e.get('date')}")
    print(f"   dateLabel: {e.get('dateLabel')}")
    print(f"   ジャンル下書き: {g}   (ぴあcat={cat!r} sub={sub!r})")
    for t in e.get('tickets', []):
        sd = t.get('startDate')
        print(f"   枠: {t.get('type')} | 締切/発売={t.get('date')}" + (f" | startDate={sd}" if sd else ''))
    print(f"   pia: {(e.get('links') or {}).get('pia')}")
    print()
