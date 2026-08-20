# -*- coding: utf-8 -*-
"""2800 MAZDA FAN FESTA: 「おもてなしラウンジ」券種の実状態をぴあ生HTMLで確認"""
import re, urllib.request

URL = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669251'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

print('HTML長: %d' % len(html))
tag = re.compile(r'<[^>]+>')

for m in re.finditer(r'ラウンジ', html):
    s = max(0, m.start() - 1800)
    e = min(len(html), m.end() + 1800)
    blk = html[s:e]
    txt = tag.sub(' ', blk)
    txt = re.sub(r'\s+', ' ', txt).strip()
    print('=== hit @%d ===' % m.start())
    print(txt[:1200])
    print()
