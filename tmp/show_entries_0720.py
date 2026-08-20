# -*- coding: utf-8 -*-
"""指定idのエントリの中身（枠・発売日・URL）を確認用に表示する。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from check_expired import extract_events_array

IDS = [int(x) for x in sys.argv[1].split(',')]

events = extract_events_array('index.html')
by_id = {e.get('id'): e for e in events}

for i in IDS:
    e = by_id.get(i)
    if not e:
        print(f'id={i} 見つからない\n')
        continue
    print(f'--- id={i} {e.get("name")}')
    print(f'    artist={e.get("artist")} / venue={e.get("venue")} / date={e.get("date")}')
    print(f'    prefecture={e.get("prefecture")} / _genre={e.get("_genre")}')
    print(f'    pia={(e.get("links") or {}).get("pia")}')
    for t in e.get('tickets', []):
        print(f'    枠: type={t.get("type")!r}')
        print(f'        date={t.get("date")} startDate={t.get("startDate")} dateLabel={t.get("dateLabel")!r}')
        print(f'        url={t.get("url")}')
    print()
