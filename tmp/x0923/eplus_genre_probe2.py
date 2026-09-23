# -*- coding: utf-8 -*-
"""e+個別ページのパンくず（BreadcrumbList）と /sf/live/ リンクを取り出す（2026-09-23 夜の調査）。
狙い＝新着プールに残る e+272件のジャンルを、売り場の申告から機械で写せるかを確かめる。
🚨日本語は目で読まずJSONに落として Read で見る（[[feedback_no_mojibake_japanese_read]]）。
使い方: python tmp/x0923/eplus_genre_probe2.py <out.json> <URL> [<URL>...]
"""
import io
import json
import re
import sys
import urllib.request

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/129.0 Safari/537.36'}
out_path = sys.argv[1]
res = {}
for url in sys.argv[2:]:
    rec = {}
    try:
        html = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30)\
            .read().decode('utf-8', 'replace')
    except Exception as e:
        res[url] = {'error': '%s %s' % (type(e).__name__, getattr(e, 'code', ''))}
        continue
    # /sf/live/<cat> リンクを全部（重複除去・出現順）
    seen, live = set(), []
    for m in re.finditer(r'/sf/live/([a-z0-9_]+)', html):
        if m.group(1) not in seen:
            seen.add(m.group(1))
            live.append(m.group(1))
    rec['sf_live'] = live
    # BreadcrumbList（JSON-LD）
    crumbs = []
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        for x in (d if isinstance(d, list) else [d]):
            if isinstance(x, dict) and x.get('@type') == 'BreadcrumbList':
                for it in x.get('itemListElement') or []:
                    nm = it.get('name') or (it.get('item') or {}).get('name')
                    crumbs.append(nm)
    rec['breadcrumb_jsonld'] = crumbs
    # HTML のパンくず（class に breadcrumb を含む塊のリンク文字）
    mb = re.search(r'<[^>]+class="[^"]*breadcrumb[^"]*"[^>]*>(.*?)</(?:ol|ul|nav|div)>', html, re.S | re.I)
    if mb:
        rec['breadcrumb_html'] = [re.sub(r'<[^>]+>', '', s).strip()
                                  for s in re.findall(r'<li[^>]*>(.*?)</li>', mb.group(1), re.S)]
    res[url] = rec

io.open(out_path, 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=1))
print('WROTE', out_path, 'urls', len(res))
