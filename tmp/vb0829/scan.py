# -*- coding: utf-8 -*-
import json, os, re, sys, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath('tmp/vb0829/fetch.py')))
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'tmp/vb0829')
from fetch import get
items = json.load(open('tmp/verify_in_b_0829.json', encoding='utf-8'))
for it in items:
    u = it['urls'][0]
    h = get(u)
    t = re.search(r'(?s)<title>(.*?)</title>', h).group(1).strip()
    links = sorted(set(re.findall(r'href="([^"]*(?:ticketInformation|lot/lot\.do|event\.do\?event)[^"]*)"', h)))
    gcd = re.findall(r'(?:ntSgenreCd|genreCd)"\s*value="(\d{7})"', h)
    print('==', it['id'], u)
    print('   title:', H.unescape(t))
    print('   genreCd:', set(gcd))
    for l in links: print('   L:', H.unescape(l))
