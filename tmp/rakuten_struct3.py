# -*- coding: utf-8 -*-
"""楽天：公演ブロック(performances/event-details)の中身を丸ごと見る＝会場の在り処特定。"""
import sys, re, urllib.request, gzip, html
sys.stdout.reconfigure(encoding='utf-8')

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept-Language': 'ja'}


def get(u):
    req = urllib.request.Request(u, headers=HDR)
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read()
        if 'gzip' in r.headers.get('Content-Encoding', ''):
            raw = gzip.decompress(raw)
        return raw.decode('utf-8', 'replace')


def strip(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


u = 'https://ticket.rakuten.co.jp/music/jpop/idle/rtvm719/'
body = get(u)
print(u, len(body))

for cls in ('performances-body', 'event-details-body', 'ticket-info-container'):
    i = body.find(cls)
    if i < 0:
        print('\n[%s] 無し' % cls); continue
    print('\n=== %s ===' % cls)
    print(strip(body[i: i + 2500])[:1200])

# ページ本文の見出し（h1-h3）
print('\n=== 見出し ===')
for m in re.findall(r'<h[123][^>]*>(.*?)</h[123]>', body, re.S)[:15]:
    s = strip(m)
    if s:
        print('  ', s[:90])
