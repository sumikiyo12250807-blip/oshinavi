# -*- coding: utf-8 -*-
"""e+の個別ページにジャンルの申告があるかを機械で確かめる（2026-09-23 夜の調査）。
新着プールに残る e+272件は _genre が無い＝振り分けられない。売り場が本当に何も言っていないのか、
それともハーベスタが拾っていないだけなのかを、生HTMLの中身で判定する。
🚨化けた日本語を目で読まないため、判定はすべて真偽値と件数で出す（[[feedback_no_mojibake_japanese_read]]）。
使い方: python tmp/x0923/eplus_genre_probe.py <URL> [<URL>...]
"""
import io
import json
import re
import sys
import urllib.request

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/129.0 Safari/537.36'}

PROBES = [
    ('jsonld', re.compile(r'application/ld\+json')),
    ('breadcrumb_word', re.compile(r'BreadcrumbList')),
    ('genre_attr', re.compile(r'(?:data-genre|genreCd|genre_cd|genreCode)')),
    ('sf_live_link', re.compile(r'/sf/live/([a-z0-9_]+)')),
    ('sf_word_link', re.compile(r'/sf/word/')),
    ('kw_genre_ja', re.compile('ジャンル')),          # 「ジャンル」
    ('kw_music_ja', re.compile('音楽')),                      # 「音楽」
]

for url in sys.argv[1:]:
    try:
        html = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30)\
            .read().decode('utf-8', 'replace')
    except Exception as e:
        print('FETCH_ERR', url, type(e).__name__, getattr(e, 'code', ''))
        continue
    print('--- %s  bytes=%d' % (url.split('/')[-1], len(html)))
    for name, rx in PROBES:
        hits = rx.findall(html)
        print('    %-16s %s %s' % (name, bool(hits), sorted(set(hits))[:8] if hits and isinstance(hits[0], str) else ''))
    # JSON-LD の中身のキーだけ出す
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception:
            print('    jsonld_parse   False')
            continue
        ds = d if isinstance(d, list) else [d]
        for x in ds:
            if isinstance(x, dict):
                print('    jsonld_keys    %s' % sorted(x.keys())[:14])
