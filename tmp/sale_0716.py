#!/usr/bin/env python3
"""7/16発売のエントリを抽出（X投稿ネタ・発売前カウントダウン向け）。
明示「M/D HH:MM発売」の券種だけ拾う（曖昧な締切は除外）。"""
import re
import sys
sys.path.insert(0, 'tools')
import build_pia_entries  # noqa stdout UTF-8
from check_expired import extract_events_array

EVENTS = extract_events_array('index.html')
TARGET = '7/16'

hits = []
for e in EVENTS:
    for t in e.get('tickets', []):
        ty = t.get('type', '')
        # 「7/16 HH:MM発売」形（発売開始が明日）
        m = re.search(r'(?<!〜)7/16\s*(\d{1,2}:\d{2})?発売', ty)
        if m and t.get('startDate') == '2026-07-16':
            hits.append((e, t, m.group(1) or '時刻未記載'))
            break

print(f'=== 7/16発売 {len(hits)}件 ===\n')
for e, t, tm in hits:
    print(f"[{e.get('genre')}] {e.get('name')}")
    print(f"    {e.get('prefecture')} {e.get('venue')} / 公演{e.get('date')}")
    print(f"    発売 {tm} | {t.get('type')}")
    print()
