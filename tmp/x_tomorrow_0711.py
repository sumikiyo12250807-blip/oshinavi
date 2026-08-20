# -*- coding: utf-8 -*-
"""7/11 発売開始のチケットを全部洗い出す（X投稿ドラフト用）。
発売時刻つき・ジャンル別。発売開始告知が基本([[feedback_x_deadline_vs_presale_by_genre]])。"""
import re, json, io, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TARGET = '2026-07-11'
h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))

rows = []
for e in E:
    for t in e.get('tickets', []):
        if t.get('startDate') != TARGET:
            continue
        ty = t.get('type') or ''
        tm = re.search(r'(\d{1,2}:\d{2})発売', ty)
        rows.append({
            'id': e['id'], 'artist': e.get('artist', ''), 'genre': e.get('genre'),
            'venue': e.get('venue', ''), 'pref': e.get('prefecture', ''),
            'date': e.get('date'), 'time': tm.group(1) if tm else '?',
            'type': ty,
        })
rows.sort(key=lambda r: (r['time'], r['artist']))
print(f'=== {TARGET} 発売開始 {len(rows)}枠 / {len({r["id"] for r in rows})}公演 ===\n')
by_time = collections.Counter(r['time'] for r in rows)
print('発売時刻の分布:', dict(by_time), '\n')
for r in rows:
    print(f"{r['time']:>5}  [{r['genre']:<8}] {r['artist'][:32]:<34} {r['pref']:<6} 公演{r['date']}")
print('\n--- ジャンル別 ---')
g = collections.Counter(r['genre'] for r in rows)
for k, v in g.most_common():
    names = [r['artist'][:20] for r in rows if r['genre'] == k]
    print(f'  {k}: {v}  {" / ".join(names[:8])}')
