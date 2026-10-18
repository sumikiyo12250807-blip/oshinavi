# -*- coding: utf-8 -*-
import re, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read().decode('utf-8', 'replace')
h = get('https://oshinavi.jp/artists.html')
m = re.findall(r"<a href='(/artist/\d+)'>([^<]*ファインディング[^<]*)</a>", h)
print(m)
for u, _ in m:
    p = get('https://oshinavi.jp' + u)
    print(u, re.search(r'<title>(.*?)</title>', p).group(1))
    print('  description:', re.findall(r'<meta name="description" content="([^"]*)"', p))
