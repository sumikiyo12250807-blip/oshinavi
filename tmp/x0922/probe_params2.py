# -*- coding: utf-8 -*-
"""sg（下位ジャンル）の番号ごとの件数と、sg と組み合わせて効く2本目の軸を探す。"""
import re, sys, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8')


def get(q):
    u = 'https://t.pia.jp/pia/rlsInfo.do?lg=01&rlsStatus=0101&page=1' + q
    h = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
    m = re.search(r'([0-9,]+)\s*件', h)
    time.sleep(1.5)
    return m.group(1) if m else '?'


for n in range(101, 116):
    print('sg=0100%d' % n, get('&sg=0100%d' % n))
for q in ['&sg=0100102&area=13', '&sg=0100102&ar=3', '&sg=0100102&areaSearchCd=13', '&sg=0100102&prefecture=13',
          '&sg=0100102&kw=a', '&sg=0100102&rlsIn=03', '&sg=0100102&perfIn=01', '&sg=0100102&pf=13', '&sg=0100102&ac=13']:
    print(q, get(q))
