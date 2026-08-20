# -*- coding: utf-8 -*-
"""明日(8/5)発売開始する枠を抽出＝X投稿の題材候補。
startDateが明示されている枠だけ（曖昧な「一般発売」を発売開始と決めつけない
＝[[feedback_sale_start_vs_deadline]]）。"""
import json
import re
import sys

sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from check_expired import extract_events_array   # noqa: E402

TARGET = '2026-08-05'
ev = extract_events_array(r'C:\Users\user\oshinavi\index.html')

seen = {}
for e in ev:
    for t in (e.get('tickets') or []):
        if t.get('startDate') == TARGET:
            seen.setdefault(e['id'], []).append(t)

lines = ['=== %s 発売開始（startDate明示）エントリ %d件 ===' % (TARGET, len(seen)), '']
for eid, ts in sorted(seen.items()):
    e = next(x for x in ev if x['id'] == eid)
    lines.append('id=%d [%s] %s' % (eid, e.get('genre'), e.get('artist')))
    lines.append('    公演: %s / %s' % (e.get('dateLabel'), e.get('venue')))
    for t in ts:
        lines.append('    枠  : %s | 締切=%s' % (t.get('type'), t.get('date')))
    lines.append('    URL : %s' % ((e.get('links') or {}).get('pia')
                                   or (e.get('links') or {}).get('rakuten')
                                   or (e.get('links') or {}).get('eplus') or '-'))
    lines.append('')
open(r'C:\Users\user\oshinavi\tmp\tomorrow_sale_0805.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('entries=%d  slots=%d' % (len(seen), sum(len(v) for v in seen.values())))
