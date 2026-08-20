# -*- coding: utf-8 -*-
"""X投稿の候補出し（8/13夕方に投稿する想定）。
 対象＝①今日8/13これから発売（発売時刻が16時以降）②明日8/14発売
 「発売開始」の枠だけ拾う（startDate==その日）。締切だけの枠は拾わない。
"""
import os, sys, json, re, collections

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from check_expired import extract_events_array

sys.stdout.reconfigure(encoding='utf-8')

TODAY = '2026-08-13'
TOMORROW = '2026-08-14'
NOW_HOUR = 16

events = extract_events_array('index.html')
rows = []
for e in events:
    for t in e.get('tickets') or []:
        sd = t.get('startDate') or ''
        if sd not in (TODAY, TOMORROW):
            continue
        # 発売時刻（バッジ末尾の「M/D HH:MM発売」or「HH:MM発売」）
        m = re.search(r'(\d{1,2}):(\d{2})\s*発売', t.get('type') or '')
        hh = int(m.group(1)) if m else None
        if sd == TODAY and (hh is None or hh < NOW_HOUR):
            continue          # 今日の分は「これから」だけ
        rows.append({
            'id': e['id'], 'name': e.get('name'), 'artist': e.get('artist'),
            'genre': e.get('genre'), '_genre': e.get('_genre'),
            'venue': e.get('venue'), 'showdate': e.get('date'),
            'sale': sd, 'hour': hh, 'badge': t.get('type'), 'end': t.get('date'),
        })

rows.sort(key=lambda r: (r['sale'], r['hour'] or 99, r['id']))
print('=== 8/13これから + 8/14発売 の枠 %d件 ===' % len(rows))
print('ジャンル内訳:', dict(collections.Counter(r['genre'] or r['_genre'] for r in rows)))
for r in rows:
    print('%s %s\tid=%d\t[%s]\t%s\t@%s\t%s' % (
        r['sale'][5:], ('%02d:00' % r['hour']) if r['hour'] is not None else '--:--',
        r['id'], r['genre'] or r['_genre'], (r['name'] or '')[:38],
        (r['venue'] or '')[:24], (r['badge'] or '')[:46]))

json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'x_cand_0813.json'),
                     'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
