# -*- coding: utf-8 -*-
"""e+ のキーワード検索(/sf/search?keyword=)の生HTMLから、公演カードを機械抽出する。
ぴあ外チャネルの取りこぼし確認用（memory: feedback_tour_cross_channel_blindspot）。
"""
import re, sys, io, html, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

kw = sys.argv[1]
url = 'https://eplus.jp/sf/search?keyword=' + urllib.parse.quote(kw)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
h = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
print('len=%d  %s' % (len(h), url))

def txt(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

# 検索結果は <li> or <div> のカード。detail URL を含むブロックで切る
blocks = re.split(r'(?=<(?:li|article|div)[^>]*class="[^"]*(?:search|list|card)[^"]*")', h)
seen = set()
n = 0
for b in blocks:
    m = re.search(r'/sf/detail/([0-9A-Za-z\-]+)', b)
    if not m or m.group(1) in seen:
        continue
    seen.add(m.group(1))
    t = txt(b)
    if len(t) < 5:
        continue
    n += 1
    print('%2d | %s' % (n, t[:190]))
print('--- 抽出 %d件 ---' % n)
