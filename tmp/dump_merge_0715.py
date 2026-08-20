#!/usr/bin/env python3
"""新着47件を統合候補判断用にダンプ（名前・会場・県・公演日・券種販売日・eventCd）"""
import re
import sys
sys.path.insert(0, 'tools')
import build_pia_entries  # noqa stdout UTF-8
from check_expired import extract_events_array

EVENTS = extract_events_array('index.html')
NEW = [e for e in EVENTS if e.get('genre') == 'new']


def ecd(e):
    u = (e.get('links') or {}).get('pia') or ''
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u)
    return m.group(1) if m else '?'


for e in NEW:
    print(f"id={e['id']} [{ecd(e)}] {e.get('name')}")
    print(f"    {e.get('prefecture')} / {e.get('venue')} / 公演{e.get('date')}")
    for t in e.get('tickets', []):
        print(f"      枠: {t.get('type')}")
