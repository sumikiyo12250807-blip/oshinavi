#!/usr/bin/env python3
"""nobinobi のぴあページ生HTMLを覗く（0券種の原因確認）"""
import io
import re
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669172'
req = urllib.request.Request(URL, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36'
})
with urllib.request.urlopen(req, timeout=60) as r:
    status = r.status
    html = r.read().decode('utf-8', 'replace')

print(f'HTTP {status} / {len(html)} bytes')

# title
m = re.search(r'<title>(.*?)</title>', html, re.S)
print('title:', (m.group(1).strip() if m else '無し'))

# 状態クラス（is-active / is-before / is-end 等）
for cls in ['is-active', 'is-before', 'is-end', 'is-close', 'soldout']:
    print(f'  class {cls}: {html.count(cls)}回')

# 販売期間らしき文字列
for kw in ['受付中', '発売前', '受付終了', '予定枚数', '販売期間', '発売', '取扱い', 'エラー', '見つかり']:
    n = html.count(kw)
    if n:
        print(f'  "{kw}": {n}回')

# 本文テキストを軽く抜く
txt = re.sub(r'<script.*?</script>', '', html, flags=re.S)
txt = re.sub(r'<style.*?</style>', '', txt, flags=re.S)
txt = re.sub(r'<[^>]+>', ' ', txt)
txt = re.sub(r'\s+', ' ', txt)
print('\n--- 本文抜粋(先頭1500字) ---')
print(txt[:1500])
