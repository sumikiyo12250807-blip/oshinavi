#!/usr/bin/env python3
"""nobinobi ぴあページの券種DOM構造を確認（ticketSalesCard-2024 が無い理由）"""
import io
import re
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669172'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')

for key in ['ticketSalesList-2024__item', 'ticketSalesCard-2024__status',
            'ticketSalesCard-2024', 'ticketInformation.do', 'チケット購入', 'is-active']:
    print(f'{key}: {html.count(key)}回')

print('\n--- "チケット購入" の周辺HTML (最初の2箇所・前後900字) ---')
for m in list(re.finditer('チケット購入', html))[:2]:
    s = max(0, m.start() - 900)
    print('=' * 70)
    print(html[s:m.end() + 120])

print('\n--- is-active の周辺HTML ---')
for m in list(re.finditer('is-active', html))[:2]:
    s = max(0, m.start() - 500)
    print('=' * 70)
    print(html[s:m.end() + 600])
