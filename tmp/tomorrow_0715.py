# -*- coding: utf-8 -*-
"""明日(7/15)発売開始の公演を抽出。startDate==date==対象日＝発売開始形のみ（締切と誤らない）。"""
import io, json, re

TARGET = '2026-07-15'
s = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\]);', s, re.S)
ev = json.loads(m.group(1))

rows = []
for e in ev:
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        if t.get('startDate') == TARGET and t.get('date') == TARGET and '発売' in ty:
            rows.append((e.get('genre'), e.get('name'), e.get('venue'),
                         e.get('prefecture'), e.get('date'), ty))

rows.sort()
with io.open('tmp/tomorrow_0715.txt', 'w', encoding='utf-8') as f:
    f.write('7/15 発売開始 %d枠\n\n' % len(rows))
    for g, n, v, p, d, ty in rows:
        f.write('[%s] %s\n    %s (%s) 公演日=%s\n    %s\n' % (g, n, v, p, d, ty))
print('done')
