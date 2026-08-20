# -*- coding: utf-8 -*-
"""ticketSalesCard-2024__place の中身と meta description の会場欄を3件ぶん出す"""
import sys, re, json
sys.path.insert(0, 'tools')
import build_pia_entries as B

URLS = {
    3272: 'https://t.pia.jp/pia/event/event.do?eventCd=2628891',
    3285: 'https://t.pia.jp/pia/event/event.do?eventCd=2629085',
    3286: 'https://t.pia.jp/pia/event/event.do?eventCd=2626459',
}
buf = []
for eid, u in URLS.items():
    h = B.fetch(u)
    buf.append(f'===== id{eid} {u}')
    places = re.findall(r'ticketSalesCard-2024__place[^>]*>(.*?)</', h, re.S)
    buf.append(f'  place要素 {len(places)}個:')
    for p in places:
        buf.append('    ' + repr(re.sub(r'\s+', ' ', p).strip()))
    md = re.search(r'<meta name="description" content="(.*?)"', h, re.S)
    if md:
        parts = [x.strip() for x in md.group(1).split('|')]
        buf.append('  meta description の区切り:')
        for i, p in enumerate(parts):
            buf.append(f'    [{i}] {p[:120]}')

open('tmp/venue_probe2.txt', 'w', encoding='utf-8').write('\n'.join(buf))
