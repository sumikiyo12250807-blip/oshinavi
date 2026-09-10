# -*- coding: utf-8 -*-
"""salesDisplayStatus の sales_status が何を意味するかを、実物と突き合わせて調べる。

対象＝data-perf を持たない「単独公演型」（さだまさし・春猿火・KOKO・理芽）。
"""
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

for U in ['https://ticket.rakuten.co.jp/music/jpop/rt4tkw2/',
          'https://ticket.rakuten.co.jp/music/rtkb710/']:
    print('===== %s' % U)
    body = P.fetch(U)
    m = re.search(r'var salesDisplayStatus\s*=\s*(\{.*?\});', body, re.S)
    if not m:
        print('  salesDisplayStatus が無い\n')
        continue
    d = json.loads(m.group(1))
    for k, v in d.items():
        print('  %-8s status=%-3s %-30s %s'
              % (k, v.get('sales_status'), (v.get('sales_group') or '')[:30], v.get('timming')))
    print()
