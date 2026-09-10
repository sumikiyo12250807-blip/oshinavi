# -*- coding: utf-8 -*-
"""特設ページのパーサを、ユーザーが持ってきた実物で試す。"""
import json
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P
import rakuten_features_sweep as F

for u in ['https://ticket.rakuten.co.jp/features/sada-tour-2026/',
          'https://ticket.rakuten.co.jp/features/tamagawa/index.html/',
          'https://ticket.rakuten.co.jp/features/disneyonice/index.html/']:
    print('===== %s' % u)
    try:
        body = P.fetch(u)
    except Exception as ex:
        print('  取得失敗 %r\n' % (ex,))
        continue
    r = F.parse_feature(u, body)
    print('  公演ページ %d本 / 日程表 %d行（扱う %d / 取り扱いなし %d）'
          % (len(r['events']), len(r['rows']), r['handled'], r['notsold']))
    for e in r['events']:
        print('    %s' % e)
    for row in r['rows'][:14]:
        print('    %-7s %-5s %-32s %s' % (row['md'], row['pref'], row['venue'][:32], row['state']))
    print()
