#!/usr/bin/env python3
"""nobinobi:「チケット購入」リンクのhrefを抽出（どこで買えるのか実データで確認）"""
import io
import re
import sys
import urllib.request
import html as _html

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669172'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')

# 「チケット購入」を含む <a ...>...</a> を全部拾う
links = re.findall(r'<a\s[^>]*href="([^"]+)"[^>]*>((?:(?!</a>).)*?チケット購入(?:(?!</a>).)*?)</a>', html, re.S)
print(f'「チケット購入」を含むaタグ: {len(links)}本')
hosts = {}
for href, label in links[:8]:
    lab = _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', label))).strip()
    print(f'  {lab[:40]!r} -> {href[:120]}')
for href, _ in links:
    m = re.match(r'https?://([^/]+)', href)
    h = m.group(1) if m else '(相対)'
    hosts[h] = hosts.get(h, 0) + 1
print('\nリンク先ホスト集計:', hosts)

# 券種テーブル周辺のテキスト（チケット情報〜）
txt = re.sub(r'<script.*?</script>', '', html, flags=re.S)
txt = re.sub(r'<style.*?</style>', '', txt, flags=re.S)
txt = re.sub(r'<[^>]+>', ' ', txt)
txt = _html.unescape(re.sub(r'\s+', ' ', txt))
i = txt.find('チケット情報')
print('\n--- 「チケット情報」以降 1800字 ---')
print(txt[i:i + 1800] if i >= 0 else '(見つからず)')
