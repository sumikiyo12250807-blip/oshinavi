# -*- coding: utf-8 -*-
"""単独公演型（data-perf が無く cart-button が生HTMLにある形）の売り状態を見る。"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

for U in ['https://ticket.rakuten.co.jp/music/jpop/rt4tkw2/',
          'https://ticket.rakuten.co.jp/music/rtkb710/',
          'https://ticket.rakuten.co.jp/event/rtb9s48/']:
    print('===== %s' % U)
    body = P.fetch(U)
    for m in list(re.finditer('salesDisplayStatus', body))[:1]:
        i = m.start()
        print('  --- salesDisplayStatus ---')
        print(body[i - 200:i + 900])
    for m in list(re.finditer('cart-button', body))[:2]:
        i = m.start()
        print('  --- cart-button ---')
        print(re.sub(r'\s+', ' ', body[max(0, i - 400):i + 300]))
    for m in list(re.finditer('予定枚数', body))[:2]:
        i = m.start()
        print('  --- 予定枚数 ---')
        print(re.sub(r'\s+', ' ', P.strip_tags(body[max(0, i - 400):i + 200])))
    print()
