#!/usr/bin/env python3
"""prefecture=全国 の誤検出を洗い出す。

バグ(2026-07-14 ANN WILSON)：実会場名に他県名が入ると県を複数拾い prefecture が「全国」に化ける。
「全国」が正しいのは複数会場ツアーだけ。単一会場なのに全国＝誤検出の疑い。
"""
import sys
sys.path.insert(0, 'tools')
from check_expired import extract_events_array
from build_pia_entries import PREF_RE   # import時にsys.stdoutをUTF-8ラップする(二重ラップ禁止)

EVENTS = extract_events_array('index.html')

zenkoku = [e for e in EVENTS if e.get('prefecture') == '全国']
print(f'prefecture=全国 のエントリ: {len(zenkoku)}件')

suspect, legit = [], []
for e in zenkoku:
    venue = e.get('venue') or ''
    # 複数会場ツアーの印：「全国ツアー」表記 or 会場名に「／」区切り
    is_tour = ('全国ツアー' in venue) or ('／' in venue) or ('ほか' in venue)
    (legit if is_tour else suspect).append(e)

print(f'  ├ 複数会場ツアー(全国が正しい): {len(legit)}件')
print(f'  └ 🚨単一会場なのに全国(誤検出の疑い): {len(suspect)}件\n')

for e in suspect:
    venue = e.get('venue') or ''
    found = PREF_RE.findall(venue)
    label = e.get('dateLabel') or ''
    print(f"id={e['id']} | {e.get('name')}")
    print(f"   会場: {venue}  ←会場名から拾える県: {found}")
    print(f"   dateLabel: {label}")
    print(f"   pia: {(e.get('links') or {}).get('pia')}")
