# -*- coding: utf-8 -*-
"""e+検索ページの生HTMLから公演detailリンクを抜けるか調べる（WebFetch要約はJS描画で空になる）。"""
import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

URL = ('https://eplus.jp/sf/search?block=true&keyword='
       '%E3%83%87%E3%82%A3%E3%82%BA%E3%83%8B%E3%83%BC%E3%83%BB%E3%82%AA%E3%83%B3%E3%83%BB%E3%82%AF%E3%83%A9%E3%82%B7%E3%83%83%E3%82%AF'
       '&kogyo=005151')
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
print('HTML長', len(h))

links = sorted(set(re.findall(r'/sf/detail/(\d+)', h)))
print('detailリンク', len(links), links[:40])

# 公演リストがJSONで埋まっている場合に備えて手がかりを探す
for kw in ('札幌', '沖縄', '秋田', '砺波', 'フェスティバルホール', '公演はありません'):
    print(f'  「{kw}」出現 {h.count(kw)}回')
