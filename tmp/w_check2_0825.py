# -*- coding: utf-8 -*-
import json, os, re
BASE = r'C:/Users/user/oshinavi'
items = json.load(open(os.path.join(BASE,'tmp','verify_in_2_0825.json'), encoding='utf-8'))
out = json.load(open(os.path.join(BASE,'tmp','verify_out_2_0825.json'), encoding='utf-8'))
bad = []
for it in items:
    eid = str(it['id'])
    h = open(os.path.join(BASE,'tmp','w_html','%s.html'%eid), encoding='utf-8').read()
    # all ticketInformation links anywhere
    links = re.findall(r'ticketInformation\.do\?([^"\']+)', h)
    keys = set()
    for l in links:
        m = re.search(r'(lotRlsCd|rlsCd)=(\d+)', l)
        if not m: continue
        e = re.search(r'eventCd=(\d+)', l)
        keys.add(((e.group(1) if e else ''), m.group(1), m.group(2)))
    # card occurrences with context of the li item
    lis = re.split(r'(?=<li class="ticketSalesList-2024__item)', h)
    li_cards = sum(1 for x in lis if 'ticketSalesCard-2024__status' in x)
    raw_stat = len(re.findall(r'ticketSalesCard-2024__status', h))
    o = out.get(eid, {})
    flag = ''
    if len(keys) != o.get('total_cards'): flag = ' <<< MISMATCH'
    print('%s rawstat=%-3d li=%-3d uniqSlot=%-3d parsed=%-3s buy=%-3s%s' % (eid, raw_stat, li_cards, len(keys), o.get('total_cards'), o.get('buyable'), flag))
    if flag: bad.append((eid, sorted(keys)))
print()
for eid, k in bad:
    print(eid, k)
