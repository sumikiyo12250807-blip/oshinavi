# -*- coding: utf-8 -*-
"""楽天チケットが機械で読めるか調べる（一覧ページの取得可否とHTML構造の確認）。"""
import sys, re, json, urllib.request, gzip, io
sys.stdout.reconfigure(encoding='utf-8')

URLS = [
    'https://ticket.rakuten.co.jp/',
    'https://ticket.rakuten.co.jp/search/',
    'https://ticket.rakuten.co.jp/genre/music/',
    'https://ticket.rakuten.co.jp/genre/stage/',
]

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
       'Accept-Language': 'ja,en;q=0.8'}


def get(u):
    req = urllib.request.Request(u, headers=HDR)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        enc = r.headers.get('Content-Encoding', '')
        if 'gzip' in enc:
            raw = gzip.decompress(raw)
        return r.status, raw.decode('utf-8', 'replace')


for u in URLS:
    try:
        st, body = get(u)
    except Exception as ex:
        print('%s -> エラー %s' % (u, ex))
        continue
    print('\n=== %s -> HTTP %s / %d bytes ===' % (u, st, len(body)))
    title = re.search(r'<title[^>]*>(.*?)</title>', body, re.S)
    print('  title:', (title.group(1).strip()[:80] if title else 'なし'))
    # 公演ページへのリンクがHTMLに埋まっているか（=静的に読めるか）
    links = set(re.findall(r'href="(https://ticket\.rakuten\.co\.jp/[^"]+)"', body))
    links |= set('https://ticket.rakuten.co.jp' + x for x in re.findall(r'href="(/[a-zA-Z0-9][^"]*)"', body))
    ev = [x for x in links if re.search(r'/(event|perform|detail)/|/[A-Z0-9]{4,}/', x)]
    print('  リンク総数 %d / 公演らしきリンク %d' % (len(links), len(ev)))
    for x in list(ev)[:8]:
        print('    ', x)
    # JSON-LD / __NEXT_DATA__ があるか
    print('  JSON-LD:', body.count('application/ld+json'), '/ __NEXT_DATA__:', ('__NEXT_DATA__' in body))
