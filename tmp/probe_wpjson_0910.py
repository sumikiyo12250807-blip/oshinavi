# -*- coding: utf-8 -*-
"""楽天チケットは WordPress。/wp-json/ で公演ページを一覧できないか当たる。

sitemap の lastmod は当てにならない（27,105件中119件しか動かない）ので、
REST API で「新しい順」「更新順」に引けるなら入口が広がる。
"""
import json
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

B = 'https://ticket.rakuten.co.jp/wp-json/'

try:
    root = json.loads(P.fetch(B))
    routes = sorted(root.get('routes', {}).keys())
    print('ルート %d本' % len(routes))
    for r in routes:
        print('   %s' % r)
except Exception as ex:
    print('失敗 %r' % (ex,))
