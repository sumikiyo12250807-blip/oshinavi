# -*- coding: utf-8 -*-
"""楽天の特設ページ（/features/…）を一覧できる入口を探す。

ユーザーが見つけた https://ticket.rakuten.co.jp/features/sada-tour-2026/ は
post-sitemap の /rtXXXX/ 形に入っておらず、いまのハーベストが1件も見ていない形。
"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

FEAT = re.compile(r'https://ticket\.rakuten\.co\.jp/features/[^\s"\'<>]+')

for name in ['sitemap.xml', 'page-sitemap.xml', 'sitemap-misc.xml',
             'category-sitemap.xml', 'static_event-sitemap.xml']:
    u = 'https://ticket.rakuten.co.jp/' + name
    try:
        body = P.fetch(u)
    except Exception as ex:
        print('%-28s 取得失敗 %r' % (name, ex))
        continue
    locs = re.findall(r'<loc>([^<]+)</loc>', body)
    feats = sorted({l for l in locs if '/features/' in l})
    print('%-28s loc=%-6d features=%d' % (name, len(locs), len(feats)))
    for f in feats[:12]:
        print('     %s' % f)

# トップページや一覧ページから拾えるか
for u in ['https://ticket.rakuten.co.jp/', 'https://ticket.rakuten.co.jp/features/']:
    try:
        body = P.fetch(u)
    except Exception as ex:
        print('\n%s 取得失敗 %r' % (u, ex))
        continue
    fs = sorted(set(FEAT.findall(body)))
    print('\n%s → features リンク %d本' % (u, len(fs)))
    for f in fs[:20]:
        print('   %s' % f)
