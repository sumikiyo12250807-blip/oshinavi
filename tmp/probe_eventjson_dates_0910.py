# -*- coding: utf-8 -*-
"""新型（data-event-json）の外部JSONの dates に、売り状態が読めるものがあるか見る。"""
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

for U in ['https://ticket.rakuten.co.jp/music/jpop/idle/rtzzz45/',
          'https://ticket.rakuten.co.jp/music/jpop/idle/rtzzz48/',
          'https://ticket.rakuten.co.jp/music/jpop/idle/rtzzz65/']:
    print('===== %s' % U)
    body = P.fetch(U)
    m = re.search(r'data-event-json=[\'"]([^\'"]+)[\'"]', body)
    if not m:
        print('  data-event-json が無い\n')
        continue
    d = json.loads(P.fetch(m.group(1)))
    ds = d.get('dates') or []
    print('  dates %d件 / 先頭の型: %s' % (len(ds), type(ds[0]).__name__ if ds else '-'))
    for x in ds[:8]:
        print('    %s' % json.dumps(x, ensure_ascii=False)[:260])
    print()
