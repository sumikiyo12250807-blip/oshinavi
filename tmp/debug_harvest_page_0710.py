# -*- coding: utf-8 -*-
"""presale_harvest の parse_page が page1/2/3 で何を返すか直接確認。
「新規ゼロで終端」判定が正しいか、それとも取りこぼしか。"""
import re, io, sys, html, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fetch(page):
    url = 'https://t.pia.jp/pia/rlsInfo.do?lg=05&rlsIn=03&page=%d' % page
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

def parse_urls(h):
    out = []
    chunks = re.split(r'(?=<li class="listWrp_title_list clearfix">)', h)
    for body in chunks:
        am = re.search(r'<a href="([^"]*event\.do\?event(?:Bundle)?Cd=\w+)"[^>]*>(.*?)</a>', body, re.S)
        if not am:
            continue
        out.append(am.group(1).replace('http://', 'https://'))
    return out

seen = set()
for p in (1, 2, 3, 4):
    h = fetch(p)
    us = parse_urls(h)
    fresh = [u for u in us if u not in seen]
    print(f'page {p}: parse_page={len(us)}件 / 新規={len(fresh)}件')
    for u in us:
        mark = 'NEW ' if u not in seen else 'dup '
        print('   ', mark, u.split('Cd=')[-1])
    seen.update(us)
print('\n累積ユニーク', len(seen))
