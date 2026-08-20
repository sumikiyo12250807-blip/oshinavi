# -*- coding: utf-8 -*-
"""楽天：解析不能ページの理由を1件ずつ見る。"""
import sys, re, html
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

URLS = [
    'https://ticket.rakuten.co.jp/music/jpop/idle/rtzzz45/',
    'https://ticket.rakuten.co.jp/music/fes/rthff26/',
    'https://ticket.rakuten.co.jp/event/museum/rtfj428/',
    'https://ticket.rakuten.co.jp/sports/golf/rtet723/',
]

for u in URLS:
    try:
        body = R.fetch(u)
    except Exception as ex:
        print(u, '取得失敗', ex); continue
    rec = R.parse_page(u, body)
    print('\n=== %s' % u)
    print('  name=%r genre=%r cats=%s' % (rec['name'], rec['_genre'], rec['cats']))
    print('  公演数=%d 枠数=%d' % (len(rec['perfs']), len(rec['windows'])))
    if not rec['perfs']:
        i = body.find('performances-body')
        seg = body[i:i + 3000] if i >= 0 else body[:2000]
        print('  --- performances-body 生テキスト ---')
        print('  ' + R.strip_tags(seg)[:700])
