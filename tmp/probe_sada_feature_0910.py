# -*- coding: utf-8 -*-
"""楽天の特設ページ（/features/…）に何が載っているかを見る。

ユーザーが見つけた https://ticket.rakuten.co.jp/features/sada-tour-2026/
＝あたしのハーベストの入口（post-sitemap の /rtXXXX/ 形）には**入っていない形**。
"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

U = 'https://ticket.rakuten.co.jp/features/sada-tour-2026/'
body = P.fetch(U)
print('len=%d' % len(body))

for kw in ['data-perf', 'performance_btn', 'let ecd', '"eid"', 'data-event-json',
           'salesDisplayStatus', 'cart-button', '予定枚数', '販売期間', '公演']:
    print('  %-20s %d' % (kw, body.count(kw)))

# 中のイベントページ(/rtXXXX/)へのリンクを拾う
links = sorted(set(re.findall(r'https://ticket\.rakuten\.co\.jp/[^\s"\']*?/rt[0-9a-z]{4,8}/', body)))
print('\n中のイベントページ %d本' % len(links))
for u in links:
    print('   %s' % u)

txt = re.sub(r'\s+', ' ', P.strip_tags(body))
i = txt.find('公演')
print('\n本文の一部:\n%s' % txt[max(0, i - 200):i + 1800])
