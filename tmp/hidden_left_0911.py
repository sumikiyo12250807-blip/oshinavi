# -*- coding: utf-8 -*-
"""残っている隠れ枠（startDate==date<=today）を、発売時刻と売り手で分けて数える（読むだけ）。"""
import collections, datetime, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
T = datetime.date.today().isoformat()
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
c = collections.Counter()
rows = []
for e in ev:
    for t in e.get('tickets') or []:
        sd, d = t.get('startDate'), t.get('date')
        if sd and sd == d and d <= T and not t.get('soldout'):
            m = re.search(r'(\d{1,2}/\d{1,2}) (\d{1,2}:\d{2})発売', t.get('type') or '')
            u = t.get('url') or (e.get('links') or {}).get('pia') or (e.get('links') or {}).get('eplus') or ''
            vend = 'pia' if 'pia.jp' in u else ('eplus' if 'eplus' in u else ('rakuten' if 'rakuten' in u else 'other'))
            key = (d, m.group(2) if m else '?', vend)
            c[key] += 1
            rows.append((key, e['id'], (e.get('name') or '')[:30], t.get('type')[:60]))
for k, v in sorted(c.items()):
    print(k, v)
print('---')
for key, i, n, ty in sorted(rows):
    if key[0] == T and key[1] != '?' and key[1] <= '12:00':
        print(key, i, n, ty)
