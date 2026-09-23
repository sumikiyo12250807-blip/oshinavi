# -*- coding: utf-8 -*-
"""新着タブ（genre=new・振り分け前）の中で、9/22〜9/24 に発売が始まる枠を持つエントリを数える（読むだけ・9/21夜）。
X投稿の素材（material_0922.py）は新着を外しているので、そこに漏れている分を見る。"""
import collections, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
DAYS = ['2026-09-22', '2026-09-23', '2026-09-24']
h = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
by = collections.defaultdict(list)
for e in ev:
    if e.get('genre') != 'new':
        continue
    for d in DAYS:
        ts = [t for t in e.get('tickets') or [] if t.get('startDate') == d and not t.get('soldout')]
        if ts:
            tm = re.search(r'(\d{1,2}:\d{2})\s*発売', ts[0].get('type') or '')
            src = next((k for k, v in (e.get('links') or {}).items() if v), '?')
            by[d].append((tm.group(1) if tm else '', e['id'], e.get('artist'), e.get('prefecture') or '', src))
for d in DAYS:
    print('== %s 新着で発売が始まる %d件' % (d, len(by[d])))
    for r in sorted(by[d]):
        print('  %s id%s %s／%s [%s]' % (r[0] or '時刻なし', r[1], (r[2] or '')[:50], r[3], r[4]))
