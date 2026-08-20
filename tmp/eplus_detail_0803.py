# -*- coding: utf-8 -*-
"""e+ の /sf/detail/ ページから公演日一覧と販売枠(受付期間・状態)を機械抽出する。
reference_eplus_machine_parse の方式。"""
import re, sys, urllib.request, html
sys.stdout.reconfigure(encoding='utf-8')

url = sys.argv[1]
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
h = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
print('len=%d' % len(h))

print('--- 公演日option ---')
for m in re.findall(r'<option[^>]*value="[^"]*"[^>]*>(.*?)</option>', h, re.S):
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', m))).strip()
    if t:
        print('  ' + t)

print('--- 販売枠ブロック ---')
for blk in re.findall(r'<header class="block-ticket__header".*?</header>', h, re.S):
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', blk))).strip()
    print('  ' + t)

print('--- 受付期間らしき文字列 ---')
for m in set(re.findall(r'受付期間[^<]{0,80}', h)):
    print('  ' + re.sub(r'\s+', ' ', html.unescape(m)).strip())
print('--- ステータス ---')
for m in set(re.findall(r'ticket-status__item[^>]*>([^<]{1,30})<', h)):
    print('  ' + m.strip())
