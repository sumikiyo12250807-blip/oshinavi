# -*- coding: utf-8 -*-
"""ぴあ rlsInfo.do の受付中一覧に、絞り込みが効く引数があるかを数件だけ試す（件数が変われば効いている）。"""
import re, sys, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'https://t.pia.jp/pia/rlsInfo.do?lg=01&rlsStatus=0101&page=1'
TRY = ['', '&area=13', '&areaCd=13', '&prefCd=13', '&pref=13', '&perfPrefCd=13', '&sg=0100102', '&sgenreCd=0100102',
       '&ntSgenreCd=0100102', '&mg=01001', '&sort=2', '&order=2', '&dispOrder=2', '&areaBlock=3']


def total(html):
    m = re.search(r'([0-9,]+)\s*件', html)
    return m.group(1) if m else '?'


for p in TRY:
    h = urllib.request.urlopen(urllib.request.Request(BASE + p, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
    first = re.findall(r'event(?:Cd|BundleCd)=([0-9a-z]+)', h)[:2]
    print('%-22s 件数=%s 先頭=%s' % (p or '(なし)', total(h), first))
    time.sleep(2)
