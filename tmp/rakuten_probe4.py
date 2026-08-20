# -*- coding: utf-8 -*-
"""楽天チケット：カテゴリ一覧ページの実体を特定する。"""
import sys, re, urllib.request, gzip
sys.stdout.reconfigure(encoding='utf-8')

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept-Language': 'ja'}


def get(u):
    req = urllib.request.Request(u, headers=HDR)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        if 'gzip' in r.headers.get('Content-Encoding', ''):
            raw = gzip.decompress(raw)
        return r.status, raw.decode('utf-8', 'replace')


CAND = [
    'https://ticket.rakuten.co.jp/music/',
    'https://ticket.rakuten.co.jp/music/jpop/',
    'https://ticket.rakuten.co.jp/music/fes/',
    'https://ticket.rakuten.co.jp/stage/',
    'https://ticket.rakuten.co.jp/event/museum/',
    'https://ticket.rakuten.co.jp/sports/',
]

for u in CAND:
    try:
        st, body = get(u)
    except Exception as ex:
        print('%s -> エラー %s' % (u, ex)); continue
    t = re.search(r'<title[^>]*>(.*?)</title>', body, re.S)
    evs = sorted(set(re.findall(r'ticket\.rakuten\.co\.jp/([a-z\-]+/(?:[a-z\-]+/)?rt[a-z0-9]+)/', body)))
    print('\n=== %s -> %s / %d bytes | %s' % (u, st, len(body), (t.group(1).strip()[:60] if t else '')))
    print('  公演URL数:', len(evs))
    for e in evs[:12]:
        print('    ', e)
    nxt = sorted(set(re.findall(r'href="([^"]*(?:page|p=)[0-9]+[^"]*)"', body)))[:5]
    if nxt:
        print('  ページング候補:', nxt)

print('\n=== sitemap.xml ===')
st, body = get('https://ticket.rakuten.co.jp/sitemap.xml')
print(body[:1500])
