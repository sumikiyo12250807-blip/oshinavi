#!/usr/bin/env python3
"""X投稿5本の事実確認＋東響クリスマス/ニューイヤー重複疑いの確認"""
import re
import sys
sys.path.insert(0, 'tools')
import build_pia_entries  # noqa
from check_expired import extract_events_array

EVENTS = extract_events_array('index.html')


def show(kw):
    for e in EVENTS:
        if kw in (e.get('name') or ''):
            u = (e.get('links') or {}).get('pia') or ''
            m = re.search(r'event(?:Bundle)?Cd=(\w+)', u)
            print(f"  id={e['id']} [{m.group(1) if m else '?'}] {e.get('name')}")
            print(f"     {e.get('prefecture')}/{e.get('venue')} | date={e.get('date')} | dateLabel={e.get('dateLabel')}")
            for t in e.get('tickets', []):
                print(f"     枠: {t.get('type')}")


for kw in ['全国高等学校野球', '「第九」', '9mm', 'ISLA DE SALSA', 'KIM DONG HEE']:
    print(f'=== {kw} ===')
    show(kw)
    print()

print('=== 東響クリスマス/ニューイヤー 重複疑い ===')
for kw in ['クリスマスコンサート2026', 'ニューイヤーコンサート2027']:
    print(f'--- {kw} ---')
    show(kw)
