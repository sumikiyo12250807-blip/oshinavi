# -*- coding: utf-8 -*-
"""e+由来2件の「チケットの関連ジャンル」を生HTMLから読む。読み取り専用。"""
import re, sys, io, urllib.request, html as _html, time
sys.stdout = io.TextIOWrapper(open(sys.__stdout__.fileno(), 'wb', closefd=False), encoding='utf-8')

TARGETS = [
    ('7707', "L' eau Claire", 'https://eplus.jp/sf/detail/4566210001-P0030001P021001'),
]
for eid, name, url in TARGETS:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    except Exception as ex:
        print('id%s %s FETCH失敗 %s' % (eid, name, ex)); continue
    blocks = re.findall(r'breadcrumb.{0,4000}?</ul>', h, re.S)
    print('id%s %s  breadcrumbブロック=%d' % (eid, name, len(blocks)))
    for b in blocks:
        t = re.sub(r'<[^>]+>', ' ', b)
        t = re.sub(r'\s+', ' ', _html.unescape(t)).strip()
        if '関連ジャンル' in t:
            print('   ', t[:300])
    time.sleep(1)
