# -*- coding: utf-8 -*-
"""ぴあ実ページの券種カードを素のテキストで出す（when='' で解析不能になった枠の裏取り用）。
使い方: python tmp/peek_pia_0816.py <url> [絞り込み語]
"""
import re, sys, html, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

url = sys.argv[1]
needle = sys.argv[2] if len(sys.argv) > 2 else ''
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
h = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
print("len=%d" % len(h))

cards = re.findall(r'<[^>]*ticketSalesList-2024__item.*?(?=<[^>]*ticketSalesList-2024__item|</main)', h, re.S)
print("券種カード %d枚" % len(cards))
for c in cards:
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', c))).strip()
    if needle and needle not in t:
        continue
    print("-" * 60)
    print(t[:420])
