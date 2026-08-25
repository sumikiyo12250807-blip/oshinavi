# -*- coding: utf-8 -*-
import json, os, re
BASE = r'C:/Users/user/oshinavi'
items = json.load(open(os.path.join(BASE,'tmp','verify_in_2_0825.json'), encoding='utf-8'))
out = json.load(open(os.path.join(BASE,'tmp','verify_out_2_0825.json'), encoding='utf-8'))
for it in items:
    eid = str(it['id'])
    h = open(os.path.join(BASE,'tmp','w_html','%s.html'%eid), encoding='utf-8').read()
    cards = len(re.findall(r'ticketSalesCard-2024__status', h))
    links = set(re.findall(r'ticketInformation\.do\?([^"&]*(?:lotRlsCd|rlsCd)=\d+[^"]*)', h))
    keys = set()
    for l in links:
        m = re.search(r'(lotRlsCd|rlsCd)=(\d+)', l); e = re.search(r'eventCd=(\d+)', l)
        keys.add(((e.group(1) if e else ''), m.group(1), m.group(2)))
    o = out.get(eid, {})
    print('%s cards=%-3d uniqlinks=%-3d parsed_total=%-3s buyable=%-3s' % (eid, cards, len(keys), o.get('total_cards'), o.get('buyable')))
