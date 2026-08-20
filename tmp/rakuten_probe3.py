# -*- coding: utf-8 -*-
"""楽天チケット：一覧(area/ジャンル)ページから公演URLを列挙できるか調べる。"""
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
    'https://ticket.rakuten.co.jp/area/kanto/',
    'https://ticket.rakuten.co.jp/area/kanto/music/',
    'https://ticket.rakuten.co.jp/list/',
    'https://ticket.rakuten.co.jp/event/',
    'https://ticket.rakuten.co.jp/sitemap.xml',
]

for u in CAND:
    try:
        st, body = get(u)
    except Exception as ex:
        print('%s -> エラー %s' % (u, ex)); continue
    t = re.search(r'<title[^>]*>(.*?)</title>', body, re.S)
    evs = sorted(set(re.findall(r'ticket\.rakuten\.co\.jp/(event/[^"\'\s<>]+)', body)))
    print('\n=== %s -> %s / %d bytes ===' % (u, st, len(body)))
    print('  title:', (t.group(1).strip()[:70] if t else 'なし'))
    print('  公演URL数:', len(evs))
    for e in evs[:10]:
        print('    ', e)
