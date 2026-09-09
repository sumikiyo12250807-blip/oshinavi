# -*- coding: utf-8 -*-
"""どのサブsitemapに公演ページ(/rtXXXX/)が入っているか、並びが新しさ順かを見る。"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

RT = re.compile(r'/rt[0-9a-z]{4,8}/?$', re.I)

for name in ['static_event-sitemap.xml', 'post-sitemap27.xml', 'post-sitemap28.xml',
             'post-sitemap.xml']:
    u = 'https://ticket.rakuten.co.jp/' + name
    try:
        body = P.fetch(u)
    except Exception as ex:
        print('%-32s 取得失敗 %r' % (name, ex))
        continue
    locs = re.findall(r'<loc>([^<]+)</loc>', body)
    mods = re.findall(r'<lastmod>([^<]+)</lastmod>', body)
    rts = [l for l in locs if RT.search(l)]
    print('%-32s len=%-8d loc=%-6d 公演URL=%-6d lastmod=%d'
          % (name, len(body), len(locs), len(rts), len(mods)))
    if rts:
        print('   先頭: %s  %s' % (rts[0], mods[0] if mods else ''))
        print('   末尾: %s  %s' % (rts[-1], mods[-1] if mods else ''))
        # lastmod の並びが単調か（＝投稿順か）
        if len(mods) == len(locs) and len(mods) > 4:
            print('   lastmod 先頭5: %s' % mods[:5])
            print('   lastmod 末尾5: %s' % mods[-5:])
