# -*- coding: utf-8 -*-
"""e+ の /sf/word/<id> ページから公演の detail URL を機械抽出する。"""
import re, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

url = sys.argv[1]
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
h = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
print('len=%d' % len(h))
for m in sorted(set(re.findall(r'https://eplus\.jp/sf/detail/[0-9A-Za-z\-]+', h))):
    print(m)
for m in sorted(set(re.findall(r'"(/sf/detail/[0-9A-Za-z\-]+)"', h))):
    print('https://eplus.jp' + m)
