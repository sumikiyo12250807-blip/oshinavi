# -*- coding: utf-8 -*-
"""新型の外部JSONの構造を丸ごと見る（buyUrl がどこに、どんな条件で入るか）。"""
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

U = 'https://ticket.rakuten.co.jp/music/jpop/idle/rtzzz48/'
body = P.fetch(U)
m = re.search(r'data-event-json=[\'"]([^\'"]+)[\'"]', body)
d = json.loads(P.fetch(m.group(1)))

for k, v in d.items():
    if isinstance(v, list):
        print('%-16s list(%d)' % (k, len(v)))
        for x in v[:4]:
            print('     %s' % json.dumps(x, ensure_ascii=False)[:400])
    elif isinstance(v, dict):
        print('%-16s dict keys=%s' % (k, list(v.keys())[:10]))
    else:
        print('%-16s %s' % (k, json.dumps(v, ensure_ascii=False)[:120]))
