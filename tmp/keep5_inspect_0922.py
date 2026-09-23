# -*- coding: utf-8 -*-
"""check_zero_badge の「31日より先で枠0」35件の中身（売り場・枠の形）を見る。"""
import io, json, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
IDS = [21880]; _X = [17476, 17477, 17479, 17481, 20738, 3085, 6233, 6420, 17508, 10762, 7819, 16314, 4410,
       20799, 5612, 4407, 6934, 4114, 13315, 13316, 4111, 5433, 6231, 17556, 5669, 3368, 7821,
       7820, 1149, 17575, 17290, 6464, 7115, 1401, 2168]
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);',
                          io.open('index.html', encoding='utf-8').read(), re.S).group(1))
by = {e['id']: e for e in ev}
for i in IDS:
    e = by[i]
    links = {k: v for k, v in (e.get('links') or {}).items() if v}
    print('id%d %s | %s | links=%s' % (i, e.get('genre'), (e.get('name') or '')[:40], ','.join(links)))
    for t in e.get('tickets') or []:
        flags = ''.join(k[0] for k in ('soldout', 'saleEnded', 'presaleEnded', 'saleEndUnknown', 'saleUntilSoldOut') if t.get(k))
        print('    %s | start=%s end=%s [%s] %s' % ((t.get('type') or '')[:50], t.get('startDate'), t.get('date'), flags, (t.get('url') or '')[:60]))
