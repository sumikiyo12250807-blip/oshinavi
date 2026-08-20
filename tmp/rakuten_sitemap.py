# -*- coding: utf-8 -*-
"""楽天チケット：sitemapから全公演URLを列挙し、既存DBに無いものを数える。"""
import sys, re, json, urllib.request, gzip
sys.stdout.reconfigure(encoding='utf-8')

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept-Language': 'ja'}


def get(u):
    req = urllib.request.Request(u, headers=HDR)
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read()
        if 'gzip' in r.headers.get('Content-Encoding', ''):
            raw = gzip.decompress(raw)
        return raw.decode('utf-8', 'replace')


idx = get('https://ticket.rakuten.co.jp/sitemap.xml')
maps = re.findall(r'<loc>([^<]+)</loc>', idx)
print('sitemap数', len(maps))

urls = {}
for mu in maps:
    if 'post-sitemap' not in mu and 'static_event' not in mu:
        continue
    try:
        body = get(mu)
    except Exception as ex:
        print(' ', mu, 'エラー', ex); continue
    got = re.findall(r'<loc>(https://ticket\.rakuten\.co\.jp/[^<]+)</loc>', body)
    mods = re.findall(r'<lastmod>([^<]+)</lastmod>', body)
    for i, u in enumerate(got):
        urls[u] = mods[i] if i < len(mods) else ''
    print('  %s -> %d件' % (mu.rsplit('/', 1)[-1], len(got)))

# 公演ページだけ（rtXXXX形のIDを含むもの）
ev = {u: m for u, m in urls.items() if re.search(r'/rt[a-z0-9]{5,}/?$', u)}
print('\n総URL %d / 公演ページ %d' % (len(urls), len(ev)))

h = open('index.html', encoding='utf-8').read()
have = 0
new = []
for u in sorted(ev):
    key = re.search(r'/(rt[a-z0-9]{5,})/?$', u).group(1)
    if key in h:
        have += 1
    else:
        new.append((u, ev[u]))
print('既にDBにある %d / DBに無い %d' % (have, len(new)))

json.dump([{'url': u, 'lastmod': m} for u, m in new], open('tmp/rakuten_new_urls.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ tmp/rakuten_new_urls.json に書いた')
for u, m in new[:15]:
    print('  ', m[:10], u)
