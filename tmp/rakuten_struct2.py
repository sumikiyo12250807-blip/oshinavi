# -*- coding: utf-8 -*-
"""楽天：salesDisplayStatus JSON と 会場/都道府県 の在り処を確認。"""
import sys, re, json, urllib.request, gzip, html
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


for u in ('https://ticket.rakuten.co.jp/music/fes/rtvmhm6/',
          'https://ticket.rakuten.co.jp/music/jpop/idle/rtvm719/'):
    body = get(u)
    print('\n' + '=' * 70)
    print(u)
    m = re.search(r'var salesDisplayStatus = (\{.*?\});', body, re.S)
    if m:
        try:
            js = json.loads(m.group(1))
            print('--- salesDisplayStatus %d枠 ---' % len(js))
            for k, v in js.items():
                print('  %s: %s | %s | status=%s | start=%s' % (
                    k, v.get('sales_group'), v.get('timming'), v.get('sales_status'), v.get('sales_start_date')))
        except Exception as ex:
            print('  JSONパース失敗', ex)
            print(m.group(1)[:400])
    else:
        print('--- salesDisplayStatus 無し（false or 単一枠）---')

    # 会場・都道府県
    for kw in ('会場', '都道府県', '開催地'):
        for mm in list(re.finditer(kw, body))[:2]:
            print('  [%s] %s' % (kw, strip(body[mm.start(): mm.start() + 220])[:150]))
    # og系メタ
    for p in re.findall(r'<meta[^>]+(?:property|name)="(og:[^"]+|description)"[^>]+content="([^"]{0,200})"', body)[:6]:
        print('  meta %s = %s' % p)
