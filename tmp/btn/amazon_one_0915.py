# -*- coding: utf-8 -*-
"""Amazonの検索1本だけ、商品名に作品名が入っている件数を測る（2026-09-15 夜・しまじろうグッズ）
数え方は tools/amazon_audit.py と同じ（data-asin の数では数えない＝0件でも関連商品が並ぶ）。
3件未満なら20秒おいて単独で測り直す（連続で叩くと偽の0件を返す）。
使い方: python amazon_one_0915.py "<検索語>" "<商品名に入っているか見る正規表現>"
"""
import html as _html
import re
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
q, wre = sys.argv[1], sys.argv[2]
URL = 'https://www.amazon.co.jp/s?k=' + urllib.parse.quote(q) + '&tag=oshinavi0a-22'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
           'Accept-Language': 'ja,en;q=0.8'}


def probe():
    h = urllib.request.urlopen(urllib.request.Request(URL, headers=HEADERS), timeout=25).read().decode('utf-8', 'replace')
    ts, seen = [], set()
    for t in re.findall(r'<h2[^>]*>.*?<span[^>]*>([^<]{4,200})</span>', h, re.S):
        t = _html.unescape(re.sub(r'\s+', ' ', t)).strip()
        if t and t not in seen:
            seen.add(t); ts.append(t)
    return [t for t in ts if re.search(wre, t)]


hits = probe()
if len(hits) < 3:
    time.sleep(20)
    hits2 = probe()
    if len(hits2) > len(hits):
        hits = hits2
print('件数', len(hits))
print('URL', URL)
for t in hits[:8]:
    print(' -', t[:70])
