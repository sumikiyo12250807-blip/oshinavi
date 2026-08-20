#!/usr/bin/env python3
"""w.pia.jp 券種ページの受付期間・状態を特定"""
import io
import re
import sys
import urllib.request
import html as _html

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL = 'https://w.pia.jp/t/nobinobi26-2days/'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')

txt = re.sub(r'<script.*?</script>', '', html, flags=re.S)
txt = re.sub(r'<style.*?</style>', '', txt, flags=re.S)
txt = re.sub(r'<[^>]+>', ' ', txt)
txt = _html.unescape(re.sub(r'\s+', ' ', txt)).strip()

i = txt.find('先行先着プリセール')
print('--- 「先行先着プリセール」以降 1200字 ---')
print(txt[i:i + 1200] if i >= 0 else '(見つからず)')

print('\n--- 状態クラス ---')
for cls in ['is-active', 'is-before', 'is-end', 'ticketSalesCard', 'ticketSalesList']:
    print(f'  {cls}: {html.count(cls)}回')

print('\n--- 日時表記すべて ---')
for d in sorted(set(re.findall(r'\d{4}/\d{1,2}/\d{1,2}\s*\([^)]{1,3}\)\s*\d{1,2}:\d{2}', txt))):
    print('  ', d)
