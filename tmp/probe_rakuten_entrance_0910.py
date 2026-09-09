# -*- coding: utf-8 -*-
"""楽天チケットに「これから発売」を絞れる入口が無いか探す。

2026-09-09 の宿題＝入口が sitemap の lastmod しか無く、27,105件中119件しか見ていない。
今日 cms-api（cms-api.ticket.rakuten.co.jp/coreui/ajax/...）が見つかったので、
一覧系のエンドポイントやサイト内の一覧ページがないかを当たる。
"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

TOP = 'https://ticket.rakuten.co.jp/'
body = P.fetch(TOP)
print('トップ len=%d' % len(body))

hrefs = re.findall(r'href="(https://ticket\.rakuten\.co\.jp/[^"]*)"', body)
paths = []
for h in hrefs:
    p = h.replace('https://ticket.rakuten.co.jp', '')
    p = re.sub(r'\?.*$', '', p)
    if p and p not in paths:
        paths.append(p)
print('内部リンク %d本（重複除去）' % len(paths))
for p in paths[:70]:
    print('   %s' % p)

print('\n--- 一覧っぽい語を含むリンク ---')
for p in paths:
    if re.search(r'search|list|calendar|new|soon|ranking|genre|coming|schedule|発売', p):
        print('   %s' % p)
