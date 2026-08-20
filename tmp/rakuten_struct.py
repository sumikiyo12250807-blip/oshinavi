# -*- coding: utf-8 -*-
"""楽天：公演ページの構造（公演名/会場/公演日/販売期間）の在り処を特定する。"""
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
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


for u in ('https://ticket.rakuten.co.jp/music/fes/rtvmhm6/',
          'https://ticket.rakuten.co.jp/music/classic/rtxn116/'):
    body = get(u)
    print('\n' + '=' * 70)
    print(u, len(body), 'bytes')
    t = re.search(r'<title[^>]*>(.*?)</title>', body, re.S)
    print('title:', strip(t.group(1))[:90] if t else 'なし')

    # 「販売期間」まわりを前後500字で見る
    for m in list(re.finditer('販売期間', body))[:3]:
        seg = body[max(0, m.start() - 700): m.start() + 700]
        print('\n--- 販売期間まわり ---')
        print(strip(seg)[:600])

    # class名の候補
    cls = re.findall(r'class="([a-zA-Z0-9_\- ]{3,40})"', body)
    import collections
    c = collections.Counter(x for x in cls if any(k in x.lower() for k in ('perform', 'ticket', 'sale', 'event', 'date', 'venue', 'place')))
    print('\n関連しそうなclass:', c.most_common(12))
