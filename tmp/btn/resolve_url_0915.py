# -*- coding: utf-8 -*-
"""短いリンク（amzn.to など）の行き先をたどって、最後のURLと検索語を出す（2026-09-15 夜）
使い方: python resolve_url_0915.py <URL>
"""
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
           'Accept-Language': 'ja,en;q=0.8'}
res = urllib.request.urlopen(urllib.request.Request(sys.argv[1], headers=HEADERS), timeout=25)
final = res.geturl()
qs = urllib.parse.parse_qs(urllib.parse.urlparse(final).query)
print('行き先', final[:300])
print('検索語', qs.get('k', ['（なし）'])[0])
print('タグ', qs.get('tag', ['（なし）'])[0])
