"""8/3に発売開始する枠を抽出（startDate明示のものだけ＝feedback_sale_start_vs_deadline）"""
import sys, json, re
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from check_expired import extract_events_array

TARGET = '2026-08-04'
ev = extract_events_array(r'C:\Users\user\oshinavi\index.html')

hits = []
for e in ev:
    for t in (e.get('tickets') or []):
        sd = t.get('startDate')
        if sd == TARGET:
            hits.append((e, t))

lines = ['=== %s 発売開始（startDate明示）%d枠 ===' % (TARGET, len(hits))]
seen = {}
for e, t in hits:
    seen.setdefault(e['id'], []).append(t)

lines.append('エントリ数 %d' % len(seen))
lines.append('')
for eid, ts in seen.items():
    e = next(x for x in ev if x['id'] == eid)
    lines.append('id=%d | %s | %s | %s | %s | 公演%s' % (
        eid, e.get('genre'), e.get('artist'), e.get('name'),
        e.get('venue'), e.get('dateLabel')))
    for t in ts:
        lines.append('     枠: %s' % t.get('type'))
    lines.append('     URL: %s' % ((e.get('links') or {}).get('pia')
                                   or (e.get('links') or {}).get('rakuten')
                                   or (e.get('links') or {}).get('eplus') or '-'))

open(r'C:\Users\user\oshinavi\tmp\tomorrow_sale_0804.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('枠', len(hits), 'エントリ', len(seen))
