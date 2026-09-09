# -*- coding: utf-8 -*-
"""どのsitemapが「今の公演」を持っているかを、lastmodの範囲で測る。

post-sitemap は投稿順（1番＝2019年／27番＝2026年）。
lastmod の最小・最大を見れば、どこから舐めれば足りるかが決まる。
"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

RT = re.compile(r'/rt[0-9a-z]{4,8}/?$', re.I)
total = 0
for n in range(27, 17, -1):
    name = 'post-sitemap%s.xml' % ('' if n == 1 else n)
    u = 'https://ticket.rakuten.co.jp/' + name
    try:
        body = P.fetch(u)
    except Exception as ex:
        print('%-22s 取得失敗' % name)
        continue
    locs = re.findall(r'<loc>([^<]+)</loc>', body)
    mods = re.findall(r'<lastmod>([^<]+)</lastmod>', body)
    rts = [l for l in locs if RT.search(l)]
    total += len(rts)
    print('%-22s 公演URL=%-6d lastmod %s 〜 %s'
          % (name, len(rts), (min(mods) if mods else '')[:10], (max(mods) if mods else '')[:10]))
print('\n27→18 の合計 公演URL=%d' % total)
