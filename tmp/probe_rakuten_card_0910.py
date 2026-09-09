# -*- coding: utf-8 -*-
"""楽天チケットの公演カードが「1枚ずつ飛び先URL」を持つか実ページで確かめる。"""
import re, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

URL = 'https://ticket.rakuten.co.jp/music/rtal267/'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
body = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace')
print('len=%d' % len(body))

CARD = re.compile(r"<div[^>]*class='(?P<state>[^']*performance[^']*)'[^>]*data-date='(?P<dd>\{[^']*\})'(?P<body>.*?)</div>\s*</div>\s*</div>", re.S)
n = 0
for m in CARD.finditer(body):
    n += 1
    if n > 3:
        break
    b = m.group('body')
    print('---- card %d state=%s' % (n, m.group('state')))
    print('  data-date=%s' % m.group('dd')[:200])
    hrefs = re.findall(r'href="([^"]+)"', b)
    print('  hrefs=%r' % (hrefs[:6],))
    print('  raw tail=%s' % re.sub(r'\s+', ' ', b[-600:]))
print('total cards matched=%d' % n)
