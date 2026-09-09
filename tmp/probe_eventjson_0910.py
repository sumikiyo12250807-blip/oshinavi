# -*- coding: utf-8 -*-
"""新型（data-event-json）の外部JSONに売り状態が入っているかを見る。"""
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

for U in ['https://ticket.rakuten.co.jp/music/jpop/idle/rtzzz45/',
          'https://ticket.rakuten.co.jp/music/jpop/idle/rtzzz48/']:
    print('===== %s' % U)
    body = P.fetch(U)
    m = re.search(r'data-event-json=[\'"]([^\'"]+)[\'"]', body)
    if not m:
        print('  data-event-json が無い\n')
        continue
    ju = m.group(1)
    print('  json: %s' % ju)
    try:
        d = json.loads(P.fetch(ju))
    except Exception as ex:
        print('  取得失敗 %r\n' % (ex,))
        continue
    print('  トップのキー: %s' % list(d.keys())[:15])
    s = json.dumps(d, ensure_ascii=False)
    for w in ['予定枚数終了', '完売', 'soldOut', 'sold_out', 'status', 'salesStatus', 'buyUrl', 'buyUrls']:
        print('    %-14s %d' % (w, s.count(w)))
    print('  先頭800字: %s\n' % s[:800])
